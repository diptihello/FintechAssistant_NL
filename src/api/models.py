"""
Pydantic schemas for the FastAPI REST interface.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    thread_id: Optional[str] = Field(default=None, description="UUID of existing conversation thread")
    query: str = Field(..., min_length=1, max_length=500, description="User question")


class ChatResponse(BaseModel):
    thread_id: str
    query: str
    response: str
    source_url: Optional[str]
    query_type: str
    timestamp: str


class ThreadResponse(BaseModel):
    thread_id: str
    created_at: str
    message_count: int


class HistoryResponse(BaseModel):
    thread_id: str
    history: List[Dict[str, str]]


class HealthResponse(BaseModel):
    status: str
    version: str
    total_threads: int
    vectorstore_count: int

