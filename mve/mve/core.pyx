# distutils: language = c++
# cython: c_string_type=unicode, c_string_encoding=utf8

cimport numpy
import numpy
from mve.util.ref_ptr cimport RefPtr
from mve.base.image_base cimport ImageBase as CImageBase, ImageType as CImageType
cimport mve.base.image_base as image_base
from mve.base.image_base cimport ImageBase as CImageBase
from mve.base.camera_info cimport CameraInfo as CCameraInfo
from mve.base.view cimport View as CView
from mve.base.scene cimport Scene as CScene
from cython.view cimport array as cvarray
from libc.string cimport memcpy
from cpython cimport PyObject, Py_INCREF

numpy.import_array()

cdef int _ImageType2NumpyDType(CImageType tp):
    if tp == image_base.IMAGE_TYPE_UINT8:
        return numpy.NPY_UINT8
    elif tp == image_base.IMAGE_TYPE_UINT16:
        return numpy.NPY_UINT16
    elif tp == image_base.IMAGE_TYPE_UINT32:
        return numpy.NPY_UINT32
    elif tp == image_base.IMAGE_TYPE_UINT64:
        return numpy.NPY_UINT64
    elif tp == image_base.IMAGE_TYPE_SINT8:
        return numpy.NPY_INT8
    elif tp == image_base.IMAGE_TYPE_SINT16:
        return numpy.NPY_INT16
    elif tp == image_base.IMAGE_TYPE_SINT32:
        return numpy.NPY_INT32
    elif tp == image_base.IMAGE_TYPE_SINT64:
        return numpy.NPY_INT64
    elif tp == image_base.IMAGE_TYPE_FLOAT:
        return numpy.NPY_FLOAT32
    elif tp == image_base.IMAGE_TYPE_DOUBLE:
        return numpy.NPY_FLOAT64
    else:
        raise TypeError('Unknown MVE Image Type')

cdef class ImageBase:
    cdef RefPtr[CImageBase] thisptr

    @staticmethod
    cdef create(RefPtr[CImageBase] ptr):
        obj = ImageBase()
        obj.thisptr = ptr
        return obj

    def __dealloc__(self):
        self.thisptr.reset()
        #print('image deallocated')

    property width:
        def __get__(self):
            return self.thisptr.get().width()

    property height:
        def __get__(self):
            return self.thisptr.get().height()

    property channels:
        def __get__(self):
            return self.thisptr.get().channels()

    property valid:
        def __get__(self):
            return self.thisptr.get().valid()

    property byte_size:
        def __get__(self):
            return self.thisptr.get().get_byte_size()

    cdef void* get_pointer(self):
        return <void*> self.thisptr.get().get_byte_pointer()

    cdef numpy.ndarray to_numpy(self):
        cdef numpy.npy_intp shape[3]
        shape[0] = <numpy.npy_intp> self.thisptr.get().height()
        shape[1] = <numpy.npy_intp> self.thisptr.get().width()
        shape[2] = <numpy.npy_intp> self.thisptr.get().channels()
        cdef int ndim = 3 if shape[2] > 1 else 2
        cdef int dtype = _ImageType2NumpyDType(self.thisptr.get().get_type())
        cdef void *ptr = self.get_pointer()
        return numpy.PyArray_SimpleNewFromData(ndim, shape, dtype, ptr)

    def __array__(self):
        return self.to_numpy()

    property raw:
        def __get__(self):
            cdef numpy.ndarray arr = numpy.array(self, copy=False)
            arr.base = <PyObject*> self
            Py_INCREF(self)
            return arr

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
    property world_to_cam_matrix:
        def __get__(self):
            cdef numpy.ndarray arr = numpy.zeros(shape=(4,4), dtype=numpy.float32, order='C')
            self.obj.fill_world_to_cam(<float*>arr.data)
            return arr
    property cam_to_world_matrix:
        def __get__(self):
            cdef numpy.ndarray arr = numpy.zeros(shape=(4,4), dtype=numpy.float32, order='C')
            self.obj.fill_cam_to_world(<float*>arr.data)
            return arr
    property position:
        def __get__(self):
            cdef float vec[3]
            self.obj.fill_camera_pos(vec)
            return (vec[0], vec[1], vec[2])
    property viewing_direction:
        def __get__(self):
            cdef float vec[3]
            self.obj.fill_viewing_direction(vec)
            return (vec[0], vec[1], vec[2])
    def calibration_matrix(self, width, height):
        cdef numpy.ndarray arr = numpy.zeros(shape=(3,3), dtype=numpy.float32, order='C')
        self.obj.fill_calibration(<float*>arr.data, width, height)
        return arr
    def inverse_calibration_matrix(self, width, height):
        cdef numpy.ndarray arr = numpy.zeros(shape=(3,3), dtype=numpy.float32, order='C')
        self.obj.fill_inverse_calibration(<float*>arr.data, width, height)
        return arr

cdef class View:
    cdef RefPtr[CView] thisptr

    @staticmethod
    cdef create(RefPtr[CView] ptr):
        obj = View()
        obj.thisptr = ptr
        return obj

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
        cdef RefPtr[CImageBase] img = self.thisptr.get().get_image(name)
        return ImageBase.create(img)

    def cleanup_cache(self):
        self.thisptr.get().cache_cleanup()

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
                views.append(View.create(ptr))
            return views
