"""
Retriever module using ChromaDB and SentenceTransformers.
Retrieves the most semantically relevant factual chunks for a query.
"""

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    RELEVANCE_THRESHOLD,
    RETRIEVER_TOP_K,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    text: str
    scheme_name: str
    field_name: str
    source_url: str
    scrape_date: str
    relevance_score: float


class FactRetriever:
    """Retrieves factual chunks from ChromaDB."""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        persist_dir: str = CHROMA_PERSIST_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ):
        import chromadb
        from chromadb.config import Settings
        from sentence_transformers import SentenceTransformer

        try:
            self.model = SentenceTransformer(model_name, local_files_only=True)
        except Exception:
            self.model = SentenceTransformer(model_name)

        self.client = chromadb.PersistentClient(
            path=str(Path(persist_dir).resolve()),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(name=collection_name)

    def retrieve(self, query: str, top_k: int = RETRIEVER_TOP_K) -> List[RetrievedChunk]:
        """Query vector database and return structured chunks."""
        # Query embedding
        embedding = self.model.encode(query, convert_to_numpy=True).tolist()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        chunks: List[RetrievedChunk] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return chunks

        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, dist in zip(docs, metadatas, distances):
            # Chroma returns cosine distance (0 to 2), convert to similarity: 1 - dist
            similarity = 1.0 - float(dist)
            
            chunk = RetrievedChunk(
                text=doc,
                scheme_name=meta.get("scheme_name", ""),
                field_name=meta.get("field_name", ""),
                source_url=meta.get("source_url", ""),
                scrape_date=meta.get("scrape_date", "2026-11-08"),
                relevance_score=similarity
            )
            chunks.append(chunk)

        # Filter by threshold if relevant
        filtered = [c for c in chunks if c.relevance_score >= RELEVANCE_THRESHOLD]
        return filtered if filtered else chunks[:1]

