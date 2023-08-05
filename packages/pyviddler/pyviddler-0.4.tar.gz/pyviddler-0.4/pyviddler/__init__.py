# -*- coding: utf-8 -*-
"""
This provides a Python wrapper around Viddler's v2 API.
"""
__version_info__ = {
    'major': 0,
    'minor': 4,
    'micro': 0,
    'releaselevel': 'final',
    'serial': 1
}


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i" % __version_info__, ]
    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i' % (
            __version_info__['releaselevel'][0], __version_info__['serial']))
    return ''.join(vers)

__version__ = get_version()

from .viddler import ViddlerAPI

__all__ = (ViddlerAPI, get_version, __version_info__, __version__)
