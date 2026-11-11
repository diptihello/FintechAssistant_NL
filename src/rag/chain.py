"""
RAG Chain orchestration module.
Coordinates: Input Sanitization -> PII Check -> Query Classification -> 
             Vector Retrieval -> LLM Generation -> Output Validation.
"""

from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from src.guardrails.classifier import QueryClassifier, QueryType
from src.guardrails.pii_detector import PIIDetector
from src.guardrails.response_validator import ResponseValidator
from src.rag.generator import ResponseGenerator
from src.rag.retriever import FactRetriever

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ChainResult:
    response: str
    query_type: str
    source_url: Optional[str]
    timestamp: str


class RAGChain:
    """Full end-to-end RAG pipeline with safety guardrails."""

    def __init__(
        self,
        retriever: Optional[FactRetriever] = None,
        generator: Optional[ResponseGenerator] = None,
        classifier: Optional[QueryClassifier] = None,
        validator: Optional[ResponseValidator] = None,
    ):
        self.retriever = retriever or FactRetriever()
        self.generator = generator or ResponseGenerator()
        self.pii_detector = PIIDetector()
        self.classifier = classifier or QueryClassifier(self.pii_detector)
        self.validator = validator or ResponseValidator(self.pii_detector)

    def run(self, query: str, chat_history: Optional[List[Dict[str, str]]] = None) -> ChainResult:
        """Process user query and return compliant, fact-checked response."""
        now_ts = datetime.now().isoformat()
        clean_query = query.strip()[:500]

        # Step 1: Classify Query (handles PII and Advisory checks)
        q_type = self.classifier.classify(clean_query)

        if q_type in (QueryType.PII_DETECTED, QueryType.ADVISORY, QueryType.OUT_OF_SCOPE):
            refusal_text = self.classifier.get_refusal_response(q_type)
            return ChainResult(
                response=refusal_text,
                query_type=q_type.value,
                source_url=None,
                timestamp=now_ts
            )

        # Step 2: Retrieve relevant facts from vector store
        chunks = self.retriever.retrieve(clean_query)
        if not chunks:
            from src.config import get_latest_scrape_date
            fallback = (
                "I do not have verified records matching your query in the curated HDFC & IRFC database. "
                "Please verify directly on the official portal."
            )
            return ChainResult(
                response=f"{fallback}\n\nSource: https://groww.in\nLast updated from sources: {get_latest_scrape_date()}",
                query_type=QueryType.FACTUAL.value,
                source_url="https://groww.in",
                timestamp=now_ts
            )

        # Step 3: LLM Generation
        generated = self.generator.generate(clean_query, chunks, chat_history=chat_history)

        # Step 4: Validate and enforce formatting (<=3 sentences, citation, footer)
        validated_text = self.validator.validate(
            raw_response=generated.text,
            source_url=generated.source_url,
            scrape_date=generated.scrape_date
        )

        return ChainResult(
            response=validated_text,
            query_type=QueryType.FACTUAL.value,
            source_url=generated.source_url,
            timestamp=now_ts
        )

