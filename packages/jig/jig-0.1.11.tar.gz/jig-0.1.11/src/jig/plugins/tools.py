import codecs
from os import mkdir, stat, chmod, listdir
from os.path import join, isdir
from stat import S_IXUSR, S_IXGRP, S_IXOTH
from functools import wraps
from datetime import datetime
from calendar import timegm
from ConfigParser import SafeConfigParser, NoSectionError, NoOptionError

import git

from jig.exc import (
    NotGitRepo, AlreadyInitialized,
    GitRepoNotInitialized)
from jig.conf import (
    JIG_DIR_NAME, JIG_PLUGIN_CONFIG_FILENAME,
    JIG_PLUGIN_DIR, PLUGIN_CONFIG_FILENAME, PLUGIN_PRE_COMMIT_SCRIPT,
    PLUGIN_PRE_COMMIT_TEMPLATE_DIR, CODEC)
from jig.gitutils.checks import is_git_repo, repo_jiginitialized
from jig.gitutils.remote import remote_has_updates
from jig.tools import slugify
from jig.plugins.manager import PluginManager


def _git_check(func):
    """
    Checks to see if the directory is a Git repo.

    Raises :py:exc:`NotGitRepo` if it's not.

    You can only use this decorator on a function where the first argument is
    the path to the Git repository.
    """
    @wraps(func)
    def wrapper(gitrepo, *args, **kwargs):
        # Is it a Git repo?
        if not is_git_repo(gitrepo):
            raise NotGitRepo(
                'Trying to initialize a directory that is '
                'not a Git repository.')

        return func(gitrepo, *args, **kwargs)
    return wrapper


@_git_check
def initializer(gitrepo):
    """
    Initializes a Git repo for use with jig.

    This will create a directory in the root of the Git repo that will contain
    files (plugins) and configuration.
    """
    # If it's already initialized, refuse to run
    if repo_jiginitialized(gitrepo):
        raise AlreadyInitialized('The repository is already initialized.')

    # Create the container for all things jig
    jig_dir = join(gitrepo, JIG_DIR_NAME)

    mkdir(jig_dir)
    mkdir(join(jig_dir, JIG_PLUGIN_DIR))

    set_jigconfig(gitrepo)

    # Initialize the date plugins were last checked to right now
    config = set_jigconfig(
        gitrepo,
        set_checked_for_updates(gitrepo))

    return config


@_git_check
def set_jigconfig(gitrepo, config=None):
    """
    Saves the config for jig in the Git repo.

    The ``config`` argument must be an instance of :py:class:`ConfigParser`.
    """
    # If it's already initialized, refuse to run
    if not repo_jiginitialized(gitrepo):
        raise GitRepoNotInitialized('The repository has not been initialized.')

    # Create the container for all things jig
    jig_dir = join(gitrepo, JIG_DIR_NAME)

    # Create an empty config parser if we were not passed one
    plugins = config if config else SafeConfigParser()

    # Create a plugin list file
    with open(join(jig_dir, JIG_PLUGIN_CONFIG_FILENAME), 'w') as fh:
        plugins.write(fh)

        return plugins


@_git_check
def get_jigconfig(gitrepo):
    """
    Gets the config for a jig initialized Git repo.
    """
    jig_dir = join(gitrepo, JIG_DIR_NAME)

    if not repo_jiginitialized(gitrepo):
        raise GitRepoNotInitialized(
            'This repository has not been initialized.')

    with open(join(jig_dir, JIG_PLUGIN_CONFIG_FILENAME), 'r') as fh:
        plugins = SafeConfigParser()
        plugins.readfp(fh)

        return plugins


@_git_check
def update_plugins(gitrepo):
    """
    For any installed plugins in :file:`.jig/plugins`, update by git pull.

    Will iterate through all cloned repositories and perform a ``git pull``
    command. This upgrades the plugins.

    Returns an dict of results from running the command. The key is an
    instance of :py:class:`jig.plugin.manager.PluginManager` corresponding to
    the plugins that were updated in each director. The value is the output
    from running the ``git pull`` command inside that directory.
    """
    jig_plugin_dir = join(gitrepo, JIG_DIR_NAME, JIG_PLUGIN_DIR)

    results = {}
    for directory in listdir(jig_plugin_dir):
        plugin_dir = join(jig_plugin_dir, directory)
        pm = PluginManager()
        pm.add(plugin_dir)

        gitobj = git.Git(plugin_dir)

        retcode, stdout, stderr = gitobj.execute(
            ['git', 'pull'], with_extended_output=True)

        results[pm] = stdout or stderr

    return results


@_git_check
def plugins_have_updates(gitrepo):
    """
    Return True if any installed plugins have updates.

    :param string gitrepo: path to the Git repository
    """
    jig_plugin_dir = join(gitrepo, JIG_DIR_NAME, JIG_PLUGIN_DIR)

    for directory in listdir(jig_plugin_dir):
        if remote_has_updates(join(jig_plugin_dir, directory)):
            return True

    return False


@_git_check
def last_checked_for_updates(gitrepo):
    """
    Find out the last time plugins were checked for updates.

    :param string gitrepo: path to the initialized Git repository
    :returns: Unix timestamp the last time it was checked, ``0`` if this is
        the first time.
    """
    retval = 0

    config = get_jigconfig(gitrepo)

    try:
        timestamp = int(config.get('jig', 'last_checked_for_updates'))
        retval = datetime.utcfromtimestamp(timestamp)
    except (NoSectionError, NoOptionError, ValueError):
        pass

    return retval


@_git_check
def set_checked_for_updates(gitrepo, date=None):
    """
    Set the date checked for updated plugins.

    By default, unless otherwise specified, it uses ``datetime.utcnow()`` as
    the date object.

    :param string gitrepo: path to the initialized Git repository
    """
    if not date:
        date = datetime.utcnow()

    date = timegm(date.replace(microsecond=0).timetuple())

    config = get_jigconfig(gitrepo)

    if not config.has_section('jig'):
        config.add_section('jig')

    config.set('jig', 'last_checked_for_updates', unicode(date))

    return config


def create_plugin(in_dir, bundle, name, template='python', settings={}):
    """
    Creates a plugin in the given directory.

    The directory ``in_dir`` must already exist.

    The plugin will be created with the given ``bundle`` and ``name``. These
    will be used in the plugin configuration file.

    The ``template`` specifies what scripting language will be used for the
    pre-commit executable. Existing templates can be found in the
    :file:`data/pre-commits` directory.
    """
    if not isdir(in_dir):
        raise ValueError('{} must be a directory.'.format(in_dir))

    # Create our plugin configuration
    config = SafeConfigParser()
    config.add_section('plugin')
    config.add_section('settings')
    config.add_section('help')
    config.set('plugin', 'bundle', bundle)
    config.set('plugin', 'name', name)

    # Add settings if applicable
    if settings:
        for key, val in settings.items():
            config.set('settings', key, str(val))

    # Create a safe directory name from the plugin name
    plugin_dir = join(in_dir, slugify(name))
    config_filename = join(plugin_dir, PLUGIN_CONFIG_FILENAME)
    pre_commit_filename = join(plugin_dir, PLUGIN_PRE_COMMIT_SCRIPT)

    # Create the directory and files
    mkdir(plugin_dir)

    with open(config_filename, 'w') as fh:
        config.write(fh)

    with open(pre_commit_filename, 'w') as fh:
        fh.write(open(join(PLUGIN_PRE_COMMIT_TEMPLATE_DIR, template)).read())

    # And make it executable
    sinfo = stat(pre_commit_filename)
    mode = sinfo.st_mode | S_IXUSR | S_IXGRP | S_IXOTH
    chmod(pre_commit_filename, mode)

    return plugin_dir


def available_templates():
    """
    Provide a list of available pre-commit templates for plugin creation.

    Templates are in :file:`jig/data`.

    This can be provided to :py:function:`create_plugin` as the
    :py:arg:`template` argument.
    """
    return listdir(PLUGIN_PRE_COMMIT_TEMPLATE_DIR)


def read_plugin_list(filename):
    """
    Reads a plugin list file and returns its contents.

    :param string filename: path to the filename
    :rtype list:
    """
    with codecs.open(filename, 'r', CODEC) as fh:
        plugin_list = fh.read()

    return plugin_list.splitlines()
