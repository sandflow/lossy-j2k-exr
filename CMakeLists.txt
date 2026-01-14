cmake_minimum_required(VERSION 3.22)
project (exrj2klossy)

set(EXECUTABLE_OUTPUT_PATH "${CMAKE_BINARY_DIR}/bin")

# add OpenEXR

add_subdirectory(ext/openexr)

# add KDU

find_path(KDU_INCLUDE_DIR kdu_args.h PATH_SUFFIXES kakadu kdu)
find_library(KDU_LIBRARY NAMES kdu_v86R PATH_SUFFIXES kakadu kdu)
find_library(KDU_AUX_LIBRARY NAMES kdu_a86R PATH_SUFFIXES kakadu kdu)
if(NOT(KDU_INCLUDE_DIR) OR NOT(KDU_LIBRARY))
  message(FATAL_ERROR "Kakadu not found. Please set KDU_INCLUDE_DIR and KDU_LIBRARY.")
endif()


# encoder app

add_executable(exrj2klossy_enc src/main/cpp/exrj2kl_enc.cpp src/main/cpp/kdu.cpp src/main/cpp/ojphl.cpp ext/openexr/src/lib/OpenEXRCore/internal_ht_common.cpp)
target_include_directories(exrj2klossy_enc PRIVATE ext/cxxopts ${KDU_INCLUDE_DIR})
target_link_libraries(exrj2klossy_enc OpenEXRCore openjph pthread ${KDU_LIBRARY} ${KDU_AUX_LIBRARY})

if(WIN32 AND (BUILD_SHARED_LIBS OR OPENEXR_BUILD_BOTH_STATIC_SHARED))
  target_compile_definitions(exrj2klossy_enc PRIVATE OPENEXR_DLL)
endif()

# decoder app

add_executable(exrj2klossy_dec src/main/cpp/exrj2kl_dec.cpp src/main/cpp/kdu.cpp src/main/cpp/ojphl.cpp ext/openexr/src/lib/OpenEXRCore/internal_ht_common.cpp)
target_include_directories(exrj2klossy_dec PRIVATE ext/cxxopts ${KDU_INCLUDE_DIR})
target_link_libraries(exrj2klossy_dec OpenEXRCore openjph pthread ${KDU_LIBRARY} ${KDU_AUX_LIBRARY})

if(WIN32 AND (BUILD_SHARED_LIBS OR OPENEXR_BUILD_BOTH_STATIC_SHARED))
  target_compile_definitions(exrj2klossy_dec PRIVATE OPENEXR_DLL)
endif()

# mse app

add_executable(exrmse src/main/cpp/exrmse.cpp)
target_include_directories(exrmse PRIVATE ext/cxxopts)
target_link_libraries(exrmse OpenEXRCore pthread)


if(WIN32 AND (BUILD_SHARED_LIBS OR OPENEXR_BUILD_BOTH_STATIC_SHARED))
  target_compile_definitions(exrmse PRIVATE OPENEXR_DLL)
endif()
