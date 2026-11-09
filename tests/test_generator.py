"""
Unit tests for ResponseGenerator.
Verifies context formatting, fallback on empty chunks, and mock LLM generation.
"""

from unittest.mock import MagicMock
import pytest
from src.rag.generator import GeneratedResponse, ResponseGenerator
from src.rag.retriever import RetrievedChunk


def test_generator_empty_chunks_fallback():
    generator = ResponseGenerator(api_key="mock_key")
    res = generator.generate(query="Sample query", chunks=[])
    assert isinstance(res, GeneratedResponse)
    assert "not have enough verified records" in res.text
    assert res.model_used == "fallback"


def test_generator_offline_mock_fallback():
    generator = ResponseGenerator(api_key=None)
    generator.client = None
    chunk = RetrievedChunk(
        text="The expense ratio of HDFC Small Cap Fund Direct Growth is 0.68%.",
        scheme_name="HDFC Small Cap Fund Direct Growth",
        field_name="expense_ratio",
        source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        scrape_date="2026-11-08",
        relevance_score=0.92,
    )
    res = generator.generate(query="What is the expense ratio?", chunks=[chunk])
    assert "0.68%" in res.text
    assert res.model_used == "offline-mock"
    assert res.source_url == chunk.source_url


def test_generator_mocked_llm_response():
    generator = ResponseGenerator(api_key="mock_key")
    generator.client = MagicMock()
    
    # Mock LLM API return
    mock_choice = MagicMock()
    mock_choice.message.content = "The expense ratio is 0.68%."
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    generator.client.chat.completions.create.return_value = mock_response

    chunk = RetrievedChunk(
        text="The expense ratio is 0.68%.",
        scheme_name="HDFC Small Cap Fund",
        field_name="expense_ratio",
        source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        scrape_date="2026-11-08",
        relevance_score=0.95,
    )

    res = generator.generate(
        query="What is the expense ratio?",
        chunks=[chunk]
    )

    assert res.text == "The expense ratio is 0.68%."
    assert res.source_url == chunk.source_url
    assert res.scrape_date == chunk.scrape_date
