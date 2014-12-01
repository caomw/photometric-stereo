#pragma once
#include <string>

struct AppSettings {
  std::string depthmap;
  std::string image;
  std::string scene;
  std::string mesh;
  int view;

  static AppSettings& initialize(int argc, char** argv);
  static AppSettings& instance();
};
