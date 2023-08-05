"""
Implementation of the Master Password algorithm v3.
See http://masterpasswordapp.com/algorithm.html for details.

"""
__all__ = [
    # Constants
    'ENCODING', 'BYTE_ORDER', 'INT_BYTES',
    'SCRYPT_N', 'SCRYPT_r', 'SCRYPT_p', 'SCRYPT_dk_len',
    'TEMPLATES', 'GROUPS',
    # Classes
    'PwdType', 'Scope',
    # Functions
    'get_password', 'get_keyhash', 'get_master_key', 'get_template_seed',
    'get_site_pwd',
]

# I "wrongly" implemented v2 and already calculated the correct lengh of the
# user name, so v3 is the same as v2 for us. :-)
from .v2 import (
    # Constants
    ENCODING, BYTE_ORDER, INT_BYTES,
    SCRYPT_N, SCRYPT_r, SCRYPT_p, SCRYPT_dk_len,
    TEMPLATES, GROUPS,
    # Functions
    get_password, get_keyhash, get_master_key, get_template_seed, get_site_pwd,
    # Classes
    PwdType, Scope
)
