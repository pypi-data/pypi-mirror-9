import os, sys

try:
    import libcapdapiRedHom_py as capd_impl
except ImportError as ex:
    error_msg='''
Cannot import capdRedHom C++ API!
Please make sure that:
1) CAPD package is installed (see http://capd.sourceforge.net/capdRedHom/docs/html/capd_getit.html).

2) Dynamic library libcapdapiRedHom_py is on PYTHONPATH:
{}


3) libcapdapiRedHom_py dependencies are on LD_LIBRARY_PATH (use 'ldd <libfile_path>') (and on DYLD_LIBRARY_PATH for OSX, use 'otool -L <libfile_path>').

Error message:
{}
'''.format(sys.path, str(ex))
    raise ImportError(error_msg), None, sys.exc_info()[2]

has_numpy_helpers = True

try:
    import numpy_helpers
except:
    has_numpy_helpers = False
    pass
