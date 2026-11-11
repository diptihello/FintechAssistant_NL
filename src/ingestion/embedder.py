"""
Embedder module for generating embeddings and storing chunks in ChromaDB.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from src.config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR, EMBEDDING_MODEL

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

class DocumentEmbedder:
    """Embeds textual chunks and persists them into ChromaDB."""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        persist_dir: str = CHROMA_PERSIST_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ):
        logger.info("Initializing SentenceTransformer: %s", model_name)
        self.model = SentenceTransformer(model_name)
        
        persist_path = Path(persist_dir)
        persist_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("Connecting to ChromaDB at: %s", persist_path.resolve())
        self.client = chromadb.PersistentClient(
            path=str(persist_path.resolve()),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def clear_collection(self) -> None:
        """Clear all existing records in the collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception as e:
            logger.info("Collection %s did not exist or could not be deleted: %s", self.collection_name, e)

        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Collection '%s' ready for ingestion.", self.collection_name)

    def embed_and_store(self, chunks: List[Dict[str, Any]]) -> int:
        """Generate embeddings and upsert into ChromaDB."""
        if not chunks:
            logger.warning("No chunks provided for embedding.")
            return 0

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = chunk["chunk_id"]
            # Rich context for semantic embedding
            text = f"{chunk['scheme_name']} - {chunk['field_name']}: {chunk['text']}"
            
            metadata = {
                "scheme_name": chunk.get("scheme_name", ""),
                "field_name": chunk.get("field_name", ""),
                "source_url": chunk.get("source_url", ""),
                "scrape_date": chunk.get("scrape_date", ""),
                "type": chunk.get("type", "mutual_fund"),
            }

            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(metadata)

        logger.info("Generating embeddings for %d documents...", len(documents))
        embeddings = self.model.encode(documents, convert_to_numpy=True).tolist()

        logger.info("Upserting into ChromaDB collection '%s'...", self.collection_name)
        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        total_count = self.collection.count()
        logger.info("Successfully stored chunks. Total collection count: %d", total_count)
        return len(ids)


if __name__ == "__main__":
    from src.config import PROCESSED_DATA_DIR
    chunks_path = PROCESSED_DATA_DIR / "chunks.json"
    if chunks_path.exists():
        with open(chunks_path, "r", encoding="utf-8") as f:
            sample_chunks = json.load(f)
        embedder = DocumentEmbedder()
        embedder.embed_and_store(sample_chunks)

