project(viewer)

add_executable(viewer viewer.cpp)
target_link_libraries(viewer ${MVE_LIBRARIES}
                             -lpng -ljpeg ${OPENCV_LIBRARIES})
