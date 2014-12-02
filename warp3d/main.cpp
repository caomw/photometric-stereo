#include "app_settings.h"
#include "warping.h"

#include <ogl/opengl.h>
#ifdef __APPLE__
#  include <GLUT/GLUT.h>
#endif

#include <iostream>

void display()
{
  glutSwapBuffers();
}

int main(int argc, char* argv[])
{
  AppSettings& conf = AppSettings::initialize(argc, argv);
  glutInit(&argc, argv);

  unsigned int mode = GLUT_RGBA | GLUT_DOUBLE;
#ifdef __APPLE__
  mode |= GLUT_3_2_CORE_PROFILE;
#endif
  glutInitDisplayMode(mode);
  glutCreateWindow("warp3d");
  glutDisplayFunc(display);

  Warping warping;
  warping.process();

  return 0;
}
