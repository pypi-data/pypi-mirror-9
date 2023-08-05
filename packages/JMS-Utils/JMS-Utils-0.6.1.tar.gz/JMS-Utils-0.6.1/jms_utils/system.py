import platform
import sys


PLATFORM = None
MACHINE = None


def get_system():
    global PLATFORM
    if PLATFORM is not None:
        return PLATFORM
    if sys.platform == u'win32':
        PLATFORM = u'win'
    elif sys.platform == u'darwin':
        PLATFORM = u'mac'
    else:
        if u'x86_64' in platform.uname():
            PLATFORM = 'nix64'
        elif u'arm' in platform.uname():
            PLATFORM = u'arm'
        else:
            PLATFORM = u'nix'
    return PLATFORM


def get_architecure():
    global MACHINE
    if MACHINE is not None:
        return MACHINE
    machine = platform.machine()
    if u'64' in machine:
        MACHINE = '64'
    else:
        MACHINE = '32'
    return MACHINE
