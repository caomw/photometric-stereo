cmake_minimum_required(VERSION 2.8)
project(photometric-stereo)
include(cmake/depends.cmake)

add_definitions("-std=c++11")

add_subdirectory(pba)
add_subdirectory(viewer)
