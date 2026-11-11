"""
Query Classifier module for classifying user intent.
Classifies as: FACTUAL, ADVISORY, OUT_OF_SCOPE, or PII_DETECTED.
"""

from enum import Enum
import re
from typing import Optional

from src.guardrails.pii_detector import PIIDetector


class QueryType(str, Enum):
    FACTUAL = "FACTUAL"
    ADVISORY = "ADVISORY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    PII_DETECTED = "PII_DETECTED"


class QueryClassifier:
    """Classifies user queries and provides compliant refusal responses."""

    ADVISORY_PATTERNS = [
        r"\bshould\s+i\b",
        r"\brecommend\b",
        r"\bsuggest\b",
        r"\bbetter\s+fund\b",
        r"\bbest\s+fund\b",
        r"\bgood\s+investment\b",
        r"\bwhich\s+is\s+better\b",
        r"\bbetter\s+between\b",
        r"\bwhich\s+is\s+best\b",
        r"\bwhich\s+(?:one|fund)\s+should\b",
        r"\bwill\s+it\s+grow\b",
        r"\bworth\s+investing\b",
        r"\bbuy\s+or\s+sell\b",
        r"\bhold\s+or\s+sell\b",
        r"\binvest\s+in\b",
        r"\bportfolio\s+review\b",
        r"\bwhich\s+one\b",
        r"\bbetter\s+than\b",
        r"\bversus\b",
        r"\b\s+vs\s+\b",
        r"\bcompare\b",
        r"\bprediction\b",
        r"\bwill\s+returns\b",
        r"\bforecast\b",
        r"\bguaranteed\b"
    ]

    IN_SCOPE_KEYWORDS = [
        "hdfc", "small cap", "large cap", "silver", "multi cap",
        "irfc", "railway", "indian railway finance corporation",
        "fund", "scheme", "sip", "expense ratio", "exit load", "riskometer",
        "benchmark", "nav", "aum", "lock-in", "lock in", "elss", "statement",
        "capital gains", "amc", "mutual fund", "etf", "growth", "redemption", "investment",
        "market cap", "p/e", "pe ratio", "dividend yield", "promoter holding"
    ]

    ADVISORY_REFUSAL = (
        "I am designed to provide facts only and cannot offer investment advice, "
        "opinions, or fund comparisons. For financial planning and scheme suitability, "
        "please consult a SEBI-registered investment advisor.\n\n"
        "Educational resource: https://www.amfiindia.com/investor-corner/knowledge-center.html\n"
        "Last updated from sources: 2026-11-08"
    )

    OUT_OF_SCOPE_REFUSAL = (
        "I can only answer objective, factual questions about the 4 curated HDFC mutual fund schemes "
        "(HDFC Small Cap, Large Cap, Silver ETF FoF, and Multi Cap). "
        "Please rephrase your question regarding scheme expense ratios, exit loads, minimum SIPs, benchmarks, or riskometers."
    )

    def __init__(self, pii_detector: Optional[PIIDetector] = None):
        self.pii_detector = pii_detector or PIIDetector()
        self._advisory_regexes = [re.compile(p, re.IGNORECASE) for p in self.ADVISORY_PATTERNS]

    def classify(self, query: str) -> QueryType:
        """Classify query into appropriate category."""
        clean_query = query.strip()
        if not clean_query:
            return QueryType.OUT_OF_SCOPE

        # Step 1: PII Check
        pii_res = self.pii_detector.detect(clean_query)
        if pii_res.has_pii:
            return QueryType.PII_DETECTED

        # Step 2: Advisory / Opinion / Comparison Check
        for regex in self._advisory_regexes:
            if regex.search(clean_query):
                return QueryType.ADVISORY

        # Step 3: Domain / Scope Check
        lower = clean_query.lower()
        has_mf_context = any(kw in lower for kw in self.IN_SCOPE_KEYWORDS)
        if not has_mf_context:
            return QueryType.OUT_OF_SCOPE

        return QueryType.FACTUAL

    def get_refusal_response(self, query_type: QueryType) -> str:
        """Return standardized refusal text based on classification."""
        if query_type == QueryType.PII_DETECTED:
            return self.pii_detector.get_rejection_message()
        if query_type == QueryType.ADVISORY:
            from src.config import get_latest_scrape_date
            latest_date = get_latest_scrape_date()
            return (
                "I am designed to provide facts only and cannot offer investment advice, "
                "opinions, or fund comparisons. For financial planning and scheme suitability, "
                "please consult a SEBI-registered investment advisor.\n\n"
                "Educational resource: https://www.amfiindia.com/investor-corner/knowledge-center.html\n"
                f"Last updated from sources: {latest_date}"
            )
        if query_type == QueryType.OUT_OF_SCOPE:
            return self.OUT_OF_SCOPE_REFUSAL
        return ""

