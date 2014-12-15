from distutils.core import setup
from distutils.extension import Extension
import platform, sys, os.path
from os.path import join, isdir
from glob import glob, iglob

try:
    from Cython.Build import cythonize
except:
    print('Cython is required to setup')
    print('pip install Cython')
    sys.exit(1)

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

def make_extensions():
    extensions = []
    for path in iglob(join('mve', '*.pyx')):
        e = Extension(path.replace(os.path.sep, '.')[:-4],
                sources = [path],
                include_dirs = get_include_dirs(),
                library_dirs = get_library_dirs(),
                libraries = get_libraries(),
                language = 'c++'
            )
        extensions.append(e)
    return extensions

setup(
    name = 'mve',
    ext_modules = cythonize(make_extensions())
)
