# Vector Search & N8N Health Data Platform

A comprehensive health and fitness data processing platform using vector similarity search, workflow automation, and high-performance data ingestion. Built with Weaviate vector database, Flask API, N8N workflows, and optimized C++ processing.

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd Project

# Start all services
sudo docker compose up -d

# Check service status
sudo docker compose ps

# Access services
# - API: http://localhost:5000
# - N8N: http://localhost:5678 (admin/adminpassword)
# - Weaviate: http://localhost:8080
```

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Services](#services)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Data Processing](#data-processing)
- [Performance](#performance)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This platform processes health and fitness data from multiple sources, generates semantic embeddings using sentence transformers, and provides similarity search capabilities through a vector database. It's designed for analyzing user health patterns, workout similarities, nutrition trends, and comprehensive health insights.

### Key Capabilities

- **Vector Similarity Search**: Find similar workouts, nutrition patterns, and health activities
- **Workflow Automation**: N8N integration for automated data pipelines  
- **High-Performance Processing**: C++ ingestion system for large datasets
- **Real-time API**: RESTful endpoints for data ingestion and querying
- **Scalable Architecture**: Docker-based microservices with GPU acceleration

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Health Data   │    │   Processing    │    │  Vector Search  │
│   Sources       │───▶│   Pipeline      │───▶│   & Analytics   │
│                 │    │                 │    │                 │
│ • Activities    │    │ • C++ Ingestion │    │ • Weaviate DB   │
│ • Workouts      │    │ • Python Scripts│    │ • Flask API     │
│ • Nutrition     │    │ • Data Cleaning │    │ • Similarity    │
│ • Sleep         │    │ • Summarization │    │   Search        │
│ • Heart Rate    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                    ┌─────────────────┐
                    │   N8N Workflow  │
                    │   Automation    │
                    │                 │
                    │ • Scheduling    │
                    │ • Monitoring    │
                    │ • Integration   │
                    │ • Alerting      │
                    └─────────────────┘
```

### Technology Stack

- **🐍 Python**: Flask API, data processing scripts, machine learning
- **⚡ C++**: High-performance ingestion system with libcurl and nlohmann/json
- **🔍 Weaviate**: Vector database for similarity search and semantic indexing
- **🔄 N8N**: Workflow automation and integration platform
- **🐳 Docker**: Containerized deployment with GPU support
- **🤖 ML**: SentenceTransformers for embedding generation (all-MiniLM-L6-v2)

## ✨ Features

### Vector Search Capabilities
- **Semantic Similarity**: Find similar activities, workouts, and health patterns
- **User Profiling**: Comprehensive user health profiles with temporal data
- **Pattern Recognition**: Identify trends in health and fitness behaviors
- **Recommendation Engine**: Suggest similar activities based on user preferences

### Data Processing
- **Multi-format Support**: JSON, CSV, and streaming data processing
- **Real-time Ingestion**: Live data processing with configurable batch sizes
- **Memory Optimization**: Efficient processing of large datasets (6.5GB+)
- **Data Validation**: Comprehensive input validation and error handling

### Workflow Automation
- **Scheduled Processing**: Automated data ingestion and processing pipelines
- **Event-driven Workflows**: Trigger processing based on data availability
- **Monitoring & Alerting**: Real-time status monitoring with notifications
- **Integration Ready**: Connect with external APIs and data sources

### Performance & Scalability
- **GPU Acceleration**: CUDA support for faster embedding generation
- **Concurrent Processing**: Parallel data processing and API calls
- **Optimized Storage**: Efficient vector storage and retrieval
- **Horizontal Scaling**: Docker-based scaling for high-throughput scenarios

## 🔧 Services

### Flask API Service (`/api`)
RESTful API for data ingestion and vector similarity search.

**Key Features:**
- `/ingest` endpoint for data ingestion with embedding generation
- `/query` endpoint for semantic similarity search
- Health checks and monitoring endpoints
- GPU-accelerated sentence transformer integration

**[📖 Full API Documentation →](api/README.md)**

### C++ Ingestion System (`/app/cpp_ingestion`)
High-performance data processing engine for large-scale health data ingestion.

**Key Features:**
- Processes 50,000+ records per second
- Memory-efficient streaming JSON processing
- Configurable batch processing (1-1000 records)
- Concurrent HTTP requests with retry logic

**[📖 Full C++ Documentation →](app/cpp_ingestion/README.md)**

### Python Data Scripts (`/app/data`)
Python utilities for data processing, analysis, and API integration.

**Key Features:**
- Memory-efficient JSON streaming with ijson
- Asynchronous HTTP requests with aiohttp
- Progress monitoring and error handling
- Health dataset structure documentation

**[📖 Full Data Documentation →](app/data/README.md)**

### N8N Workflow Platform
Web-based workflow automation for data pipeline orchestration.

**Access:** http://localhost:5678 (admin/adminpassword)

**Capabilities:**
- Visual workflow designer
- Scheduled data processing
- API integration and monitoring
- Event-driven automation

### Weaviate Vector Database
Specialized vector database for similarity search and semantic indexing.

**Access:** http://localhost:8080

**Features:**
- 384-dimensional vector storage
- GraphQL and REST APIs
- Real-time similarity search
- Persistent data storage

## 💻 Installation

### Prerequisites

**System Requirements:**
- Linux/macOS/Windows with Docker support
- 8GB+ RAM (16GB recommended for large datasets)
- NVIDIA GPU (optional, for acceleration)
- 20GB+ disk space

**Software Dependencies:**
```bash
# Docker & Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# NVIDIA Container Toolkit (optional, for GPU support)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Installation Steps

1. **Clone Repository**
```bash
git clone <repository-url>
cd Project
```

2. **Start Services**
```bash
# Build and start all services
sudo docker compose up -d --build

# Verify services are running
sudo docker compose ps
```

3. **Verify Installation**
```bash
# Check API health
curl http://localhost:5000/health

# Check Weaviate status
curl http://localhost:8080/v1/.well-known/ready

# Access N8N interface
open http://localhost:5678
```

**[📖 Complete Docker Guide →](DOCKER.md)**

## 📊 Usage

### Data Ingestion

#### Using the C++ High-Performance Ingester
```bash
# Run ingestion with default settings (1000 records per batch)
sudo docker compose logs ingestion -f

# Monitor progress
sudo docker compose exec ingestion tail -f /var/log/ingestion.log
```

#### Using Python Scripts
```bash
# Run Python ingestion
sudo docker compose exec api python /data/main.py

# Custom configuration
BATCH_SIZE=500 python /data/main.py
```

### API Usage Examples

#### Ingest Health Data
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John completed a 30-minute cardio workout, burned 320 calories",
    "meta": {
      "user_id": "john_doe",
      "date": "2024-01-15",
      "type": "workout"
    }
  }'
```

#### Similarity Search
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Find similar cardio workouts"
  }' | jq .
```

### N8N Workflow Creation

1. Access N8N at http://localhost:5678
2. Login with admin/adminpassword
3. Create workflows for:
   - Scheduled data processing
   - API monitoring and alerting
   - Data pipeline orchestration
   - Integration with external services

## 📚 API Documentation

### Core Endpoints

#### Health Check
```http
GET /health
```
Returns API and database connectivity status.

#### Data Ingestion
```http
POST /ingest
Content-Type: application/json

{
  "text": "Natural language description of health activity",
  "meta": {
    "user_id": "string",
    "date": "YYYY-MM-DD",
    "type": "activity_type"
  },
  "embedding": [0.1, 0.2, ...] // Optional, generated if not provided
}
```

#### Similarity Search
```http
POST /query
Content-Type: application/json

{
  "text": "Search query for similar activities",
  "embedding": [0.1, 0.2, ...] // Optional, generated if not provided
}
```

### Response Formats

#### Successful Ingestion
```json
{
  "status": "ok",
  "message": "Data ingested successfully",
  "id": "uuid-generated-id"
}
```

#### Search Results
```json
{
  "results": [
    {
      "text": "Similar activity description",
      "meta": {
        "user_id": "user123",
        "date": "2024-01-14",
        "type": "workout"
      },
      "distance": 0.15,
      "id": "result-uuid"
    }
  ],
  "query_time_ms": 45
}
```

## 🗂️ Data Processing

### Health Dataset Schema

The platform processes various health data types:

#### User Profiles
```json
{
  "user_id": "unique_identifier",
  "name": "User Name",
  "age": 30,
  "gender": "male/female",
  "height": 180,
  "weight": 75,
  "fitness_level": "beginner/intermediate/advanced"
}
```

#### Activity Data
```json
{
  "user_id": "user123",
  "date": "2024-01-15",
  "activity_type": "running/cycling/swimming",
  "duration": 30,
  "distance": 5.2,
  "calories_burned": 320,
  "heart_rate_avg": 145
}
```

#### Nutrition Data  
```json
{
  "user_id": "user123",
  "date": "2024-01-15",
  "meal_type": "breakfast/lunch/dinner",
  "calories": 450,
  "protein": 25,
  "carbs": 40,
  "fat": 18
}
```

### Processing Pipeline

1. **Data Validation**: Input sanitization and format validation
2. **User Enrichment**: Combine activity data with user profiles
3. **Daily Aggregation**: Group activities by user and date
4. **Summary Generation**: Create natural language descriptions
5. **Embedding Generation**: Convert text to 384-dimensional vectors
6. **Vector Storage**: Store in Weaviate for similarity search
7. **Indexing**: Create searchable indices for fast retrieval

## ⚡ Performance

### Benchmarks

#### C++ Ingestion System
- **Processing Speed**: 50,000+ records/second
- **Memory Usage**: ~200MB peak for large datasets
- **Batch Processing**: Optimized for 1000 records per batch
- **API Throughput**: 1000 concurrent requests supported

#### Python Processing
- **Standard Mode**: ~5,000 records/second
- **Optimized Mode**: ~15,000 records/second
- **Memory Efficiency**: Streaming processing for 6.5GB+ datasets
- **Async Processing**: Concurrent API requests with aiohttp

#### Vector Search Performance
- **Search Latency**: <50ms for typical queries
- **Index Size**: ~2GB for 1M vectors (384 dimensions)
- **Concurrent Queries**: 100+ simultaneous searches
- **Storage Efficiency**: Compressed vector storage

### Optimization Features

- **GPU Acceleration**: CUDA support for 3-5x faster embedding generation
- **Memory Optimization**: Streaming processing and efficient data structures
- **Connection Pooling**: Persistent HTTP connections for API calls
- **Batch Optimization**: Configurable batch sizes for optimal throughput
- **Caching**: In-memory caching for frequently accessed data

## 🛠️ Development

### Project Structure

```
Project/
├── README.md                    # This file
├── DOCKER.md                    # Docker deployment guide
├── docker-compose.yml           # Service orchestration
├── .github/                     # GitHub workflows and templates
│   └── copilot-instructions.md  # AI assistant guidelines
├── api/                         # Flask API service
│   ├── app.py                   # Main API application
│   ├── Dockerfile               # API container build
│   ├── requirements.txt         # Python dependencies
│   └── README.md               # API documentation
├── app/
│   ├── cpp_ingestion/          # High-performance C++ ingester
│   │   ├── health_processor.cpp # Core processing logic
│   │   ├── health_processor.hpp # Header definitions
│   │   ├── main.cpp            # CLI entry point
│   │   ├── CMakeLists.txt      # Build configuration
│   │   ├── Dockerfile          # C++ container build
│   │   └── README.md           # C++ documentation
│   └── data/                   # Python data processing
│       ├── main.py             # Primary processing script
│       ├── main_optimized.py   # Enhanced version
│       ├── *.json              # Health dataset files
│       └── README.md           # Data documentation
├── benchmark.sh                 # Performance benchmarking
├── check_records.sh            # Data validation scripts
└── test.HTTP                   # API testing requests
```

### Local Development

#### API Development
```bash
# Install Python dependencies
cd api
pip install -r requirements.txt

# Set environment variables
export WEAVIATE_URL=http://localhost:8080

# Run development server
python app.py
```

#### C++ Development
```bash
# Build C++ ingestion system
cd app/cpp_ingestion
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)

# Run with debugger
gdb ./health_ingestion
```

#### Testing
```bash
# Run API tests
curl -X GET http://localhost:5000/health

# Test data ingestion
bash test.HTTP

# Performance benchmarking
bash benchmark.sh

# Data validation
bash check_records.sh
```

### Configuration

#### Environment Variables
```env
# API Configuration
WEAVIATE_URL=http://weaviate:8080
FLASK_ENV=development

# C++ Ingestion
API_URL=http://api:5000/ingest
BATCH_SIZE=1000
MAX_CONCURRENT=1000

# N8N Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=adminpassword
```

#### Performance Tuning
```cpp
// C++ Configuration (health_processor.cpp)
batch_size_(1000)        // Records per batch
max_concurrent_(1000)    // Concurrent API calls

// Python Configuration
BATCH_SIZE = 100         // Python batch size
MAX_WORKERS = 10         // Async workers
```

## 🤝 Contributing

### Development Guidelines

1. **Code Style**
   - Python: Follow PEP 8 guidelines
   - C++: Use C++17 standards with consistent naming
   - Documentation: Include comprehensive docstrings and comments

2. **Testing Requirements**
   - Unit tests for new features
   - Integration tests for API endpoints
   - Performance benchmarks for optimization changes
   - Documentation updates for new functionality

3. **Pull Request Process**
   - Fork the repository and create a feature branch
   - Ensure all tests pass and maintain code coverage
   - Update documentation and add examples
   - Submit PR with detailed description and test results

### Development Setup

```bash
# Fork and clone repository
git clone https://github.com/your-username/project.git
cd project

# Create development branch
git checkout -b feature/your-feature-name

# Set up development environment
sudo docker compose -f docker-compose.dev.yml up -d

# Run tests
make test

# Submit changes
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

## 📈 Monitoring & Maintenance

### Health Monitoring

```bash
# Service health checks
curl http://localhost:5000/health
curl http://localhost:8080/v1/.well-known/ready

# Service logs
sudo docker compose logs -f api
sudo docker compose logs -f weaviate
sudo docker compose logs -f ingestion

# Resource monitoring
docker stats $(sudo docker compose ps -q)
```

### Performance Monitoring

- **API Response Times**: Monitor `/health` endpoint latency
- **Vector Search Performance**: Track query response times
- **Ingestion Throughput**: Monitor records processed per second
- **Memory Usage**: Track container memory consumption
- **GPU Utilization**: Monitor CUDA device usage (if available)

### Backup & Recovery

```bash
# Backup Weaviate data
sudo docker run --rm -v project_weaviate_data:/data -v $(pwd):/backup alpine tar czf /backup/weaviate_backup.tar.gz /data

# Backup N8N workflows
sudo docker run --rm -v project_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n_backup.tar.gz /data

# Restore from backup
sudo docker run --rm -v project_weaviate_data:/data -v $(pwd):/backup alpine tar xzf /backup/weaviate_backup.tar.gz -C /data --strip 1
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](api/README.md) - Flask API endpoints and usage
- [C++ Ingestion Guide](app/cpp_ingestion/README.md) - High-performance processing
- [Data Processing Guide](app/data/README.md) - Python scripts and datasets
- [Docker Deployment](DOCKER.md) - Container orchestration and deployment

### Troubleshooting

**Common Issues:**
- **Service won't start**: Check logs with `sudo docker compose logs service_name`
- **API connectivity**: Verify all services are healthy with `sudo docker compose ps`
- **Performance issues**: Monitor resource usage with `docker stats`
- **GPU not detected**: Verify NVIDIA Container Toolkit installation

**Getting Help:**
- Check service logs for error messages
- Review health check endpoints for connectivity issues
- Verify data file formats and permissions
- Monitor resource usage and scaling requirements

### Community

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas
- **Contributions**: See [Contributing](#contributing) section for development guidelines
- **Updates**: Follow repository for latest features and improvements

---

**Built with ❤️ for health and fitness data analysis**

*Vector Search & N8N Platform - Transforming health data into actionable insights through advanced vector similarity search and workflow automation.*