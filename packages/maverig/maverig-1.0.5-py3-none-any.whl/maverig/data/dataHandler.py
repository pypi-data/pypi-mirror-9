import sys
import os

"""
This module is used for handling the paths to static files like icons or locales so that files can be found before and
after freezing the application. Freezing is done with
`cx_Freeze <http://cx-freeze.readthedocs.org/en/latest/overview.html>`_.
"""


def ensure_dir(path):
    """Create directories contained in path if they don't exist."""
    d = os.path.dirname(path)
    if not os.path.exists(d):
        os.makedirs(d)


def get_maverig_dir():
    """Return the maverig directory, e.g. ``'C:\Programs\maverig\maverig'``."""
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    else:
        import maverig
        return os.path.dirname(maverig.__file__)
        #  Alternative: the application directory (faulty in tests being called from system location)
        #return os.path.dirname(sys.argv[0])


def get_relpath(path):
    """Return the path relative to maverig directory.

    For example ``get_relpath('C:\Programs\maverig\maverig\data')`` will return ``'maverig\data'``."""
    return path.replace(get_maverig_dir(), 'maverig')


def get_normpath(path, sub_dir='', create_dir=False):
    """Return the complete normalized path for the current os environment.

    For example ``get_normpath('maverig\data\configs\cfg.json')``
    or ``get_normpath('cfg.json', sub_dir='maverig\data\configs\')``
    will return ``'C:\Programs\maverig\maverig\data\configs\cfg.json'``.

    Set *create_dir* to True if non existing directories should be created.
    """
    if sub_dir and 'maverig' not in path:
        path = os.path.join(sub_dir, path)

    path = path.replace(os.sep, '/')

    # if application is frozen, set path to base name (e.g. "maverig/icons" when data_dir="maverig/data/icons")
    frozen = getattr(sys, 'frozen', False)
    if frozen:
        for old, new in [('maverig/data/configs', 'maverig/configs'),
                         ('maverig/data/languages', 'maverig/languages'),
                         ('maverig/data/icons', 'maverig/icons'),
                         ('maverig/data/components', 'maverig/components'),
                         ('maverig/data/temp', 'maverig/temp'),
                         ('maverig/data/user_guide', 'maverig/user_guide'),
                         ('maverig/tests/data', 'maverig/data')]:
            path = path.replace(old, new, 1)

    # make absolute path from application directory
    if path.startswith('maverig/'):
        rel_path = path.replace('maverig/', '', 1)
        abs_path = os.path.join(get_maverig_dir(), rel_path)
    else:
        abs_path = path

    # convert path to os conform path
    abs_path = os.path.normpath(abs_path)

    if create_dir:
        ensure_dir(abs_path)
    return abs_path


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