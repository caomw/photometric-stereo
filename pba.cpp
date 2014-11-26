#include <ceres/ceres.h>
#include <glog/logging.h>

#include <mve/image.h>
#include <mve/image_io.h>
#include <mve/view.h>
#include <mve/scene.h>

#include <util/arguments.h>

static void _initArguments(util::Arguments& args);

int main(int argc, char* argv[])
{
  google::InitGoogleLogging(argv[0]);

  util::Arguments args;
  _initArguments(args);
  args.parse(argc, argv);

  mve::Scene::Ptr scene = mve::Scene::create();
  scene->load_scene(args.get_nth_nonopt(0));

  mve::Scene::ViewList const& views = scene->get_views();
  for (mve::View::Ptr view : views) {
    
  }

  return 0;
}

static void _initArguments(util::Arguments& args)
{
  args.set_exit_on_error(true);
  args.set_nonopt_minnum(1);
  args.set_nonopt_maxnum(3);
  args.set_helptext_indent(25);
  args.set_usage("Usage: ph-bundle-adjust [ OPTS ] SCENE_DIR MESH_IN MESH_OUT");
  args.set_description("Perform Photometric Bundle Adjustment to Refine Mesh");
  // args.add_option
}
