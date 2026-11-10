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
    """Retrieves factual chunks from ChromaDB (with zero-dependency serverless fallback)."""

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        persist_dir: str = CHROMA_PERSIST_DIR,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ):
        self.use_lightweight = os.getenv("VERCEL") == "1"
        self.chunks_cache = None

        if not self.use_lightweight:
            try:
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
            except Exception as exc:
                logger.info("ChromaDB/PyTorch unavailable (%s). Initializing serverless ranker.", exc)
                self.use_lightweight = True

        if self.use_lightweight:
            self._load_lightweight_corpus()

    def _load_lightweight_corpus(self) -> None:
        """Load in-memory factual chunks for zero-dependency serverless environments."""
        from src.ingestion.clean_data import CLEAN_SCHEME_DATA
        from src.ingestion.processor import DocumentProcessor

        processor = DocumentProcessor()
        self.chunks_cache = processor.process_all(CLEAN_SCHEME_DATA)

        class MockCollection:
            def __init__(self, count: int):
                self._count = count
            def count(self) -> int:
                return self._count

        self.collection = MockCollection(len(self.chunks_cache))

    def _retrieve_lightweight(self, query: str, top_k: int = 5) -> List[RetrievedChunk]:
        """Rank chunks using term-frequency and field relevance for serverless runtime."""
        import re
        query_words = set(re.findall(r"\w+", query.lower()))
        scored = []

        for c in self.chunks_cache or []:
            text_lower = c["text"].lower()
            field_lower = c.get("field_name", "").lower()
            scheme_lower = c.get("scheme_name", "").lower()

            score = 0.0
            for w in query_words:
                if len(w) <= 2:
                    continue
                if w in field_lower:
                    score += 3.0
                if w in scheme_lower:
                    score += 2.0
                if w in text_lower:
                    score += 1.0

            scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: List[RetrievedChunk] = []
        for score, c in scored[:top_k]:
            if score > 0:
                results.append(
                    RetrievedChunk(
                        text=c["text"],
                        scheme_name=c["scheme_name"],
                        field_name=c["field_name"],
                        source_url=c["source_url"],
                        scrape_date=c.get("scrape_date", "2026-11-10"),
                        relevance_score=min(1.0, score / 10.0),
                    )
                )

        if not results and self.chunks_cache:
            c = self.chunks_cache[0]
            results.append(
                RetrievedChunk(
                    text=c["text"],
                    scheme_name=c["scheme_name"],
                    field_name=c["field_name"],
                    source_url=c["source_url"],
                    scrape_date=c.get("scrape_date", "2026-11-10"),
                    relevance_score=0.5,
                )
            )
        return results

    def retrieve(self, query: str, top_k: int = RETRIEVER_TOP_K) -> List[RetrievedChunk]:
        """Query vector database or serverless ranker and return structured chunks."""
        if self.use_lightweight:
            return self._retrieve_lightweight(query, top_k)

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

        filtered = [c for c in chunks if c.relevance_score >= RELEVANCE_THRESHOLD]
        return filtered if filtered else chunks[:1]

