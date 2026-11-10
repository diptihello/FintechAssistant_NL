"""
Document processor for chunking structured mutual fund data into field-aware chunks.
Generates deterministic IDs and metadata for vector store insertion.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes scraped scheme facts into granular, field-aware chunks."""

    def __init__(self, processed_dir: Optional[Path] = None):
        self.processed_dir = processed_dir or PROCESSED_DATA_DIR
        try:
            self.processed_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    @staticmethod
    def generate_chunk_id(url: str, field_name: str) -> str:
        """Create deterministic chunk ID using md5 hash."""
        key = f"{url}:{field_name}".encode("utf-8")
        return hashlib.md5(key).hexdigest()

    def process_scheme(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert a scheme's raw factual record into multiple atomic facts/chunks."""
        scheme_name = data.get("scheme_name", "Mutual Fund Scheme")
        url = data.get("url", "")
        scrape_date = data.get("scrape_date", "2026-11-08")
        scheme_type = data.get("type", "mutual_fund")

        # Field definitions mapping to clean statements
        fields_map = [
            ("expense_ratio", f"The expense ratio of {scheme_name} is {data.get('expense_ratio')}."),
            ("exit_load", f"The exit load for {scheme_name} is {data.get('exit_load')}."),
            ("min_sip", f"The minimum SIP (Systematic Investment Plan) amount for {scheme_name} is {data.get('min_sip')}."),
            ("min_lumpsum", f"The minimum lump sum investment amount for {scheme_name} is {data.get('min_lumpsum')}."),
            ("benchmark", f"The benchmark index for {scheme_name} is {data.get('benchmark')}."),
            ("riskometer", f"The riskometer classification for {scheme_name} is {data.get('riskometer')}."),
            ("category", f"{scheme_name} belongs to the category: {data.get('category')}."),
            ("fund_manager", f"The fund manager for {scheme_name} is {data.get('fund_manager')}."),
            ("lock_in", f"The lock-in period for {scheme_name} is {data.get('lock_in')}."),
            ("tax_treatment", f"Taxation rules for {scheme_name}: {data.get('tax_treatment', 'Subject to standard capital gains taxation rules under the Income Tax Act.')}"),
            ("statements_download", (
                f"For downloading statements, statement of account (SoA), or capital gains reports for {scheme_name}, "
                f"investors can visit the official AMC website (hdfcfund.com) or CAMS/MFCentral online portals using PAN and Folio."
            ))
        ]

        chunks = []
        for field_name, sentence in fields_map:
            chunk_id = self.generate_chunk_id(url, field_name)
            chunk = {
                "chunk_id": chunk_id,
                "text": sentence,
                "scheme_name": scheme_name,
                "field_name": field_name,
                "source_url": url,
                "scrape_date": scrape_date,
                "type": scheme_type
            }
            chunks.append(chunk)

        # Overview chunk
        overview_id = self.generate_chunk_id(url, "overview")
        overview_text = (
            f"{scheme_name} ({data.get('category')}) has an expense ratio of {data.get('expense_ratio')}, "
            f"exit load of {data.get('exit_load')}, minimum SIP of {data.get('min_sip')}, "
            f"and benchmark {data.get('benchmark')}. Risk is classified as {data.get('riskometer')}."
        )
        chunks.append({
            "chunk_id": overview_id,
            "text": overview_text,
            "scheme_name": scheme_name,
            "field_name": "overview",
            "source_url": url,
            "scrape_date": scrape_date,
            "type": scheme_type
        })

        return chunks

    def process_stock(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert stock record (e.g. IRFC) into atomic factual chunks."""
        name = data.get("scheme_name", "Indian Railway Finance Corporation Ltd (IRFC)")
        url = data.get("url", "")
        scrape_date = data.get("scrape_date", "2026-11-08")

        stock_fields = [
            ("market_cap", f"The market capitalization of {name} is {data.get('market_cap')}."),
            ("pe_ratio", f"The Price-to-Earnings (P/E) ratio of {name} is {data.get('pe_ratio')}."),
            ("dividend_yield", f"The dividend yield of {name} is {data.get('dividend_yield')}."),
            ("pb_ratio", f"The Price-to-Book (P/B) ratio of {name} is {data.get('pb_ratio', '4.1')}."),
            ("52w_high_low", f"The 52-week high for {name} is {data.get('high_52w')} and the 52-week low is {data.get('low_52w')}."),
            ("sector", f"{name} operates in the {data.get('sector')} sector ({data.get('industry')})."),
            ("promoter_holding", f"The promoter holding of {name} is {data.get('promoter_holding')}."),
            ("reports_download", f"Official financial statements, annual reports, quarterly investor presentations, and shareholder disclosures for {name} can be downloaded from the official IRFC investor relations portal (irfc.co.in) or BSE/NSE website disclosures.")
        ]

        chunks = []
        for field_name, sentence in stock_fields:
            chunk_id = self.generate_chunk_id(url, field_name)
            chunks.append({
                "chunk_id": chunk_id,
                "text": sentence,
                "scheme_name": name,
                "field_name": field_name,
                "source_url": url,
                "scrape_date": scrape_date,
                "type": "stock"
            })

        overview_id = self.generate_chunk_id(url, "overview")
        chunks.append({
            "chunk_id": overview_id,
            "text": f"{name} is a PSU infrastructure finance company in {data.get('sector')} with a market cap of {data.get('market_cap')}, P/E ratio of {data.get('pe_ratio')}, dividend yield of {data.get('dividend_yield')}, and promoter holding of {data.get('promoter_holding')}.",
            "scheme_name": name,
            "field_name": "overview",
            "source_url": url,
            "scrape_date": scrape_date,
            "type": "stock"
        })
        return chunks

    def process_all(self, raw_items: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Process all raw data files or in-memory items and save processed chunks."""
        if raw_items is None:
            raw_items = []
            for file_path in RAW_DATA_DIR.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_items.append(json.load(f))

        all_chunks = []
        for item in raw_items:
            if item.get("type") == "stock":
                chunks = self.process_stock(item)
            else:
                chunks = self.process_scheme(item)
            all_chunks.extend(chunks)

        try:
            out_file = self.processed_dir / "chunks.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(all_chunks, f, indent=2, ensure_ascii=False)
            logger.info("Processed %d total chunks saved to %s", len(all_chunks), out_file)
        except OSError as e:
            logger.warning("Read-only filesystem detected (%s). Chunks processed in-memory only.", e)
        return all_chunks


if __name__ == "__main__":
    processor = DocumentProcessor()
    res = processor.process_all()
    print(f"Generated {len(res)} chunks.")

