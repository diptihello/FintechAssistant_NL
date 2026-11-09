"""
Multi-thread chat session manager for handling independent user conversations.
Maintains history, isolation, and automatic session cleanup.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import uuid

from src.config import MAX_HISTORY_TURNS, THREAD_EXPIRY_MINUTES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ChatThread:
    thread_id: str
    created_at: datetime
    last_active: datetime
    history: List[Dict[str, str]] = field(default_factory=list)
    max_history: int = MAX_HISTORY_TURNS * 2  # 10 turns = 20 messages


class ThreadManager:
    """Manages multi-thread independent chat sessions."""

    def __init__(self, expiry_minutes: int = THREAD_EXPIRY_MINUTES):
        self.expiry_minutes = expiry_minutes
        self._threads: Dict[str, ChatThread] = {}
        self._lock = asyncio.Lock()

    def create_thread(self) -> str:
        """Create and register a new chat thread."""
        thread_id = str(uuid.uuid4())
        now = datetime.now()
        self._threads[thread_id] = ChatThread(
            thread_id=thread_id,
            created_at=now,
            last_active=now,
            history=[]
        )
        logger.info("Created new thread session: %s", thread_id)
        return thread_id

    def get_thread(self, thread_id: str) -> Optional[ChatThread]:
        """Retrieve thread if valid and unexpired."""
        thread = self._threads.get(thread_id)
        if not thread:
            return None

        # Expiry check
        if datetime.now() - thread.last_active > timedelta(minutes=self.expiry_minutes):
            logger.info("Thread %s has expired due to inactivity.", thread_id)
            del self._threads[thread_id]
            return None

        return thread

    def add_message(self, thread_id: str, role: str, content: str) -> None:
        """Append user or assistant message to thread history."""
        thread = self.get_thread(thread_id)
        if not thread:
            thread_id = self.create_thread()
            thread = self._threads[thread_id]

        thread.history.append({"role": role, "content": content})
        if len(thread.history) > thread.max_history:
            thread.history = thread.history[-thread.max_history:]
        thread.last_active = datetime.now()

    def get_history(self, thread_id: str) -> List[Dict[str, str]]:
        """Return history for a specific thread."""
        thread = self.get_thread(thread_id)
        return thread.history if thread else []

    def list_threads(self) -> List[Dict[str, str]]:
        """List all active thread IDs and creation times."""
        active = []
        for t_id, thread in list(self._threads.items()):
            if datetime.now() - thread.last_active <= timedelta(minutes=self.expiry_minutes):
                active.append({
                    "thread_id": t_id,
                    "created_at": thread.created_at.isoformat(),
                    "message_count": len(thread.history)
                })
        return active

    def delete_thread(self, thread_id: str) -> bool:
        """Delete thread from memory."""
        if thread_id in self._threads:
            del self._threads[thread_id]
            logger.info("Deleted thread: %s", thread_id)
            return True
        return False

    def cleanup_expired(self) -> int:
        """Prune inactive threads exceeding expiry threshold."""
        now = datetime.now()
        expired = [
            t_id for t_id, t in self._threads.items()
            if now - t.last_active > timedelta(minutes=self.expiry_minutes)
        ]
        for t_id in expired:
            del self._threads[t_id]
        if expired:
            logger.info("Cleaned up %d expired threads.", len(expired))
        return len(expired)

