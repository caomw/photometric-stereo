# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

cimport base
cimport util

cdef class Scene:
    cdef util.RefPtr[base.Scene] thisptr
    def __init__(self):
        self.thisptr = base.Scene.create()
    def __dealloc__(self):
        self.thisptr.reset()
    def load(self, path):
        self.thisptr.get().load_scene(path)

cdef class View:
    pass

cdef class CameraInfo:
    pass

