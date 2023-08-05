"""
Implementation of the Master Password algorithm v2.
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
import enum
import hashlib
import hmac

import scrypt

from .v1 import (
    # Constants
    ENCODING, BYTE_ORDER, INT_BYTES,
    SCRYPT_N, SCRYPT_r, SCRYPT_p, SCRYPT_dk_len,
    TEMPLATES, GROUPS,
    # Functions
    get_keyhash, get_site_pwd,
    # Classes
    PwdType,
)


class Scope(enum.Enum):
    password = b'com.lyndir.masterpassword'
    login = b'com.lyndir.masterpassword.login'
    answer = b'com.lyndir.masterpassword.answer'


def get_password(master_key, site, counter, pwd_type, variant, context):
    """Get a unique password for a given site.

    :param bytes master_key:  The master key derived from the master password
    :param str site:          Name of the site for which to generate a password
    :param int counter:       Password counter for *site* (to generate
                              new/multiple passwords for the same site)
    :param PwdType pwd_type:  Password type / length: "max", "lon", "medium",
                              "basic", "short" or "pin"
    :param Scope variant:     Whether to generate a password, a random login
                              name or a random answer to a security question.
    :param str context:       Additional argument to *variant* (e.g., for
                              different security questions).

    """
    seed = get_template_seed(master_key, site, counter, variant, context)
    pwd = get_site_pwd(seed, pwd_type)
    return pwd


def get_master_key(password, user):
    """Calculate and return the master key from the master password *mpw*
    and your *name*.
    """
    password = password.encode(ENCODING)
    user = user.encode(ENCODING)
    salt = b'com.lyndir.masterpassword'
    salt += len(user).to_bytes(INT_BYTES, BYTE_ORDER)
    salt += user

    key = scrypt.hash(password, salt,
                      SCRYPT_N, SCRYPT_r, SCRYPT_p, SCRYPT_dk_len)
    return key


def get_template_seed(key, site, counter, variant, context):
    """Compute and return the template seed for the Master Password *key*, a
    given *site* and *counter* value.
    """
    site = site.encode(ENCODING)
    context = context.encode(ENCODING)

    msg = variant.value
    msg += len(site).to_bytes(INT_BYTES, BYTE_ORDER)
    msg += site
    msg += counter.to_bytes(INT_BYTES, BYTE_ORDER)
    if context:
        msg += len(context).to_bytes(INT_BYTES, BYTE_ORDER)
        msg += context

    seed = hmac.new(key, msg, hashlib.sha256)
    return seed.digest()
