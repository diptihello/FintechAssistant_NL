"""
Unit tests for PII Detector.
"""

from src.guardrails.pii_detector import PIIDetector


def test_detect_pan():
    detector = PIIDetector()
    res = detector.detect("My PAN is ABCDE1234F, tell me my returns")
    assert res.has_pii is True
    assert "PAN" in res.pii_types


def test_detect_aadhaar():
    detector = PIIDetector()
    res = detector.detect("Here is my Aadhaar: 1234 5678 9012")
    assert res.has_pii is True
    assert "Aadhaar" in res.pii_types


def test_detect_phone():
    detector = PIIDetector()
    res = detector.detect("Contact me at 9876543210 for fund updates")
    assert res.has_pii is True
    assert "Phone" in res.pii_types


def test_detect_email():
    detector = PIIDetector()
    res = detector.detect("Send details to investor@example.com please")
    assert res.has_pii is True
    assert "Email" in res.pii_types


def test_clean_factual_query():
    detector = PIIDetector()
    res = detector.detect("What is the expense ratio of HDFC Small Cap Fund?")
    assert res.has_pii is False
    assert len(res.pii_types) == 0

