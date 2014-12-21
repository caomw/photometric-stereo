from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser(description='Generate images of a simple cube')
    parser.add_argument('--width', type=int, help='Width [640]', default=640)
    parser.add_argument('--height', type=int, help='Height [480]', default=480)
    parser.add_argument('name', help='Base Name of output images')
    return parser.parse_args()

ARGS = parse_args()

import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLUT import *

class CubeRenderer:

    def __init__(self):
        self._build_mesh()
        self._setup_vbo()
        self._setup_shaders()
        self._setup_fbo()

    def __del__(self):
        self._cleanup_fbo()
        self._cleanup_shaders()
        self._cleanup_vbo()

    def draw(self):
        pass

    def get_result(self):
        pass

    def _setup_vbo(self):
        pass

    def _setup_fbo(self):
        pass

    def _setup_shaders(self):
        pass

    def _cleanup_vbo(self):
        pass

    def _cleanup_fbo(self):
        pass

    def _cleanup_shaders(self):
        pass

    def _build_mesh(self):
        vert = np.empty((8,3), dtype=np.float32)
        vert[0,:] = [1, 1, 1]
        vert[1,:] = [1, 1, -1]
        vert[2,:] = [-1, 1, -1]
        vert[3,:] = [-1, 1, 1]
        vert[4,:] = [1, -1, 1]
        vert[5,:] = [1, -1, -1]
        vert[6,:] = [-1, -1, -1]
        vert[7,:] = [-1, -1, 1]
        indi = np.empty((20), dtype=np.uint16)
        indi[0:3] = [0, 1, 3]
        indi[3:5] = [2, 7]
        indi[5:7] = [6, 4]
        indi[7:9] = [5, 0]
        indi[9:11] = [1, 100]
        indi[11:16] = [6, 2, 5, 1, 100]
        indi[16:20] = [4, 0, 7, 3]
        self.vertices = vert
        self.indices = indi
        self.primitive_restart_index = 100
        self.primitive_type = GL_TRIANGLE_STRIP

    # Cube Vertices
    #
    #  Y
    #  ^
    #  |
    #  |  2 ----- 1
    #  |  |\      |\
    #  |  | \     | \
    #  |  |  3 ---+- 0
    #  |  |  |    |  |
    #  |  6 -+--- 5  |
    #  |   \ |     \ |
    #  |    \|      \|
    #  |     7 ----- 4
    #  |
    #  |--------------------> X

cube_renderer = CubeRenderer()
#print(cube_renderer.vertices)
#print(cube_renderer.indices)
