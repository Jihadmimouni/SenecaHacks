# Use Ubuntu base image with build tools
FROM ubuntu:22.04 as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libcurl4-openssl-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy source code
COPY health_processor.hpp health_processor.cpp main.cpp main_test.cpp CMakeLists.txt ./

# Build the application
RUN mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release \
    && make -j$(nproc)

# Runtime image
FROM ubuntu:22.04

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libcurl4 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built executable and script
COPY --from=builder /app/build/health_ingestion /usr/local/bin/
COPY run_ingestion.sh /usr/local/bin/

# Set permissions
RUN chmod +x /usr/local/bin/health_ingestion /usr/local/bin/run_ingestion.sh

# Create data directory and set working directory
WORKDIR /data

# Default command
CMD ["run_ingestion.sh"]