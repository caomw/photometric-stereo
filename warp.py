from os.path import dirname, abspath, join
import sys
ROOT_PATH = dirname(abspath(__file__))
sys.path.append(join(ROOT_PATH, 'mve'))
sys.path.append(join(ROOT_PATH, 'plyfile'))
import mve, numpy, cv2
from argparse import ArgumentParser
from plyfile import PlyData

parser = ArgumentParser(description='3D Warping')
parser.add_argument('-i', '--image', nargs='?', help='Image Name [undistored]', default='undistored')
parser.add_argument('-r', '--reference', nargs='?', help='Reference View ID [0]', default=0, type=int)
parser.add_argument('-v', '--view', nargs='*', help='View ID to Warp [ALL]', type=int)
parser.add_argument('scene', help='Scene Directory')
parser.add_argument('mesh', help='Triangle Mesh')
ARGS = parser.parse_args()

# Load Scene
print('Scene: ' + ARGS.scene)
SCENE = mve.Scene()
SCENE.load(ARGS.scene)

# Select Views
if ARGS.view == None:
    ARGS.view = map(lambda x: x.id, SCENE.views)
print('Reference View: ' + str(ARGS.reference))
print('Views to warp: ' + str(ARGS.view))

VIEWS = SCENE.views
REF_VIEW = VIEWS[ARGS.reference]
REF_IMG = REF_VIEW.get_image(ARGS.image)
WIDTH, HEIGHT = REF_IMG.shape[1], REF_IMG.shape[0]
print('Ref Image Dim = (' + str(WIDTH) + ', ' + str(HEIGHT) + ')')
VIEWS = filter(lambda x: x.id in ARGS.view, VIEWS)

# Initialize OpenGL
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from OpenGL.GLUT import *
glutInit(sys.argv)
glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH | 2048)
glutCreateWindow("warp")
def display():
    glutSwapBuffers()
glutDisplayFunc(display)

# Create VBO
data = PlyData.read(ARGS.mesh)
vdata = data['vertex'].data
vdata = (vdata['x'], vdata['y'], vdata['z'])
vdata = numpy.transpose(vdata).flatten()
fdata = data['face'].data['vertex_indices']
fdata = map(lambda x: numpy.frombuffer(x, dtype=numpy.uint32), fdata)
fdata = numpy.ravel(fdata)
VERTEX_DATA = numpy.frombuffer(vdata, dtype=numpy.float32)
INDEX_DATA = numpy.frombuffer(fdata, dtype=numpy.uint32)
VERTEX_DATA = numpy.array([
  1.0, 1.0, 0.0,
  -1.0, 1.0, 0.0,
  -1.0, -1.0, 0.0,
  1.0, -1.0, 0.0
], dtype=numpy.float32)
INDEX_DATA = numpy.array([
  0, 1, 2, 2, 3, 0
], dtype=numpy.uint32)
VERTEX_BUFFER, INDEX_BUFFER = glGenBuffers(2)
glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
glBufferData(GL_ARRAY_BUFFER, VERTEX_DATA, GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDEX_DATA, GL_STATIC_DRAW)
NUM_ELEMENTS = len(INDEX_DATA)

# Create VAO
VERTEX_ARRAY = glGenVertexArrays(1)
glBindVertexArray(VERTEX_ARRAY)
glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)

# Create Program
VertCode = """#version 330 core
layout(location=0) in vec4 pos;
out vec4 texcoord;
void main()
{
  texcoord = pos;
  gl_Position = pos;
}
"""
FragCode = """#version 330 core
in vec4 texcoord;
uniform sampler2D viewTex;
layout(location=0) out vec4 color;
void main()
{
  //color = vec4(1.0, 1.0, 0.0, 1.0);
  color = texture(viewTex, texcoord.xy * 0.5 + vec2(0.5));
}
"""
PROGRAM = shaders.compileProgram(
  shaders.compileShader(VertCode, GL_VERTEX_SHADER),
  shaders.compileShader(FragCode, GL_FRAGMENT_SHADER)
)

# Create Texture
VIEW_TEX, COLOR_TEX, DEPTH_TEX = glGenTextures(3)
glBindTexture(GL_TEXTURE_2D, VIEW_TEX)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, REF_IMG)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glBindTexture(GL_TEXTURE_2D, COLOR_TEX)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, WIDTH, HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
glBindTexture(GL_TEXTURE_2D, DEPTH_TEX)
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH24_STENCIL8, WIDTH, HEIGHT, 0, GL_DEPTH_STENCIL, GL_UNSIGNED_INT_24_8, None)

# Create Framebuffer
FRAMEBUFFER = glGenFramebuffers(1)
glBindFramebuffer(GL_FRAMEBUFFER, FRAMEBUFFER)
glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, COLOR_TEX, 0)
glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, DEPTH_TEX, 0)
glCheckFramebufferStatus(GL_FRAMEBUFFER)

# Draw
for view in VIEWS:
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, VIEW_TEX)
    img = view.get_image(ARGS.image)
    width, height = img.shape[1], img.shape[0]
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, FRAMEBUFFER)
    glViewport(0, 0, WIDTH, HEIGHT)
    glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glUseProgram(PROGRAM)
    glUniform1i(glGetUniformLocation(PROGRAM, 'viewTex'), 0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glDrawElements(GL_TRIANGLES, NUM_ELEMENTS, GL_UNSIGNED_INT, None)
    glFlush()
    
    # Readback Result
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, COLOR_TEX)
    output = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    RESULT = numpy.ndarray(shape=(HEIGHT,WIDTH,3), dtype=numpy.uint8, order='C', buffer=output)
    cv2.imshow("Result", cv2.cvtColor(RESULT, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)

# Cleanup
glDeleteProgram(PROGRAM)
glDeleteVertexArrays(1, [VERTEX_ARRAY])
glDeleteFramebuffers(1, [FRAMEBUFFER])
glDeleteBuffers(2, [VERTEX_BUFFER, INDEX_BUFFER])
glDeleteTextures([VIEW_TEX, COLOR_TEX, DEPTH_TEX])
