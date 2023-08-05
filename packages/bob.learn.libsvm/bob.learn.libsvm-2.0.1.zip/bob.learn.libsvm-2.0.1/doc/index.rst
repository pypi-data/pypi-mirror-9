.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Fri 13 Dec 2013 12:50:06 CET
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _bob.learn.libsvm:

============================
 Bob-LIBSVM Python Bindings
============================

.. todolist::

This module contains a set of Pythonic bindings to LIBSVM that work well with
Bob, following its Machine/Trainer machine learning model. Our extension can
load and save native LIBSVM files for trained machines, but also supports
loading and saving machine models in HDF5 files, so that normalization
parameters are kept together with the machine.

Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api
   c_cpp_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst
