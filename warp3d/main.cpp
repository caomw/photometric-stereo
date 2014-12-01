#include "app_settings.h"
#include "warping.h"

#include <ogl/opengl.h>
#ifdef __APPLE__
#  include <GLUT/GLUT.h>
#endif

#include <iostream>

int main(int argc, char* argv[])
{
  AppSettings& conf = AppSettings::initialize(argc, argv);

  Warping warping;
  warping.process();

  return 0;
}
