#include "health_processor.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <thread>
#include <chrono>
#include <algorithm>
#include <curl/curl.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using namespace std::chrono;

namespace health_ingestion {

// CURL callback for HTTP responses
static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
    userp->append((char*)contents, size * nmemb);
    return size * nmemb;
}

HealthDataProcessor::HealthDataProcessor(const std::string& data_dir)
    : data_dir_(data_dir)
    , api_url_("http://localhost:5000/ingest")
    , batch_size_(100)
    , max_concurrent_(10) {
    
    // Initialize CURL globally
    curl_global_init(CURL_GLOBAL_DEFAULT);
    
    std::cout << "Initialized HealthDataProcessor for directory: " << data_dir_ << std::endl;
}

bool HealthDataProcessor::loadUserProfiles() {
    std::ifstream file(data_dir_ + "/users.json");
    if (!file.is_open()) {
        std::cerr << "Failed to open users.json" << std::endl;
        return false;
    }
    
    try {
        json users_json;
        file >> users_json;
        
        for (const auto& user_obj : users_json) {
            UserProfile profile;
            profile.user_id = user_obj["user_id"];
            profile.name = user_obj["name"];
            profile.age = user_obj["age"];
            profile.gender = user_obj["gender"];
            profile.height = user_obj["height"];
            profile.weight = user_obj["weight"];
            profile.fitness_level = user_obj["fitness_level"];
            
            users_[profile.user_id] = profile;
        }
        
        std::cout << "Loaded " << users_.size() << " user profiles" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Error parsing users.json: " << e.what() << std::endl;
        return false;
    }
}

void HealthDataProcessor::processAllFiles() {
    std::cout << "Starting optimized C++ health data processing..." << std::endl;
    
    auto start_time = high_resolution_clock::now();
    
    // Map to accumulate user-day data efficiently
    std::unordered_map<std::string, DayData> user_day_data;
    
    // Process files in optimal order (smaller to larger)
    std::vector<std::pair<std::string, std::string>> files = {
        {"users.json", "users"},
        {"measurements.json", "measurements"},
        {"activities.json", "activities"},
        {"workouts.json", "workouts"},
        {"sleep.json", "sleep"},
        {"nutrition.json", "nutrition"},
        {"heart_rate.json", "heart_rate"}
    };
    
    size_t total_records = 0;
    std::vector<std::tuple<std::string, std::string, std::string>> batch;
    
    for (const auto& [filename, data_type] : files) {
        if (data_type == "users") continue; // Already loaded
        
        std::cout << "Processing " << filename << "..." << std::endl;
        
        std::ifstream file(data_dir_ + "/" + filename);
        if (!file.is_open()) {
            std::cerr << "Warning: Could not open " << filename << std::endl;
            continue;
        }
        
        try {
            // Parse JSON in streaming fashion for memory efficiency
            json file_json;
            file >> file_json;
            
            for (const auto& record : file_json) {
                std::string user_id = record["user_id"];
                std::string date = extractDate(record.dump());
                
                if (date.empty()) continue;
                
                std::string key = user_id + "|" + date;
                
                // Store relevant data efficiently based on type
                if (data_type == "activities") {
                    std::ostringstream activity;
                    activity << "did " << record["activity_type"] 
                             << " for " << record["duration"] << " minutes in " 
                             << record["weather"] << " weather, burning " 
                             << record["calories_burned"] << " calories, covering "
                             << record["distance"] << " km with " << record["steps"]
                             << " steps, avg HR " << record["heart_rate_avg"]
                             << " bpm (max " << record["heart_rate_max"] << ").";
                    user_day_data[key].activities.push_back(activity.str());
                }
                else if (data_type == "workouts") {
                    std::ostringstream workout;
                    workout << "Completed a " << record["workout_type"] 
                            << " workout for " << record["duration"] << " minutes, "
                            << record["sets"] << " sets of " << record["reps"]
                            << " reps, burned " << record["calories_burned"] << " calories.";
                    user_day_data[key].workouts.push_back(workout.str());
                }
                else if (data_type == "nutrition") {
                    std::ostringstream nutrition;
                    nutrition << "Ate " << record["calories"] << " calories at " 
                              << record["meal_type"] << " (" << record["protein"]
                              << "g protein, " << record["carbs"] << "g carbs, "
                              << record["fat"] << "g fat).";
                    user_day_data[key].nutrition.push_back(nutrition.str());
                }
                else if (data_type == "sleep") {
                    std::ostringstream sleep;
                    sleep << "Slept " << record["total_sleep"] << " hours (deep "
                          << record["deep_sleep"] << "h, REM " << record["rem_sleep"]
                          << "h), quality " << record["sleep_quality"]
                          << ", resting HR " << record["resting_heart_rate"] << " bpm.";
                    user_day_data[key].sleep.push_back(sleep.str());
                }
                else if (data_type == "heart_rate") {
                    user_day_data[key].heart_rates.push_back(record["value"]);
                }
                
                total_records++;
                
                // Process batches periodically to manage memory
                if (total_records % 50000 == 0) {
                    std::cout << "Processed " << total_records << " records..." << std::endl;
                    
                    // Generate summaries for completed days and add to batch
                    for (auto it = user_day_data.begin(); it != user_day_data.end();) {
                        const std::string& key = it->first;
                        size_t pos = key.find('|');
                        std::string user_id = key.substr(0, pos);
                        std::string date = key.substr(pos + 1);
                        
                        // Create summary if we have substantial data
                        if (!it->second.activities.empty() || !it->second.nutrition.empty()) {
                            std::string summary = createSummary(user_id, date, it->second);
                            batch.emplace_back(user_id, date, summary);
                            
                            if (batch.size() >= batch_size_) {
                                processBatch(batch);
                                batch.clear();
                            }
                            
                            it = user_day_data.erase(it);
                        } else {
                            ++it;
                        }
                    }
                }
            }
            
        } catch (const std::exception& e) {
            std::cerr << "Error processing " << filename << ": " << e.what() << std::endl;
        }
    }
    
    // Process remaining data
    for (const auto& [key, day_data] : user_day_data) {
        size_t pos = key.find('|');
        std::string user_id = key.substr(0, pos);
        std::string date = key.substr(pos + 1);
        
        std::string summary = createSummary(user_id, date, day_data);
        batch.emplace_back(user_id, date, summary);
        
        if (batch.size() >= batch_size_) {
            processBatch(batch);
            batch.clear();
        }
    }
    
    // Process final batch
    if (!batch.empty()) {
        processBatch(batch);
    }
    
    auto end_time = high_resolution_clock::now();
    auto duration = duration_cast<seconds>(end_time - start_time);
    
    std::cout << "C++ Processing completed!" << std::endl;
    std::cout << "Total records processed: " << total_records << std::endl;
    std::cout << "Time taken: " << duration.count() << " seconds" << std::endl;
}

std::string HealthDataProcessor::extractDate(const std::string& json_str) {
    try {
        json obj = json::parse(json_str);
        
        if (obj.contains("date")) {
            return obj["date"];
        } else if (obj.contains("date_time")) {
            std::string datetime = obj["date_time"];
            size_t space_pos = datetime.find(' ');
            return space_pos != std::string::npos ? datetime.substr(0, space_pos) : datetime;
        }
    } catch (const std::exception&) {
        // Ignore parsing errors for date extraction
    }
    
    return "";
}

std::string HealthDataProcessor::createSummary(const std::string& user_id, 
                                               const std::string& date,
                                               const DayData& data) {
    auto it = users_.find(user_id);
    if (it == users_.end()) {
        return "Unknown user " + user_id + " on " + date;
    }
    
    const UserProfile& profile = it->second;
    
    std::ostringstream summary;
    summary << profile.name << " (" << profile.age << " years old " << profile.gender
            << ", " << profile.height << " cm, " << profile.weight << " kg, "
            << profile.fitness_level << " fitness level)";
    
    // Add activities
    for (const auto& activity : data.activities) {
        summary << " " << activity;
    }
    
    // Add workouts
    for (const auto& workout : data.workouts) {
        summary << " " << workout;
    }
    
    // Add nutrition
    for (const auto& nutrition : data.nutrition) {
        summary << " " << nutrition;
    }
    
    // Add sleep
    for (const auto& sleep : data.sleep) {
        summary << " " << sleep;
    }
    
    // Add heart rate summary
    if (!data.heart_rates.empty()) {
        auto minmax = std::minmax_element(data.heart_rates.begin(), data.heart_rates.end());
        summary << " Heart rate ranged " << *minmax.first << "–" << *minmax.second 
                << " bpm during the day.";
    }
    
    return summary.str();
}

bool HealthDataProcessor::sendToVectorAPI(const std::string& user_id, 
                                          const std::string& date,
                                          const std::string& summary) {
    // Check for print mode (dry run)
    if (api_url_ == "PRINT_MODE") {
        std::cout << "[" << user_id << " - " << date << "] " 
                  << summary.substr(0, 150) << "..." << std::endl;
        return true;
    }
    
    CURL* curl = curl_easy_init();
    if (!curl) {
        std::cerr << "Failed to initialize CURL for " << user_id << std::endl;
        return false;
    }
    
    // Prepare JSON payload
    json payload = {
        {"text", summary},
        {"meta", {
            {"user_id", user_id},
            {"date", date},
            {"type", "daily_summary"}
        }}
    };
    
    std::string json_string = payload.dump();
    std::string response_string;
    
    // Set CURL options with improved timeout and retry logic
    curl_easy_setopt(curl, CURLOPT_URL, api_url_.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_string.c_str());
    curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, json_string.length());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_string);
    
    // Improved timeout settings - wait longer for server response
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 60L);           // Total timeout: 60 seconds
    curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 10L);    // Connection timeout: 10 seconds
    curl_easy_setopt(curl, CURLOPT_LOW_SPEED_TIME, 30L);    // Low speed timeout: 30 seconds
    curl_easy_setopt(curl, CURLOPT_LOW_SPEED_LIMIT, 100L);  // Min 100 bytes/sec
    
    // Enable verbose logging for debugging (optional)
    // curl_easy_setopt(curl, CURLOPT_VERBOSE, 1L);
    
    // Set headers
    struct curl_slist* headers = nullptr;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    headers = curl_slist_append(headers, "Accept: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    
    // Perform request with retry logic
    CURLcode res;
    long response_code = 0;
    int max_retries = 3;
    
    for (int attempt = 1; attempt <= max_retries; ++attempt) {
        response_string.clear();
        res = curl_easy_perform(curl);
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);
        
        if (res == CURLE_OK && (response_code == 200 || response_code == 201)) {
            break; // Success!
        }
        
        if (attempt < max_retries) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500 * attempt)); // Exponential backoff
            std::cout << "Retry " << attempt << "/" << max_retries << " for " << user_id 
                      << " (HTTP " << response_code << ")" << std::endl;
        } else {
            std::cerr << "Failed after " << max_retries << " attempts for " << user_id 
                      << " - CURL: " << curl_easy_strerror(res) 
                      << ", HTTP: " << response_code << std::endl;
        }
    }
    
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    
    // Check if we got a valid response (accept both 200 and 201)
    bool success = (res == CURLE_OK && (response_code == 200 || response_code == 201));
    if (success && !response_string.empty()) {
        // Parse response to verify it's valid JSON with "status": "ok"
        try {
            json response_json = json::parse(response_string);
            if (response_json.contains("status") && response_json["status"] == "ok") {
                return true;
            }
        } catch (const std::exception& e) {
            std::cerr << "Invalid response JSON for " << user_id << ": " << e.what() << std::endl;
        }
    }
    
    return false;
}

void HealthDataProcessor::processBatch(const std::vector<std::tuple<std::string, std::string, std::string>>& batch) {
    std::cout << "Processing batch of " << batch.size() << " summaries..." << std::endl;
    
    // Use thread pool for concurrent API calls
    std::vector<std::future<bool>> futures;
    size_t concurrent_count = std::min(batch.size(), max_concurrent_);
    
    for (size_t i = 0; i < batch.size(); i += concurrent_count) {
        futures.clear();
        
        for (size_t j = i; j < std::min(i + concurrent_count, batch.size()); ++j) {
            const auto& [user_id, date, summary] = batch[j];
            
            futures.push_back(std::async(std::launch::async, [this, user_id, date, summary]() {
                return sendToVectorAPI(user_id, date, summary);
            }));
        }
        
        // Wait for this chunk to complete
        size_t success_count = 0;
        for (auto& future : futures) {
            if (future.get()) {
                success_count++;
            }
        }
        
        std::cout << "Chunk completed: " << success_count << "/" << futures.size() << " successful" << std::endl;
    }
}

} // namespace health_ingestion