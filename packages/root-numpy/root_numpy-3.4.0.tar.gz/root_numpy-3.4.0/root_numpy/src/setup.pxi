# cython: experimental_cpp_class_def=True
import numpy as np
cimport numpy as np
np.import_array()

from cpython cimport array
from cpython.ref cimport Py_INCREF, Py_XDECREF
from cpython cimport PyObject
from cpython.cobject cimport (PyCObject_AsVoidPtr,
                              PyCObject_Check,
                              PyCObject_FromVoidPtr)
from cython.operator cimport dereference as deref, preincrement as inc

from libcpp.vector cimport vector
from libcpp.map cimport map as cpp_map
from libcpp.pair cimport pair
from libcpp.string cimport string, const_char
from libc.string cimport memcpy
from libc.stdlib cimport malloc, free, realloc

try:
    from collections import OrderedDict
except ImportError:
    # Fall back on drop-in
    from .extern.ordereddict import OrderedDict

import atexit
import warnings
from _warnings import RootNumpyUnconvertibleWarning

ctypedef unsigned char unsigned_char
ctypedef unsigned short unsigned_short
ctypedef unsigned int unsigned_int
ctypedef unsigned long unsigned_long
ctypedef long long long_long
ctypedef unsigned long long unsigned_long_long

include "ROOT.pxi"
include "root_numpy.pxi"

