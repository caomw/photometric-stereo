#include "warping.h"
#include "app_settings.h"

#include <mve/depthmap.h>
#include <mve/image_io.h>
#include <mve/mesh_info.h>
#include <mve/mesh_io.h>
#include <mve/mesh_tools.h>
#include <mve/view.h>

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

mve::ByteImage::Ptr Warping::warp(mve::View::Ptr view,
                                  mve::View::Ptr ref_view)
{
  mve::ByteImage::Ptr img = view->get_byte_image(m_ImageName);
  if (img == NULL)
    return mve::ByteImage::Ptr();

  mve::FloatImage::Ptr dmap = view->get_float_image(m_DepthMapName);
  if (dmap == NULL)
    return mve::ByteImage::Ptr();

  const mve::CameraInfo& cam = view->get_camera();
  const mve::CameraInfo& ref_cam = ref_view->get_camera();

  // TODO: Generate Depth Map
  // TODO: 3D warping
  mve::ByteImage::Ptr registered_img = mve::ByteImage::create();

  return registered_img;
}
