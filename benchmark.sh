#!/bin/bash

# Health Data Ingestion - Performance Comparison Script
# Compares Python (original), Python (optimized), and C++ implementations

set -e

echo "=== Health Data Ingestion Performance Comparison ==="
echo

# Configuration
DATA_DIR="/home/gl1tch/Repos/Project/app/data"
CPP_DIR="/home/gl1tch/Repos/Project/app/cpp_ingestion"
API_URL="http://localhost:5000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if API is running
check_api() {
    if curl -s "$API_URL/query" > /dev/null 2>&1; then
        print_status "Vector API is running at $API_URL"
        return 0
    else
        print_warning "Vector API not available at $API_URL"
        return 1
    fi
}

# Build C++ version
build_cpp() {
    print_status "Building C++ ingestion system..."
    
    cd "$CPP_DIR"
    
    # Check dependencies
    if ! command -v cmake &> /dev/null; then
        print_error "CMake not found. Please install: sudo apt install cmake"
        return 1
    fi
    
    if ! pkg-config --exists libcurl; then
        print_error "libcurl not found. Please install: sudo apt install libcurl4-openssl-dev"
        return 1
    fi
    
    # Build
    mkdir -p build
    cd build
    
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j$(nproc)
    
    if [ -f "./health_ingestion" ]; then
        print_status "C++ build successful!"
        return 0
    else
        print_error "C++ build failed!"
        return 1
    fi
}

# Install Python dependencies 
setup_python() {
    print_status "Setting up Python dependencies..."
    
    cd "$DATA_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install required packages
    pip install -q ijson aiohttp requests
    
    print_status "Python environment ready"
}

# Run performance test
run_test() {
    local test_name="$1"
    local command="$2"
    local description="$3"
    
    echo
    print_status "Running $test_name test..."
    echo "Description: $description"
    echo "Command: $command"
    echo
    
    # Start timing
    start_time=$(date +%s.%N)
    
    # Run command and capture output
    if eval "$command"; then
        end_time=$(date +%s.%N)
        duration=$(echo "$end_time - $start_time" | bc)
        
        print_status "$test_name completed in ${duration}s"
        echo "$test_name,$duration" >> benchmark_results.csv
    else
        print_error "$test_name failed!"
        echo "$test_name,FAILED" >> benchmark_results.csv
    fi
}

# Main execution
main() {
    echo "Data directory: $DATA_DIR"
    echo "C++ directory: $CPP_DIR"
    echo
    
    # Initialize results file
    echo "Test,Duration(seconds)" > benchmark_results.csv
    
    # Check API availability
    api_available=false
    if check_api; then
        api_available=true
    fi
    
    # Setup Python environment
    setup_python
    
    # Build C++ if requested
    if [ "${1:-}" = "--build-cpp" ] || [ "${1:-}" = "-c" ]; then
        if build_cpp; then
            cpp_available=true
        else
            cpp_available=false
        fi
    else
        if [ -f "$CPP_DIR/build/health_ingestion" ]; then
            cpp_available=true
            print_status "C++ executable found (skipping build)"
        else
            cpp_available=false
            print_warning "C++ executable not found. Use --build-cpp to build it."
        fi
    fi
    
    echo
    print_status "Starting performance comparison..."
    
    # Test 1: Python Original (dry run - no API calls)
    cd "$DATA_DIR"
    source venv/bin/activate
    run_test "Python_Original_DryRun" \
        "python3 main.py --mode=original --no-api | head -20" \
        "Original Python implementation without API calls"
    
    # Test 2: Python Optimized (dry run - no API calls)  
    run_test "Python_Optimized_DryRun" \
        "python3 main.py --mode=optimized --no-api | head -20" \
        "Optimized Python implementation without API calls"
    
    # Test 3: C++ Implementation (dry run if no API)
    if [ "$cpp_available" = true ]; then
        # TODO: Add --dry-run flag to C++ implementation
        print_warning "C++ dry-run mode not implemented yet"
        # run_test "CPP_DryRun" \
        #     "$CPP_DIR/build/health_ingestion --dry-run" \
        #     "C++ implementation without API calls"
    fi
    
    # API-based tests (if API is available)
    if [ "$api_available" = true ]; then
        print_status "Running API integration tests..."
        
        # Test 4: Python Optimized with API (limited batch)
        run_test "Python_Optimized_API_Sample" \
            "timeout 300s python3 main.py --mode=optimized | head -100" \
            "Optimized Python with API calls (5 min timeout)"
        
        # Test 5: C++ with API (if available)
        if [ "$cpp_available" = true ]; then
            cd "$CPP_DIR/build"
            run_test "CPP_API_Full" \
                "timeout 600s ./health_ingestion" \
                "C++ implementation with full API integration (10 min timeout)"
        fi
    else
        print_warning "Skipping API tests - vector API not available"
        echo "To run full tests:"
        echo "1. Start the vector API: cd /home/gl1tch/Repos/Project && docker-compose up -d"
        echo "2. Re-run this script"
    fi
    
    # Display results
    echo
    print_status "=== PERFORMANCE RESULTS ==="
    echo
    cat benchmark_results.csv | column -t -s','
    echo
    
    # Generate summary
    echo "=== SUMMARY ==="
    echo "• Python Original: Basic implementation, high memory usage"
    echo "• Python Optimized: Memory-efficient streaming, async API calls"  
    echo "• C++ Implementation: Native performance, minimal memory footprint"
    echo
    echo "Expected performance for 6.5GB data:"
    echo "• Python Original: 15-30 minutes"
    echo "• Python Optimized: 8-15 minutes"
    echo "• C++: 2-5 minutes"
    echo
    
    print_status "Benchmark complete! Results saved to benchmark_results.csv"
}

# Help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -c, --build-cpp    Build C++ implementation before testing"
    echo "  -h, --help         Show this help message"
    echo
    echo "Prerequisites:"
    echo "1. Install dependencies:"
    echo "   sudo apt install cmake libcurl4-openssl-dev nlohmann-json3-dev python3-venv"
    echo
    echo "2. (Optional) Start vector API:"
    echo "   cd /home/gl1tch/Repos/Project && docker-compose up -d"
    echo
}

# Parse arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -c|--build-cpp)
        main --build-cpp
        ;;
    *)
        main "$@"
        ;;
esac