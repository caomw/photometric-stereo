#include "app_settings.h"
#include <util/arguments.h>

AppSettings& AppSettings::instance()
{
  static AppSettings _inst;
  return _inst;
}

AppSettings& AppSettings::initialize(int argc, char** argv)
{
  util::Arguments args;
  args.set_exit_on_error(true);
  args.set_nonopt_minnum(2);
  args.set_nonopt_maxnum(3);
  args.set_helptext_indent(25);
  args.set_usage("Usage: ph-bundle-adjust [ OPTS ] SCENE_DIR MESH_IN MESH_OUT");
  args.set_description("Perform Photometric Bundle Adjustment to Refine Mesh");
  args.add_option('i', "image", true, "Name of color image to use [undistorted]");
  args.add_option('d', "depth", true, "Name of depth map to use [depth-L0]");
  args.add_option('v', "view", true, "Selected view [0]");
  args.parse(argc, argv);

  AppSettings& conf = instance();
  conf.depthmap = "depth-L0";
  conf.image = "undistored";
  conf.view = 0;

  while (util::ArgResult const* arg = args.next_result()) {
    if (!arg->opt)
      continue;

    switch (arg->opt->sopt) {
      case 'd': conf.depthmap = arg->arg; break;
      case 'i': conf.image = arg->arg; break;
      case 'v': conf.view = arg->get_arg<int>(); break;
      case 'F':
        {
          int scale = arg->get_arg<int>();
          conf.depthmap = "depth-L" + util::string::get<int>(scale);
          conf.image = (scale == 0 ?
                        "undistored" :
                        "undist-L" + util::string::get<int>(scale));
        } break;
      default: throw std::runtime_error("Unknown option");
    }
  }

  conf.scene = args.get_nth_nonopt(0);
  conf.mesh = args.get_nth_nonopt(1);

  return conf;
}
