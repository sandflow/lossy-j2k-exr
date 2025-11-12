cmake_minimum_required(VERSION 3.24)
project (exrj2klossy)

set(EXECUTABLE_OUTPUT_PATH "${CMAKE_BINARY_DIR}/bin")

# add OpenEXR

add_subdirectory(ext/openexr)

# encoder app

add_executable(exrj2klossy_enc src/main/cpp/ojphl_enc.cpp src/main/cpp/ojphl.cpp ext/openexr/src/lib/OpenEXRCore/internal_ht_common.cpp)
target_include_directories(exrj2klossy_enc PRIVATE ext/cxxopts)
target_link_libraries(exrj2klossy_enc OpenEXRCore openjph pthread)

if(WIN32 AND (BUILD_SHARED_LIBS OR OPENEXR_BUILD_BOTH_STATIC_SHARED))
  target_compile_definitions(exrj2klossy_enc PRIVATE OPENEXR_DLL)
endif()

# decoder app

add_executable(exrj2klossy_dec src/main/cpp/ojphl_dec.cpp src/main/cpp/ojphl.cpp ext/openexr/src/lib/OpenEXRCore/internal_ht_common.cpp)
target_include_directories(exrj2klossy_dec PRIVATE ext/cxxopts)
target_link_libraries(exrj2klossy_dec OpenEXRCore openjph pthread)
