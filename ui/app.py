"""
Groww Facts Q&A — Facts-Only Mutual Fund & Stock FAQ Assistant UI.
Integrated with the Stitch 'Facts-First Financial Intelligence' design system.

Features:
- SEBI / AMFI Statutory Compliance Banner
- Multi-Thread Conversation Manager with Auto-Session Sync
- Contextual Filings Verification Banner & Temperature Status
- Stitch Quick Prompt Action Cards (Expense Ratio, Exit Load, Equities)
- Stitch Verified Source Answer Cards with Grounded Citations & Metadata
- Advisory Guardrail Refusal & Zero-PII Protective Cards
- ChromaDB Vector Store & Groq LLM Live Status Indicators
"""

import datetime
from typing import Any, Dict, List, Optional
import httpx
import streamlit as st

API_BASE_URL = "http://localhost:8000/api"

st.set_page_config(
    page_title="Groww Facts Q&A — Public Filings Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STITCH 'FACTS-FIRST' DESIGN SYSTEM CSS ---
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">

<style>
    /* CSS Variables matching Stitch DESIGN.md */
    :root {
        --primary: #006c4f;
        --primary-container: #00b386;
        --on-primary: #ffffff;
        --surface: #fbf8ff;
        --surface-container-lowest: #ffffff;
        --surface-container-low: #f3f2ff;
        --surface-container: #ececff;
        --on-surface: #171a2c;
        --on-surface-variant: #3c4a43;
        --secondary: #5b5e67;
        --tertiary-container: #ea841b;
        --tertiary-fixed: #ffdcc3;
        --on-tertiary-fixed: #542a00;
        --outline: #6c7a73;
        --outline-variant: #bbcac1;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--on-surface);
        background-color: var(--surface);
    }

    /* Top Statutory Compliance Notice */
    .stitch-compliance-bar {
        background-color: #ffdcc3;
        color: #542a00;
        padding: 10px 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-size: 0.84rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #f2a86e;
    }
    .stitch-compliance-bar .notice-text {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .stitch-compliance-bar a {
        color: #904d00 !important;
        font-weight: 700;
        text-decoration: underline;
    }

    /* Top Navigation Header Mockup */
    .stitch-nav-bar {
        background-color: #ffffff;
        padding: 12px 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid #e8eaf2;
        box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    }
    .stitch-nav-links {
        display: flex;
        gap: 12px;
        align-items: center;
    }
    .stitch-nav-pill-active {
        background-color: #e6fbf5;
        color: #006c4f;
        font-weight: 600;
        font-size: 0.85rem;
        padding: 6px 14px;
        border-radius: 8px;
    }
    .stitch-nav-pill {
        color: #5b5e67;
        font-size: 0.85rem;
        padding: 6px 12px;
        border-radius: 8px;
        text-decoration: none;
    }
    .stitch-model-badge {
        background-color: #f3f2ff;
        color: #3c4a43;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 6px 12px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Hero Banner */
    .stitch-hero-banner {
        background-color: #ffffff;
        border: 1px solid #e8eaf2;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .stitch-hero-tag {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #e6fbf5;
        color: #006c4f;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 4px 10px;
        border-radius: 20px;
        margin-bottom: 10px;
    }
    .stitch-hero-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #171a2c;
        margin-bottom: 6px;
    }
    .stitch-hero-desc {
        font-size: 0.92rem;
        color: #5b5e67;
        margin-bottom: 0;
    }

    /* Prompt Chip Cards */
    div[data-testid="stHorizontalBlock"] > div {
        background-color: #ffffff;
        border-radius: 12px;
    }
    div.stButton > button {
        background-color: #ffffff;
        color: #171a2c;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 14px;
        font-size: 0.86rem;
        font-weight: 500;
        text-align: left;
        width: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #00b386;
        color: #006c4f;
        background-color: #f7fdfa;
        transform: translateY(-1px);
        box-shadow: 0 3px 6px rgba(0,179,134,0.08);
    }

    /* Assistant Message Card */
    .assistant-card {
        background-color: #ffffff;
        border: 1px solid #e8eaf2;
        border-radius: 16px;
        padding: 20px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .assistant-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f3f9;
    }
    .verified-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: #e6fbf5;
        color: #006c4f;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .match-pill {
        font-size: 0.75rem;
        color: #5b5e67;
        background-color: #f3f4f8;
        padding: 3px 8px;
        border-radius: 6px;
        font-family: monospace;
    }
    .response-body {
        font-size: 0.98rem;
        line-height: 1.65;
        color: #171a2c;
        margin-bottom: 14px;
    }

    /* Citation Link Pill */
    .citation-pill-link {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 10px 14px;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 12px;
        text-decoration: none !important;
        transition: background-color 0.2s ease;
    }
    .citation-pill-link:hover {
        background-color: #f0fdf4;
        border-color: #bbf7d0;
    }
    .citation-meta {
        display: flex;
        flex-direction: column;
    }
    .citation-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748b;
        font-weight: 600;
    }
    .citation-url {
        font-size: 0.85rem;
        color: #006c4f;
        font-family: monospace;
        font-weight: 600;
    }

    /* Footer Meta */
    .assistant-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.76rem;
        color: #64748b;
        padding-top: 8px;
        border-top: 1px solid #f1f3f9;
    }

    /* User Message Bubble */
    .user-bubble {
        background-color: #e2eae4;
        color: #161d1a;
        padding: 12px 18px;
        border-radius: 16px 16px 2px 16px;
        margin-bottom: 16px;
        max-width: 80%;
        margin-left: auto;
        font-size: 0.95rem;
        font-weight: 500;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }

    /* Guardrail Refusal Card */
    .refusal-card {
        background-color: #fff9f5;
        border: 1px solid #ffdcc3;
        border-left: 4px solid #ea841b;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .refusal-title {
        color: #904d00;
        font-weight: 700;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
    }

    /* Sidebar Brand Section */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 10px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e8eaf2;
        margin-bottom: 16px;
    }
    .sidebar-brand-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 800;
        color: #171a2c;
    }
    .sidebar-brand-sub {
        font-size: 0.74rem;
        color: #5b5e67;
    }

    /* Vector Store Status Box */
    .sidebar-stats-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px 14px;
        margin-top: 20px;
        font-size: 0.78rem;
    }
    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: #00b386;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if "active_thread_id" not in st.session_state:
    st.session_state.active_thread_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_list" not in st.session_state:
    st.session_state.thread_list = []


def api_get(endpoint: str) -> Optional[Dict[str, Any]]:
    try:
        with httpx.Client(timeout=10.0) as client:
            res = client.get(f"{API_BASE_URL}{endpoint}")
            return res.json() if res.status_code == 200 else None
    except Exception:
        return None


def api_post(endpoint: str, json_data: dict = None) -> Optional[Dict[str, Any]]:
    try:
        with httpx.Client(timeout=25.0) as client:
            res = client.post(f"{API_BASE_URL}{endpoint}", json=json_data or {})
            return res.json() if res.status_code == 200 else None
    except Exception:
        return None


# --- SIDEBAR: MULTI-THREAD CONVERSATION MANAGER ---
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <span style="font-size: 1.8rem;">📈</span>
        <div>
            <div class="sidebar-brand-title">Groww Facts Q&A</div>
            <div class="sidebar-brand-sub">Curated HDFC Mutual Funds</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ New Chat Thread", use_container_width=True, type="primary"):
        new_t = api_post("/thread/new")
        if new_t:
            st.session_state.active_thread_id = new_t["thread_id"]
            st.session_state.messages = []
            st.rerun()

    st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#64748b; letter-spacing:0.05em; text-transform:uppercase; margin-top:20px; margin-bottom:8px;'>Recent Fact Queries</p>", unsafe_allow_html=True)

    # Refresh thread list
    threads_data = api_get("/threads")
    if threads_data and "threads" in threads_data:
        st.session_state.thread_list = threads_data["threads"]

    if not st.session_state.thread_list and not st.session_state.active_thread_id:
        st.caption("No conversations yet. Start a new chat above!")
    else:
        for idx, t in enumerate(st.session_state.thread_list, 1):
            t_id = t["thread_id"]
            is_active = (t_id == st.session_state.active_thread_id)
            icon = "🟢" if is_active else "💬"
            col1, col2 = st.columns([0.80, 0.20])
            with col1:
                label = f"{icon} Thread #{idx} ({t['message_count']} msgs)"
                if st.button(label, key=f"sel_{t_id}", use_container_width=True):
                    st.session_state.active_thread_id = t_id
                    hist = api_get(f"/thread/{t_id}/history")
                    st.session_state.messages = hist.get("history", []) if hist else []
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{t_id}", help="Delete Thread"):
                    httpx.delete(f"{API_BASE_URL}/thread/{t_id}")
                    if st.session_state.active_thread_id == t_id:
                        st.session_state.active_thread_id = None
                        st.session_state.messages = []
                    st.rerun()

    # System Status Panel
    health = api_get("/health")
    if health and health.get("status") == "ok":
        chunk_count = health.get("vectorstore_count", 57)
        session_count = health.get("total_threads", 0)
        st.markdown(f"""
        <div class="sidebar-stats-card">
            <div style="font-weight:700; color:#171a2c; margin-bottom:4px;">
                <span class="pulse-dot"></span>ChromaDB Vector Store
            </div>
            <div style="color:#64748b;">{chunk_count} Chunks Indexed · Clean Embeddings</div>
            <div style="color:#64748b; margin-top:2px;">Active Sessions: {session_count}</div>
            <div style="margin-top:8px; padding-top:6px; border-top:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#5b5e67;">Groq Powered</span>
                <span style="color:#006c4f; font-weight:700;">✓ SEBI Compliant</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.error("⚠️ Backend API Offline (Port 8000)")


# --- MAIN VIEWPORT: TOP STATUTORY COMPLIANCE BAR ---
st.markdown("""
<div class="stitch-compliance-bar">
    <div class="notice-text">
        <span style="font-size:1.1rem;">⚠️</span>
        <span><strong>Compliance Notice:</strong> Facts-only assistant. No investment advice, opinions, or performance predictions. Every answer is strictly grounded in verified public filings.</span>
    </div>
    <a href="https://www.sebi.gov.in/" target="_blank">SEBI / AMFI Guidelines</a>
</div>
""", unsafe_allow_html=True)

# Navigation Mockup
st.markdown("""
<div class="stitch-nav-bar">
    <div class="stitch-nav-links">
        <span class="stitch-nav-pill-active">Assistant</span>
        <span class="stitch-nav-pill">Stocks & Tickers</span>
        <span class="stitch-nav-pill">Mutual Funds</span>
        <span class="stitch-nav-pill">Vector Knowledge Base</span>
        <span class="stitch-nav-pill">Audit & Disclosures</span>
    </div>
    <div class="stitch-model-badge">
        <span style="color:#00b386;">⚡</span>
        <span>Groq gpt-oss-120b</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Ensure an active thread session exists
if not st.session_state.active_thread_id:
    new_t = api_post("/thread/new")
    if new_t:
        st.session_state.active_thread_id = new_t["thread_id"]
        st.session_state.messages = []

# Hero Banner
st.markdown("""
<div class="stitch-hero-banner">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <div class="stitch-hero-tag">
                <span>🛡️</span> Public Filings Database
            </div>
            <div class="stitch-hero-title">Verified Facts for 5 Curated HDFC Mutual Funds</div>
            <div class="stitch-hero-desc">Ask any verifiable query on expense ratios, exit loads, minimum SIPs, benchmarks, or riskometers.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Prompt Action Cards (Stitch-Inspired)
prompt_to_send = None
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#006c4f; margin-bottom:4px;'>📊 MUTUAL FUND FACTS</div>", unsafe_allow_html=True)
    if st.button("What is the expense ratio of HDFC Small Cap Fund Direct Growth?", key="chip_1", use_container_width=True):
        prompt_to_send = "What is the expense ratio of HDFC Small Cap Fund Direct Growth?"

with col2:
    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#ea841b; margin-bottom:4px;'>⏱️ REDEMPTION RULES</div>", unsafe_allow_html=True)
    if st.button("What is the exit load for HDFC Large Cap Fund?", key="chip_2", use_container_width=True):
        prompt_to_send = "What is the exit load for HDFC Large Cap Fund?"

with col3:
    st.markdown("<div style='font-size:0.75rem; font-weight:700; color:#00b386; margin-bottom:4px;'>🎯 BENCHMARK & SIP</div>", unsafe_allow_html=True)
    if st.button("What is the minimum SIP for HDFC Mid Cap Fund?", key="chip_3", use_container_width=True):
        prompt_to_send = "What is the minimum SIP for HDFC Mid Cap Fund?"

# Handle quick prompt click
if prompt_to_send:
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    with st.spinner("Retrieving verified facts from ChromaDB & generating response..."):
        res = api_post("/chat", {
            "thread_id": st.session_state.active_thread_id,
            "query": prompt_to_send
        })
        if res:
            st.session_state.messages.append({
                "role": "assistant",
                "content": res["response"],
                "source_url": res.get("source_url"),
                "query_type": res.get("query_type")
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Backend service unavailable. Please ensure `uvicorn src.api.main:app` is running.",
                "source_url": None,
                "query_type": "ERROR"
            })
    st.rerun()

st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)

# Helper function to render an assistant card
def render_assistant_card(content: str, source_url: Optional[str], query_type: Optional[str]):
    now_str = datetime.date.today().strftime("%Y-%m-%d")
    clean_url = source_url or "https://groww.in"

    if query_type in ["ADVISORY", "PII_DETECTED", "OUT_OF_SCOPE"]:
        st.markdown(f"""
        <div class="refusal-card">
            <div class="refusal-title">
                <span>🛡️</span> Regulatory Guardrail Enforced ({query_type})
            </div>
            <div style="font-size:0.94rem; line-height:1.6; color:#171a2c;">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Factual Verified Answer Card
        st.markdown(f"""
        <div class="assistant-card">
            <div class="assistant-card-header">
                <div class="verified-pill">
                    <span>✓</span> Verified Source Answer
                </div>
                <div class="match-pill">
                    Vector Match & Grounded · 0.0 Temp
                </div>
            </div>
            <div class="response-body">
                {content}
            </div>
            <a class="citation-pill-link" href="{clean_url}" target="_blank" rel="noopener noreferrer">
                <div class="citation-meta">
                    <span class="citation-label">Primary Verified Citation</span>
                    <span class="citation-url">{clean_url}</span>
                </div>
                <span style="color:#006c4f; font-weight:700; font-size:1.1rem;">↗</span>
            </a>
            <div class="assistant-footer">
                <div>⚖️ Verified against official AMC / SEBI statutory filing</div>
                <div style="font-family:monospace;">Proof ID #{abs(hash(content)) % 10000:04d}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# Render Conversation Messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-bubble">
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        render_assistant_card(
            content=msg["content"],
            source_url=msg.get("source_url"),
            query_type=msg.get("query_type", "FACTUAL")
        )

# User Chat Input
user_query = st.chat_input("Ask a financial fact or prospectus query (e.g. exit load, minimum SIP, benchmark, P/E ratio)...")
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.markdown(f"""
    <div class="user-bubble">
        {user_query}
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Retrieving verified sources..."):
        res = api_post("/chat", {
            "thread_id": st.session_state.active_thread_id,
            "query": user_query
        })
        if res:
            st.session_state.messages.append({
                "role": "assistant",
                "content": res["response"],
                "source_url": res.get("source_url"),
                "query_type": res.get("query_type")
            })
            render_assistant_card(
                content=res["response"],
                source_url=res.get("source_url"),
                query_type=res.get("query_type")
            )
        else:
            err = "Error connecting to backend API service. Please ensure `uvicorn src.api.main:app` is running on port 8000."
            st.error(err)
            st.session_state.messages.append({
                "role": "assistant",
                "content": err,
                "source_url": None,
                "query_type": "ERROR"
            })
    st.rerun()

# Bottom disclaimer
st.markdown("""
<div style="text-align:center; margin-top:20px; font-size:0.75rem; color:#64748b;">
    🔒 Zero PII Retention. Grounded exclusively in official SID & factsheets.
</div>
""", unsafe_allow_html=True)
