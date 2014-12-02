project(warp3d)

add_executable(warp3d main.cpp app_settings.cpp warping.cpp)
target_link_libraries(warp3d ${CERES_LIBRARIES} ${MVE_LIBRARIES}
                             -lpng -ljpeg ${OPENCV_LIBRARIES})
#set_property(TARGET pba PROPERTY COMPILE_OPTIONS "-std=c++11")

if(${APPLE})
  set_property(TARGET warp3d APPEND_STRING PROPERTY LINK_FLAGS
               " -framework OpenGL -framework GLUT ")
else()
  set_property(TARGET warp3d APPEND_STRING PROPERTY LINK_FLAGS
               " -lGL -lglut ")
endif()
