"""
Vercel Serverless Function entry point for the FastAPI application.
Routes incoming HTTP traffic to the ASGI application.
Operates with zero-dependency, low-latency in-memory factual retrieval.
"""

import os
import sys
from pathlib import Path

# Explicitly flag Vercel serverless environment
os.environ["VERCEL"] = "1"

# Add project root to sys.path so 'src' and other modules resolve cleanly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import ASGI application
from src.api.main import app
