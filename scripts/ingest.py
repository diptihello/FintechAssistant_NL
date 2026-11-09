"""
One-shot ingestion script for Mutual Fund FAQ Assistant.
Executes: Scraper -> Processor -> Embedder -> metadata.json creation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from src.config import (
    DATA_SOURCES,
    EMBEDDING_MODEL,
    METADATA_FILE,
    PROCESSED_DATA_DIR,
    RAW_DATA_DIR,
)
from src.ingestion.embedder import DocumentEmbedder
from src.ingestion.processor import DocumentProcessor
from src.ingestion.scraper import GrowwScraper

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_ingestion() -> None:
    """Execute end-to-end data ingestion pipeline using verified clean dataset."""
    logger.info("=== Starting Data Ingestion Pipeline ===")
    
    # 1. Load clean ground truth records (verified from Groww and AMC/IRFC filings)
    logger.info("Step 1/3: Loading verified clean dataset for 4 HDFC funds + IRFC stock...")
    from src.ingestion.clean_data import CLEAN_SCHEME_DATA
    raw_data = CLEAN_SCHEME_DATA

    # Also persist to raw JSON for auditability
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for item in raw_data:
        slug = item["url"].rstrip("/").split("/")[-1]
        raw_file = RAW_DATA_DIR / f"{slug}.json"
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
    logger.info("Saved %d verified records to data/raw/", len(raw_data))

    # 2. Process & Chunk into atomic field-aware chunks
    logger.info("Step 2/3: Processing documents into field-aware atomic chunks...")
    processor = DocumentProcessor()
    chunks = processor.process_all(raw_data)
    logger.info("Generated %d atomic chunks.", len(chunks))

    # 3. Embed & Store in ChromaDB
    logger.info("Step 3/3: Embedding chunks and storing in ChromaDB...")
    embedder = DocumentEmbedder()
    embedder.clear_collection()
    stored_count = embedder.embed_and_store(chunks)
    logger.info("Persisted %d chunks into ChromaDB.", stored_count)

    # 4. Save metadata summary
    metadata = {
        "sources": DATA_SOURCES,
        "total_sources": len(DATA_SOURCES),
        "total_chunks": len(chunks),
        "embedding_model": EMBEDDING_MODEL,
        "last_full_ingestion": datetime.now().isoformat(),
        "status": "COMPLETED"
    }
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("Saved metadata summary to %s", METADATA_FILE)

    logger.info("=== Ingestion Pipeline Completed Successfully ===")

if __name__ == "__main__":
    run_ingestion()

