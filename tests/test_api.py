"""
Unit & Integration tests for FastAPI endpoints.
Tests /api/health, /api/thread/new, /api/chat, /api/thread/{id}/history, and /api/thread/{id}.
"""

from unittest.mock import MagicMock
import pytest
from src.api.models import ChatRequest
from src.api.routes import (
    chat_endpoint,
    create_thread_endpoint,
    delete_thread_endpoint,
    get_history_endpoint,
    health_check,
    list_threads_endpoint,
)
from src.chat.thread_manager import ThreadManager
from src.rag.chain import ChainResult


def get_mock_request():
    mock_app = MagicMock()
    mock_rag = MagicMock()
    mock_rag.retriever.collection.count.return_value = 57

    def mock_run(query, chat_history=None):
        if "expense ratio" in query.lower():
            return ChainResult(
                response="The expense ratio of HDFC Small Cap Fund Direct Growth is 0.68%. Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth\nLast updated from sources: 2026-11-08",
                query_type="FACTUAL",
                source_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
                timestamp="2026-11-08T12:00:00"
            )
        elif "invest" in query.lower():
            return ChainResult(
                response="I am designed to provide facts only and cannot offer investment advice. Please consult https://www.amfiindia.com.",
                query_type="ADVISORY",
                source_url=None,
                timestamp="2026-11-08T12:00:00"
            )
        elif "pan" in query.lower():
            return ChainResult(
                response="I cannot process personal or sensitive information like PAN or Aadhaar.",
                query_type="PII_DETECTED",
                source_url=None,
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


def test_api_health():
    mock_req = get_mock_request()
    res = health_check(mock_req)
    assert res.status == "ok"
    assert res.vectorstore_count >= 40


def test_api_thread_lifecycle():
    mock_req = get_mock_request()

    # 1. Create thread
    new_res = create_thread_endpoint(mock_req)
    assert new_res.thread_id is not None
    t_id = new_res.thread_id

    # 2. Get history (should be empty initially)
    hist_res = get_history_endpoint(t_id, mock_req)
    assert len(hist_res.history) == 0

    # 3. List threads
    list_res = list_threads_endpoint(mock_req)
    assert len(list_res["threads"]) == 1

    # 4. Delete thread
    del_res = delete_thread_endpoint(t_id, mock_req)
    assert del_res["deleted"] is True


def test_api_chat_factual():
    mock_req = get_mock_request()
    req = ChatRequest(query="What is the expense ratio of HDFC Small Cap Fund?")
    res = chat_endpoint(req, mock_req)
    assert res.query_type == "FACTUAL"
    assert "0.68%" in res.response
    assert "https://groww.in" in res.source_url


def test_api_chat_advisory_refusal():
    mock_req = get_mock_request()
    req = ChatRequest(query="Should I invest in HDFC Small Cap Fund?")
    res = chat_endpoint(req, mock_req)
    assert res.query_type == "ADVISORY"
    assert "amfiindia.com" in res.response


def test_api_chat_pii_rejection():
    mock_req = get_mock_request()
    req = ChatRequest(query="My PAN is ABCDE1234F, show my report")
    res = chat_endpoint(req, mock_req)
    assert res.query_type == "PII_DETECTED"
    assert "cannot process personal or sensitive information" in res.response


def test_api_serve_index():
    from src.api.main import serve_index
    response = serve_index()
    assert response.status_code == 200
    assert "Groww Facts Q&A" in response.body.decode("utf-8")
