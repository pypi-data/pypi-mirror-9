"""
Implementation of the Master Password algorithm. See
http://masterpasswordapp.com/algorithm.html for details.

"""
import hashlib
import hmac

import scrypt


ENCODING = 'utf-8'
BYTE_ORDER = 'big'
INT_BYTES = 4  # 4 bytes for an 32 bit integer


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


def get_master_key(mpw, name, N=32768, r=8, p=2, dk_len=64):
    """Calculate and return the master key from the master password *mpw*
    and your *name*."""
    mpw = mpw.encode(ENCODING)
    salt = b'com.lyndir.masterpassword'
    salt += len(name).to_bytes(INT_BYTES, BYTE_ORDER)
    salt += name.encode(ENCODING)

    key = scrypt.hash(mpw, salt, N, r, p, dk_len)
    return key


def get_template_seed(key, site_name, counter):
    """Compute and return the template seed for the Master Password *key*, a
    given *site_name* and *counter* value."""
    msg = b'com.lyndir.masterpassword'
    msg += len(site_name).to_bytes(INT_BYTES, BYTE_ORDER)
    msg += site_name.encode(ENCODING)
    msg += counter.to_bytes(INT_BYTES, BYTE_ORDER)

    seed = hmac.new(key, msg, hashlib.sha256)
    return seed.digest()


def get_site_pwd(seed, template_type):
    """Return the actual password based on the *seed* for a certain
    *template_type."""
    template_list = TEMPLATES[template_type]
    idx = seed[0]
    template = template_list[idx % len(template_list)]
    pwd = []
    for i, group in enumerate(template):
        chars = GROUPS[group]
        idx = seed[i + 1]
        pwd.append(chars[idx % len(chars)])

    return ''.join(pwd)


def get_password(mpw, name, site_name, counter, pwd_type):
    """Get a unique password for a given site."""
    key = get_master_key(mpw, name)
    seed = get_template_seed(key, site_name, counter)
    pwd = get_site_pwd(seed, pwd_type)
    return pwd
