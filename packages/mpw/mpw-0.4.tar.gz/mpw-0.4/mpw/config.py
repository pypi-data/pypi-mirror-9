"""
This module implements config file handling

"""
import json
import os

import click


APP_NAME = 'Master Password'
CFG_FILE = 'config.json'


def load_config():
    """Return the configuration from the config file.

    If the config file does not exist, create it and populate it with default
    values.

    The return value is a dictionary with the following keys:

    - *default* contains the default user name or ``None``
    - *users* is a dictionary mapping user names to their list of configured
      sites.

    """
    try:
        cfg_file = _get_config_filename()
        config = json.load(open(cfg_file, 'r'))
    except FileNotFoundError:
        config = {
            'default': None,
            'users': {},
        }
    return config


def write_config(config):
    """Write the *config* to the config file."""
    cfg_file = _get_config_filename()
    with open(cfg_file, 'w') as fp:
        json.dump(config, fp, indent=4)


def _get_config_filename():
    """Return the config file name and ensure its parent directory exists."""
    app_dir = click.get_app_dir(APP_NAME)
    if not os.path.isdir(app_dir):
        os.mkdir(app_dir, mode=0o755)
    return os.path.join(app_dir, CFG_FILE)
