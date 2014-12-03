# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

cimport base
cimport util
cimport numpy

cdef class CameraInfo:
    cdef base.CameraInfo obj
    def __init__(self):
        pass
    def __dealloc__(self):
        pass
    property focal_length:
        def __get__(self):
            return self.obj.flen
    property principal_point:
        def __get__(self):
            return (self.obj.ppoint[0], self.obj.ppoint[1])
    property pixel_apsect:
        def __get__(self):
            return self.obj.paspect
    property distortion_parameters:
        def __get__(self):
            return (self.obj.dist[0], self.obj.dist[1])
    #property translation_vector:
    #property rotation_matrix:

cdef class View:
    cdef util.RefPtr[base.View] thisptr
    def __init__(self):
        pass
    def __dealloc__(self):
        self.thisptr.reset()
    property id:
        def __get__(self):
            return self.thisptr.get().get_id()
        def __set__(self, value):
            self.thisptr.get().set_id(value)
    property name:
        def __get__(self):
            return str(self.thisptr.get().get_name())
        def __set__(self, value):
            self.thisptr.get().set_name(value.encode());
    property camera:
        def __get__(self):
            cam = CameraInfo()
            cam.obj = self.thisptr.get().get_camera()
            return cam

cdef class Scene:
    cdef util.RefPtr[base.Scene] thisptr
    def __init__(self):
        self.thisptr = base.Scene.create()
    def __dealloc__(self):
        self.thisptr.reset()
    def load(self, path):
        self.thisptr.get().load_scene(path.encode())
    property views:
        def __get__(self):
            n_views = self.thisptr.get().get_views()
            views = []
            for ptr in n_views:
                obj = View()
                obj.thisptr = ptr
                views.append(obj)
            return views

