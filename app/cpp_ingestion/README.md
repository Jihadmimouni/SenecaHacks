# C++ Health Data Ingestion System

A high-performance C++ system for processing and ingesting health/fitness data into a vector search API using batch processing and concurrent HTTP requests.

## Overview

This C++ ingestion system efficiently processes large health datasets, aggregates user daily summaries, and sends them to a vector search API for semantic indexing. It's designed for high throughput with configurable batch processing and concurrent API calls.

## Architecture

### Components

- **HealthDataProcessor**: Main processing engine
- **Batch Processing**: Configurable batch sizes (default: 1000 records)
### Data Flow

1. **Load User Profiles**: Parse user metadata from `users.json`
2. **Process Health Files**: Stream through activity, workout, nutrition, sleep, and heart rate data
3. **Aggregate Daily Data**: Group records by user and date
4. **Generate Summaries**: Create comprehensive daily health summaries
5. **Batch Processing**: Send data in configurable batch sizes
6. **API Integration**: HTTP POST to vector search API

## Features

### Performance Optimizations

- **Streaming JSON Processing**: Memory-efficient parsing of large files
- **Batch Processing**: Configurable batch sizes (1-1000 records)
- **Concurrent HTTP Requests**: Parallel API calls for faster ingestion
- **Memory Management**: Efficient data structures and cleanup
- **Progress Reporting**: Real-time processing statistics

### Data Processing

- **Multi-source Integration**: Combines data from 7 different health data types
- **Daily Aggregation**: Groups all user activities by date
- **Rich Summaries**: Natural language descriptions of daily health activities
- **Metadata Preservation**: Maintains user context and temporal information

## Build Instructions

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libcurl4-openssl-dev \
    nlohmann-json3-dev

# Or using vcpkg
vcpkg install curl nlohmann-json
```

### Compilation

```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release

# Build (parallel compilation)
make -j$(nproc)

# Run tests
./health_test
```

### Docker Build

```bash
# Build Docker image
docker build -t health-ingestion .

# Run ingestion
docker run -v /path/to/data:/data health-ingestion
```

## Usage

### Command Line

```bash
# Run ingestion with default settings
./health_ingestion /path/to/data

# Environment variables
export API_URL=http://localhost:5000/ingest
./health_ingestion /data
```

### Configuration

The system can be configured through:

- **Batch Size**: Set via `batch_size_` (default: 1000)
- **Concurrency**: Set via `max_concurrent_` (default: 1000)
- **API URL**: Environment variable `API_URL` or default `http://localhost:5000/ingest`

### Data Directory Structure

Expected data files in the input directory:

```
data/
├── users.json          # User profiles and metadata
├── activities.json     # Physical activities and exercises
├── workouts.json       # Structured workout sessions
├── nutrition.json      # Meal and nutrition data
├── sleep.json         # Sleep patterns and quality
├── heart_rate.json    # Heart rate measurements
└── measurements.json  # Body measurements
```

## Data Schema

### Input Format

Each JSON file contains arrays of records with user_id and date fields:

```json
{
  "user_id": "user123",
  "date": "2024-01-15",
  // ... type-specific fields
}
```

### Output Format

Generated summaries are sent to the API as:

```json
{
  "text": "John Doe (25 years old male, 180 cm, 75 kg) completed a 30-minute cardio workout...",
  "meta": {
    "user_id": "user123",
    "date": "2024-01-15",
    "type": "daily_summary"
  }
}
```

## Performance

### Benchmarks

- **Processing Speed**: ~50,000 records/second (depends on hardware)
- **Memory Usage**: ~200MB peak for large datasets
- **API Throughput**: 1000 concurrent requests supported
- **Batch Efficiency**: Optimized for network and API performance

### Optimization Features

- **Compiler Optimizations**: `-O3 -march=native` for release builds
- **Memory Pool**: Efficient string and object allocation
- **HTTP Connection Reuse**: Persistent connections for API calls
- **JSON Streaming**: Incremental parsing to reduce memory footprint

## Configuration Options

### Build-time Configuration

```cpp
// In health_processor.cpp constructor
batch_size_(1000)        // Records per batch
max_concurrent_(1000)    // Maximum concurrent API calls
```

### Runtime Configuration

```bash
# API endpoint
export API_URL=http://api:5000/ingest

# Print mode (dry run)
export API_URL=PRINT_MODE
```

## Error Handling

### Network Resilience

- **Retry Logic**: Exponential backoff for failed API calls
- **Timeout Management**: Configurable connection and request timeouts
- **Connection Pooling**: Efficient HTTP connection management

### Data Validation

- **JSON Schema Validation**: Ensures data integrity
- **Missing File Handling**: Graceful degradation for missing data files
- **Date Format Validation**: Robust date parsing and validation

## Monitoring and Logging

### Progress Reporting

```cpp
std::cout << "Processing batch of " << batch.size() << " summaries..." << std::endl;
std::cout << "Batch completed: " << success_count << "/" << batch.size() << " successful" << std::endl;
```

### Performance Metrics

- Processing time per batch
- Success/failure rates for API calls
- Memory usage statistics
- Total records processed

## Integration

### Docker Compose Integration

```yaml
ingestion:
  build: ./app/cpp_ingestion
  depends_on:
    - api
  volumes:
    - ./app/data:/data:ro
  environment:
    - API_URL=http://api:5000/ingest
```

### API Compatibility

Compatible with the Flask Vector Search API:
- Sends JSON payloads to `/ingest` endpoint
- Handles HTTP 200/201 responses
- Includes metadata for vector indexing

## Future Enhancements

1. **Memory mapping**: Use `mmap()` for even faster file I/O
2. **SIMD optimization**: Vectorized operations for numeric aggregations  
3. **Custom allocators**: Pool allocators for frequent allocations
4. **Protocol Buffers**: Replace JSON with binary serialization
5. **GPU acceleration**: CUDA for parallel processing of embeddings