MAVERIG
=======

MAVERIG is a visualization component for the mosaik framework. Read the `documentation`__ for further information.

__ http://maverig.readthedocs.org/index.html

Install Dependencies
--------------------

* `PySide`__
* `mosaik`__
* `mosaik-api`__
* `mosaik-pypower`__
* `numpy`__
* `networkx`__
* `matplotlib`__
* `polib`__
* `colormath`__
* `python-dateutil`__
* `pyzmq`__

__ https://pypi.python.org/pypi/PySide#installation
__ https://mosaik.offis.de/install/
__ https://bitbucket.org/mosaik/mosaik-api-python
__ https://bitbucket.org/mosaik/mosaik-pypower/
__ http://www.numpy.org/
__ https://networkx.github.io/
__ http://matplotlib.org/
__ https://polib.readthedocs.org/en/latest/
__ http://python-colormath.readthedocs.org/en/latest/
__ https://dateutil.readthedocs.org/en/latest/
__ http://zeromq.github.io/pyzmq/

NOTE: Especially follow the detailed `mosaik install instructions`__ for the different operating systems
(inlcuding the instructions to run the demo). Windows users should install the dependencies from `this site`__ if available.

__ http://mosaik.readthedocs.org/en/latest/installation.html
__ http://www.lfd.uci.edu/~gohlke/pythonlibs/

Install MAVERIG
---------------

Install with `pip`__:

  $ pip install maverig

Or clone the repository and make a build with python or `cx_Freeze`__ (simulation is not running on Windows currently):

  $ python setup.py sdist bdist bdist_wheel

  $ python setup_cx.py build

NOTE: If you use cx_Freeze you have to rename *zmq.libzmq* to *libzmq* in the main folder after creating the build.

__ https://pip.pypa.io/en/latest/installing.html
__ http://cx-freeze.readthedocs.org/en/latest/overview.html

Downloads
---------

Maverig builds

* `Linux (64-Bit)`__

__ https://bitbucket.org/Sash221/maverig/downloads/maverig-1.0.4-linux-x86_64-3.4.zip

Virtual environments with maverig and all dependencies installed

* `Linux`__
* `Windows`__
* `Mac OS`__

__ https://bitbucket.org/Sash221/maverig/downloads/maverig1.0.4-virtualenv-linux-x86_64-3.4.zip
__ https://bitbucket.org/Sash221/maverig/downloads/maverig1.0.5-virtualenv-win32-3.4.zip
__ https://bitbucket.org/Sash221/maverig/downloads/maverig1.0.4-virtualenv-osx-3.4.zip.zip

User guides

* `English`__
* `German`__

__ https://bitbucket.org/Sash221/maverig/downloads/maverig_guide_en.pdf
__ https://bitbucket.org/Sash221/maverig/downloads/maverig_guide_de.pdf

LICENSE
-------

**LGPL**

LATEST CHANGES (v1.0)
---------------------

* Increased simulation performance
* Increased usability
* Improved graphs
* Defined components in JSON for better extensibility
* Implemented a component wizard so that new components can be added by user via the GUI
* Components can be hided and removed
* Settings can be changed while simulation is running
* Improved documentation
* Fixed minor bugs