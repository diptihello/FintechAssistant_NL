"""
FastAPI application entry point.
Initializes RAG Chain, Thread Manager, and CORS middleware.
"""

import os
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from src.api.routes import router
from src.chat.thread_manager import ThreadManager
from src.rag.chain import RAGChain

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

STATIC_INDEX_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ui", "static", "index.html")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan setup."""
    logger.info("Groww Facts Q&A API starting up...")
    yield
    logger.info("Application shutdown completed.")


app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Compliant, facts-only RAG assistant for HDFC Mutual Funds.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware (permitting frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the Native Stitch Facts-Only Web Dashboard."""
    if os.path.exists(STATIC_INDEX_PATH):
        with open(STATIC_INDEX_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Groww Facts Q&A Assistant</h1><p>Visit /docs for API documentation.</p>")


if __name__ == "__main__":
    import uvicorn
    from src.config import API_HOST, API_PORT
    uvicorn.run("src.api.main:app", host=API_HOST, port=API_PORT, reload=True)


