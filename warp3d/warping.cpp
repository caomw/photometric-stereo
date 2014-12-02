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
#include <ogl/texture.h>

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

const char* WarpPassVertCode = 
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

const char* WarpPassFragCode =
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

mve::ByteImage::Ptr Warping::warp(mve::View::Ptr view,
                                  mve::View::Ptr ref_view)
{
  mve::ByteImage::Ptr img = view->get_byte_image(m_ImageName);
  if (img == NULL)
    return mve::ByteImage::Ptr();
  mve::ByteImage::Ptr ref_img = ref_view->get_byte_image(m_ImageName);

  //mve::TriangleMesh::Ptr mesh = m_Mesh;
  auto mesh = mve::TriangleMesh::create();
  {
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

  auto mesh_renderer = ogl::MeshRenderer::create();
  mesh_renderer->set_mesh(mesh);

  const mve::CameraInfo& cam = view->get_camera();
  const mve::CameraInfo& ref_cam = ref_view->get_camera();
  int width = ref_img->width(), height = ref_img->height();

  auto warp_program = ogl::ShaderProgram::create();
  warp_program->load_vert_code(WarpPassVertCode);
  warp_program->load_frag_code(WarpPassFragCode);

  auto view_tex = ogl::Texture::create();
  view_tex->upload(img);

  //GLuint warp_tex, warp_fbo, depth_rbo;
  //glGenTextures(1, &warp_tex);
  //glGenFramebuffers(1, &warp_fbo);
  //glGenRenderbuffers(1, &depth_rbo);
  //glBindTexture(GL_TEXTURE_2D, warp_tex);
  //glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0,
  //             GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, NULL);
  //glBindFramebuffer(GL_FRAMEBUFFER, warp_fbo);
  //glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, warp_tex, 0);
  //glFramebufferRenderbuffer(GL_FRAMEBUFFER, )
  //glBindFramebuffer(GL_FRAMEBUFFER, 0);

  // TODO: 3D warping
  //glBindFramebuffer(GL_DRAW_FRAMEBUFFER, warp_fbo);
  //glDrawBuffer(GL_COLOR_ATTACHMENT0);
  view_tex->bind();
  mesh_renderer->set_shader(warp_program);
  mesh_renderer->draw();

  //glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
  //glBindTexture(GL_TEXTURE_2D, 0);
  glFlush();

  

  mve::ByteImage::Ptr registered_img = mve::ByteImage::create();

  //glDeleteFramebuffers(1, &warp_fbo);
  //glDeleteTextures(1, &warp_tex);
  //glDeleteRenderbuffers(1, &depth_rbo);

  return registered_img;
}
