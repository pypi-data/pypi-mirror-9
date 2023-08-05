"""
Provides acces to the different versions of the algorithm.

"""
__all__ = [
    'PwdType', 'Scope',
    'get_password', 'get_master_key', 'get_keyhash',
]

import importlib

from .v2 import PwdType, Scope


VERSIONS = ['v1', 'v2', 'v3']
CURRENT = VERSIONS[-1]


def get_password(master_key, site, counter, pwd_type, variant, context,
                 version=CURRENT):
    """Get a unique password for a given site.

    Depending on *version* an alias for

    - :func:`mpw.algorithm.v1.get_password()
    - :func:`mpw.algorithm.v2.get_password()

    """
    algorithm = _get_algorithm(version)
    return algorithm.get_password(master_key, site, counter, pwd_type,
                                  variant, context)


def get_master_key(password, user, version=CURRENT):
    """Calculate and return the master key from the master password *mpw*
    and *user* name.

    Depending on *version* an alias for

    - :func:`mpw.algorithm.v1.get_master_key()
    - :func:`mpw.algorithm.v2.get_master_key()

    """
    algorithm = _get_algorithm(version)
    return algorithm.get_master_key(password, user)


def get_keyhash(master_key, user, version=CURRENT):
    """Return a hashed version (as urlsafe base64 encoded unicode string) of
    the *master_key* and *user* which can be stored on disk.

    Depending on *version* an alias for

    - :func:`mpw.algorithm.v1.get_keyhash()
    - :func:`mpw.algorithm.v2.get_keyhash()

    """
    algorithm = _get_algorithm(version)
    return algorithm.get_keyhash(master_key, user)


def _get_algorithm(version):
    if version not in VERSIONS:
        raise ValueError('Unknown algorithm version: %s' % version)
    algorithm = importlib.import_module('mpw.algorithm.%s' % version)
    return algorithm
