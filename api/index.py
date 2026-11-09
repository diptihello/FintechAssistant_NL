"""
Vercel Serverless Function entry point for the FastAPI application.
Routes incoming HTTP traffic to the ASGI application.
Adapts ephemeral /tmp filesystem for ChromaDB SQLite storage and HuggingFace cache.
"""

import os
import sys
from pathlib import Path

# Mark environment as Vercel
os.environ["VERCEL"] = "1"

# Add project root to sys.path so 'src' and other modules resolve
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# On AWS Lambda / Vercel, the local root is read-only; configure /tmp for writable assets
os.environ["HF_HOME"] = "/tmp/huggingface"
os.environ["TRANSFORMERS_CACHE"] = "/tmp/huggingface"
os.environ["TORCH_HOME"] = "/tmp/torch"
os.environ["CHROMA_PERSIST_DIR"] = "/tmp/chroma_db"

# Ensure ChromaDB vector store is populated in /tmp on first cold start
tmp_chroma = Path("/tmp/chroma_db")
if not tmp_chroma.exists() or not any(tmp_chroma.iterdir()):
    try:
        from scripts.ingest import run_ingestion
        run_ingestion()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Vercel cold-start ingestion: %s", e)

from src.api.main import app

