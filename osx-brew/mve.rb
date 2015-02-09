require 'formula'

class Mve < Formula
  homepage 'http://www.gris.tu-darmstadt.de/projects/multiview-environment/'
  head 'https://github.com/simonfuhrmann/mve.git'

  depends_on :libpng
  depends_on 'jpeg'
  depends_on 'libtiff'

  def mve_root
    lib/'mve'
  end

  def install
    if ENV.compiler == :clang
      ENV['CXXFLAGS'] = '-stdlib=libc++'
      ENV['LDFLAGS'] = '-stdlib=libc++'
    end

    system 'make'
    system 'make', '-C', 'apps/bundle2ply'
    system 'make', '-C', 'apps/dmrecon'
    system 'make', '-C', 'apps/makescene'
    system 'make', '-C', 'apps/meshconvert'
    system 'make', '-C', 'apps/mveshell'
    system 'make', '-C', 'apps/scene2pset'
    system 'make', '-C', 'apps/sfmrecon'

    IO.write 'mve-config.cmake',
             (MVE_CONFIG_CMAKE).gsub('$(MVE_ROOT)', mve_root)

    mve_root.install 'Makefile.inc'
    cd 'libs' do
      %w(math dmrecon mve ogl sfm util).each do |name|
        (mve_root/'libs'/name).install Dir["#{name}/*.{h,a,inc}"]
      end
    end
    bin.install 'apps/bundle2ply/bundle2ply' => 'mve-bundle2ply'
    bin.install 'apps/dmrecon/dmrecon' => 'mve-dmrecon'
    bin.install 'apps/makescene/makescene' => 'mve-makescene'
    bin.install 'apps/meshconvert/meshconvert' => 'mve-meshconvert'
    bin.install 'apps/mveshell/mveshell' => 'mve-mveshell'
    bin.install 'apps/scene2pset/scene2pset' => 'mve-scene2pset'
    bin.install 'apps/sfmrecon/sfmrecon' => 'mve-sfmrecon'
    (lib/'cmake/mve').install 'mve-config.cmake'
  end

  MVE_CONFIG_CMAKE = <<CMAKE
set(MVE_INCLUDE_DIRS "$(MVE_ROOT)/libs")
set(MVE_LIBRARIES "$(MVE_ROOT)/libs/dmrecon/libmve_dmrecon.a"
                  "$(MVE_ROOT)/libs/mve/libmve.a"
                  "$(MVE_ROOT)/libs/ogl/libmve_ogl.a"
                  "$(MVE_ROOT)/libs/sfm/libmve_sfm.a"
                  "$(MVE_ROOT)/libs/util/libmve_util.a")
set(MVE_FOUND TRUE)
CMAKE

end
