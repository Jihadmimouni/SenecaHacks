# Flask Vector Search API

A Flask-based API service for health data vector similarity search using Weaviate and sentence transformers.

## Overview

This API provides endpoints for ingesting text data and performing semantic similarity searches using vector embeddings. It uses the `all-MiniLM-L6-v2` model from sentence-transformers to generate embeddings and Weaviate as the vector database.

## Architecture

- **Flask**: Web framework for REST API endpoints
- **Weaviate**: Vector database for storing and searching embeddings
- **SentenceTransformer**: `all-MiniLM-L6-v2` model for generating 384-dimensional embeddings
- **Docker**: Containerized deployment with GPU support

## API Endpoints

### Health Check
```http
GET /health
```
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "weaviate": "connected"
}
```

### Ingest Data
```http
POST /ingest
```
Ingests text data with optional metadata and generates embeddings.

**Request Body:**
```json
{
  "text": "User completed a 30-minute cardio workout",
  "meta": {
    "user_id": "user123",
    "date": "2024-01-15",
    "type": "workout"
  },
  "embedding": [0.1, 0.2, ...] // Optional - will generate if not provided
}
```

**Response:**
```json
{
  "status": "ok",
  "message": "Data ingested successfully"
}
```

### Query Similarity Search
```http
POST /query
```
Performs semantic similarity search against stored embeddings.

**Request Body:**
```json
{
  "text": "Find similar cardio workouts",
  "embedding": [0.1, 0.2, ...] // Optional - will generate if not provided
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "User completed a 45-minute running session",
      "meta": {
        "user_id": "user456",
        "date": "2024-01-14",
        "type": "workout"
      },
      "distance": 0.15
    }
  ]
}
```

## Configuration

### Environment Variables

- `WEAVIATE_URL`: Weaviate instance URL (default: `http://weaviate:8080`)
- `FLASK_ENV`: Flask environment (development/production)

### Weaviate Schema

The API uses a single Weaviate class `"Sentence"` with the following properties:

```python
{
    "class": "Sentence",
    "vectorizer": "none",
    "properties": [
        {
            "name": "text",
            "dataType": ["text"]
        },
        {
            "name": "meta",
            "dataType": ["text"]
        }
    ]
}
```

## Usage Examples

### Basic Ingestion
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "User ran 5km in Central Park",
    "meta": {
      "user_id": "alice",
      "activity": "running",
      "location": "Central Park"
    }
  }'
```

### Similarity Search
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "outdoor running activities"
  }' | jq .
```

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export WEAVIATE_URL=http://localhost:8080

# Run development server
python app.py
```

### Docker Build
```bash
# Build image
docker build -t vector-api .

# Run with GPU support
docker run --gpus all -p 5000:5000 vector-api
```

## Performance

- **Model Loading**: SentenceTransformer model is loaded once at startup
- **GPU Acceleration**: CUDA support for faster embedding generation
- **Retry Logic**: Automatic retry with exponential backoff for Weaviate connectivity
- **Production Server**: Gunicorn with 2 workers and 2 threads per worker

## Dependencies

See `requirements.txt`:
- Flask==2.3.3
- weaviate-client==3.25.0
- sentence-transformers==2.2.2
- gunicorn==21.2.0

## Error Handling

The API implements comprehensive error handling:

- **Weaviate Connection**: Retries with exponential backoff during startup
- **Invalid Requests**: Returns appropriate HTTP status codes
- **Schema Management**: Automatic schema creation and validation
- **GPU Fallback**: Graceful fallback to CPU if GPU unavailable

## Monitoring

- Health check endpoint for container orchestration
- Detailed logging for debugging and monitoring
- Schema validation on startup
- Connection pooling for Weaviate client

## Security Considerations

- Input validation for JSON payloads
- Rate limiting (recommended for production)
- Authentication (to be implemented)
- CORS configuration (if needed for web frontend)