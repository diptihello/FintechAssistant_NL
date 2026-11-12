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


def test_retriever_exit_load(retriever):
    chunks = retriever.retrieve("What is the exit load for HDFC Large Cap Fund?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Large Cap" in top.scheme_name
    assert top.field_name == "exit_load"


def test_retriever_mid_cap_expense_ratio(retriever):
    chunks = retriever.retrieve("What is the expense ratio of HDFC Mid Cap Fund?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Mid Cap" in top.scheme_name
    assert top.field_name == "expense_ratio"
    assert "0.6%" in top.text


def test_retriever_silver_benchmark(retriever):
    chunks = retriever.retrieve("What is the benchmark index for HDFC Silver ETF FoF?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Silver" in top.scheme_name
    assert top.field_name == "benchmark"


def test_retriever_mid_cap_nav(retriever):
    chunks = retriever.retrieve("What is the NAV of HDFC Mid Cap Fund?", top_k=3)
    assert len(chunks) > 0
    top = chunks[0]
    assert "HDFC Mid Cap" in top.scheme_name
    fields = [c.field_name for c in chunks]
    assert "nav" in fields or "overview" in fields
    assert any("227.10" in c.text for c in chunks)




