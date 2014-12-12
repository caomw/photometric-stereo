from os.path import dirname, abspath, join
import sys
ROOT_PATH = dirname(abspath(__file__))
sys.path.append(join(ROOT_PATH, 'mve'))
sys.path.append(join(ROOT_PATH, 'plyfile'))
import mve, numpy, cv2
from argparse import ArgumentParser
from plyfile import PlyData

parser = ArgumentParser(description='3D Warping')
parser.add_argument('-i', '--image', nargs='?', help='Image Name [undistorted]', default='undistorted')
parser.add_argument('-r', '--reference', nargs='?', help='Reference View ID [0]', default=0, type=int)
parser.add_argument('-v', '--view', nargs='*', help='View ID to Warp [ALL]', type=int)
parser.add_argument('--znear', nargs='?', help='Nearest Z Value (for Depth)', default=2.0, type=float)
parser.add_argument('--zfar', nargs='?', help='Farest Z Value (for Depth)', default=500.0, type=float)
parser.add_argument('--debug-resize', dest='debug_resize', action='store_true')
parser.add_argument('--no-debug-resize', dest='debug_resize', action='store_false')
parser.set_defaults(debug_resize=False)
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

# define camera projection matrix
def camera_projection_matrix(cam, width, height, znear, zfar):
    view_mat = cam.world_to_cam_matrix
    proj_mat = numpy.zeros(shape=(4,4), dtype=numpy.float32)
    proj_mat[0:3,0:3] = cam.calibration_matrix(width, height)
    proj_mat[2,2] = (znear+zfar) / (zfar-znear)
    proj_mat[2,3] = (-2*znear*zfar) / (zfar-znear)
    proj_mat[3,:] = [0, 0, 1, 0]
    proj_mat[0,:] *= 1.0 / float(width)
    proj_mat[1,:] *= 1.0 / float(height)
    return numpy.dot(proj_mat, view_mat)

ZNEAR, ZFAR = ARGS.znear, ARGS.zfar

REF_CAM = REF_VIEW.camera
REF_TRANSFORM_MATRIX = camera_projection_matrix(REF_CAM, WIDTH, HEIGHT, ZNEAR, ZFAR)
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
# cv2.namedWindow('gl', cv2.WINDOW_AUTOSIZE | cv2.WINDOW_OPENGL)

# Create VBO
if True:
    data = PlyData.read(ARGS.mesh)
    vdata = data['vertex'].data
    vdata = (vdata['x'], vdata['y'], vdata['z'])
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

uniform mat4 refTransform;
uniform mat4 camTransform;
uniform vec3 camPosition;

out V2G {
  vec4 texcoord;
  vec3 dir_to_cam;
  vec3 position;
} result;

void main()
{
  result.texcoord = camTransform * pos;
  result.dir_to_cam = normalize(camPosition - pos.xyz);
  result.position = pos.xyz;
  
  vec4 proj_pos = refTransform * pos;
  float w = proj_pos.w;
  vec2 xy = proj_pos.xy;
  xy.y = w - xy.y;
  xy = (2.0 * xy) - vec2(w);
  proj_pos.xy = xy;
  gl_Position = proj_pos;
}
"""
GeomCode = """#version 330 core
layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

in V2G {
  vec4 texcoord;
  vec3 dir_to_cam;
  vec3 position;
} vs_input[];

out G2F {
  vec4 texcoord;
  vec3 dir_to_cam;
  vec3 normal;
} result;

void main()
{
  // Compute Normal
  vec3 v1 = vs_input[1].position - vs_input[0].position;
  vec3 v2 = vs_input[2].position - vs_input[0].position;
  vec3 normal = normalize(cross(v1, v2));
  
  for (int i = 0; i < 3; ++i) {
    gl_Position = gl_in[i].gl_Position;
    result.texcoord = vs_input[i].texcoord;
    result.dir_to_cam = vs_input[i].dir_to_cam;
    result.normal = normal;
    EmitVertex();
  }
  EndPrimitive();
}
"""

FragCode = """#version 330 core
layout(location=0) out vec4 FragColor;

uniform sampler2D viewTex;
uniform sampler2D shadowTex;

in G2F {
  vec4 texcoord;
  vec3 dir_to_cam;
  vec3 normal;
} gs_input;

void main()
{
  vec4 texcoord = gs_input.texcoord;
  vec3 normal = gs_input.normal;
  vec3 dir_to_cam = gs_input.dir_to_cam;
  vec3 coord = texcoord.xyz / texcoord.w;
  //coord = coord * 0.5 + vec3(0.5);
  //coord = coord - vec3(0.5);
  float depth = texture(shadowTex, coord.xy).r - (coord.z + 1.0)*0.5;
  if (depth < -0.001) { discard; }
  //if (depth < -0.0001 || dot(normal, dir_to_cam) < 0.001) { discard; }
  FragColor = texture(viewTex, coord.xy);
  //FragColor = vec4(normal * 0.5 + vec3(0.5), 1.0);
}
"""

DepthFragCode = """#version 330 core
layout(location=0) out vec4 color;
void main()
{
  color = vec4(1.0);
}
"""
PROGRAM = shaders.compileProgram(
  shaders.compileShader(VertCode, GL_VERTEX_SHADER),
  shaders.compileShader(GeomCode, GL_GEOMETRY_SHADER),
  shaders.compileShader(FragCode, GL_FRAGMENT_SHADER)
)
DEPTH_PROGRAM = shaders.compileProgram(
  shaders.compileShader(VertCode, GL_VERTEX_SHADER),
  shaders.compileShader(DepthFragCode, GL_FRAGMENT_SHADER)
)

ShadowVertCode = """#version 330 core
layout(location=0) in vec4 pos;
uniform mat4 transform;
void main()
{
  vec4 proj_pos = transform * pos;
  float w = proj_pos.w;
  vec2 xy = proj_pos.xy;
  // Vertically flip depth map on purpose!
  //xy.y = w - xy.y; // original version, should be commented out
  xy = (2.0 * xy) - vec2(w);
  proj_pos.xy = xy;
  gl_Position = proj_pos;
}
"""
ShadowFragCode = """#version 330 core
void main() {}
"""
SHADOW_PROGRAM = shaders.compileProgram(
  shaders.compileShader(ShadowVertCode, GL_VERTEX_SHADER),
  shaders.compileShader(ShadowFragCode, GL_FRAGMENT_SHADER)
)

# Create Texture
VIEW_TEX, COLOR_TEX, DEPTH_TEX, SHADOW_TEX = glGenTextures(4)
glBindTexture(GL_TEXTURE_2D, COLOR_TEX)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, WIDTH, HEIGHT, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
glBindTexture(GL_TEXTURE_2D, DEPTH_TEX)
glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH24_STENCIL8, WIDTH, HEIGHT, 0, GL_DEPTH_STENCIL, GL_UNSIGNED_INT_24_8, None)
# VIEW_TEX, SHADOw_TEX will be initialized later

# Create Framebuffer
FRAMEBUFFER, SHADOW_FRAMEBUFFER = glGenFramebuffers(2)
glBindFramebuffer(GL_FRAMEBUFFER, FRAMEBUFFER)
glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, COLOR_TEX, 0)
glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, DEPTH_TEX, 0)
glCheckFramebufferStatus(GL_FRAMEBUFFER)
# SHADOW_FRAMEBUFFER will be initialized later

# Draw
for view in VIEWS:
    # Prepare View Texture
    glBindTexture(GL_TEXTURE_2D, VIEW_TEX)
    img = view.get_image(ARGS.image)
    if img is None:
        continue
    width, height = img.shape[1], img.shape[0]
    #img.fill(255)
    # X: Because OpenGL Texture's origin is at left-bottom, not left-top
    # img = numpy.flipud(img)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    
    # Prepare Shadow Texture
    glBindTexture(GL_TEXTURE_2D, SHADOW_TEX)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT32, width, height, 0, GL_DEPTH_COMPONENT, GL_UNSIGNED_INT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
    
    # Prepare Shadow Framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, SHADOW_FRAMEBUFFER)
    glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, SHADOW_TEX, 0)
    
    # Projection Matrix
    cam = view.camera
    cam_transform_matrix = camera_projection_matrix(cam, width, height, ZNEAR, ZFAR)
    
    # Bind Model (Vertex Array, Vertex Buffer, Index Buffer)
    glBindVertexArray(VERTEX_ARRAY)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, INDEX_BUFFER)
    
    # Generate Shadow Map
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, SHADOW_FRAMEBUFFER)
    glViewport(0, 0, width, height)
    glDrawBuffer(GL_NONE)
    glClear(GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glDisable(GL_CULL_FACE) # Eliminate isolated fragments
    glUseProgram(SHADOW_PROGRAM)
    loc = glGetUniformLocation(SHADOW_PROGRAM, 'transform')
    glUniformMatrix4fv(loc, 1, GL_TRUE, cam_transform_matrix)
    glDrawElements(GL_TRIANGLES, NUM_ELEMENTS, GL_UNSIGNED_INT, None)
    
    # Setup Render Target
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, FRAMEBUFFER)
    glViewport(0, 0, WIDTH, HEIGHT)
    glDrawBuffers(1, [GL_COLOR_ATTACHMENT0])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    
    # Bind Texture
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, VIEW_TEX)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, SHADOW_TEX)
    
    # Depth Pass
    glUseProgram(DEPTH_PROGRAM)
    loc = glGetUniformLocation(DEPTH_PROGRAM, 'refTransform')
    glUniformMatrix4fv(loc, 1, GL_TRUE, REF_TRANSFORM_MATRIX)
    glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
    glEnable(GL_DEPTH_TEST)
    # GL_CULL_FACE is disabled to eliminate isolated fragments
    glDepthFunc(GL_LESS)
    glDrawElements(GL_TRIANGLES, NUM_ELEMENTS, GL_UNSIGNED_INT, None)
    
    # Color Pass
    glUseProgram(PROGRAM)
    glUniform1i(glGetUniformLocation(PROGRAM, 'viewTex'), 0)
    glUniform1i(glGetUniformLocation(PROGRAM, 'shadowTex'), 1)
    loc = glGetUniformLocation(PROGRAM, 'refTransform')
    glUniformMatrix4fv(loc, 1, GL_TRUE, REF_TRANSFORM_MATRIX)
    loc = glGetUniformLocation(PROGRAM, 'camTransform')
    glUniformMatrix4fv(loc, 1, GL_TRUE, cam_transform_matrix)
    loc = glGetUniformLocation(PROGRAM, 'camPosition')
    glUniform3f(loc, *(cam.position))
    glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_CULL_FACE) # For speed
    glDrawElements(GL_TRIANGLES, NUM_ELEMENTS, GL_UNSIGNED_INT, None)
    
    glFlush()
    
    # Readback Result
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, COLOR_TEX)
    output = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    output = numpy.ndarray(shape=(HEIGHT,WIDTH,3), dtype=numpy.uint8, order='C', buffer=output)
    # Because the origin of OpenGL framebuffer is at left-bottom,
    # It's required to vertically flip the result image
    RESULT = numpy.flipud(output)
    if ARGS.debug_resize:
        RESULT = cv2.resize(RESULT, (800, 600))
    cv2.imshow("Result", cv2.cvtColor(RESULT, cv2.COLOR_RGB2BGR))
    glBindTexture(GL_TEXTURE_2D, SHADOW_TEX)
    output = glGetTexImage(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
    output = numpy.ndarray(shape=(height,width), dtype=numpy.float32, order='C', buffer=output)
    #print(numpy.amin(output))
    SHADOW_RESULT = output
    if ARGS.debug_resize:
        SHADOW_RESULT = cv2.resize(SHADOW_RESULT, (800, 600))
    cv2.imshow("Shadow", SHADOW_RESULT)
    cv2.waitKey(0)
    
    # Cleanup View
    view.cleanup_cache()

# Cleanup
glDeleteProgram(PROGRAM)
glDeleteProgram(DEPTH_PROGRAM)
glDeleteProgram(SHADOW_PROGRAM)
glDeleteVertexArrays(1, [VERTEX_ARRAY])
glDeleteFramebuffers(2, [FRAMEBUFFER, SHADOW_FRAMEBUFFER])
glDeleteBuffers(2, [VERTEX_BUFFER, INDEX_BUFFER])
glDeleteTextures([VIEW_TEX, COLOR_TEX, DEPTH_TEX, SHADOW_TEX])
