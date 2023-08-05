import base64
import contextlib
import json
import time

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDFExpand
from cryptography.hazmat.backends import default_backend

import mpw.algorithm


def add_user(config, user, master_key):
    """Add *user* name with *master_key* to *config* and set it as default user.

    Raise a :exc:`ValueError` if *user* already exists.

    """
    if user in config['users']:
        raise ValueError('User "%s" already exists.' % user)

    keyhash = mpw.algorithm.get_keyhash(master_key, user)

    config['users'][user] = {
        'keyhash': keyhash,
        'keyhash_version': mpw.algorithm.CURRENT,
        'sites': {},
    }

    set_default_user(config, user)


def delete_user(config, user):
    """Delete user *name* from *config*.

    Raise a :exc:`ValueError` if *user* does not exist.

    """
    _check_user(config, user)

    del config['users'][user]
    if config['default'] == user:
        config['default'] = None


def set_default_user(config, user):
    """Set *user* as default user in *config*.

    Raise a :exc:`ValueError` if *user* does not exist.

    """
    _check_user(config, user)
    config['default'] = user


def list_users(config):
    """Return a sorted list of tuples ``(user_name, is_default)`` from the
    *config*."""
    return [(user, user == config['default'])
            for user in sorted(config['users'])]


def add_site(config, user, master_key, site, pwd_type, counter, login=None):
    """Add *site* for *user* with *master_key* to its *config* and set the
    *pwd_type*, *counter* value and, optionally, the *login* name.

    Raise a :exc:`ValueError` if *user* does not exist or if *site* does exist.

    """
    _check_user(config, user)

    with decrypted_sites(config, user, master_key) as sites:
        if site in sites:
            raise ValueError('Site "%s" for user "%s" already exists.' %
                             (site, user))
        sites.update({site: {
            'pwd_type': pwd_type,
            'counter': counter,
            'login': login,
            'version': mpw.algorithm.CURRENT,
            'access_time': time.time(),
        }})


def get_site(config, user, master_key, site):
    """Get the site config for *site* for *user* with *master_key* from *config*.

    Raise a :exc:`ValueError` if *user* or *site* do not exist.

    """
    _check_user(config, user)

    with decrypted_sites(config, user, master_key) as sites:
        _check_site(user, site, sites)
        return sites[site]


def delete_site(config, user, master_key, site):
    """Delete the site *site* for *user* with *master_key* from *config*.

    Raise a :exc:`ValueError` if *user* or *site* do not exist.

    """
    _check_user(config, user)

    with decrypted_sites(config, user, master_key) as sites:
        _check_site(user, site, sites)
        del sites[site]


def update_site(config, user, master_key, site, update_version=False,
                **kwargs):
    """Update the access time for the *site* for *user* with *master_key* in
    *config*.

    Also update all entries in the site conf for which an entry in *kwargs*
    exists.

    Raise a :exc:`ValueError` if *user* or *site* do not exist.

    """
    _check_user(config, user)

    with decrypted_sites(config, user, master_key) as sites:
        _check_site(user, site, sites)
        siteconf = sites[site]

        if update_version:
            siteconf['version'] = mpw.algorithm.CURRENT

        for key, val in siteconf.items():
            if key in kwargs:
                siteconf[key] = kwargs[key]
        siteconf['access_time'] = time.time()


def get_site_pwd(config, user, master_key, site):
    """Return a *site* specific master_key for the given *user* and *master_key*.

    Raise a :exc:`ValueError` if *user* or *site* do not exist.

    """
    _check_user(config, user)

    with decrypted_sites(config, user, master_key) as sites:
        _check_site(user, site, sites)
        pwd_type = sites[site]['pwd_type']
        counter = sites[site]['counter']
        version = sites[site]['version']

    pwd = mpw.algorithm.get_password(master_key, site,
                                     counter=counter,
                                     pwd_type=mpw.algorithm.PwdType(pwd_type),
                                     variant=mpw.algorithm.Scope.password,
                                     context='',
                                     version=version)

    return pwd


def change_password(config, user, old_key, new_key):
    """Change the master_key for *user* from *old_key* to *new_key*.

    Update the user's keyhash and re-encode their sites with the new password.

    """
    _check_user(config, user)

    new_keyhash = mpw.algorithm.get_keyhash(new_key, user)
    config['users'][user]['keyhash'] = new_keyhash

    old_fernet = _make_fernet(user, old_key)
    sites = _decrypt_sites(config, user, old_fernet)

    new_fernet = _make_fernet(user, new_key)
    _encrypt_sites(config, user, sites, new_fernet)


def list_sites(config, user, master_key):
    """Get the sites for *user* with *master_key* from *config* sorted by access
    time in descending order.

    Raise a :exc:`ValueError` if *user* does not exist.

    """
    _check_user(config, user)
    with decrypted_sites(config, user, master_key) as sites:
        return [name for name, data in sorted(
            sites.items(), key=lambda s: s[1]['access_time'], reverse=True)]


def check_password(config, user, password):
    version = config['users'][user]['keyhash_version']
    master_key = mpw.algorithm.get_master_key(password, user, version)
    keyhash = mpw.algorithm.get_keyhash(master_key, user, version)
    if keyhash != config['users'][user]['keyhash']:
        raise ValueError('Wrong master password.')

    if version != mpw.algorithm.CURRENT:
        new_key = mpw.algorithm.get_master_key(password, user)
        new_keyhash = mpw.algorithm.get_keyhash(new_key, user)
        config['users'][user]['keyhash'] = new_keyhash
        config['users'][user]['keyhash_version'] = mpw.algorithm.CURRENT
        change_password(config, user, master_key, new_key)
        master_key = new_key

    return master_key


@contextlib.contextmanager
def decrypted_sites(config, user, master_key):
    """Context manager that decrypts the sites of *user* in *config* with the
    given *master_key* and encryptes it again afterwards.

    """
    fernet = _make_fernet(user, master_key)
    sites = _decrypt_sites(config, user, fernet)

    yield sites

    _encrypt_sites(config, user, sites, fernet)


def _make_fernet(user, master_key):
    backend = default_backend()
    info = b'masterpassword.userdata.' + user.encode()
    hkdf = HKDFExpand(algorithm=hashes.SHA256(), length=32, info=info,
                      backend=backend)
    key = base64.urlsafe_b64encode(hkdf.derive(master_key))
    return Fernet(key)


def _decrypt_sites(config, user, fernet):
    sites = config['users'][user]['sites']
    if sites != {}:
        sites = fernet.decrypt(sites.encode())  # decrypt() needs bytes
        sites = json.loads(sites.decode())  # loads() needs str

    return sites


def _encrypt_sites(config, user, sites, fernet):
    # encrypt() needs and gives us bytes. In the end, we need str
    data = json.dumps(sites).encode()
    config['users'][user]['sites'] = fernet.encrypt(data).decode()


def _check_user(config, user):
    """Check if *user* is in *config*.  Raise a :exc:`ValueError` if not."""
    if user not in config['users']:
        raise ValueError('User "%s" does not exist.' % user)


def _check_site(user, site, sites):
    """Check if *site* for *user* is in *sites*.  Raise a :exc:`ValueError`
    if not."""
    if site not in sites:
        raise ValueError('Site "%s" for user "%s" does not exist.' %
                         (site, user))
