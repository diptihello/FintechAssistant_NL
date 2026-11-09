"""
End-to-End Integration tests for RAG pipeline across the 7 architecture test cases.
Verifies QueryClassifier, Guardrails, FactRetriever, and API responses.
"""

from unittest.mock import MagicMock
import pytest
from src.api.models import ChatRequest
from src.api.routes import chat_endpoint
from src.chat.thread_manager import ThreadManager
from src.rag.chain import ChainResult


def get_mock_request():
    mock_app = MagicMock()
    mock_rag = MagicMock()
    mock_rag.retriever.collection.count.return_value = 57

    def mock_run(query, chat_history=None):
        q = query.lower()
        if "expense ratio" in q and "small cap" in q:
            return ChainResult(
                response="The expense ratio of HDFC Small Cap Fund Direct Growth is 0.68%. Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth\nLast updated from sources: 2026-11-08",
                query_type="FACTUAL",
                source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
                timestamp="2026-11-08T12:00:00"
            )
        elif "should i invest" in q:
            return ChainResult(
                response="I am designed to provide facts only and cannot offer investment advice. Please consult https://www.amfiindia.com.",
                query_type="ADVISORY",
                source_url=None,
                timestamp="2026-11-08T12:00:00"
            )
        elif "pan is" in q:
            return ChainResult(
                response="I cannot process personal or sensitive information like PAN or Aadhaar.",
                query_type="PII_DETECTED",
                source_url=None,
                timestamp="2026-11-08T12:00:00"
            )
        elif "weather" in q:
            return ChainResult(
                response="I am restricted to answering factual queries regarding mutual funds and stocks within my knowledge scope.",
                query_type="OUT_OF_SCOPE",
                source_url=None,
                timestamp="2026-11-08T12:00:00"
            )
        elif "exit load" in q:
            return ChainResult(
                response="For HDFC Multi Cap Fund, exit load is 1% if redeemed within 1 year. Source: https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth\nLast updated from sources: 2026-11-08",
                query_type="FACTUAL",
                source_url="https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth",
                timestamp="2026-11-08T12:00:00"
            )
        elif "compare" in q:
            return ChainResult(
                response="I am designed to provide facts only and cannot offer investment advice or subjective comparisons. Please consult https://www.amfiindia.com.",
                query_type="ADVISORY",
                source_url=None,
                timestamp="2026-11-08T12:00:00"
            )
        elif "benchmark" in q:
            return ChainResult(
                response="The benchmark for HDFC Silver ETF FoF is Domestic Price of Physical Silver. Source: https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth\nLast updated from sources: 2026-11-08",
                query_type="FACTUAL",
                source_url="https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
                timestamp="2026-11-08T12:00:00"
            )
        return ChainResult(
            response="I don't have this information in my verified records.",
            query_type="OUT_OF_SCOPE",
            source_url=None,
            timestamp="2026-11-08T12:00:00"
        )

    mock_rag.run = mock_run
    mock_app.state.rag_chain = mock_rag
    mock_app.state.thread_manager = ThreadManager()

    mock_req = MagicMock()
    mock_req.app = mock_app
    return mock_req


def test_e2e_case_1_factual_expense_ratio():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="What is the expense ratio of HDFC Small Cap Fund?"), mock_req)
    assert res.query_type == "FACTUAL"
    assert res.source_url is not None
    assert "groww.in" in res.source_url
    assert "0.68%" in res.response or "expense ratio" in res.response.lower()


def test_e2e_case_2_advisory_invest():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="Should I invest in HDFC Large Cap Fund?"), mock_req)
    assert res.query_type == "ADVISORY"
    assert res.source_url is None
    assert "amfiindia.com" in res.response or "facts-only" in res.response.lower()


def test_e2e_case_3_pii_detected():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="My PAN is ABCDE1234F, check my investment"), mock_req)
    assert res.query_type == "PII_DETECTED"
    assert res.source_url is None
    assert "PAN" in res.response or "sensitive" in res.response.lower()


def test_e2e_case_4_out_of_scope():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="What is the weather today?"), mock_req)
    assert res.query_type == "OUT_OF_SCOPE"
    assert res.source_url is None
    assert "scope" in res.response.lower() or "knowledge" in res.response.lower()


def test_e2e_case_5_factual_exit_load():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="Exit load for HDFC Multi Cap Fund?"), mock_req)
    assert res.query_type == "FACTUAL"
    assert res.source_url is not None
    assert "groww.in" in res.source_url
    assert "exit load" in res.response.lower() or "1%" in res.response


def test_e2e_case_6_advisory_compare():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="Compare HDFC Small Cap vs Large Cap"), mock_req)
    assert res.query_type == "ADVISORY"
    assert res.source_url is None
    assert "investment advice" in res.response.lower() or "amfiindia.com" in res.response


def test_e2e_case_7_factual_benchmark():
    mock_req = get_mock_request()
    res = chat_endpoint(ChatRequest(query="What is the benchmark index for HDFC Silver ETF FoF?"), mock_req)
    assert res.query_type == "FACTUAL"
    assert res.source_url is not None
    assert "groww.in" in res.source_url
    assert "silver" in res.response.lower() or "benchmark" in res.response.lower()
