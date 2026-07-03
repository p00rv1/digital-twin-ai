# 🧬 Digital Twin AI

Evidence-based clinical decision support system using Retrieval-Augmented Generation (RAG).

## Features

- Europe PMC paper ingestion
- XML parsing
- Semantic chunking
- FAISS vector search
- BM25 retrieval
- Hybrid Retrieval
- Cross Encoder reranking
- Groq LLM integration
- Patient biomarker analytics
- Literature-backed diagnosis generation

## Tech Stack

- Python
- PostgreSQL
- FAISS
- Sentence Transformers
- Groq
- Streamlit

## Architecture

Patient
↓
Snapshot
↓
Query Builder
↓
Hybrid Retrieval
↓
Cross Encoder
↓
Prompt Builder
↓
Groq LLM
↓
Diagnosis

## Future Work

- Multi-disease support
- Better evaluation metrics
- PDF report generation
