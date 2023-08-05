"""
The DTrace data structures.

Created on Oct 10, 2011

@author: tmetsch
"""

# disabling 'too few public meth' pylint check (R0903)
# disabling 'Invalid name' pylint check (C0103)
# pylint: disable=R0903,C0103

from ctypes import Structure, c_int, c_void_p, c_char_p, c_char, c_uint


class dtrace_recdesc(Structure):
    """
    sys/dtrace.h:931
    """
    _fields_ = [("dtrd_offset", c_uint)]


class dtrace_aggdesc(Structure):
    """
    sys/dtrace.h:950
    """
    _fields_ = [("dtagd_rec", c_void_p)]


class dtrace_aggdata(Structure):
    """
    As defined in dtrace.h:351
    """
    _fields_ = [("dtada_handle", c_void_p),
                ("dtada_desc", dtrace_aggdesc),
                ("dtada_edesc", c_void_p),
                ("dtada_pdesc", c_void_p),
                ("dtada_data", c_void_p),
                ("dtada_normal", c_void_p),
                ("dtada_size", c_int),
                ("dtada_delta", c_void_p),
                ("dtada_percpu", c_void_p),
                ("dtada_percpu_delta", c_void_p),
                ("dtada_total", c_void_p),
                ("dtada_minbin", c_void_p),
                ("dtada_maxbin", c_void_p),
                ("dtada_flags", c_void_p)]


class dtrace_bufdata(Structure):
    """
    As defined in dtrace.h:310
    """
    _fields_ = [("dtbda_handle", c_void_p),
                ("dtbda_buffered", c_char_p),
                ("dtbda_probe", c_void_p),
                ("dtbda_recdesc", c_void_p),
                ("dtbda_aggdata", c_void_p),
                ("dtbda_flags", c_uint)]


class dtrace_probedesc(Structure):
    """
    As defined in sys/dtrace.h:884
    """
    _fields_ = [("dtrace_id_t", c_uint),
                ("dtpd_provider", c_char),
                ("dtpd_mod", c_char),
                ("dtpd_func", c_char_p),
                ("dtpd_name", c_char_p)]


class dtrace_probedata(Structure):
    """
    As defined in dtrace.h:186
    """
    _fields_ = [("dtpda_handle", c_void_p),
                ("dtpda_edesc", c_void_p),
                ("dtpda_pdesc", dtrace_probedesc),
                ("dtpda_cpu", c_int),
                ("dtpda_data", c_void_p),
                ("dtpda_flow", c_void_p),
                ("dtpda_prefix", c_void_p),
                ("dtpda_indent", c_int)]
