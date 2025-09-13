#!/bin/bash

echo "🔍 Checking Vector Database Records..."
echo "======================================"

# Check if Weaviate is running
if ! curl -f -s http://localhost:8080/v1/.well-known/ready > /dev/null 2>&1; then
    echo "❌ Weaviate is not running or not ready"
    echo "💡 Start with: sudo docker compose up -d"
    exit 1
fi

echo "✅ Weaviate is running"

# Get record count from Weaviate
echo "📊 Querying database..."

RESPONSE=$(curl -s -X POST http://localhost:8080/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Aggregate { Sentence { meta { count } } } }"}')

if [ $? -eq 0 ]; then
    # Extract count using jq if available, otherwise use grep
    if command -v jq > /dev/null 2>&1; then
        RECORD_COUNT=$(echo "$RESPONSE" | jq -r '.data.Aggregate.Sentence[0].meta.count // 0')
    else
        RECORD_COUNT=$(echo "$RESPONSE" | grep -o '"count":[0-9]*' | grep -o '[0-9]*' | head -1)
        if [ -z "$RECORD_COUNT" ]; then
            RECORD_COUNT="0"
        fi
    fi
    
    echo ""
    echo "📈 Total Records in Vector Database: $RECORD_COUNT"
    echo ""
    
    if [ "$RECORD_COUNT" -gt 0 ]; then
        echo "🎉 Database contains health data records!"
        echo "🔗 Query API: curl -X POST http://localhost:5000/query -H 'Content-Type: application/json' -d '{\"text\": \"your search query\"}'"
    else
        echo "⚠️  Database is empty - ingestion may not have completed yet"
        echo "🔄 Check ingestion status: sudo docker compose logs ingestion"
    fi
else
    echo "❌ Failed to query database"
    echo "🔧 Check if all services are running: sudo docker compose ps"
fi

echo ""
echo "🌐 Available endpoints:"
echo "   • Vector Search API: http://localhost:5000"
echo "   • Weaviate Admin:    http://localhost:8080"
echo "   • N8N Workflows:     http://localhost:5678"