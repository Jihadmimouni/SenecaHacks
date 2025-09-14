#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <future>
#include <chrono>
#include <thread>

namespace health_ingestion {

struct UserProfile {
    std::string user_id;
    std::string name;
    int age;
    std::string gender;
    double height;
    double weight;
    std::string fitness_level;
};

struct DayData {
    std::vector<std::string> activities;
    std::vector<std::string> workouts;
    std::vector<std::string> nutrition;
    std::vector<std::string> sleep;
    std::vector<double> heart_rates;
    std::vector<std::string> measurements;
};

class HealthDataProcessor {
public:
    explicit HealthDataProcessor(const std::string& data_dir);
    ~HealthDataProcessor() = default;

    // Main processing methods
    bool loadUserProfiles();
    void processAllFiles();
    
    // Configuration
    void setApiUrl(const std::string& url) { api_url_ = url; }
    void setBatchSize(size_t size) { batch_size_ = size; }
    void setMaxConcurrentRequests(size_t max) { max_concurrent_ = max; }

private:
    std::string data_dir_;
    std::string api_url_;
    size_t batch_size_;
    size_t max_concurrent_;
    
    std::unordered_map<std::string, UserProfile> users_;
    
    // File processing
    void processFile(const std::string& filename, const std::string& data_type);
    std::string extractDate(const std::string& json_obj);
    
    // Summary generation
    std::string createSummary(const std::string& user_id, const std::string& date, 
                             const DayData& data);
    
    // API integration
    bool sendToVectorAPI(const std::string& user_id, const std::string& date, 
                        const std::string& summary);
    void processBatch(const std::vector<std::tuple<std::string, std::string, std::string>>& batch);
};

} // namespace health_ingestion