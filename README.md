Photometric Stereo
==================

## Dependencies

- Python 2.7
- OpenCV 2.4 / 3.x
- Numpy (`pip install numpy`)
- Cython (`pip install Cython`)
- PyOpenGL (`pip install PyOpenGL PyOpenGL-accelerate`)
- MVE (Multi-View Environment)

## Build

    cd mve
    python setup.py build_ext --inplace

## Run

    python warp.py -iIMANE_NAME SCENE PLY_MESH

## References

### 1. Ceres Solver

by Sameer Agarwal, Keir Mierle and Others

- [website](http://ceres-solver.org)

### 2. Photometric Bundle Adjustment for Dense Multi-View 3D Modeling (CVPR'14)

by Amaël Delaunoy and Marc Pollefeys

- [paper](http://www.inf.ethz.ch/personal/marc.pollefeys/pubs/DelaunoyCVPR14.pdf)
- [website](https://hal.inria.fr/hal-00985811/)

### 3. Photometric Stereo Using Internet Images (3DV'14)

by Boxin Shi, Kenji Inose, Yasuyuki Matsushita, Ping Tan, Sai-Kit Yeung, and Katsushi Ikeuchi

- [paper](http://web.media.mit.edu/~shiboxin/project_pages/Shi_3DV14_Web_files/Shi_3DV14.pdf)
- [website](https://www.google.com.tw/search?client=safari&rls=en&q=photometric+stereo+using+internet+images&ie=UTF-8&oe=UTF-8&gfe_rd=cr&ei=3KJwVM3uGYLB8AXV-ICgDA)

### 4. Numpy

NumPy is the fundamental package for scientific computing with Python

- [website](http://www.numpy.org)
- [github](https://github.com/numpy/numpy)
- [openhub](https://www.openhub.net/p/numpy)
