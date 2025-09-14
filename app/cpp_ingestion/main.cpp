#include "health_processor.hpp"
#include <iostream>
#include <filesystem>
#include <cstdlib>

int main(int argc, char* argv[]) {
    std::cout << "=== High-Performance C++ Health Data Ingestion ===" << std::endl;
    
    // Determine data directory
    std::string data_dir = "/home/gl1tch/Repos/Project/app/data";
    if (argc > 1) {
        data_dir = argv[1];
    }
    
    // Check if data directory exists
    if (!std::filesystem::exists(data_dir)) {
        std::cerr << "Error: Data directory does not exist: " << data_dir << std::endl;
        return 1;
    }
    
    std::cout << "Using data directory: " << data_dir << std::endl;
    
    // Initialize processor
    health_ingestion::HealthDataProcessor processor(data_dir);
    
    // Configure settings - use environment variable or default
    const char* api_url = std::getenv("API_URL");
    if (!api_url) {
        api_url = "http://localhost:5000/ingest";
    }
    
    processor.setApiUrl(api_url);
    processor.setBatchSize(100);
    processor.setMaxConcurrentRequests(10);
    
    // Load user profiles
    if (!processor.loadUserProfiles()) {
        std::cerr << "Failed to load user profiles. Exiting." << std::endl;
        return 1;
    }
    
    // Process all data files
    processor.processAllFiles();
    
    std::cout << "Ingestion completed successfully!" << std::endl;
    return 0;
}