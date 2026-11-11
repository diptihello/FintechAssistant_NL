"""
Response Validator module for post-processing and enforcing RAG response constraints.
Constraints: Max 3 sentences, exactly one citation URL, footer with last updated date, and PII protection.
"""

import re
from typing import Optional

from src.guardrails.pii_detector import PIIDetector


class ResponseValidator:
    """Enforces facts-only formatting constraints on final generated answers."""

    def __init__(self, pii_detector: Optional[PIIDetector] = None):
        self.pii_detector = pii_detector or PIIDetector()

    @staticmethod
    def count_sentences(text: str) -> int:
        """Count sentences by standard punctuation delimiters."""
        clean = text.strip()
        if not clean:
            return 0
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        return len([s for s in sentences if s.strip()])

    @staticmethod
    def truncate_to_sentences(text: str, max_sentences: int = 3) -> str:
        """Limit response body to at most max_sentences."""
        clean = text.strip()
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        if len(sentences) <= max_sentences:
            return clean
        return " ".join(sentences[:max_sentences]).strip()

    def validate(
        self,
        raw_response: str,
        source_url: str,
        scrape_date: Optional[str] = None
    ) -> str:
        """
        Validate and format the output:
        1. Strip PII if any accidentally produced.
        2. Enforce <= 3 sentences for main response body.
        3. Enforce exactly 1 source citation link.
        4. Append 'Last updated from sources: <date>' footer.
        """
        if not scrape_date:
            from src.config import get_latest_scrape_date
            scrape_date = get_latest_scrape_date()
        # Strip accidental PII
        pii_res = self.pii_detector.detect(raw_response)
        if pii_res.has_pii:
            return (
                "Response omitted due to potential sensitive information detection. "
                "Please verify scheme details on the official HDFC Mutual Fund website."
            )

        # Extract existing URL if any
        url_match = re.search(r"https?://[^\s)\]]+", raw_response)
        body = re.sub(r"https?://[^\s)\]]+", "", raw_response).strip()
        body = re.sub(r"Last updated from sources:.*$", "", body, flags=re.MULTILINE | re.IGNORECASE).strip()
        body = re.sub(r"Source:.*$", "", body, flags=re.MULTILINE | re.IGNORECASE).strip()

        # Enforce max 3 sentences on body
        truncated_body = self.truncate_to_sentences(body, max_sentences=3)
        if not truncated_body.endswith((".", "!", "?")):
            truncated_body += "."

        # Guarantee citation URL
        final_url = source_url if source_url else (url_match.group(0) if url_match else "https://groww.in")

        # Guarantee footer
        footer = f"Last updated from sources: {scrape_date}"

        return f"{truncated_body}\n\nSource: {final_url}\n{footer}"

