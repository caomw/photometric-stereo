project(pba)

add_executable(pba pba.cpp)
target_link_libraries(pba ${CERES_LIBRARIES} ${MVE_LIBRARIES}
                          -lpng -ljpeg)
#set_property(TARGET pba PROPERTY COMPILE_OPTIONS "-std=c++11")

#if(${APPLE})
#  set_property(TARGET pba APPEND_STRING PROPERTY LINK_FLAGS
#               " -framework OpenGL -framework GLUT ")
#else()
#  set_property(TARGET pba APPEND_STRING PROPERTY LINK_FLAGS
#               " -lGL -lglut ")
#endif()
