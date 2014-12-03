# cython: c_string_type=unicode, c_string_encoding=utf8

from base.view cimport View
from util.ref_ptr cimport RefPtr
from libcpp.string cimport string
from libcpp.vector cimport vector

cdef extern from 'mve/scene.h' namespace 'mve':
    cdef cppclass Scene:
        void load_scene(string&)
        vector[RefPtr[View]]& get_views()
        @staticmethod
        RefPtr[Scene] create()
