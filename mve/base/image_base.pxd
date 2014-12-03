# cython: c_string_type=unicode, c_string_encoding=utf8

from util.ref_ptr cimport RefPtr

cdef extern from 'mve/image_base.h' namespace 'mve':
    cdef enum ImageType:
        IMAGE_TYPE_UNKNOWN,
        IMAGE_TYPE_UINT8,
        IMAGE_TYPE_UINT16,
        IMAGE_TYPE_UINT32,
        IMAGE_TYPE_UINT64,
        IMAGE_TYPE_SINT8,
        IMAGE_TYPE_SINT16,
        IMAGE_TYPE_SINT32,
        IMAGE_TYPE_SINT64,
        IMAGE_TYPE_FLOAT,
        IMAGE_TYPE_DOUBLE
    cdef cppclass ImageBase:
        ImageBase() except +
        RefPtr[ImageBase] duplicate()
        int width()
        int height()
        int channels()
        bint valid()
        bint reinterpret(int,int,int)
        size_t get_byte_size()
        char* get_byte_pointer()
        ImageType get_type()
        char* get_type_string()
