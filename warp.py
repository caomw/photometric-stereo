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

ZNEAR, ZFAR = 0.1, 500.0

REF_CAM = REF_VIEW.camera
#view_mat = numpy.identity(4, dtype=numpy.float32)
#view_mat[0:3, 3] = -REF_CAM.translation_vector
#view_mat[0:3, 3] = [ 0.0, 0.0, -10.0 ]
world_mat = numpy.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, -1.0, 0.0, 0.0],
    [0.0, 0.0, -1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0]
], dtype=numpy.float32)
view_mat = numpy.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, -10.0],
    [0.0, 0.0, 0.0, 1.0]
], dtype=numpy.float32)
view_mat = numpy.dot(view_mat, world_mat)
#view_mat = REF_CAM.world_to_cam_matrix
#view_mat = REF_CAM.cam_to_world_matrix
#correction_mat = numpy.identity(4, dtype=numpy.float32)
#correction_mat[3,3] = 1
#view_mat = numpy.dot(correction_mat, REF_CAM.world_to_cam_matrix)
#print(numpy.dot(REF_CAM.cam_to_world_matrix, [0, 0, 0, 1]))
#print(numpy.dot(REF_CAM.cam_to_world_matrix, [0, 0, 1, 0]))
#print(REF_CAM.viewing_direction)
proj_mat = numpy.identity(4, dtype=numpy.float32)
aspect = float(WIDTH) / float(HEIGHT)
proj_mat[0, 0] = 1.0 / aspect
proj_mat[2, 2:4] = [(ZNEAR+ZFAR)/(ZNEAR-ZFAR), (2*ZNEAR*ZFAR)/(ZNEAR-ZFAR)]
proj_mat[3, :] = [0, 0, -1, 0]
REF_TRANSFORM_MATRIX = numpy.dot(proj_mat, view_mat)
#print(REF_TRANSFORM_MATRIX)

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
if True:
    data = PlyData.read(ARGS.mesh)
    vdata = data['vertex'].data
    vdata = (vdata['x'], vdata['y'], vdata['z'])
    #vmax = tuple(numpy.amax(vdata[i]) for i in range(0,3))
    #vmin = tuple(numpy.amin(vdata[i]) for i in range(0,3))
    #vmean = tuple(numpy.mean(vdata[i]) for i in range(0,3))
    #print(vmax)
    #print(vmin)
    #print(vmean)
    vdata = numpy.transpose(vdata).flatten()
    fdata = data['face'].data['vertex_indices']
    fdata = map(lambda x: numpy.frombuffer(x, dtype=numpy.uint32), fdata)
    fdata = numpy.ravel(fdata)
    VERTEX_DATA = numpy.frombuffer(vdata, dtype=numpy.float32)
    INDEX_DATA = numpy.frombuffer(fdata, dtype=numpy.uint32)
else:
    VERTEX_DATA = numpy.array([
        1.0, 1.0, 0.0,
        -1.0, 1.0, 0.0,
        -1.0, -1.0, 0.0,
        1.0, -1.0, 0.0
    ], dtype=numpy.float32)
    INDEX_DATA = numpy.array([
        0, 1, 2, 2, 3, 0
    ], dtype=numpy.uint32)
VERTEX_BUFFER, INDEX_BUFFER, CONE_BUFFER = glGenBuffers(3)
glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
glBufferData(GL_ARRAY_BUFFER, VERTEX_DATA, GL_STATIC_DRAW)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, INDEX_DATA, GL_STATIC_DRAW)
NUM_ELEMENTS = len(INDEX_DATA)
CONE_DATA = numpy.array([
    0.0, 0.0, 0.0,
    0.5, 0.5, 1.0,
    -0.5, 0.5, 1.0,
    0.0, 0.0, 0.0,
    0.5, -0.5, 1.0,
    -0.5, -0.5, 1.0,
    0.0, 0.0, 0.0
], dtype=numpy.float32)
glBindBuffer(GL_ARRAY_BUFFER, CONE_BUFFER)
glBufferData(GL_ARRAY_BUFFER, CONE_DATA, GL_STATIC_DRAW)
CONE_NUM_ELEMENTS = len(CONE_DATA)/3

# Create VAO
VERTEX_ARRAY, CONE_ARRAY = glGenVertexArrays(2)
glBindVertexArray(VERTEX_ARRAY)
glBindBuffer(GL_ARRAY_BUFFER, VERTEX_BUFFER)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
glBindVertexArray(CONE_ARRAY)
glBindBuffer(GL_ARRAY_BUFFER, CONE_BUFFER)
glEnableVertexAttribArray(0)
glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)

# Create Program
VertCode = """#version 330 core
layout(location=0) in vec4 pos;
out vec4 texcoord;
uniform mat4 refTransform;
uniform mat4 camTransform;
void main()
{
  //texcoord = pos;
  //gl_Position = pos;
  texcoord = camTransform * pos;
  gl_Position = refTransform * pos;
}
"""
FragCode = """#version 330 core
in vec4 texcoord;
uniform sampler2D viewTex;
layout(location=0) out vec4 color;
void main()
{
  vec3 coord = texcoord.xyz / texcoord.w;
  //coord = coord * 0.5 + vec3(0.5);
  //coord = coord - vec3(0.5);
  color = texture(viewTex, coord.xy);
}
"""
PROGRAM = shaders.compileProgram(
  shaders.compileShader(VertCode, GL_VERTEX_SHADER),
  shaders.compileShader(FragCode, GL_FRAGMENT_SHADER)
)

ConeVertCode = """#version 330 core
layout(location=0) in vec4 pos;
out vec4 color;
uniform mat4 refTransform;
void main()
{
  color = mix(vec4(1.0), vec4(1.0, 0.0, 0.0, 0.0), abs(pos.z));
  gl_Position = refTransform * pos;
}
"""
ConeFragCode = """#version 330 core
layout(location=0) out vec4 FragColor;
in vec4 color;
void main()
{
  FragColor = color;
}
"""
CONE_PROGRAM = shaders.compileProgram(
  shaders.compileShader(ConeVertCode, GL_VERTEX_SHADER),
  shaders.compileShader(ConeFragCode, GL_FRAGMENT_SHADER)
)

# Create Texture
VIEW_TEX, COLOR_TEX, DEPTH_TEX = glGenTextures(3)
glBindTexture(GL_TEXTURE_2D, VIEW_TEX)
#glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, REF_IMG)
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
    if img is None:
        continue
    width, height = img.shape[1], img.shape[0]
    # X: Because OpenGL Texture's origin is at left-bottom, not left-top
    # img = numpy.flipud(img)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    
    cam = view.camera
    view_mat = cam.world_to_cam_matrix
    proj_mat = numpy.zeros(shape=(4,4), dtype=numpy.float32)
    proj_mat[0:3,0:3] = cam.calibration_matrix(width, height)
    proj_mat[2,:] = [0, 0, 1, 0]
    proj_mat[3,:] = [0, 0, 1, 0]
    proj_mat[0,:] *= 1.0 / float(width)
    proj_mat[1,:] *= 1.0 / float(height)
    print(proj_mat)
    cam_transform_matrix = numpy.dot(proj_mat, view_mat)
    
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, FRAMEBUFFER)
    glViewport(0, 0, WIDTH, HEIGHT)
    glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    #glEnable(GL_CULL_FACE)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    if True:
        glBindVertexArray(VERTEX_ARRAY)
        glUseProgram(PROGRAM)
        glUniform1i(glGetUniformLocation(PROGRAM, 'viewTex'), 0)
        loc = glGetUniformLocation(PROGRAM, 'refTransform')
        glUniformMatrix4fv(loc, 1, GL_TRUE, REF_TRANSFORM_MATRIX)
        loc = glGetUniformLocation(PROGRAM, 'camTransform')
        glUniformMatrix4fv(loc, 1, GL_TRUE, cam_transform_matrix)
        glDrawElements(GL_TRIANGLES, NUM_ELEMENTS, GL_UNSIGNED_INT, None)
    if True:
        glBindVertexArray(CONE_ARRAY)
        glUseProgram(CONE_PROGRAM)
        loc = glGetUniformLocation(CONE_PROGRAM, 'refTransform')
        mat = numpy.dot(REF_TRANSFORM_MATRIX, cam.cam_to_world_matrix)
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat)
        glDrawArrays(GL_LINE_STRIP, 0, CONE_NUM_ELEMENTS)
    glFlush()
    
    # Readback Result
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, COLOR_TEX)
    output = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    output = numpy.ndarray(shape=(HEIGHT,WIDTH,3), dtype=numpy.uint8, order='C', buffer=output)
    # Because the origin of OpenGL framebuffer is at left-bottom,
    # It's required to vertically flip the result image
    RESULT = numpy.flipud(output)
    cv2.imshow("Result", cv2.cvtColor(RESULT, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)

# Cleanup
glDeleteProgram(PROGRAM)
glDeleteProgram(CONE_PROGRAM)
glDeleteVertexArrays(2, [VERTEX_ARRAY, CONE_ARRAY])
glDeleteFramebuffers(1, [FRAMEBUFFER])
glDeleteBuffers(3, [VERTEX_BUFFER, INDEX_BUFFER, CONE_BUFFER])
glDeleteTextures([VIEW_TEX, COLOR_TEX, DEPTH_TEX])
