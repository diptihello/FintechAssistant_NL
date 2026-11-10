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
@app.get("/api/index", include_in_schema=False)
@app.get("/api", include_in_schema=False)
def root_from_api():
    return serve_index()

# Allow Swagger UI when accessed via /api/docs
@app.get("/api/docs", include_in_schema=False)
def api_docs():
    from fastapi.openapi.docs import get_swagger_ui_html
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title=app.title + " - Swagger UI")

@app.get("/api/openapi.json", include_in_schema=False)
def api_openapi():
    from fastapi.responses import JSONResponse
    return JSONResponse(app.openapi())
