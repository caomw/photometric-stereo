# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp.string cimport string

cdef extern from 'mve/camera.h' namespace 'mve':
    cdef cppclass CameraInfo:
        CameraInfo() except +
        float flen
        float ppoint[2]
        float paspect
        float dist[2]
        float trans[3]
        float rot[9]
        void fill_camera_pos(float*)
        void fill_camera_translation(float*)
        void fill_viewing_direction(float*)
        void fill_calibration(float*, float, float)
        void fill_inverse_calibration(float*, float, float)
        void fill_cam_to_world(float*)
        void fill_world_to_cam(float*)
        void fill_reprojection(CameraInfo&, float, float, float, float, float*, float*)
        string to_ext_string()
        void from_ext_string(string&)
        string to_int_string()
        void from_int_string(string&)
        void debug_print()
