"""
Configuration module for the Mutual Fund FAQ Assistant.
Loads settings from environment variables with sensible defaults.
Uses Groq as the LLM provider.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure HuggingFace Hub and transformers use local cached weights locally, while allowing download in serverless environments (Vercel)
if os.getenv("VERCEL") != "1":
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
else:
    os.environ["HF_HUB_OFFLINE"] = "0"
    os.environ["TRANSFORMERS_OFFLINE"] = "0"
    os.environ.setdefault("HF_HOME", "/tmp/huggingface")
    os.environ.setdefault("TRANSFORMERS_CACHE", "/tmp/huggingface")
    os.environ.setdefault("TORCH_HOME", "/tmp/torch")

# Load .env file
load_dotenv()

# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if os.getenv("VERCEL") == "1":
    DATA_DIR = Path("/tmp/data")
    RAW_DATA_DIR = Path("/tmp/raw")
    PROCESSED_DATA_DIR = Path("/tmp/processed")
    METADATA_FILE = Path("/tmp/metadata.json")
else:
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    METADATA_FILE = DATA_DIR / "metadata.json"
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore" / "chroma_db"

# ── LLM (Groq) ─────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "200"))

# ── Embedding ──────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# ── ChromaDB ───────────────────────────────────────────────────────────────────
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(VECTORSTORE_DIR))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "mutual_fund_facts")

# ── RAG ────────────────────────────────────────────────────────────────────────
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "5"))
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.3"))

# ── Server ─────────────────────────────────────────────────────────────────────
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))

# ── Thread management ─────────────────────────────────────────────────────────
THREAD_EXPIRY_MINUTES = int(os.getenv("THREAD_EXPIRY_MINUTES", "30"))
MAX_HISTORY_TURNS = int(os.getenv("MAX_HISTORY_TURNS", "10"))

# ── Data sources (4 HDFC Mutual Funds + 1 Stock: IRFC) ────────────────────────
DATA_SOURCES = [
    {
        "type": "mutual_fund",
        "name": "HDFC Small Cap Fund - Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    },
    {
        "type": "mutual_fund",
        "name": "HDFC Large Cap Fund - Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    },
    {
        "type": "mutual_fund",
        "name": "HDFC Silver ETF FoF - Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    },
    {
        "type": "mutual_fund",
        "name": "HDFC Multi Cap Fund - Direct Growth",
        "url": "https://groww.in/mutual-funds/hdfc-multi-cap-fund-direct-growth",
    },
    {
        "type": "stock",
        "name": "Indian Railway Finance Corporation Ltd (IRFC)",
        "url": "https://groww.in/stocks/indian-railway-finance-corporation-ltd",
    },
]
