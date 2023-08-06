from cx_Freeze import setup, Executable
import sys

"""
Setup script for cx_Freeze. Build with:
    $ python setup_cx.py build
"""

base = None
targetName = 'maverig'
if sys.platform == 'win32':
    base = 'Win32GUI'
    targetName += '.exe'

build_exe_options = {
    'include_files': ['README.rst', 'LICENSE.txt', './maverig/scenarios', './maverig/data/configs',
                      './maverig/data/languages', './maverig/data/icons', './maverig/data/temp',
                      './maverig/data/user_guide', './maverig/tests/data', 'maverig/data/components'],
    'packages': ['pypower', 'mosaik_pypower'],
    'copy_dependent_files': 'True'
}

executables = [
    Executable('./maverig/EntryPoint.py',
               base=base,
               targetName=targetName)
]

setup(name='Maverig',
      version='1.0.2',
      description='Maverig',
      options={'build_exe': build_exe_options},
      executables=executables)