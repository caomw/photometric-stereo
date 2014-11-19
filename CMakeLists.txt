cmake_minimum_required(VERSION 2.8)
project(pba)

find_package(PkgConfig REQUIRED)
pkg_check_modules(eigen3 REQUIRED eigen3)
include_directories(${EIGEN3_INCLUDE_DIRS})

find_package(Ceres REQUIRED)
include_directories(${CERES_INCLUDE_DIRS})
message(STATUS "Ceres Lib: ${CERES_INCLUDE_DIRS}")

add_executable(pba pba.cpp)
message(STATUS "Ceres Lib: ${CERES_LIBRARIES}")
target_link_libraries(pba ${CERES_LIBRARIES})
