from mesh import Mesh, GLMesh
from OpenGL.GL import *
from OpenGL.GLUT import *
import numpy

mesh = Mesh()
mesh.load('tmp/surface.ply')
print(mesh.vertices)
print(mesh.faces)

glmesh = None
glprogram = 0
glcamera = 0

def init():
    global glmesh, mesh
    glEnable(GL_DEPTH_TEST)
    glmesh = GLMesh(mesh)
    

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH | 2048)
    glutCreateWindow("PLY File View")
    init()
    #glutDisplayFunc(display)
    #glutReshapeFunc(reshape)
    #glutMainLoop()

if __name__ == '__main__':
    main()
