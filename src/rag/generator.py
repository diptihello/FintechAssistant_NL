"""
Generator module using Groq LLM (llama-3.3-70b-versatile).
Generates facts-only responses using retrieved context.
"""

from dataclasses import dataclass
import logging
from typing import List, Optional
from groq import Groq

from src.config import (
    GROQ_API_KEY,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
)
from src.rag.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.rag.retriever import RetrievedChunk

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class GeneratedResponse:
    text: str
    source_url: str
    scrape_date: str
    model_used: str


class ResponseGenerator:
    """Generates answers strictly grounded in retrieved factual chunks."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ):
        self.api_key = api_key or GROQ_API_KEY
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = Groq(api_key=self.api_key) if self.api_key else None

    def generate(
        self,
        query: str,
        chunks: List[RetrievedChunk],
        chat_history: Optional[List[dict]] = None
    ) -> GeneratedResponse:
        """Call Groq LLM with retrieved context and prompt constraints."""
        if not chunks:
            return GeneratedResponse(
                text="I do not have enough verified records to answer this query. Please check the official scheme portal.",
                source_url="https://groww.in",
                scrape_date="2026-11-08",
                model_used="fallback"
            )

        # Primary source URL is taken from the top chunk
        primary_url = chunks[0].source_url
        scrape_date = chunks[0].scrape_date

        # Context assembly
        context_body = "\n\n".join(
            f"[{c.scheme_name} - {c.field_name}]: {c.text}" for c in chunks
        )

        user_content = USER_PROMPT_TEMPLATE.format(context=context_body, query=query)

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Inject conversation history if available (last few turns)
        if chat_history:
            for turn in chat_history[-4:]:
                messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})

        messages.append({"role": "user", "content": user_content})

        if not self.client:
            # Fallback mock for testing without API key
            raw_text = chunks[0].text
            return GeneratedResponse(
                text=raw_text,
                source_url=primary_url,
                scrape_date=scrape_date,
                model_used="offline-mock"
            )

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            raw_text = completion.choices[0].message.content.strip()
            return GeneratedResponse(
                text=raw_text,
                source_url=primary_url,
                scrape_date=scrape_date,
                model_used=self.model_name
            )
        except Exception as e:
            logger.error("Groq API call error: %s", e)
            # Fallback to top retrieved chunk sentence
            return GeneratedResponse(
                text=chunks[0].text,
                source_url=primary_url,
                scrape_date=scrape_date,
                model_used="retrieval-fallback"
            )

