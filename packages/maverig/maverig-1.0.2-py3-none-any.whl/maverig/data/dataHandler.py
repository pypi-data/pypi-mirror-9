import sys
import os
import re
import time

"""
This module is used for handling the paths to static files like icons or locales so that files can be found before and
after freezing the application. Freezing is done with
`cx_Freeze <http://cx-freeze.readthedocs.org/en/latest/overview.html>`_.
"""

maverig_dir = None


def ensure_dir(path):
    """Create directories contained in path if they don't exist."""
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)


def find_dir(dir_name, timeout=3):
    """Searches recursively for *dir_name* in current directory within *timeout* seconds.
    Return found directory or ``False`` if not found."""
    timout_time = time.time() + timeout
    for root, dirs, files in os.walk(os.path.curdir):
        if dir_name in dirs:
            return os.path.join(root, dir_name)
        if time.time() > timout_time:
            return False
    return False


def get_maverig_dir():
    """Return the parent maverig directory, e.g. ``'C:\Programs\maverig'``."""
    global maverig_dir

    if not maverig_dir:
        real_path = os.path.realpath(os.path.curdir)
        if not 'maverig' in real_path:
            found_dir = find_dir('maverig')
            if not found_dir:
                raise os.error('Maverig working directory not found in "%s".' % real_path)
            real_path = found_dir

        raw_sep = os.sep.replace("\\", "\\\\")
        maverig_dir = re.sub('maverig' + raw_sep + 'maverig.*', 'maverig', real_path)
    return maverig_dir


def get_relpath(path):
    """Return the path relative to maverig directory.

    For example ``get_relpath('C:\Programs\maverig\maverig\data')`` will return ``'maverig\data'``."""
    return path.replace(get_maverig_dir() + os.sep, '')


def get_normpath(path, sub_dir='', create_dir=False):
    """Return the complete normalized path for the current os environment.

    For example ``get_normpath('maverig\data\configs\cfg.json')``
    or ``get_normpath('cfg.json', sub_dir='maverig\data\configs\')``
    will return ``'C:\Programs\maverig\maverig\data\configs\cfg.json'``.

    Set *create_dir* to True if non existing directories should be created.
    """
    if not 'maverig' in path and sub_dir:
        path = os.path.join(sub_dir, path)

    # if application is frozen, set path to base name (e.g. "icons" when data_dir="maverig/data/icons")
    frozen = getattr(sys, 'frozen', False)
    if frozen:
        for include_file in ['maverig/data/languages', 'maverig/data/icons', '/maverig/data/temp',
                             'maverig/data/configs', 'maverig/data/components',
                             'maverig/data/components/simulators']:
            path = path.replace(include_file, os.path.basename(include_file))
        path = os.path.normpath(path)
    else:
        path = os.path.join(get_maverig_dir(), path)
        path = os.path.normpath(path)
        if create_dir:
            ensure_dir(path)
    return path


def get_component_icon(filename):
    """Return the complete component icon path for the given *filename* relative to *maverig/data/components/icons*."""
    return get_normpath(filename, sub_dir='maverig/data/components/icons')


def get_icon(filename):
    """Return the complete icon path for the given filename relative to *maverig/data/icons*."""
    return get_normpath(filename, sub_dir='maverig/data/icons')


def get_lang_path(create_dir=False):
    """Return the complete languages locale path of *maverig/data/languages/*."""
    return get_normpath('maverig/data/languages/', create_dir=create_dir)


def get_temp_file(filename):
    """Return the complete temporary files path for the given filename relative to *maverig/data/temp*."""
    return get_normpath(filename, sub_dir='maverig/data/temp')


def get_config_file(filename):
    """Return the complete configuration file path for the given filename relative to *maverig/data/configs*."""
    return get_normpath(filename, sub_dir='maverig/data/configs')