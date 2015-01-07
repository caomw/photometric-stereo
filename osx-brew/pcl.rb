require 'formula'

class Pcl < Formula
  homepage 'http://pointclouds.org'
  url 'https://github.com/PointCloudLibrary/pcl/archive/pcl-1.7.2.zip'
  sha1 '54328ee79f13c77f7a9cbd0b812506e2a0d01cdc'
  head 'https://github.com/PointCloudLibrary/pcl.git'

  option "with-fzapi", "Build with Fotonic Camera support"
  option "with-pxcapi", "Build with PXC Device support"
  option "without-qt", "Build without Qt"
  option "with-cuda", "Build with CUDA"
  option "without-vtk", "Build without VTK"
  option "with-qhull", "Build with Qhull"
  option "with-libusb", "Build with libusb"
  #option "with-openni", "Build with OpenNI"
  #option "with-openni2", "Build with OpenNI 2"

  #option :cxx11

  depends_on "pkg-config"  => :build
  depends_on "cmake"      => :build # >= 2.8.3
  depends_on "boost" # >= 1.46.1
  depends_on "eigen" # >= 3.0.0
  depends_on "flann" # >= 1.6.8
  depends_on "qt"         => :recommended
  depends_on "vtk"        => [:recommended, "with-qt"] # >= 5.6.1
  depends_on "qhull"      => :optional # >= 2011.1
  depends_on "libusb"     => :optional
  #depends_on "openni"     => :optional
  #depends_on "openni2"     => :optional
  depends_on :libpng
  #depends_on "python"     => :recommended

  #resource "python-binding" do
  #  url 'https://github.com/strawlab/python-pcl.git'
  #end

  def install
    args = std_cmake_args + %W(
      -DCMAKE_OSX_DEPLOYMENT_TARGET=
    )

    args << "-DWITH_LIBUSB=#{build.with?("libusb").to_s.upcase}"
    #args << "-DWITH_OPENNI=#{build.with?("openni").to_s.upcase}"
    #args << "-DWITH_OPENNI2=#{build.with?("openni2").to_s.upcase}"
    args << "-DWITH_OPENNI=FALSE"
    args << "-DWITH_OPENNI2=FALSE"
    args << "-DWITH_FZAPI=#{build.with?("fzapi").to_s.upcase}"
    args << "-DWITH_PXCAPI=#{build.with?("pxcapi").to_s.upcase}"
    args << "-DWITH_QHULL=#{build.with?("qhull").to_s.upcase}"
    args << "-DWITH_QT=#{build.with?("qt").to_s.upcase}"
    args << "-DWITH_VTK=#{build.with?("vtk").to_s.upcase}"
    args << "-DWITH_MPI=FALSE"
    args << "-DWITH_DOCS=FALSE"
    args << "-DWITH_PCAP=FALSE"

    if build.with?("cuda")
      args << "-DWITH_CUDA=TRUE"
      args << "-DCMAKE_CXX_FLAGS=-stdlib=libstdc++"
    else
      args << "-DWITH_CUDA=FALSE"
    end

    mkdir "macbuild" do
      system "cmake", "..", *args
      system "make"
      system "make install"
    end

    #if build.with? "python"
    #  ENV['PKG_CONFIG_PATH'] = (lib/'pkgconfig').to_s
    #  resource("python-binding").stage do
    #    system "python", "setup.py", "install", "--prefix=#{prefix}"
    #  end
    #end

  end
end
