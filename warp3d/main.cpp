#include "app_settings.h"
#include "warping.h"

#include <mve/depthmap.h>
#include <mve/image_io.h>
#include <mve/mesh_io.h>
#include <mve/view.h>
#include <ogl/opengl.h>
#include <ogl/mesh_renderer.h>
#include <ogl/shader_program.h>
#include <ogl/camera.h>
#include <ogl/texture.h>
#ifdef __APPLE__
#  include <GLUT/GLUT.h>
#endif

#include <iostream>

static mve::Scene::Ptr scene;
static mve::TriangleMesh::Ptr mesh;
static ogl::MeshRenderer::Ptr mesh_renderer;
static ogl::ShaderProgram::Ptr warp_program; 

static const char* WarpPassVertCode = 
"#version 330 core\n"
"in vec4 pos;\n"
"out vec4 position;\n"
"//uniform mat4 viewmat;\n"
"//uniform mat4 projmat;\n"
"void main()\n"
"{\n"
"  position = pos;\n"
"  //gl_Position = projmat * (viewmat * pos);\n"
"  gl_Position = pos;\n"
"}\n"
;

static const char* WarpPassFragCode =
"#version 330 core\n"
"in vec4 position;\n"
"uniform sampler2D view_tex;\n"
"out vec4 color;\n"
"void main()\n"
"{\n"
"  color = texture(view_tex, position.xy);\n"
"}\n"
;
// TODO: position -> another camera view -> read texel

static void init()
{
  AppSettings& conf = AppSettings::instance();

  scene = mve::Scene::create();
  scene->load_scene(conf.scene);
  mesh = mve::geom::load_mesh(conf.mesh);
  if (1) {
    mesh = mve::TriangleMesh::create();
    auto vert = mesh->get_vertices();
    vert.push_back(math::Vec3f(1.0, 1.0, 0.0));
    vert.push_back(math::Vec3f(-1.0, 1.0, 0.0));
    vert.push_back(math::Vec3f(-1.0, -1.0, 0.0));
    vert.push_back(math::Vec3f(1.0, -1.0, 0.0));
    auto face = mesh->get_faces();
    face.push_back(0);
    face.push_back(1);
    face.push_back(2);
    face.push_back(2);
    face.push_back(3);
    face.push_back(0);
  }
  mesh_renderer = ogl::MeshRenderer::create(mesh);
  warp_program = ogl::ShaderProgram::create();
  warp_program->load_vert_code(WarpPassVertCode);
  warp_program->load_frag_code(WarpPassFragCode);
}

static void render_warp(mve::View::Ptr view,
                        mve::View::Ptr ref_view)
{
  mve::ByteImage::Ptr img = view->get_byte_image(m_ImageName);
  if (img == NULL)
    return;
  mve::ByteImage::Ptr ref_img = ref_view->get_byte_image(m_ImageName);

  const mve::CameraInfo& cam = view->get_camera();
  const mve::CameraInfo& ref_cam = ref_view->get_camera();
  int width = ref_img->width(), height = ref_img->height();

  auto view_tex = ogl::Texture::create();
  view_tex->upload(img);
  view_tex->bind();
  mesh_renderer->set_shader(warp_program);
  mesh_renderer->draw();
}

static void display()
{
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  

  glutSwapBuffers();
}

int main(int argc, char* argv[])
{
  AppSettings& conf = AppSettings::initialize(argc, argv);
  glutInit(&argc, argv);

  unsigned int mode = GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH;
#ifdef __APPLE__
  mode |= GLUT_3_2_CORE_PROFILE;
#endif
  glutInitDisplayMode(mode);
  glutCreateWindow("warp3d");

  glutDisplayFunc(display);

  return 0;
}
