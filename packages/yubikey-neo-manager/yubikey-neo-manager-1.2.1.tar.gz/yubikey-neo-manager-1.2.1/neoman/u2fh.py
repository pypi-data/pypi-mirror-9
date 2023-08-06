# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from ctypes import (Structure, POINTER, c_int, c_uint, c_uint8, c_uint16,
                    c_char_p, c_size_t, c_ubyte)
from neoman.libloader import load_library

_lib = load_library('u2f-host', '0')


u2fh_rc = c_int
u2fh_initflags = c_uint


def define(name, args, res=None):
    fn = getattr(_lib, name)
    fn.argtypes = args
    fn.restype = res
    return fn


u2fh_check_version = define('u2fh_check_version', [c_char_p], c_char_p)

u2fh_devs = type('u2fh_devs', (Structure,), {})

u2fh_global_init = define('u2fh_global_init', [u2fh_initflags], u2fh_rc)
u2fh_global_done = define('u2fh_global_done', [])

u2fh_devs_init = define('u2fh_devs_init', [POINTER(POINTER(u2fh_devs))],
                        u2fh_rc)
u2fh_devs_discover = define('u2fh_devs_discover', [POINTER(u2fh_devs),
                                                   POINTER(c_uint)], u2fh_rc)
u2fh_devs_done = define('u2fh_devs_done', [POINTER(u2fh_devs)])

u2fh_is_alive = define('u2fh_is_alive', [POINTER(u2fh_devs), c_uint], c_int)
u2fh_sendrecv = define('u2fh_sendrecv', [POINTER(u2fh_devs), c_uint, c_uint8,
                                         c_char_p, c_uint16,
                                         c_char_p, POINTER(c_size_t)],
                       u2fh_rc)
u2fh_get_device_description = define('u2fh_get_device_description',
                                     [POINTER(u2fh_devs), c_int, c_char_p,
                                      POINTER(c_size_t)], u2fh_rc)


__all__ = [x for x in globals().keys() if x.lower().startswith('u2fh')]
