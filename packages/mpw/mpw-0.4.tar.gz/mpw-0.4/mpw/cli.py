"""
Master Password command line client.

"""
import functools
import time

import click
import pyperclip

import mpw
import mpw.algorithm
import mpw.commands as commands
import mpw.config


PWD_TYPES = {
    'x': 'max',     'max':   'max',     'maximum': 'max',
    'l': 'long',    'long':  'long',
    'm': 'medium',  'med':   'medium',  'medium':  'medium',
    'b': 'basic',   'basic': 'basic',
    's': 'short',   'short': 'short',
    'p': 'pin',     'pin':   'pin',
}
DEFAULT_USER = mpw.config.load_config()['default']
DEFAULT_USER = ' (default: %s)' % DEFAULT_USER if DEFAULT_USER else ''


#
# Config and validation
#

def with_config(func):
    """A decorator for automatically loading and writing the configuration.

    It loads the config file, passes the config to the decorated function as
    first argument and writes the config back to the config file after the
    call.

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = mpw.config.load_config()
        ret = func(config, *args, **kwargs)
        mpw.config.write_config(config)
        return ret
    return wrapper


def print_version(ctx, param, value):
    """*Click* callback for printing the program version."""
    if not value or ctx.resilient_parsing:
        return  # pragma: no cover
    click.echo('mpw version %s' % mpw.__version__)
    ctx.exit()


def validate_user(ctx, param, user):
    """If no user was specified, try to get the default user.

    Raise :exc:`click.BadParameter` if an invalid user name was passed or if
    no user name was passed and no default user is set.

    """
    config = mpw.config.load_config()
    if user is not None and user not in config['users']:
        raise click.BadParameter('User "%s" does not exist.' % user)

    if user is None:
        user = mpw.config.load_config()['default']
        if user is None:
            raise click.BadParameter('You need to pass a valid user name or '
                                     'set a default user.')

    return user


def validate_pwd_type(ctx, param, value):
    """*Click* callback for validating the ``--pwd-type`` option.

    Either return a valid password type or raise a :exc:`click.BadParameter`.

    """
    try:
        return PWD_TYPES[value]
    except KeyError:
        raise click.BadParameter('Use --help to list valid password types') \
            from None


def validate_counter(ctx, param, value):
    """*Click* callback for validating the ``--counter`` option.

    Either return a valid counter value or raise a :exc:`click.BadParameter`.

    """
    min, max = 1, 0xFFFFFFFF  # min and max for uint32 (4 bytes)
    if not (min <= value <= max):
        raise click.BadParameter('counter not in [%d, %d]' % (min, max))
    return value


def require_password(config, user):
    for i in range(3):
        try:
            # click 4.0 is needed for the "err=True" flag. Work around this
            # password = click.prompt('Enter master password for "%s"' % user,
            #                         hide_input=True, err=True)
            click.echo('Enter master password for "%s": ' % user,
                       nl=False, err=True)
            password = click.prompt('', prompt_suffix='', hide_input=True)
            master_key = commands.check_password(config, user, password)
            break
        except ValueError:
            pass
    else:
        raise click.ClickException('Wrong master password.')

    return master_key


#
# Main command and helpers for options
#

@click.group()
@click.option('--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True,
              help='Show version number and exit.')
def main():
    """The main entry point for mpw; only prints help and version number."""
    pass


def mpw_command(*args):
    """Decorator that combines ``main.command()``, :func:`with_config()` and
    one :func:`click.argument()` call for every entry in *args*.

    So instead of writing::

        @main.command()
        @with_config
        @click.argument('site')
        @click.argument('user')
        def my_command(config, site, user):
            pass

    you just need to write::

        @mpw_command('site', 'user')
        def my_command(config, site, user):
            pass

    """
    def decorator(func):
        for arg in reversed(args):
            func = click.argument(arg)(func)
        return main.command()(with_config(func))
    return decorator


def option_user():
    """Return a decorator that creates the ``--user`` option for a command."""
    return click.option('-u', '--user',
                        callback=validate_user,
                        help='Full name of the user%s' % DEFAULT_USER)


def option_pwd_type():
    """Return a decorator that creates the ``--pwd-type`` option for a
    command."""
    return click.option('-t', '--pwd-type', default='long',
                        callback=validate_pwd_type,
                        help='The password template to use (default: long)')


def option_counter():
    """Return a decorator that creates the ``--counter`` option for a
    command."""
    return click.option('-c', '--counter', default=1,
                        callback=validate_counter,
                        help='The value for the counter (default: 1)')


def option_login():
    """Return a decorator that creates the ``--login`` option for a
    command."""
    return click.option('-a', '--login', default=None,
                        help='Your login name for this site.')


def option_update_version():
    """Return a decorator that creates the ``--update-version`` opion for a
    command."""
    return click.option('-U', '--update-version', is_flag=True, default=False,
                        help='Update the algorithm version')


def option_echo():
    """Return a decorator taht creates the ``-e`` option for a command."""
    return click.option('-e', '--echo', is_flag=True, default=False,
                        help='Echo password to stdout instead of copying it.')


#
# Sub-commands
#

@mpw_command('site')
@option_user()
@option_echo()
def get(config, site, user, echo):
    """Get a site password.

    Generate a password for SITE and the provided user (or the default user)
    based on your master password.

    """
    master_key = require_password(config, user)
    try:
        pwd = commands.get_site_pwd(config, user, master_key, site)
    except ValueError:
        raise click.UsageError('The site "%s" does not exist. Please create '
                               'it via "mpw addsite".' % site)

    if echo:
        click.echo(pwd)
    else:
        pyperclip.copy(pwd)
        click.echo('Password for "%s" for user "%s" was copied to the '
                   'clipboard.' % (site, user))


@mpw_command('name')
def adduser(config, name):
    """Add a user."""
    while True:
        password = click.prompt('Enter master password', hide_input=True)
        confirm_pw = click.prompt('Confirm master password', hide_input=True)
        if password == confirm_pw:
            break
        else:
            click.echo('Passwords do not match.', err=True)
    try:
        master_key = mpw.algorithm.get_master_key(password, name)
        commands.add_user(config, name, master_key)
        click.echo('Added user "%s".' % name)
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command('name')
def setuser(config, name):
    """Set a user as default."""
    try:
        commands.set_default_user(config, name)
        click.echo('Set "%s" as default user.' % name)
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command('name')
def deluser(config, name):
    """Delete a user."""
    try:
        commands.delete_user(config, name)
        click.echo('User "%s" deleted.' % name)
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command()
def users(config):
    """List all users."""
    users = commands.list_users(config)
    for user, is_default in users:
        click.echo('%s%s' % ('*' if is_default else ' ', user))


@mpw_command()
@option_user()
def changepw(config, user):
    """Change a user's password."""
    click.echo('WARNING! Changing your master password results in different '
               'different passwords for all your sites. Press *Ctrl+C* to '
               'abort.', err=True)

    old_key = require_password(config, user)
    while True:
        new_pw = click.prompt('Enter new password', hide_input=True)
        new_pw2 = click.prompt('Confirm password', hide_input=True)
        if new_pw == new_pw2:
            break
        else:
            click.echo('Passwords do not match.', err=True)

    new_key = mpw.algorithm.get_master_key(new_pw, user)
    commands.change_password(config, user, old_key, new_key)
    click.echo('Password for user "%s" changed.' % user)


@mpw_command('site')
@option_user()
@option_pwd_type()
@option_counter()
@option_login()
def addsite(config, site, user, pwd_type, counter, login):
    """Add a site for a user.

    Master password supports the following password types:

    \b
      x, max, maximum  20 characters, contains symbols
      l, long          14 characters, contains symbols
      m, med, medium    8 characters, contains symbols
      b, basic          8 characters, no symbols
      s, short          4 characters, no symbols
      p, pin            4 numbers

    The counter value can be any positive number.

    """
    master_key = require_password(config, user)
    try:
        commands.add_site(config, user, master_key, site, pwd_type, counter,
                          login)
        click.echo('Added site "%s" for user "%s".' % (site, user))
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command('site')
@option_user()
def getsite(config, site, user):
    """Print site config."""
    master_key = require_password(config, user)
    try:
        siteconf = commands.get_site(config, user, master_key, site)
        strtime = time.strftime('%Y-%m-%d %H:%M:%S',
                                time.localtime(siteconf['access_time']))
        if siteconf['version'] == mpw.algorithm.CURRENT:
            version = siteconf['version']
        else:
            version = '%s (current: %s)' % (siteconf['version'],
                                            mpw.algorithm.CURRENT)
        click.echo('Password type: %s' % siteconf['pwd_type'])
        click.echo('Counter value: %d' % siteconf['counter'])
        click.echo('login name:    %s' % siteconf['login'])
        click.echo('Algorithm:     %s' % version)
        click.echo('Last access:   %s' % strtime)
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command('site')
@option_user()
@option_pwd_type()
@option_counter()
@option_login()
@option_update_version()
def updatesite(config, site, user, update_version, pwd_type, counter, login):
    """Update the settings for a site.

    Master password supports the following password types:

    \b
      x, max, maximum  20 characters, contains symbols
      l, long          14 characters, contains symbols
      m, med, medium    8 characters, contains symbols
      b, basic          8 characters, no symbols
      s, short          4 characters, no symbols
      p, pin            4 numbers

    The counter value can be any positive number.

    """
    master_key = require_password(config, user)
    try:
        commands.update_site(config, user, master_key, site,
                             update_version=update_version,
                             pwd_type=pwd_type, counter=counter,
                             login=login)
        click.echo('Updated site "%s" for user "%s".' % (site, user))
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command('site')
@option_user()
def delsite(config, site, user):
    """Delete a site."""
    master_key = require_password(config, user)
    try:
        commands.delete_site(config, user, master_key, site)
        click.echo('Deleted site "%s" for user "%s".' % (site, user))
    except ValueError as e:
        raise click.ClickException(e)


@mpw_command()
@option_user()
def sites(config, user):
    """List all sites for a user."""
    master_key = require_password(config, user)
    sites = commands.list_sites(config, user, master_key)
    for site in sites:
        click.echo(site)
