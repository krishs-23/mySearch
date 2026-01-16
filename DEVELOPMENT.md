# Development Guide

## Project Goals
Building a local, real-time RAG system for personal documents.

## Architecture
- Vector Store: FAISS (chosen for local persistence)
- Embeddings: Google Gemini

## Retrieval Strategy
Using k=3 for nearest neighbor search to balance context and token usage.
