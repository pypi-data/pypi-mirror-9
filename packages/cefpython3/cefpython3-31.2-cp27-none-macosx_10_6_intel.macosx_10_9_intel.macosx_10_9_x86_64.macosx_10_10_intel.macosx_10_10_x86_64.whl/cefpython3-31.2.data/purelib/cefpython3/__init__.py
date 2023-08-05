__all__ = ["cefpython", "wx"]
__version__ = "31.2"
__author__ = "The CEF Python authors"

import os
import ctypes

package_dir = os.path.dirname(os.path.abspath(__file__))

# On Mac it works without setting library paths, but let's set it
# just to be sure.
os.environ["LD_LIBRARY_PATH"] = package_dir
os.environ["DYLD_LIBRARY_PATH"] = package_dir

# This env variable will be returned by cefpython.GetModuleDirectory().
os.environ["CEFPYTHON3_PATH"] = package_dir

# This loads the libcef.so library for the main python executable.
# The libffmpegsumo.so library shouldn't be loaded here, it could
# cause issues to load it in the browser process.
libcef_so = os.path.join(package_dir, "libcef.dylib")
ctypes.CDLL(libcef_so, ctypes.RTLD_GLOBAL)

import sys
if 0x02070000 <=  sys.hexversion < 0x03000000:
    from . import cefpython_py27 as cefpython
else:
    raise Exception("Unsupported python version: " + sys.version)
