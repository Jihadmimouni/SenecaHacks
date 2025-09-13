#include "health_processor.hpp"
#include <iostream>
#include <filesystem>

int main(int argc, char* argv[]) {
    std::cout << "=== High-Performance C++ Health Data Ingestion (Test Mode) ===" << std::endl;
    
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
    std::cout << "NOTE: Running in test mode - will print summaries instead of sending to API" << std::endl;
    
    // Initialize processor with dry-run mode
    health_ingestion::HealthDataProcessor processor(data_dir);
    processor.setApiUrl("PRINT_MODE");  // Special flag to print instead of send
    processor.setBatchSize(10);         // Smaller batches for testing
    
    if (!processor.loadUserProfiles()) {
        std::cerr << "Failed to load user profiles. Exiting." << std::endl;
        return 1;
    }
    
    // Process a limited amount for demonstration
    processor.processAllFiles();
    
    std::cout << "C++ test completed!" << std::endl;
    return 0;
}