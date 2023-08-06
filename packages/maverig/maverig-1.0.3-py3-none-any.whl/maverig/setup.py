from setuptools import setup, find_packages

setup(
    # meta
    name='maverig',
    version='1.0.3',
    author="Project MAVERIG",
    author_email="pg-maverig@offis.de",
    description="MAVERIG is a visualization component for the mosaik framework",
    long_description=(open("README.rst").read()),
    license='LGPL',
    url="https://bitbucket.org/Sash221/maverig",

    # package data
    packages=find_packages(exclude=['maverig.tests', 'maverig.tests.*']),
    package_data={'': ['*txt', '*.in', '*.rst']},
    include_package_data=True,

    # dependencies
    install_requires=[
        'PySide==1.2.2',
    ],

    # entry points
    entry_points={
        'gui_scripts': ['maverig = maverig.EntryPoint:main']
    }
)
