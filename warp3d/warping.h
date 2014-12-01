#pragma once

#include <mve/camera.h>
#include <mve/image.h>
#include <mve/mesh.h>
#include <mve/scene.h>

class Warping {
public:
  Warping();
  ~Warping();
  void process(int view_id = -1);
private:
  mve::ByteImage::Ptr warp(mve::View::Ptr view, mve::View::Ptr ref_view);
private:
  mve::Scene::Ptr m_Scene;
  mve::TriangleMesh::Ptr m_Mesh;
  std::string m_ImageName;
  std::string m_DepthMapName;
};
