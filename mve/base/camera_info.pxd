# cython: c_string_type=unicode, c_string_encoding=utf8

cdef extern from 'mve/camera.h' namespace 'mve':
    cdef cppclass CameraInfo:
        CameraInfo() except +
        float flen
        float ppoint[2]
        float paspect
        float dist[2]
        float trans[3]
        float rot[9]
