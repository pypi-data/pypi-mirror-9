"""
Implementation of the Master Password algorithm v1.
See http://masterpasswordapp.com/algorithm.html for details.

"""
__all__ = [
    # Constants
    'ENCODING', 'BYTE_ORDER', 'INT_BYTES',
    'SCRYPT_N', 'SCRYPT_r', 'SCRYPT_p', 'SCRYPT_dk_len',
    'TEMPLATES', 'GROUPS',
    # Classes
    'PwdType',
    # Functions
    'get_password', 'get_keyhash', 'get_master_key', 'get_template_seed',
    'get_site_pwd',
]

import base64
import enum
import hashlib
import hmac

import scrypt


ENCODING = 'utf-8'
BYTE_ORDER = 'big'
INT_BYTES = 4  # 4 bytes for an 32 bit integer

SCRYPT_N = 32768
SCRYPT_r = 8
SCRYPT_p = 2
SCRYPT_dk_len = 64


TEMPLATES = {
    'max': [
        'anoxxxxxxxxxxxxxxxxx',
        'axxxxxxxxxxxxxxxxxno',
    ],
    'long': [
        'CvcvnoCvcvCvcv',
        'CvcvCvcvnoCvcv',
        'CvcvCvcvCvcvno',
        'CvccnoCvcvCvcv',
        'CvccCvcvnoCvcv',
        'CvccCvcvCvcvno',
        'CvcvnoCvccCvcv',
        'CvcvCvccnoCvcv',
        'CvcvCvccCvcvno',
        'CvcvnoCvcvCvcc',
        'CvcvCvcvnoCvcc',
        'CvcvCvcvCvccno',
        'CvccnoCvccCvcv',
        'CvccCvccnoCvcv',
        'CvccCvccCvcvno',
        'CvcvnoCvccCvcc',
        'CvcvCvccnoCvcc',
        'CvcvCvccCvccno',
        'CvccnoCvcvCvcc',
        'CvccCvcvnoCvcc',
        'CvccCvcvCvccno',
    ],
    'medium': [
        'CvcnoCvc',
        'CvcCvcno',
    ],
    'basic': [
        'aaanaaan',
        'aannaaan',
        'aaannaaa',
    ],
    'short': [
        'Cvcn',
    ],
    'pin': [
        'nnnn',
    ],
}
GROUPS = {
    'V': 'AEIOU',
    'C': 'BCDFGHJKLMNPQRSTVWXYZ',
    'v': 'aeiou',
    'c': 'bcdfghjklmnpqrstvwxyz',
    'n': '0123456789',
    'o': "@&%?,=[]_:-+*$#!'^~;()/.",
}
GROUPS['A'] = GROUPS['V'] + GROUPS['C']
GROUPS['a'] = GROUPS['V'] + GROUPS['v'] + GROUPS['C'] + GROUPS['c']
# Due to an error(?), "x" actually does not contain the "'" sign in the
# official implementation.
# GROUPS['x'] = GROUPS['a'] + GROUPS['n'] + GROUPS['o']
GROUPS['x'] = 'AEIOUaeiouBCDFGHJKLMNPQRSTVWXYZbcdfghjklmnpqrstvwxyz' \
              '0123456789!@#$%^&*()'


class PwdType(enum.Enum):
    max = 'max'
    long = 'long'
    medium = 'medium'
    basic = 'basic'
    short = 'short'
    pin = 'pin'


def get_password(master_key, site, counter, pwd_type,
                 variant=None, context=None):
    """Get a unique password for a given site.

    :param bytes master_key:  The master key derived from the master password
    :param str site:          Name of the site for which to generate a password
    :param int counter:       Password counter for *site* (to generate
                              new/multiple passwords for the same site)
    :param PwdType pwd_type:  Password type / length: "max", "lon", "medium",
                              "basic", "short" or "pin"
    :param Scope variant:     Ignored in this version of the algorithm
    :param str context:       Ignored in this version of the algorithm

    """
    seed = get_template_seed(master_key, site, counter)
    pwd = get_site_pwd(seed, pwd_type)
    return pwd


def get_keyhash(master_key, user):
    """Return a hashed version (as urlsafe base64 encoded unicode string) of
    the *master_key* and *user* which can be stored on disk.
    """
    salt = b'com.lyndir.masterpassword.keyhash'
    salt += len(user).to_bytes(INT_BYTES, BYTE_ORDER)
    salt += user.encode(ENCODING)
    keyhash = scrypt.hash(master_key, salt,
                          SCRYPT_N, SCRYPT_r, SCRYPT_p, SCRYPT_dk_len)
    # Encode to urlsafe base64 and decode the result to a string
    keyhash = base64.urlsafe_b64encode(keyhash).decode()
    return keyhash


def get_master_key(password, user):
    """Calculate and return the master key from the master password *mpw*
    and *user* name.
    """
    password = password.encode(ENCODING)
    salt = b'com.lyndir.masterpassword'
    salt += len(user).to_bytes(INT_BYTES, BYTE_ORDER)
    salt += user.encode(ENCODING)

    key = scrypt.hash(password, salt,
                      SCRYPT_N, SCRYPT_r, SCRYPT_p, SCRYPT_dk_len)
    return key


def get_template_seed(key, site, counter):
    """Compute and return the template seed for the Master Password *key*, a
    given *site* and *counter* value.
    """
    msg = b'com.lyndir.masterpassword'
    msg += len(site).to_bytes(INT_BYTES, BYTE_ORDER)
    msg += site.encode(ENCODING)
    msg += counter.to_bytes(INT_BYTES, BYTE_ORDER)

    seed = hmac.new(key, msg, hashlib.sha256)
    return seed.digest()


def get_site_pwd(seed, template_type):
    """Return the actual password based on the *seed* for a certain
    *template_type*.
    """
    template_list = TEMPLATES[template_type.value]
    idx = seed[0]
    template = template_list[idx % len(template_list)]
    pwd = []
    for i, group in enumerate(template):
        chars = GROUPS[group]
        idx = seed[i + 1]
        pwd.append(chars[idx % len(chars)])

    return ''.join(pwd)
