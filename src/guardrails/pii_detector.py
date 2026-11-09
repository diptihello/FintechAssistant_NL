"""
PII Detector module for detecting and preventing processing of sensitive personal information.
Patterns: PAN, Aadhaar, Phone, Email, OTP.
"""

import re
from dataclasses import dataclass, field
from typing import List


@dataclass
class PIIResult:
    has_pii: bool
    pii_types: List[str] = field(default_factory=list)
    sanitized_text: str = ""


class PIIDetector:
    """Detects and rejects personal identifiable information (PII)."""

    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
    AADHAAR_PATTERN = re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}\b")
    PHONE_PATTERN = re.compile(r"\b[6-9]\d{9}\b")
    EMAIL_PATTERN = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w{2,}\b")
    OTP_PATTERN = re.compile(r"\b(?:otp|verify|code)\b.*?\b\d{4,6}\b", re.IGNORECASE)

    REJECTION_MESSAGE = (
        "I cannot process personal or sensitive information such as PAN, Aadhaar, "
        "phone numbers, email addresses, or OTPs. Please do not share personal credentials. "
        "For account-related queries, please visit the official HDFC Mutual Fund portal directly."
    )

    def detect(self, text: str) -> PIIResult:
        """Scan input query for any matching PII pattern."""
        detected = []

        if self.PAN_PATTERN.search(text):
            detected.append("PAN")
        if self.AADHAAR_PATTERN.search(text):
            # Exclude standard 4-digit years like 2024, 2025, 2026
            match = self.AADHAAR_PATTERN.search(text).group(0)
            digits_only = re.sub(r"\D", "", match)
            if len(digits_only) == 12:
                detected.append("Aadhaar")
        if self.PHONE_PATTERN.search(text):
            detected.append("Phone")
        if self.EMAIL_PATTERN.search(text):
            detected.append("Email")
        if self.OTP_PATTERN.search(text):
            detected.append("OTP")

        has_pii = len(detected) > 0
        return PIIResult(has_pii=has_pii, pii_types=detected, sanitized_text=text)

    def get_rejection_message(self) -> str:
        """Return standardized canned refusal message."""
        return self.REJECTION_MESSAGE

