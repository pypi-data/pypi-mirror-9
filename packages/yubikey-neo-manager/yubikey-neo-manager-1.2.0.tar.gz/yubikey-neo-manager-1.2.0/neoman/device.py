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

from neoman.model.modes import MODE


class BaseDevice(object):

    @property
    def default_name(self):
        return 'YubiKey NEO'

    @property
    def supported(self):
        return True

    @property
    def device_type(self):
        raise NotImplementedError()

    @property
    def mode(self):
        raise NotImplementedError()

    @property
    def allowed_modes(self):
        return (True, True, self.version >= (3, 3, 0))

    @property
    def has_ccid(self):
        return MODE.flags_for_mode(self.mode)[1]

    @property
    def serial(self):
        raise NotImplementedError()

    @property
    def version(self):
        raise NotImplementedError()

    def __del__(self):
        if hasattr(self, 'close'):
            self.close()

    def __str__(self):
        return "NEO[mode=%x, serial=%s]" % (self.mode, self.serial)


class ResetStateException(Exception):
    def __init__(self, devs):
        self.devices = devs


def open_all_devices(existing=None):
    devices = []

    # CCID devices
    try:
        from neoman.device_ccid import open_all_devices as open_ccid_all
        for dev in open_ccid_all(existing):
            devices.append(dev)
    except Exception:
        pass

    # OTP devices (only if no CCIDs were found)
    if not devices:
        dev = None
        try:
            from neoman.device_otp import (OTPDevice,
                                           open_first_device as open_otp)
            # Close any existing OTP devices as we are going to reopen them.
            for e_dev in existing:
                if isinstance(e_dev, OTPDevice):
                    e_dev.close()
            dev = open_otp()
            devices.append(dev)
        except Exception:
            pass

        if dev and dev.has_ccid:
            print "OTP device with CCID, sleep..."
            # This key should have been picked up as CCID device,
            # Make sure it gets a change to next time
            raise ResetStateException(devices)

    # U2F devices (No CCIDs nor OTPs)
    if not devices:
        u2f_devs = []
        try:
            from neoman.device_u2f import open_all_devices as open_u2f_all
            u2f_devs = open_u2f_all()
            devices.extend(u2f_devs)
        except Exception:
            pass

        if filter(lambda x: x.has_ccid, u2f_devs):
            print "U2F device with CCID, sleep..."
            # This key should have been picked up as CCID device,
            # Make sure it gets a change to next time
            raise ResetStateException(devices)

    return devices
