#!/bin/bash
set -e

echo "=== Health Data Ingestion Container ==="
echo "Waiting for API to be ready..."

# Wait for API to be available
max_attempts=60
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f -s http://api:5000/health > /dev/null 2>&1; then
        echo "✓ API is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "Attempt $attempt/$max_attempts - API not ready, waiting 5 seconds..."
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "✗ API failed to become ready after $max_attempts attempts"
    exit 1
fi

echo "Starting C++ health data ingestion..."
echo "Data directory: /data"
echo "API URL: ${API_URL:-http://api:5000/ingest}"

# Run the ingestion
/usr/local/bin/health_ingestion /data

echo "🎉 Ingestion completed successfully!"
echo "📊 Final vector database status:"

# Get final count from Weaviate
echo "Checking total records in vector database..."
RECORD_COUNT=$(curl -s -X POST http://weaviate:8080/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Aggregate { Sentence { meta { count } } } }"}' \
  | grep -o '"count":[0-9]*' | grep -o '[0-9]*' || echo "0")

echo "✅ Total records in vector database: ${RECORD_COUNT}"
echo "🌐 Vector search API available at: http://localhost:5000"
echo "🔍 Weaviate admin interface: http://localhost:8080"
echo "⚡ N8N workflows: http://localhost:5678"
echo ""
echo "🚀 System is ready for similarity search queries!"
echo "📝 To test: curl -X POST http://localhost:5000/query -H 'Content-Type: application/json' -d '{\"text\": \"cardio workout\"}'"
echo ""
echo "Container will stay alive to keep the stack running..."
echo "Press Ctrl+C to stop all services, or use: docker compose down"

# Keep container alive to maintain the stack
while true; do
    sleep 30
    # Health check - verify API is still responding
    if ! curl -f -s http://api:5000/health > /dev/null 2>&1; then
        echo "⚠️  API health check failed - services may be down"
    fi
done