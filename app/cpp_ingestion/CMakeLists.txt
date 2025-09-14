cmake_minimum_required(VERSION 3.16)
project(HealthDataIngestion VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Threads REQUIRED)

# Find curl
find_package(CURL REQUIRED)

# Find nlohmann/json
find_package(nlohmann_json 3.2.0 REQUIRED)

# Compiler flags for optimization
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -march=native -DNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-g -O0 -Wall -Wextra")

# Source files
set(SOURCES
    health_processor.cpp
    main.cpp
)

set(TEST_SOURCES
    health_processor.cpp
    main_test.cpp
)

# Create executables
add_executable(health_ingestion ${SOURCES})
add_executable(health_test ${TEST_SOURCES})

# Link libraries for both executables
target_link_libraries(health_ingestion 
    PRIVATE 
    ${CURL_LIBRARIES}
    nlohmann_json::nlohmann_json
    Threads::Threads
)

target_link_libraries(health_test
    PRIVATE 
    ${CURL_LIBRARIES}
    nlohmann_json::nlohmann_json
    Threads::Threads
)

# Include directories
target_include_directories(health_ingestion 
    PRIVATE 
    ${CURL_INCLUDE_DIRS}
)

target_include_directories(health_test
    PRIVATE 
    ${CURL_INCLUDE_DIRS}
)

# Installation
install(TARGETS health_ingestion 
    RUNTIME DESTINATION bin
)

# CPack configuration for packaging
set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)