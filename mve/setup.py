from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from platform import system
from os.path import join, isdir
import numpy

if system() == 'Darwin':
    prefix = '/usr/local/lib/mve/libs'
elif system() == 'Linux':
    prefix = '/opt/mve/libs'
else:
    raise RuntimeError('Unknown Operating System')

if not isdir(prefix):
    raise RuntimeError(prefix + ' should be a directory')

extensions = [
    Extension("*", ["*.pyx"],
        include_dirs = [prefix, numpy.get_include()],
        library_dirs = [join(prefix, 'mve'), join(prefix, 'util')],
        libraries = ['mve', 'mve_util'],
        language = 'c++'
    )
]

setup(
    name = 'mve',
    ext_modules = cythonize(extensions)
)
