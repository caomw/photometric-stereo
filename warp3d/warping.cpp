#include "warping.h"
#include "app_settings.h"

#include <mve/depthmap.h>
#include <mve/image_io.h>
#include <mve/mesh_io.h>
#include <mve/view.h>

#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

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

    cv::Mat cv_img(reg_img->height(), reg_img->width(), CV_8UC3,
                   reg_img->get_byte_pointer());
    cv::imshow("view image", cv_img);
    cv::waitKey(0);

    view->cache_cleanup();
  }

  ref_view->cache_cleanup();
}

const char* WarpPassVertCode =
  "#version 330 core\n"
  "in vec4 pos;\n"
  "out vec4 position;\n"
  "uniform mat4 ref_viewmat;\n"
  "uniform mat4 ref_projmat;\n"
  "void main()\n"
  "{\n"
  "  position = pos;\n"
  "  gl_Position = ref_projmat * (ref_viewmat * pos);\n"
  "  //gl_Position = pos;\n"
  "}\n"
;

const char* WarpPassFragCode =
  "#version 330 core\n"
  "in vec4 position;\n"
  "uniform sampler2D view_tex;\n"
  "uniform mat4 viewmat;\n"
  "uniform mat4 ref_projmat;\n"
  "layout(location=0) out vec4 color;\n"
  "void main()\n"
  "{\n"
  "  //color = texture(view_tex, position.xy);\n"
  "  color = vec4(1.0, 0.0, 0.0, 1.0);\n"
  "}\n"
;

mve::ByteImage::Ptr Warping::warp(mve::View::Ptr view,
                                  mve::View::Ptr ref_view)
{
  mve::ByteImage::Ptr img = view->get_byte_image(m_ImageName);
  if (img == NULL)
    return mve::ByteImage::Ptr();
  mve::ByteImage::Ptr ref_img = ref_view->get_byte_image(m_ImageName);

  const mve::CameraInfo& cam = view->get_camera();
  const mve::CameraInfo& ref_cam = ref_view->get_camera();
  int width = ref_img->width(), height = ref_img->height();
  ref_cam.debug_print();

  // OpenGL
  mve::TriangleMesh::Ptr mesh = m_Mesh;
  auto mesh_renderer = ogl::MeshRenderer::create(mesh);
  auto program = ogl::ShaderProgram::create();
  program->load_vert_code(WarpPassVertCode);
  program->load_frag_code(WarpPassFragCode);
  program->bind();
  program->send_uniform("view_tex", 0);
  {
    float mat[16], pos[3];
    ref_cam.fill_camera_pos(pos);
    //ref_cam.fill_world_to_cam(mat);
    mat[0] = 1.0f, mat[1] = 0.0f, mat[2] = 0.0f, mat[3] = -pos[0];
    mat[4] = 0.0f, mat[5] = 1.0f, mat[6] = 0.0f, mat[7] = -pos[1];
    mat[8] = 0.0f, mat[9] = 0.0f, mat[10] = 1.0f, mat[11] = -pos[2];
    mat[12] = 0.0f, mat[13] = 0.0f, mat[14] = 0.0f, mat[15] = 1.0f;
    //ref_cam.fill_cam_to_world(mat);
    program->send_uniform("ref_viewmat", math::Matrix4f(mat));
  }
  {
    float dim_aspect = width / height;
    float image_aspect = dim_aspect * ref_cam.paspect;
    float ax, ay;
    if (image_aspect < 1.0f) /* Portrait. */ {
      ax = ref_cam.flen * height / ref_cam.paspect;
      ay = ref_cam.flen * height;
    } else /* Landscape. */ {
      ax = ref_cam.flen * width;
      ay = ref_cam.flen * width * ref_cam.paspect;
    }
    float znear = 0.1f, zfar = 500.0f;
    math::Matrix4f mat(0.0f);
    //mat(0, 0) = ax / width;
    //std::cout << ax << "\n";
    mat(0, 0) = 0.5f;
    //mat(0, 2) = /* width */ ref_cam.ppoint[0];
    //mat(1, 1) = ay / height;
    mat(1, 1) = 0.5f;
    //mat(1, 2) = /* height */ ref_cam.ppoint[1];
    mat(2, 2) = -(zfar + znear) / (zfar - znear);
    mat(2, 3) = -2.0f * zfar * znear / (zfar - znear);
    mat(3,2) = -1;
    //mat(2, 2) = 1.0f;
    program->send_uniform("ref_projmat", mat);
  }
  mesh_renderer->set_shader(program);

  auto view_tex = ogl::Texture::create();
  view_tex->upload(img);

  GLuint color_tex, depth_rbo, fbo;
  glGenTextures(1, &color_tex);
  glGenRenderbuffers(1, &depth_rbo);
  glGenFramebuffers(1, &fbo);
  glBindTexture(GL_TEXTURE_2D, color_tex);
  glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, width, height, 0,
               GL_RGBA, GL_UNSIGNED_INT_8_8_8_8, NULL);
  glBindRenderbuffer(GL_RENDERBUFFER, depth_rbo);
  glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height);
  glBindFramebuffer(GL_FRAMEBUFFER, fbo);
  glFramebufferTexture(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, color_tex, 0);
  glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                            GL_RENDERBUFFER, depth_rbo);
  glBindFramebuffer(GL_FRAMEBUFFER, 0);
  glBindRenderbuffer(GL_RENDERBUFFER, 0);
  glBindTexture(GL_TEXTURE_2D, 0);

  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, fbo);
  glDrawBuffer(GL_COLOR_ATTACHMENT0);
  glViewport(0, 0, width, height);
  //glClearColor(1.0, 0.0, 0.0 , 1.0);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  glEnable(GL_DEPTH_TEST);
  glActiveTexture(GL_TEXTURE0);
  view_tex->bind();
  mesh_renderer->draw();
  glFlush();

  mve::ByteImage::Ptr registered_img = mve::ByteImage::create();
  mve::ByteImage::Ptr out_img = registered_img;
  out_img->allocate(width, height, 4);

  // Read Pixel Output
  glBindTexture(GL_TEXTURE_2D, color_tex);
  //view_tex->bind();
  glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8,
                out_img->get_byte_pointer());

  // Clean up
  glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);

  out_img->delete_channel(3);
  return registered_img;
}
