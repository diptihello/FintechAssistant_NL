# Stitch UI Design Prompt — Mutual Fund & Stock FAQ Assistant

> **Target Tool:** Google Stitch (or AI UI/UX Generator / Claude Artifacts / v0)  
> **Product Name:** Mutual Fund & Stock FAQ Assistant (Groww-Inspired Design)  
> **Theme:** FinTech Clean / Minimalist / Trust & Compliance Focused  
> **File Location:** `docs/stitch_ui_prompt.md`

---

## Copy-Paste Prompt for Stitch

```markdown
Design a modern, high-trust, minimalist Web Application UI for a "Facts-Only Mutual Fund & Stock FAQ Assistant" inspired by the sleek FinTech aesthetic of Groww, Linear, and Stripe.

### 🎨 Visual Identity & Design System
- **Color Palette:**
  - Background: Crisp off-white `#F9FAFB` with white `#FFFFFF` card containers.
  - Primary Brand Accent: Groww Emerald Green (`#00D09C` / `#00B386`) for interactive elements, active thread indicators, and verified badges.
  - Secondary Accents: Trust Navy (`#1E2229` for headings, `#44475B` for body text), Slate Gray (`#7C7E8C` for captions/metadata).
  - Compliance Warning: Muted Amber/Ochre (`#FFF8E6` background, `#D97706` border/text) for regulatory banners.
  - Border & Dividers: Subtle `#EAECEF`.
- **Typography:** Modern clean sans-serif (Inter / Plus Jakarta Sans) with crisp hierarchy:
  - Header: Bold 20px `#1E2229`
  - Body: Regular 14px `#44475B` (line-height: 1.6)
  - Footers & Citations: Semi-bold 12px monospace or muted sans.
- **Elevation:** Subtle soft shadows (`0 2px 8px rgba(0,0,0,0.04)`), rounded card corners (12px–16px).

---

### 🖥️ Screen Layout & Key Components

#### 1. Left Sidebar — Multi-Thread Manager (Width: ~280px)
- **Header:** Brand Logo (minimalist geometric icon) + App Name: `"Groww Facts Q&A"`.
- **Primary CTA Button:** `"+ New Chat Thread"` with emerald pill styling.
- **Thread List:** Scrollable list of active conversations:
  - Each item displays thread title (e.g. *"HDFC Small Cap Expense"*, *"IRFC Market Cap"*), timestamp, message count chip (`3 msgs`), and a subtle delete icon on hover.
  - Active thread highlighted with an emerald left-border or light emerald background tint.
- **Footer:** 
  - Backend connection status indicator: Green pulsing dot with text `"ChromaDB Vector Store: 57 Chunks Indexed"`.
  - Version tag: `v1.0.0 (Groq Powered)`.

#### 2. Top Header & Regulatory Disclaimer Banner
- Persistent top disclaimer banner:
  > *"⚠️ Compliance Notice: Facts-only assistant. No investment advice, opinions, or performance predictions. Every answer is strictly grounded in verified public filings."*
- Styled in a soft amber badge with a discreet info tooltip link to AMFI/SEBI guidelines.

#### 3. Main Chat Viewport
- **Welcome / Empty State (When starting a new conversation):**
  - Friendly header: `"Verified Facts for HDFC Mutual Funds & IRFC Stock"`.
  - Sub-caption: `"Ask any verifiable query on expense ratios, exit loads, minimum SIPs, benchmarks, or stock fundamentals."`
  - **Quick Prompt Cards (3 Interactive Clickable Chips):**
    1. 📊 *"What is the expense ratio of HDFC Small Cap Fund?"*
    2. ⏱️ *"What is the exit load for HDFC Large Cap Fund?"*
    3. 🚂 *"What is the market cap & P/E ratio of IRFC?"*

- **Chat Message Bubbles:**
  - **User Bubble:** Right-aligned, subtle light slate background (`#F0F3F7`), dark text, rounded corners (16px).
  - **Assistant Bubble:** Left-aligned, white card background with thin border `#EAECEF`, soft shadow:
    - **Header:** Emerald verified badge `"Verified Source Answer"`.
    - **Response Body:** Strict maximum 2–3 concise sentences.
    - **Citation Card:** Clickable pill link: `🔗 Source: groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth`.
    - **Timestamp Footer:** `"Last updated from sources: 2026-11-08"` in muted 11px font.

- **Refusal / Advisory Bubble Style:**
  - Distinct styling for advice or comparison queries:
  - Soft warning badge: `"Advisory Query Refused (Compliance Policy)"`.
  - Polite explanation with direct educational link button: `📘 Visit AMFI Investor Knowledge Center`.

#### 4. Bottom Sticky Input Bar
- Floating rounded search/chat bar (54px height) with placeholder:
  `"Ask a factual question (e.g. exit load, minimum SIP, benchmark)..."`
- Send button: Emerald green arrow button, active state with smooth hover transition.
- Character count indicator: `0/500`.
- Privacy reminder caption below input: `"🔒 Zero PII Retention. Do not share PAN, Aadhaar, phone, or OTP credentials."`

---

### 📱 Responsive Behavior & Micro-Interactions
- Mobile-responsive sidebar collapsable into a hamburger drawer on tablets/smartphones.
- Smooth transition animations when generating responses.
- Skeleton loader effect while vector search and Groq LLM completion are executing.
```

---

## Instructions for Applying to Streamlit (`ui/app.py`)

If you want to apply this theme directly into your current Streamlit app:
1. Copy the CSS styles and color tokens into the `<style>` block in [ui/app.py](file:///d:/Dipti/NextLeap_RAG_Project_Assignment2/ui/app.py).
2. The color hex codes (`#00D09C` for Groww Emerald, `#FFF8E6` for compliance, `#1E2229` for dark navy text) match the Groww brand language.

