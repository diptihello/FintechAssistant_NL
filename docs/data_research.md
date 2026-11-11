# Data Research & RAG Architecture Optimization Report

> **Project:** Mutual Fund FAQ Assistant (Facts-Only Q&A)  
> **Location:** `docs/data_research.md`  
> **Scope:** Ground truth analysis on clean dataset, optimal chunking strategy, embedding model benchmark, and vector database evaluation.

---

## 1. Executive Summary & Clean Data Audit

An empirical audit of the raw scraped records from Groww revealed significant semantic parsing nuances across the 5 target assets (5 HDFC mutual fund schemes):

### Key Observations from Raw Data
1. **Dynamic Text Conflation:** On mutual fund pages, key investment constraints (such as *"Minimum SIP Investment is set to ₹100"* and *"Exit load of 1% if redeemed within 1 year"*) appear grouped inside unstructured fund overview text blocks rather than individual standalone CSS selectors.
2. **Tabular Formatting:** Dynamic tables on scheme pages require clean key-value normalization to prevent label-value offset collisions.
3. **Requirement for High-Fidelity Ground Truth:** To guarantee **zero hallucination** and strict regulatory compliance, the RAG knowledge base must ingest clean, verified facts containing unambiguous figures, terms, and regulatory footnotes.

---

## 2. Chunking Strategy Research & Recommendations

### Comparison of Chunking Methodologies

| Chunking Strategy | Description | Precision for Facts | Risk for FAQ RAG | Recommendation |
| :--- | :--- | :---: | :--- | :---: |
| **Fixed-Size Character Chunking** (e.g. 500 chars, 50 overlap) | Blind character slicing | 🔴 Low | High risk of splitting a financial figure (e.g. `1.0%` separated from `if redeemed within 1 year`) | **Reject** |
| **Hierarchical / Recursive Chunking** | Splits by headers, then paragraphs | 🟡 Medium | Inefficient for small tabular financial metric lookups | **Reject** |
| **Field-Aware Atomic Chunking** (Entity + Metric) | One self-contained declarative sentence per metric with entity prefix | 🟢 **Ultra-High** | Near-zero cross-metric contamination; exact match for query intent | **Adopt** |

### Selected Chunking Strategy: **Field-Aware Atomic Chunking**
Every chunk is constructed as a **self-contained semantic unit**:
```
Chunk Structure:
[Entity Name] - [Metric Name]: [Clean Fact Statement with full context]
```

#### Examples:
- **Small Cap Exit Load:**
  > `"HDFC Small Cap Fund Direct Growth - exit_load: The exit load for HDFC Small Cap Fund Direct Growth is 1.0% if redeemed or switched out on or before 1 year from the date of allotment; Nil thereafter."`
- **Mid Cap Expense Ratio:**
  > `"HDFC Mid Cap Fund Direct Growth - expense_ratio: The expense ratio of HDFC Mid Cap Fund Direct Growth is 0.6%."`
- **ELSS / Lock-in Inquiry:**
  > `"HDFC Small Cap Fund Direct Growth - lock_in: The lock-in period for HDFC Small Cap Fund Direct Growth is Nil (It is an open-ended equity fund with no statutory lock-in period)."`

#### Benefits:
- **Context Length:** 120–250 characters per chunk (optimal for dense retrieval).
- **Zero Ambiguity:** Entity name is always present, eliminating pronoun ambiguity.
- **Deterministic MD5 ID:** `md5(url + ":" + field_name)` ensures idempotent upserts into vector store.

---

## 3. Embedding Model Benchmark & Evaluation

| Embedding Model | Dim | MTEB Retrieval Score | Latency (CPU) | Storage Footprint | Suitability for this Project |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`sentence-transformers/all-MiniLM-L6-v2`** | **384** | **56.3** | **~8 ms / query** | **~80 MB** | **Recommended & Selected:** Fast, lightweight, zero API cost, runs locally on CPU with high accuracy for short FAQ queries. |
| `BAAI/bge-small-en-v1.5` | 384 | 58.4 | ~12 ms / query | ~130 MB | Higher accuracy but slightly larger latency and memory requirements. |
| `text-embedding-3-small` (OpenAI) | 1536 | 62.3 | ~150 ms (Network) | Remote | Requires paid external OpenAI key and adds network latency. |
| `Groq Embeddings` | N/A | N/A | N/A | N/A | Groq does not currently provide a native embeddings inference endpoint (LLM completions only). |

**Conclusion:** `sentence-transformers/all-MiniLM-L6-v2` is the optimal model for this project's requirements: deterministic, local, runs on CPU with zero network latency or rate-limit concerns.

---

## 4. Vector Database Architecture & Evaluation

| Vector Store | Deployment Mode | Metadata Filtering | Concurrency / Persistence | Recommendation |
| :--- | :--- | :--- | :--- | :--- |
| **ChromaDB** | **Embedded / Local Persistent** | **Full HNSW Cosine + Metadata Filter** | **Zero-config SQLite/parquet backing** | **Adopted (Current)** |
| FAISS | In-memory library | Basic | No native metadata storage (requires external map) | Suboptimal |
| Qdrant / Pinecone | Client-server / Managed cloud | Advanced | Requires docker container or cloud account setup | Overkill for 5 sources |

**Storage Strategy in ChromaDB:**
- **Distance Metric:** Cosine similarity (`hnsw:space: "cosine"`).
- **Metadata Fields:** `scheme_name`, `field_name`, `source_url`, `scrape_date`, `type`.
- **Top-K:** `K = 3` with relevance score threshold `>= 0.3`.

---

## 5. Phase 3 & Implementation Plan Updates

To reflect this data research:
1. Seed the ingestion pipeline with [src/ingestion/clean_data.py](file:///d:/Dipti\NextLeap_RAG_Project_Assignment2\src\ingestion\clean_data.py) so raw scraped values are validated against verified ground truth facts.
2. Update [docs/implementation-plan.md](file:///d:/Dipti\NextLeap_RAG_Project_Assignment2\docs\implementation-plan.md) with the verified chunking taxonomy and embedding benchmarks.

