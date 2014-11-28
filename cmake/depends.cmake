find_package(PkgConfig REQUIRED)

pkg_check_modules(eigen3 REQUIRED eigen3)
include_directories(${EIGEN3_INCLUDE_DIRS})

find_package(Ceres REQUIRED)
include_directories(${CERES_INCLUDE_DIRS})

find_package(Mve REQUIRED)
include_directories(${MVE_INCLUDE_DIRS})

set(OPENCV_LIBRARIES -lopencv_core -lopencv_imgproc -lopencv_imgcodecs
                     -lopencv_highgui -lopencv_viz)

#add_library(mve STATIC IMPORTED)
#set_property(TARGET mve APPEND INTERFACE_INCLUDE_DIRECTORIES
#  ${MVE_INCLUDE_DIRS}
#  )
#set_property(TARGET mve )

#if(APPLE)
#  add_library(ceres SHARED IMPORTED)
#else()
#  add_library(ceres STATIC IMPORTED)
#endif()


