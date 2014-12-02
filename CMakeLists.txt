cmake_minimum_required(VERSION 2.8)
project(photometric-stereo)

#set(EXECUTABLE_OUTPUT_PATH "${CMAKE_BINARY_DIR}/bin")
set(EXECUTABLE_OUTPUT_PATH "${CMAKE_SOURCE_DIR}/bin")

include(cmake/depends.cmake)
add_definitions("-std=c++11")

add_subdirectory(pba)
add_subdirectory(viewer)
add_subdirectory(warp3d)
