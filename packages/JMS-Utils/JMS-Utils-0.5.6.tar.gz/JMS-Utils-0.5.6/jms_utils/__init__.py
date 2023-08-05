import sys

VERSION = (0, 5, 6)

FROZEN = getattr(sys, u'frozen', False)


def get_version():
    version = '{}.{}'.format(VERSION[0], VERSION[1])
    if VERSION[2]:
        version = '{}.{}'.format(version, VERSION[2])
    return version
