# Copilot Instructions for Vector Search & N8N Project

## Architecture Overview

This is a **Weaviate-based vector search API** designed for fitness/health data analysis, running in a Docker Compose stack:
- **API Service** (`/api/`): Flask app with sentence-transformers for embedding generation  
- **Weaviate**: Vector database for similarity search
- **N8N**: Workflow automation platform
- **Dataset**: Health/fitness JSON files in `/app/data/` (users, workouts, nutrition, etc.)

The core workflow: ingest text → generate embeddings → store in Weaviate → query via similarity search.

## Key Components & Patterns

### API Structure (`/api/app.py`)
- **Single Flask file** with two main endpoints: `/ingest` (POST) and `/query` (POST)
- **Weaviate Schema**: Uses a single class `"Sentence"` with `text` and `meta` properties
- **Embedding Model**: `all-MiniLM-L6-v2` loaded once at startup for performance
- **Retry Pattern**: `ensure_schema()` function handles Weaviate startup delays with exponential backoff

### Docker & GPU Setup
- **CUDA Runtime**: API uses `nvidia/cuda:12.1.1-runtime-ubuntu22.04` base image
- **Model Pre-download**: SentenceTransformer model cached during build to avoid runtime downloads
- **GPU Allocation**: Docker Compose reserves all GPUs for the API service
- **Production Server**: Gunicorn with 2 workers + 2 threads per worker

### Development Environment
- **Two Requirements Files**: 
  - `/api/requirements.txt` (minimal Flask app deps)
  - `/requirments.txt` (typo preserved - full ML stack with FAISS, FastAPI alternatives)
- **Empty Placeholder Files**: `/app/main.py`, `/app/embeddings.py`, `/app/utils.py` exist but unused

## Critical Workflows

### Running the Stack
```bash
docker-compose up -d  # Starts all services (weaviate, n8n, api)
```
- **Weaviate**: http://localhost:8080 (vector DB admin)  
- **N8N**: http://localhost:5678 (admin/adminpassword)
- **API**: http://localhost:5000 (Flask endpoints)

### Data Ingestion Pattern
```python
# POST /ingest
{
  "text": "User workout data...",
  "meta": {"user_id": "123", "type": "workout"},
  "embedding": [0.1, 0.2, ...]  # optional - will generate if missing
}
```

### Similarity Search Pattern  
```python
# POST /query
{
  "text": "Find similar workouts",
  "embedding": [...]  # optional - will generate if missing
}
# Returns top 10 matches from Weaviate
```

## Project-Specific Conventions

### Environment Variables
- `WEAVIATE_URL`: Defaults to `http://weaviate:8080` for Docker networking
- Flask app expects Weaviate to be accessible on startup (with retries)

### Data Handling
- **Health Dataset**: 7 JSON files (users, workouts, nutrition, etc.) - treat as static reference data
- **Metadata Storage**: JSON serialized as strings in Weaviate `meta` field
- **Vector Dimensions**: SentenceTransformer outputs 384-dimensional embeddings

### Error Handling
- API returns 500 errors for Weaviate connection issues
- Schema creation is idempotent (checks existing classes before creating)
- Network timeouts handled by Docker Compose `restart: unless-stopped`

## Integration Points

- **N8N Workflows**: Can call API endpoints for vector operations in automation pipelines
- **Weaviate Direct Access**: Port 8080 exposed for direct vector DB queries/admin
- **GPU Dependency**: API service requires NVIDIA runtime for sentence-transformers acceleration

When working with this codebase, focus on the Flask API patterns, Weaviate schema management, and Docker GPU configuration rather than the empty `/app/` directory.