#include "warping.h"
#include "app_settings.h"

#include <mve/depthmap.h>
#include <mve/image_io.h>
#include <mve/mesh_io.h>
#include <mve/view.h>
// TODO: replace ogl module with glfx (by david)
#include <ogl/mesh_renderer.h>
#include <ogl/shader_program.h>
#include <ogl/camera.h>

#include <iostream>

Warping::Warping()
{
  AppSettings& conf = AppSettings::instance();

  std::cout << "Image name: " << conf.image << "\n";
  std::cout << "Depthmap name: " << conf.depthmap << "\n";

  mve::Scene::Ptr scene = mve::Scene::create();
  scene->load_scene(conf.scene);

  mve::TriangleMesh::Ptr mesh = mve::geom::load_mesh(conf.mesh);
  std::cout << "Mesh faces = " << mesh->get_faces().size() << "\n";
  std::cout << "Mesh vertices = " << mesh->get_vertices().size() << "\n";

  m_Scene = scene;
  m_Mesh = mesh;
  m_ImageName = conf.image;
  m_DepthMapName = conf.depthmap;
}

Warping::~Warping()
{
  m_Mesh.reset();
  m_Scene.reset();
}

void Warping::process(int view_id)
{
  AppSettings& conf = AppSettings::instance();
  mve::Scene::Ptr scene = m_Scene;
  //mve::TriangleMesh::Ptr mesh = m_Mesh;

  const mve::Scene::ViewList& views = scene->get_views();

  // Reference View
  mve::View::Ptr ref_view = views[(view_id < 0 ? conf.view : view_id)];
  if (ref_view == NULL) {
    throw std::runtime_error("Reference view is null");
  }

  // For each view except the reference view
  for (mve::View::Ptr view : views) {
    if (view == NULL)
      continue;
    if (view->get_id() == ref_view->get_id())
      continue;

    mve::ByteImage::Ptr reg_img = warp(view, ref_view);
    if (reg_img == NULL)
      continue;

    // TODO: Next? Save?

    view->cache_cleanup();
  }

  ref_view->cache_cleanup();
}

const char* DepthPassVertCode = 
"#version 330 core\n"
"in vec4 pos;\n"
"uniform mat4 viewmat;\n"
"uniform mat4 projmat;\n"
"void main()\n"
"{\n"
"  gl_Position = projmat * (viewmat * pos);\n"
"}\n"
;

const char* DepthPassFragCode =
"#version 330 core\n"
"void main()\n"
"{\n"
"}\n"
;

mve::ByteImage::Ptr Warping::warp(mve::View::Ptr view,
                                  mve::View::Ptr ref_view)
{
  mve::ByteImage::Ptr img = view->get_byte_image(m_ImageName);
  if (img == NULL)
    return mve::ByteImage::Ptr();
  mve::ByteImage::Ptr ref_img = ref_view->get_byte_image(m_ImageName);

  //mve::FloatImage::Ptr dmap = view->get_float_image(m_DepthMapName);
  //if (dmap == NULL)
  //  return mve::ByteImage::Ptr();

  //mve::TriangleMesh::Ptr mesh = m_Mesh;
  auto mesh_renderer = ogl::MeshRenderer::create();
  mesh_renderer->set_mesh(m_Mesh);

  const mve::CameraInfo& cam = view->get_camera();
  const mve::CameraInfo& ref_cam = ref_view->get_camera();
  int width = ref_img->width(), height = ref_img->height();

  

  auto depth_program = ogl::ShaderProgram::create();
  depth_program->load_vert_code(DepthPassVertCode);
  depth_program->load_frag_code(DepthPassFragCode);
  auto warp_program = ogl::ShaderProgram::create();

  GLuint depth_tex, depth_fbo, warp_tex, warp_fbo;
  glGenTextures(1, &depth_tex);
  glGenTextures(1, &warp_tex);
  glGenFramebuffers(1, &depth_fbo);
  glGenFramebuffers(1, &warp_fbo);
  glBindTexture(GL_TEXTURE_2D, depth_tex);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT16, width, height, 0,
               GL_DEPTH_COMPONENT, GL_UNSIGNED_SHORT, NULL);
  glBindTexture(GL_TEXTURE_2D, warp_tex);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0,
               GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, NULL);
  glBindFramebuffer(GL_FRAMEBUFFER, depth_fbo);
  glFramebufferTexture(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, depth_tex, 0);
  glBindFramebuffer(GL_FRAMEBUFFER, warp_fbo);
  glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, warp_tex, 0);
  glBindFramebuffer(GL_FRAMEBUFFER, 0);

  // TODO: Generate Depth Map
  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, depth_fbo);
  glViewport(0, 0, width, height);
  glDrawBuffer(GL_NONE);
  glBindTexture(GL_TEXTURE_2D, 0);
  depth_program->bind();
  depth_program->send_uniform();
  mesh_renderer->set_shader(depth_program);

  // TODO: 3D warping
  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, warp_fbo);
  glDrawBuffer(GL_COLOR_ATTACHMENT0);
  glBindTexture(GL_TEXTURE_2D, depth_tex);

  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
  glBindTexture(GL_TEXTURE_2D, 0);

  glFlush();

  mve::ByteImage::Ptr registered_img = mve::ByteImage::create();

  glDeleteTextures(1, &depth_tex);
  glDeleteTextures(1, &warp_tex);
  glDeleteFramebuffers(1, &depth_fbo);
  glDeleteFramebuffers(1, &warp_fbo);

  return registered_img;
}
