# Approach Explanation - Round 1B: Persona-Driven Document Intelligence

## 🧠 Objective
The goal of this challenge is to extract and prioritize relevant sections from a set of PDFs, based on a given persona and their specific task (job to be done), and present a structured output. The entire solution must work **offline**, be **CPU-only**, run within **60 seconds**, and use models under **1GB**.

---

## 🏗️ Solution Architecture

Our solution is modular, efficient, and designed for fast offline execution:

### 1. **PDF Parsing and Section Segmentation (`parser.py`)**
We parse all PDFs using PyMuPDF (`fitz`) and extract document sections using a robust **multi-signal heading detection heuristic**:
- Bold text or `Bold` font names
- Uppercase text
- Numbered headings (e.g., 2.1.3)
- Short line length
- Extra spacing (layout-aware)

This allows us to identify `H1`, `H2`, or `H3`-like sections even in PDFs where font size is inconsistent. We avoid false positives like headers/footers by checking for repetition and location.

---

### 2. **Semantic Relevance Ranking (`engine.py`)**

We use a **two-stage retrieval system**:
- **Bi-Encoder (fast)**: `all-MiniLM-L6-v2` (65MB) encodes the persona+job query and all section texts for quick top-K candidate filtering via cosine similarity.
- **Cross-Encoder (precise)**: `ms-marco-MiniLM-L-6-v2` (120MB) re-ranks top candidates based on the actual query-section pairs.

We also apply a **keyword boost** system where titles with context-relevant words (e.g., "trip", "group", "food", "nightlife") receive a small score bump.

---

### 3. **Subsection Refinement**
From each top-ranked section, we extract the **top 5 semantically relevant sentences** to create a concise and targeted summary. Sentences are selected based on cosine similarity and reordered to preserve flow.

---

## 📦 Deployment (Docker)

The pipeline is packaged in a Docker image with:
- Pre-downloaded models (no internet required at runtime)
- Only CPU dependencies
- Total model + code size well below 1GB
- Average runtime < 60 seconds for 5–7 PDFs

---

## ✅ Compliance with Constraints

| Constraint                   | Status      |
|-----------------------------|-------------|
| Offline-only                | ✅ Fully offline (models downloaded at build) |
| CPU-only                    | ✅ Docker disables GPU/CUDA |
| Model size ≤ 1GB            | ✅ Total ~185MB |
| Execution time ≤ 60s        | ✅ Runs in ~30–40s for 5 PDFs |
| Input/output folder format  | ✅ Compliant |
| Output structure (JSON)     | ✅ As per spec |

---

## 🧠 Why This Works
The strength of our solution lies in its ability to **intelligently extract document structure**, and use **semantic understanding** to adaptively prioritize content — all within limited resources. It scales well, avoids brittle assumptions like font-size-only parsing, and focuses on end-task relevance.

---

**Submitted by:** [Your Name or Team]  
**Track:** Adobe India Hackathon 2025 - Round 1B  
