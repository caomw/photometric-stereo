# cython: c_string_type=unicode, c_string_encoding=utf8

from util.ref_ptr cimport RefPtr
from libcpp.vector cimport vector
from libcpp.string cimport string

ctypedef unsigned int VertexID

cdef packed struct Vec3f:
    np.float32_t x, y, z

cdef extern from 'mve/mesh.h' namespace 'mve':
    cdef cppclass TriangleMesh:
        RefPtr[TriangleMesh] duplicate()
        vector[Vec3f]& get_vertices()
        vector[Vec3f]& get_vertex_normals()
        vector[VertexID]& get_faces()
        @staticmethod
        RefPtr[TriangleMesh] create()

