.. -*- mode: rst -*-

scikit-umfpack
==============

scikit-umfpack provides wrapper of UMFPACK sparse direct solver to SciPy.

Use this if you wish to use the UMFPACK solver via
scipy.sparse.linalg.dsolve.linsolve(), for SciPy >= 0.14.0.

Dependencies
============

scikit-umfpack depends on NumPy and SciPy, swig is a build-time dependency.

Install
=======

This package uses distutils, which is the default way of installing python
modules. In the directory scikit-umfpack (the same as the file you are reading
now) do::

  python setup.py install

or for a local installation::

  python setup.py install --root=<DIRECTORY>

Development
===========

Code
----

You can check the latest sources with the command::

  git clone https://github.com/rc/scikit-umfpack.git

or if you have write privileges::

  git clone git@github.com:rc/scikit-umfpack.git

Testing
-------

After installation, you can launch the test suite from outside the
source directory (you will need to have the ``nose`` package installed)::

  nosetests -v scikits.umfpack


