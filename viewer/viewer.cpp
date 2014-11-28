#include <mve/camera.h>
#include <mve/depthmap.h>
#include <mve/image.h>
#include <mve/image_io.h>
#include <mve/mesh.h>
#include <mve/mesh_info.h>
#include <mve/mesh_io.h>
#include <mve/mesh_tools.h>
#include <mve/view.h>
#include <mve/scene.h>
#include <util/arguments.h>

#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/viz.hpp>

#include <iostream>

struct AppSettings {
   //std::string depthmap;
   std::string image;
   std::string scene;
};

static AppSettings& _conf();
static void _setup_settings(int argc, const char * const * argv);

int main(int argc, char* argv[])
{
  _setup_settings(argc, argv);

  std::cout << "Image name: " << _conf().image << "\n";
  //std::cout << "Depthmap name: " << _conf().depthmap << "\n";

  mve::Scene::Ptr scene = mve::Scene::create();
  scene->load_scene(_conf().scene);

  const mve::Scene::ViewList& views = scene->get_views();
  for (mve::View::Ptr view : views) {
    if (view == NULL)
      continue;

    mve::ByteImage::Ptr img = view->get_byte_image(_conf().image);
    if (img == NULL) {
      std::cout << "img is null\n";
      continue;
    }

    //mve::FloatImage::Ptr dmap = view->get_float_image(_conf().depthmap);
    //if (dmap == NULL)
    //  continue;

    const mve::CameraInfo& cam = view->get_camera();

    cv::Mat mveimg(img->height(), img->width(), CV_8UC3,
                   img->get_byte_pointer());
    cv::Mat cvimg;
    cv::cvtColor(mveimg, cvimg, cv::COLOR_RGB2BGR);
    cv::imshow("view image", cvimg);
    cv::waitKey(0);

    //dmap.reset();
    img.reset();
    view->cache_cleanup();
  }

  return 0;
}

static AppSettings& _conf()
{
  static AppSettings instance;
  return instance;
}

static void _init_arguments(util::Arguments& args);

static void _setup_settings(int argc, const char * const * argv)
{
  util::Arguments args;
  _init_arguments(args);
  args.parse(argc, argv);

  AppSettings& conf = _conf();
  //conf.depthmap = "depth-L0";
  conf.image = "undistored";

  // Scan Arguments
  while (util::ArgResult const* arg = args.next_result()) {
    if (!arg->opt)
      continue;

    switch (arg->opt->sopt) {
      //case 'd': conf.depthmap = arg->arg; break;
      case 'i': conf.image = arg->arg; break;
      case 'F':
        {
          int scale = arg->get_arg<int>();
          //conf.depthmap = "depth-L" + util::string::get<int>(scale);
          conf.image = (scale == 0 ?
                        "undistored" :
                        "undist-L" + util::string::get<int>(scale));
        } break;
      default: throw std::runtime_error("Unknown option");
    }
  }

  conf.scene = args.get_nth_nonopt(0);
}

static void _init_arguments(util::Arguments& args)
{
  args.set_exit_on_error(true);
  args.set_nonopt_minnum(1);
  args.set_nonopt_maxnum(3);
  args.set_helptext_indent(25);
  args.set_usage("Usage: ph-bundle-adjust [ OPTS ] SCENE_DIR MESH_IN MESH_OUT");
  args.set_description("Perform Photometric Bundle Adjustment to Refine Mesh");
  args.add_option('i', "image", true, "Name of color image to use [undistorted]");
}
