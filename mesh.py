# Mesh in OpenGL

import numpy
from plyfile import PlyData

class Mesh:
    """A Triangle Mesh"""
    def __init__(self):
        pass
    def load(self, filename):
        data = PlyData.read(filename)
        vdata = data['vertex'].data
        self.vertices = (vdata['x'], vdata['y'], vdata['z'])
        self.vsize = 3 * 4
        self.vcount = len(vdata['x'])
        self.faces = data['face'].data['vertex_indices']

import OpenGL
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *

class GLMesh:
    """A Triangle Mesh for OpenGL"""
    def __init__(self, mesh):
        vb = glGenBuffers(1)
        ib = glGenBuffers(1)
        vao = glGenVertexArrays(1)
        self._vertex_buffer = vb
        self._index_buffer = ib
        self._vertex_array_object = vao
        # Initialize Vertex Buffer
        vbsize = mesh.vsize * mesh.vcount
        vbdata = numpy.transpose(mesh.vertices).flatten()
        glBindBuffer(GL_ARRAY_BUFFER, vb)
        glBufferData(GL_ARRAY_BUFFER, vbsize, vbdata, GL_STATIC_DRAW)
        # Initialize Index Buffer
        ibsize = len(mesh.faces) * 3 * 4
        self._num_faces = len(mesh.faces)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ibsize, mesh.faces.flatten(), GL_STATIC_DRAW)
        # Initialize Vertex Array Object
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vb)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ib)
        # Cleanup
        glBindVertexArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    def draw(self):
        glBindVertexArray(self._vertex_array_object)
        glDrawElements(GL_TRIANGLES, self._num_faces, GL_UNSIGNED_INT, 0)
        # Cleanup
        glBindVertexArray(0)

