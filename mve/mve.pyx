# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

cimport numpy
import numpy
from util.ref_ptr cimport RefPtr
from base.image_base cimport ImageBase as CImageBase, ImageType as CImageType
cimport base.image_base as image_base
from base.camera_info cimport CameraInfo as CCameraInfo
from base.view cimport View as CView
from base.scene cimport Scene as CScene
from cython.view cimport array as cvarray
from libc.string cimport memcpy

cdef class CameraInfo:
    cdef CCameraInfo obj
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
    property translation_vector:
        def __get__(self):
            cdef float[:] t = self.obj.trans
            arr = numpy.ndarray(shape=(3), dtype=numpy.float32)
            for i in range(0,3):
                arr[i] = t[i]
            return arr
    property rotation_matrix:
        def __get__(self):
            cdef float[:] r = self.obj.rot
            arr = numpy.ndarray(shape=(3,3), dtype=numpy.float32, order='C')
            for i in range(0,3):
                for j in range(0,3):
                    arr[i, j] = r[i * 3 + j]
            return arr

cdef _image2ndarray(RefPtr[CImageBase] image):
  cdef CImageBase* img = image.get()
  cdef int height = img.height()
  cdef int width = img.width()
  cdef int channels = img.channels()
  cdef CImageType imgtype = img.get_type()
  shape = (height, width, channels)
  if imgtype == image_base.IMAGE_TYPE_UINT8:
      dtype = numpy.uint8
  elif imgtype == image_base.IMAGE_TYPE_UINT16:
      dtype = numpy.uint16
  elif imgtype == image_base.IMAGE_TYPE_FLOAT:
      dtype = numpy.float32
  cdef void *ptr = <void*> img.get_byte_pointer()
  #cdef numpy.ndarray arr = numpy.ndarray(shape=shape, dtype=dtype, order='C')
  cdef numpy.ndarray arr = numpy.zeros(shape=shape, dtype=dtype, order='C')
  memcpy(<void*>arr.data, ptr, img.get_byte_size())
  return arr

cdef class View:
    cdef RefPtr[CView] thisptr
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
            self.thisptr.get().set_name(value);
    property camera:
        def __get__(self):
            cam = CameraInfo()
            cam.obj = self.thisptr.get().get_camera()
            return cam
    def get_image(self, name):
        if not self.thisptr.get().has_image_embedding(name):
            return None
        raw = self.thisptr.get().get_image(name)
        return _image2ndarray(raw)

cdef class Scene:
    cdef RefPtr[CScene] thisptr
    def __init__(self):
        self.thisptr = CScene.create()
    def __dealloc__(self):
        self.thisptr.reset()
    def load(self, path):
        self.thisptr.get().load_scene(path)
    property views:
        def __get__(self):
            n_views = self.thisptr.get().get_views()
            views = []
            for ptr in n_views:
                obj = View()
                obj.thisptr = ptr
                views.append(obj)
            return views
