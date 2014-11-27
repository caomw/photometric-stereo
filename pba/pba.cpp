#include <ceres/ceres.h>
#include <glog/logging.h>

#include <mve/camera.h>
#include <mve/image.h>
#include <mve/image_io.h>
#include <mve/view.h>
#include <mve/scene.h>
#include <util/arguments.h>

#include <iostream>

struct AppSettings {
   std::string image;
};

static AppSettings& _conf();
static void _initArguments(util::Arguments& args);

int main(int argc, char* argv[])
{
  google::InitGoogleLogging(argv[0]);

  util::Arguments args;
  _initArguments(args);
  args.parse(argc, argv);

  AppSettings& conf = _conf();
  // conf.depthmap = "depth-L0";
  conf.image = "undistored";

  // Scan Arguments
  while (util::ArgResult const* arg = args.next_result()) {
    if (!arg->opt)
      continue;

    switch (arg->opt->sopt) {
      // case 'd': conf.depthmap = arg->arg; break;
      case 'i': conf.image = arg->arg; break;
      case 'F':
        {
          int scale = arg->get_arg<int>();
          // depthmap = "depth-L" + util::string::get<int>(scale);
          conf.image = (scale == 0 ?
                        "undistored" :
                        "undist-L" + util::string::get<int>(scale));
        } break;
      default: throw std::runtime_error("Unknown option");
    }
  }

  mve::Scene::Ptr scene = mve::Scene::create();
  scene->load_scene(args.get_nth_nonopt(0));

  const mve::Scene::ViewList& views = scene->get_views();
  for (mve::View::Ptr view : views) {
    const mve::CameraInfo& cam = view->get_camera();
    mve::ByteImage::Ptr img = view->get_byte_image(conf.image);
    
    // std::cout << img->width() << ", " << img->height() << "\n";
    //float pos[3];
    //cam.fill_camera_pos(pos);
    //std::cout << pos[0] << ' ' << pos[1] << ' ' << pos[2] << "\n";
  }

  return 0;
}

static AppSettings& _conf()
{
  static AppSettings instance;
  return instance;
}

static void _initArguments(util::Arguments& args)
{
  args.set_exit_on_error(true);
  args.set_nonopt_minnum(1);
  args.set_nonopt_maxnum(3);
  args.set_helptext_indent(25);
  args.set_usage("Usage: ph-bundle-adjust [ OPTS ] SCENE_DIR MESH_IN MESH_OUT");
  args.set_description("Perform Photometric Bundle Adjustment to Refine Mesh");
  args.add_option('i', "image", true, "Name of color image to use [undistorted]");
}
