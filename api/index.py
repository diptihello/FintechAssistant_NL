"""
Vercel Serverless Function entry point for the FastAPI application.
Routes incoming HTTP traffic to the ASGI application.
Operates with zero-dependency factual retrieval and dynamic environment adaptation.
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
from src.api.main import app, serve_index

# Allow root UI to be served when Vercel routes /api/index or /api to this function
@app.get("/api/index")
@app.get("/api")
def root_from_api():
    return serve_index()
