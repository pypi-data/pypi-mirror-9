************
Installation
************

.. Contents::

Introduction
============

We recommended that you perform a binary installation. You should not attempt
to build SIMA if you are not familiar with compiling software from sources.

On Windows, we recommend using a scientific python distribution for installing
the various prerequisites. Recommended distributions are:

* `Python(x,y) <http://code.google.com/p/pythonxy/>`_
* `WinPython <http://winpython.sourceforge.net/>`_
* `Anaconda <https://store.continuum.io/cshop/anaconda>`_

For Mac OS X, we recommend installing the prerequisites, especially OpenCV,
using a package manager, such as `MacPorts <http://www.macports.org>`_.

Prerequisites
=============

SIMA depends on various freely available, open source software. Whenever
possible, we recommend installing these dependencies with your operating
system's or Python distribution's package manager prior to installing SIMA.

* `Python <http://python.org>`_ 2.7 
* `numpy <http://www.scipy.org>`_ >= 1.6.2
* `scipy <http://www.scipy.org>`_ >= 0.13.0
* `scikit-image <http://scikit-image.org>`_ >= 0.9.3
* `scikit-learn <http://scikit-learn.org>`_ >= 0.11
* `shapely <https://pypi.python.org/pypi/Shapely>`_ >= 1.2.14 (**Windows users**: be sure to install from `Christophe Gohlke's built wheels <http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely>`__)
* `pillow <https://pypi.python.org/pypi/Pillow>`_ >= 2.6.1
* `future <https://pypi.python.org/pypi/future>`_

Depending on the features and data formats you wish to use, you may also need
to install the following packages:

* `OpenCV <http://opencv.org>`_ >= 2.4.8, required for segmentation,
  registration of ROIs across multiple datasets, and the ROI Buddy GUI
* `h5py <http://www.h5py.org>`_ >= 2.2.1 (2.3.1 recommended), required for HDF5 file format 
* `bottleneck <http://pypi.python.org/pypi/Bottleneck>`_ >=0.8, for faster calculations
* `matplotlib <http://matplotlib.org>`_ >= 1.2.1, for saving extraction summary plots
* `mdp <http://mdp-toolkit.sourceforge.net>`_, required for ICA demixing of
  channels

If you build the package from source, you may also need:

* `Cython <http://cython.org>`_


SIMA installation
=================

Linux
-----
The SIMA package can be installed from the python package index::

    $ pip install sima --user 

Source code can be downloaded from https://pypi.python.org/pypi/sima.  If you
download the source, you can install the package with setuptools::

    $ python setup.py build
    $ python setup.py install --user

Windows
-------
The SIMA package can be installed from the python package index::

    $ pip install sima

Alternatively, the packaged wheel is available at
<https://pypi.python.org/pypi/sima> to be installed with your Python
distribution's package manager.

NOTE: You may need to install shapely separately from the package at:
<http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely>

If building SIMA from source or using pip or easy_install on Windows, you may
also need to follow these `instructions for compiling the Cython extensions
<https://github.com/cython/cython/wiki/64BitCythonExtensionsOnWindows>`_.

Mac OS X
--------
For installing the dependencies, we recommend using MacPorts. If you do not already
have XCode installed, downloading XCode from the App Store, and then run the following
commands in the Terminal to complete the XCode installation and license agreement::

    $ xcode-select --install
    $ gcc -v

Next, download and install MacPorts. Then run the following command in terminal to
install SIMA and its dependencies::

    $ sudo port selfupdate
    $ sudo port install python27 py27-numpy py27-scipy py27-scikit-image py27-scikit-learn py27-shapely py27-Pillow py27-matplotlib py27-bottleneck py27-pip py27-h5py opencv +python27
    $ sudo port select --set python python27
    $ sudo port select --set pip pip27
    $ pip install sima --user
