.. _installation:

Installation
============

The easiest way to install xlwings is via pip::

    pip install xlwings

or conda::

    conda install xlwings


Alternatively, it can be installed from source. From within the ``xlwings`` directory, execute::

    python setup.py install



Dependencies
------------

* **Windows**: ``pywin32``

  On Windows, it is recommended to use one of the scientific Python distributions like
  `Anaconda <https://store.continuum.io/cshop/anaconda/>`_,
  `WinPython <https://winpython.github.io/>`_ or
  `Canopy <https://www.enthought.com/products/canopy/>`_ as they already include pywin32. Otherwise it needs to be
  installed from `here <http://sourceforge.net/projects/pywin32/files/pywin32/>`_.

* **Mac**: ``psutil``, ``appscript``

  On Mac, the dependencies are automatically being handled if xlwings is installed with ``pip``. However,
  the Xcode command line tools need to be available. Mac OS X 10.4 (*Tiger*) or later is required.
  The recommended Python distribution for Mac is `Anaconda <https://store.continuum.io/cshop/anaconda/>`_.

Optional Dependencies
---------------------

* NumPy
* Pandas

These packages are not required but highly recommended as NumPy arrays and Pandas DataFrames/Series play very nicely
with xlwings.


Python version support
----------------------

xlwings runs on Python 2.6-2.7 and 3.1-3.4