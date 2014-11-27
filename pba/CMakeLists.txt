project(pba)

add_executable(pba pba.cpp)
target_link_libraries(pba ${CERES_LIBRARIES} ${MVE_LIBRARIES})
set_property(TARGET pba PROPERTY COMPILE_OPTIONS "-std=c++11")
