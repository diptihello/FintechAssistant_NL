"""
One-shot ingestion script for Mutual Fund FAQ Assistant.
Executes: Scraper -> Normalization & Cleaning -> Chunking -> Embedder -> ChromaDB -> metadata.json creation.
"""

import copy
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.config import (
    DATA_SOURCES,
    EMBEDDING_MODEL,
    METADATA_FILE,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from src.ingestion.clean_data import CLEAN_SCHEME_DATA
from src.ingestion.embedder import DocumentEmbedder
from src.ingestion.processor import DocumentProcessor
from src.ingestion.scraper import GrowwScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_ingestion() -> None:
    """Execute end-to-end data ingestion pipeline: scraping, cleaning, chunking, and embedding."""
    logger.info("=== Starting Automated Daily Ingestion Pipeline (Phase 7) ===")
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Step 1: Web Scraping from Groww sources
    logger.info("Step 1/5: Attempting live scrape of %d sources from Groww...", len(DATA_SOURCES))
    scraper = GrowwScraper(timeout=10, max_retries=2)
    scraped_results: List[Dict[str, Any]] = []
    try:
        scraped_results = scraper.scrape_all(DATA_SOURCES)
        logger.info("Scraped %d source pages.", len(scraped_results))
    except Exception as exc:
        logger.warning("Scraping encountered exception (%s). Proceeding with baseline ground truth.", exc)

    # Step 2: Data Normalization and Cleaning
    logger.info("Step 2/5: Normalizing and cleaning scraped data with ground-truth facts...")
    clean_by_url = {item["url"]: copy.deepcopy(item) for item in CLEAN_SCHEME_DATA}
    scraped_by_url = {item["url"]: item for item in scraped_results if "url" in item}

    normalized_data: List[Dict[str, Any]] = []
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for source in DATA_SOURCES:
        url = source["url"]
        record = clean_by_url.get(url, {
            "scheme_name": source["name"],
            "url": url,
            "type": source.get("type", "mutual_fund")
        })

        # Merge live scraped fields if valid (not empty / not N/A)
        scraped = scraped_by_url.get(url)
        if scraped:
            for k, v in scraped.items():
                if v and str(v).strip() != "N/A" and k not in ("raw_text_snippets",):
                    record[k] = v

        # Always update scrape_date to today
        record["scrape_date"] = today_str
        normalized_data.append(record)

        # Persist raw normalized record for auditability
        slug = url.rstrip("/").split("/")[-1]
        raw_file = RAW_DATA_DIR / f"{slug}.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

    logger.info("Saved %d normalized records to %s", len(normalized_data), RAW_DATA_DIR)

    # Step 3: Atomic Field-Aware Chunking
    logger.info("Step 3/5: Generating atomic field-aware chunks...")
    processor = DocumentProcessor()
    chunks = processor.process_all(normalized_data)
    logger.info("Generated %d atomic chunks across %d sources.", len(chunks), len(normalized_data))

    # Step 4: Embedding and Storing in ChromaDB
    logger.info("Step 4/5: Generating MiniLM embeddings and persisting into ChromaDB...")
    embedder = DocumentEmbedder()
    embedder.clear_collection()
    stored_count = embedder.embed_and_store(chunks)
    logger.info("Persisted %d chunks into ChromaDB vector store.", stored_count)

    # Step 5: Save Metadata Summary
    logger.info("Step 5/5: Updating metadata summary...")
    metadata = {
        "sources": DATA_SOURCES,
        "total_sources": len(DATA_SOURCES),
        "total_chunks": len(chunks),
        "embedding_model": EMBEDDING_MODEL,
        "last_full_ingestion": datetime.now().isoformat(),
        "last_scrape_date": today_str,
        "status": "COMPLETED"
    }
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata summary to %s", METADATA_FILE)

    logger.info("=== Phase 7 Ingestion Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_ingestion()


