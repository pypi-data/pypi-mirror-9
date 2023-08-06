from setuptools import setup, Extension
import os, stat
from distutils.extension import Extension
#from Cython.Distutils import build_ext
#from setuptools.command.build_ext import build_ext


# ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install  -e .

def remove_readonly(func, path, excinfo):
    os.chmod(os.path.dirname(path), stat.S_IRWXU)
    os.chmod(path, stat.S_IRWXU)
    func(path)

library_dirs = []

if 'CAPD_SRCDIR' in os.environ:
    import shutil

    for p in ['capdRedHom','tests', 'src']:
        if os.path.exists(p):
            shutil.rmtree(p, onerror=remove_readonly)

    for p in ['capdRedHom', 'tests', 'src']:
        if not os.path.exists(p):
            shutil.copytree(os.environ['CAPD_SRCDIR'] + '/python/' + p, p, shutil.ignore_patterns('*.pyc', '*~', '#*'))
            os.chmod(p, 0755) # for generated files



    if os.path.exists('capdRedHom/version.py'):
        if os.access('capdRedHom/version.py', os.W_OK):
            shutil.copy('version.py', 'capdRedHom/version.py')
    elif os.access('capdRedHom', os.W_OK):
        shutil.copy('version.py', 'capdRedHom/version.py')



if 'CAPD_LIB_DIR'  in os.environ:
    library_dirs.append(os.environ['CAPD_LIB_DIR']) # force -L flag, do not trust LIBRARY_PATH env, because compiler ignorse its order it when a library is in multiple places


# We need to have api.so linked with libcapdapiRedHom_py, because then api.so can be on PYTHONPATH (in package directory) and we do not worry about dependencies in runtime.
ext_modules = [
    Extension('capdRedHom.api', ['src/api.cpp'],
              language='C++',
              library_dirs=library_dirs,
              libraries=['capdapiRedHom_py'],
              )
]

try:
    import numpy
    numpy_helpers_ext = Extension("capdRedHom.numpy_helpers",
                                sources=["src/numpy_helpers.c"],
                                include_dirs=[numpy.get_include()],
                                library_dirs=library_dirs,
                                libraries=['capdapiRedHom_py'])
    ext_modules.append(numpy_helpers_ext)
except ImportError as ex:
    pass


setup(name='capdRedHomPy',
      version='4.2.81',
      packages=[
          'capdRedHom',
          'capdRedHom.persistence',
      ],
      package_dir = {
          'capdRedHom' : 'capdRedHom',
          'capdRedHom.persistence' : 'capdRedHom/persistence',
      },
#      setup_requires=['nose>=1.0'],
#      install_requires=['cython'],
      test_suite = 'nose.collector',
#      cmdclass = {'build_ext': build_ext},
      ext_modules = ext_modules,
      )
