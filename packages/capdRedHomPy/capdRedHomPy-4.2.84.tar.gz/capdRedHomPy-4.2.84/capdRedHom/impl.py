import os, sys


def __bootstrap__():
   global __bootstrap__, __loader__, __file__
   import sys, pkg_resources, imp
   __file__ = pkg_resources.resource_filename(__name__,'api.so')
   __loader__ = None; del __bootstrap__, __loader__
   try:
       imp.load_dynamic('capdRedHom',__file__)
   except ImportError as ex:
       error_msg='''

Cannot import capdRedHom C++ API!
Please make sure that:
1) CAPD package is installed (see http://capd.sourceforge.net/capdRedHom/docs/html/capd_getit.html).

2) Dynamic libraries: libcapd, libcapdapiRedHom_py are on LD_LIBRARY_PATH (and on DYLD_LIBRARY_PATH for OSX).

3) libcapdapiRedHom_py dependencies are on LD_LIBRARY_PATH (use 'ldd <libfile_path>') (and on DYLD_LIBRARY_PATH for OSX, use 'otool -L <libfile_path>').

Error message:
{}
'''.format(sys.path, str(ex))
       raise ImportError(error_msg), None, sys.exc_info()[2]


__bootstrap__()
import libcapdapiRedHom_py as capd_impl

has_numpy_helpers = True

try:
    import numpy_helpers
except ImportError as ex:
    has_numpy_helpers = False
    pass
