from distutils.core import setup
from distutils.extension import Extension
import platform, sys, os.path
from os.path import join, isdir
from glob import glob, iglob

try:
    import numpy
except:
    print('Numpy is required')
    print('pip install numpy')
    sys.exit(1)

if platform.system() == 'Darwin':
    LIB_PREFIX = '/usr/local/lib/mve/libs'
elif platform.system() == 'Linux':
    LIB_PREFIX = '/opt/mve/libs'
else:
    raise RuntimeError('Unknown Operating System')

if not isdir(LIB_PREFIX):
    raise RuntimeError(LIB_PREFIX + ' should be a directory')

def get_include_dirs():
    global LIB_PREFIX
    return [LIB_PREFIX, numpy.get_include()]

def get_library_dirs():
    global LIB_PREFIX
    return [join(LIB_PREFIX, 'mve'), join(LIB_PREFIX, 'util')]

def get_libraries():
    return ['mve', 'mve_util']

def extensions():
    return [Extension('mve.core', 
                      sources = glob(join('src', 'core', '*.cpp')),
                      include_dirs = get_include_dirs(),
                      library_dirs = get_library_dirs(),
                      libraries = get_libraries(),
                      language = 'c++',
                      define_macros = [('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')]
                      )]

setup(
    name = 'mve',
    ext_modules = extensions()
)
