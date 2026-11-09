"""
FastAPI route definitions for Chat, Threads, and Health checks.
"""

from fastapi import APIRouter, HTTPException, Request

from src.api.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    HistoryResponse,
    ThreadResponse,
)

router = APIRouter(prefix="/api")


def _get_singletons(request: Request):
    """Retrieve or lazily initialize singletons."""
    rag_chain = getattr(request.app.state, "rag_chain", None)
    if rag_chain is None:
        from src.rag.chain import RAGChain
        rag_chain = RAGChain()
        request.app.state.rag_chain = rag_chain

    thread_mgr = getattr(request.app.state, "thread_manager", None)
    if thread_mgr is None:
        from src.chat.thread_manager import ThreadManager
        thread_mgr = ThreadManager()
        request.app.state.thread_manager = thread_mgr

    return rag_chain, thread_mgr


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, request: Request):
    """Send query and receive grounded, facts-only cited response."""
    rag_chain, thread_mgr = _get_singletons(request)

    # 1. Resolve or create thread
    thread_id = req.thread_id
    if not thread_id or not thread_mgr.get_thread(thread_id):
        thread_id = thread_mgr.create_thread()

    # 2. Get past history for conversational continuity
    history = thread_mgr.get_history(thread_id)

    # 3. Process query through RAG pipeline
    result = rag_chain.run(query=req.query, chat_history=history)

    # 4. Update thread history
    thread_mgr.add_message(thread_id, role="user", content=req.query)
    thread_mgr.add_message(thread_id, role="assistant", content=result.response)

    return ChatResponse(
        thread_id=thread_id,
        query=req.query,
        response=result.response,
        source_url=result.source_url,
        query_type=result.query_type,
        timestamp=result.timestamp,
    )


@router.post("/thread/new", response_model=ThreadResponse)
def create_thread_endpoint(request: Request):
    """Initialize a brand-new independent chat thread."""
    _, thread_mgr = _get_singletons(request)
    t_id = thread_mgr.create_thread()
    thread = thread_mgr.get_thread(t_id)
    return ThreadResponse(
        thread_id=t_id,
        created_at=thread.created_at.isoformat(),
        message_count=0
    )


@router.get("/threads")
def list_threads_endpoint(request: Request):
    """List active thread sessions."""
    _, thread_mgr = _get_singletons(request)
    return {"threads": thread_mgr.list_threads()}


@router.get("/thread/{thread_id}/history", response_model=HistoryResponse)
def get_history_endpoint(thread_id: str, request: Request):
    """Retrieve message history for a specific thread."""
    _, thread_mgr = _get_singletons(request)
    thread = thread_mgr.get_thread(thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found or expired")
    return HistoryResponse(thread_id=thread_id, history=thread.history)


@router.delete("/thread/{thread_id}")
def delete_thread_endpoint(thread_id: str, request: Request):
    """Delete thread session."""
    _, thread_mgr = _get_singletons(request)
    deleted = thread_mgr.delete_thread(thread_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"deleted": True, "thread_id": thread_id}


@router.get("/health", response_model=HealthResponse)
def health_check(request: Request):
    """System health check and stats."""
    rag_chain, thread_mgr = _get_singletons(request)
    count = rag_chain.retriever.collection.count()
    return HealthResponse(
        status="ok",
        version="1.0.0",
        total_threads=len(thread_mgr.list_threads()),
        vectorstore_count=count
    )

