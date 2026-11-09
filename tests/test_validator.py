"""
Unit tests for ResponseValidator.
Verifies <=3 sentence enforcement, single-citation guarantee, footer, and PII protection.
"""

from src.guardrails.response_validator import ResponseValidator


def test_validator_sentence_truncation():
    validator = ResponseValidator()
    five_sentences = (
        "First sentence. Second sentence. Third sentence. "
        "Fourth sentence. Fifth sentence."
    )
    res = validator.validate(
        raw_response=five_sentences,
        source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        scrape_date="2026-11-08"
    )
    # The body should only have 3 sentences
    assert "Fourth sentence" not in res
    assert "Fifth sentence" not in res
    assert "First sentence" in res
    assert "Third sentence" in res


def test_validator_citation_and_footer():
    validator = ResponseValidator()
    short_answer = "The expense ratio of HDFC Small Cap Fund is 0.79%."
    res = validator.validate(
        raw_response=short_answer,
        source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        scrape_date="2026-11-08"
    )
    assert "Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in res
    assert "Last updated from sources: 2026-11-08" in res


def test_validator_pii_suppression():
    validator = ResponseValidator()
    pii_response = "Here is the details for PAN ABCDE1234F with phone 9876543210."
    res = validator.validate(
        raw_response=pii_response,
        source_url="https://groww.in",
        scrape_date="2026-11-08"
    )
    assert "ABCDE1234F" not in res
    assert "9876543210" not in res
    assert "sensitive information detection" in res

