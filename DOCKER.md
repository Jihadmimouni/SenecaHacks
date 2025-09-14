# Docker Deployment Guide

Comprehensive guide for deploying and managing the Vector Search & N8N health data processing platform using Docker Compose.

## Overview

This project uses Docker Compose to orchestrate a multi-service architecture for health data processing and vector similarity search. The stack includes a Flask API, Weaviate vector database, N8N workflow automation, and a high-performance C++ ingestion service.

## Architecture

### Services Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│     N8N     │    │   Weaviate  │    │  Flask API  │    │  Ingestion  │
│  Workflow   │    │   Vector    │    │   Service   │    │   Service   │
│ Automation  │    │  Database   │    │             │    │    (C++)    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      :5678              :8080             :5000             :9090
```

### Network Configuration

- **Network**: `vectnet` (custom bridge network)
- **Service Discovery**: Automatic DNS resolution between services
- **Port Mapping**: External access to web interfaces and APIs

## Services Configuration

### N8N Workflow Automation

```yaml
n8n:
  image: n8nio/n8n:latest
  restart: unless-stopped
  ports:
    - "5678:5678"
  environment:
    - N8N_BASIC_AUTH_ACTIVE=true
    - N8N_BASIC_AUTH_USER=admin
    - N8N_BASIC_AUTH_PASSWORD=adminpassword
```

**Features:**
- Web interface at http://localhost:5678
- Persistent workflow data storage
- Basic authentication enabled
- Auto-restart on failure

### Weaviate Vector Database

```yaml
weaviate:
  image: semitechnologies/weaviate:1.22.0
  restart: unless-stopped
  environment:
    - QUERY_DEFAULTS_LIMIT=20
    - AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true
    - PERSISTENCE_DATA_PATH=/var/lib/weaviate
```

**Features:**
- Vector similarity search capabilities
- Persistent data storage
- RESTful API interface
- Health check monitoring
- Anonymous access for development

### Flask API Service

```yaml
api:
  build: ./api
  restart: unless-stopped
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

**Features:**
- Custom Docker build from `./api` directory
- GPU acceleration support (NVIDIA)
- Health check endpoint
- Automatic dependency management
- Environment-based configuration

### C++ Ingestion Service

```yaml
ingestion:
  build: ./app/cpp_ingestion
  restart: unless-stopped
  depends_on:
    api:
      condition: service_healthy
  volumes:
    - ./app/data:/data:ro
```

**Features:**
- High-performance C++ data processing
- Read-only data volume mounting
- Health check dependency on API
- Automatic restart after completion
- Environment variable configuration

## Deployment Instructions

### Prerequisites

```bash
# Docker and Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# NVIDIA Container Toolkit (for GPU support)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Quick Start

```bash
# Clone and navigate to project
cd /path/to/project

# Start all services
sudo docker compose up -d

# Check service status
sudo docker compose ps

# View logs
sudo docker compose logs -f
```

### Build and Deploy

```bash
# Build and start services
sudo docker compose up -d --build

# Build specific service
sudo docker compose build api
sudo docker compose up -d api

# Force rebuild without cache
sudo docker compose build --no-cache
```

## Service Management

### Starting Services

```bash
# Start all services
sudo docker compose up -d

# Start specific services
sudo docker compose up -d weaviate api

# Start with logs
sudo docker compose up
```

### Stopping Services

```bash
# Stop all services
sudo docker compose down

# Stop specific service
sudo docker compose stop ingestion

# Remove containers and volumes
sudo docker compose down -v
```

### Monitoring Services

```bash
# Check service status
sudo docker compose ps

# View real-time logs
sudo docker compose logs -f

# View logs for specific service
sudo docker compose logs -f api

# Monitor resource usage
docker stats $(docker compose ps -q)
```

## Health Checks

### Service Health Monitoring

Each service includes health checks for monitoring:

```yaml
# API Health Check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 10s
  timeout: 5s
  retries: 10
  start_period: 30s

# Weaviate Health Check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
  interval: 10s
  timeout: 10s
  retries: 30
  start_period: 40s
```

### Manual Health Verification

```bash
# Check API health
curl http://localhost:5000/health

# Check Weaviate status
curl http://localhost:8080/v1/.well-known/ready

# Check N8N interface
curl http://localhost:5678

# Verify ingestion service logs
sudo docker compose logs ingestion --tail 20
```

## Data Management

### Volume Management

```yaml
volumes:
  n8n_data:          # N8N workflows and configurations
  weaviate_data:     # Weaviate vector database storage
```

### Data Persistence

```bash
# Backup volumes
sudo docker run --rm -v project_weaviate_data:/data -v $(pwd):/backup alpine tar czf /backup/weaviate_backup.tar.gz /data

# Restore volumes
sudo docker run --rm -v project_weaviate_data:/data -v $(pwd):/backup alpine tar xzf /backup/weaviate_backup.tar.gz -C /data --strip 1

# List volume contents
sudo docker run --rm -v project_weaviate_data:/data alpine ls -la /data
```

### Data Directory Mounting

```yaml
# Read-only data access for ingestion
volumes:
  - ./app/data:/data:ro
```

## Environment Configuration

### Environment Variables

#### API Service
- `WEAVIATE_URL`: Weaviate connection URL (default: `http://weaviate:8080`)
- `FLASK_ENV`: Flask environment mode
- `CUDA_VISIBLE_DEVICES`: GPU device selection

#### Ingestion Service  
- `API_URL`: Flask API endpoint (default: `http://api:5000/ingest`)
- `BATCH_SIZE`: Processing batch size
- `MAX_CONCURRENT`: Maximum concurrent requests

#### N8N Service
- `N8N_BASIC_AUTH_USER`: Authentication username
- `N8N_BASIC_AUTH_PASSWORD`: Authentication password
- `N8N_HOST`: Hostname configuration

### Custom Environment File

Create `.env` file for environment customization:

```env
# API Configuration
WEAVIATE_URL=http://weaviate:8080
FLASK_ENV=production

# N8N Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=secure_password

# Ingestion Configuration
API_URL=http://api:5000/ingest
BATCH_SIZE=1000
```

## Performance Optimization

### Resource Allocation

```yaml
# GPU allocation for API service
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]

# Memory limits
deploy:
  resources:
    limits:
      memory: 4G
    reservations:
      memory: 2G
```

### Network Optimization

```yaml
# Custom network configuration
networks:
  vectnet:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: vectnet
      com.docker.network.driver.mtu: 1450
```

## Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs for errors
sudo docker compose logs service_name

# Verify port availability
sudo netstat -tlnp | grep :5000

# Check resource constraints
docker system df
```

#### GPU Not Available
```bash
# Verify NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Check Docker daemon configuration
cat /etc/docker/daemon.json
```

#### Network Connectivity Issues
```bash
# Test internal connectivity
sudo docker compose exec api ping weaviate
sudo docker compose exec ingestion curl http://api:5000/health

# Check network configuration
docker network ls
docker network inspect project_vectnet
```

### Log Analysis

```bash
# Service-specific logs
sudo docker compose logs -f --tail 100 api
sudo docker compose logs -f --tail 100 weaviate
sudo docker compose logs -f --tail 100 ingestion

# Search logs for errors
sudo docker compose logs | grep -i error
sudo docker compose logs | grep -i failed
```

### Performance Monitoring

```bash
# Container resource usage
docker stats $(sudo docker compose ps -q)

# System resource monitoring
htop
iostat -x 1
nvidia-smi -l 1

# Network monitoring
sudo docker compose exec api netstat -i
sudo docker compose exec weaviate ss -tulpn
```

## Security Considerations

### Network Security

- Services communicate through internal Docker network
- Only necessary ports exposed to host
- No direct database access from external networks

### Authentication

```yaml
# N8N basic authentication
environment:
  - N8N_BASIC_AUTH_ACTIVE=true
  - N8N_BASIC_AUTH_USER=admin
  - N8N_BASIC_AUTH_PASSWORD=secure_password
```

### Data Protection

- Read-only volume mounts for data directories
- Persistent volume encryption (optional)
- Regular backup procedures

## Production Deployment

### Scaling Considerations

```yaml
# Horizontal scaling example
api:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

### High Availability Setup

- Load balancer for API services
- Weaviate clustering for redundancy
- Persistent volume replication
- Health check monitoring with alerting

### Monitoring and Alerting

```yaml
# Health check configuration
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 1m
```

## Maintenance

### Updates and Upgrades

```bash
# Update images
sudo docker compose pull

# Restart with new images
sudo docker compose up -d

# Rolling update strategy
sudo docker compose up -d --no-deps api
```

### Cleanup

```bash
# Remove unused containers and images
docker system prune -f

# Remove project resources
sudo docker compose down -v --rmi all

# Clean build cache
docker builder prune -f
```