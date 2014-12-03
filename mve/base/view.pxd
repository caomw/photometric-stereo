# cython: c_string_type=unicode, c_string_encoding=utf8

from base.camera_info cimport CameraInfo
from base.image_base cimport ImageBase
from util.ref_ptr cimport RefPtr
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef extern from 'mve/view.h' namespace 'mve':
    cdef cppclass View:
        void set_id(size_t)
        size_t get_id()
        void set_name(string&)
        string& get_name()
        void set_camera(CameraInfo&)
        CameraInfo& get_camera()
        bint is_camera_valid()
        void clear()
        size_t cache_cleanup()
        bint has_image_embedding(string&)
        RefPtr[ImageBase] get_image(string&)
        #RefPtr[FloatImage] get_float_image(string&)
        #RefPtr[ByteImage] get_byte_image(string&)
        void print_debug()
        @staticmethod
        RefPtr[View] create()
