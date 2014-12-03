# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

from libcpp.string cimport string
from libcpp.vector cimport vector
from util cimport RefPtr

cdef extern from 'mve/scene.h' namespace 'mve':
    cdef cppclass Scene:
        void load_scene(string)
        @staticmethod
        RefPtr[Scene] create()

cdef class PyScene:
    cdef RefPtr[Scene] thisptr
    def __init__(self):
        self.thisptr = Scene.create()
    def __dealloc__(self):
        self.thisptr.reset()
    def load(self, path):
        self.thisptr.get().load_scene(path)

