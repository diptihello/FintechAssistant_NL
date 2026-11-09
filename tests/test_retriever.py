"""
Unit tests for FactRetriever.
Verifies vector similarity search against the populated ChromaDB collection.
"""

import pytest
from src.rag.retriever import FactRetriever


@pytest.fixture(scope="module")
def retriever():
    return FactRetriever()


def test_retriever_initialization(retriever):
    assert retriever.collection is not None
    assert retriever.collection.count() >= 40


def test_retriever_expense_ratio(retriever):
    chunks = retriever.retrieve("What is the expense ratio of HDFC Small Cap Fund?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Small Cap" in top.scheme_name
    assert top.field_name == "expense_ratio"
    assert "groww.in" in top.source_url


def test_retriever_irfc_stock(retriever):
    chunks = retriever.retrieve("What is the market cap of IRFC?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "Indian Railway Finance Corporation" in top.scheme_name
    assert "groww.in/stocks" in top.source_url


def test_retriever_exit_load(retriever):
    chunks = retriever.retrieve("What is the exit load for HDFC Large Cap Fund?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Large Cap" in top.scheme_name
    assert top.field_name == "exit_load"


