.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Fri 13 Dec 2013 12:35:22 CET

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.learn.libsvm/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.learn.libsvm/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.learn.libsvm.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.learn.libsvm
.. image:: https://coveralls.io/repos/bioidiap/bob.learn.libsvm/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.learn.libsvm
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.learn.libsvm/tree/master
.. image:: http://img.shields.io/pypi/v/bob.learn.libsvm.png
   :target: https://pypi.python.org/pypi/bob.learn.libsvm
.. image:: http://img.shields.io/pypi/dm/bob.learn.libsvm.png
   :target: https://pypi.python.org/pypi/bob.learn.libsvm

==================================
 Bob's Python bindings for LIBSVM
==================================

This package contains a set of Pythonic bindings for LIBSVM.

External Software Requirements
------------------------------

This package requires you have ``LIBSVM`` installed on your system.
If ``LIBSVM`` is installed on a standard location, this package will find it automatically.
You can just skip to the installation instructions.

In case you have installed ``LIBSVM`` on a non-standard location (e.g. your home directory), then you can specify the path to the root of that installation using the environment variable ``BOB_PREFIX_PATH``, **before** building and installing the package.
For example, if ``BOB_PREFIX_PATH`` is set to ``/home/user/libsvm-3.12``, then we will search for the header file ``svm.h`` in ``/home/user/libsvm-3.12/include`` and expect that the library file file is found under ``/home/user/libsvm-3.12/lib``.

If you are installing this package via ``pip`` for example, just set the environment variable like this::

  $ BOB_PREFIX_PATH=/home/user/libsvm-3.12 pip install bob.learn.libsvm

If you are installing this package via ``zc.buildout``, we recommend you use our `bob.buildout <http://pypi.python.org/pypi/bob.buildout>`_ extension and set the ``[environ]`` section to define ``BOB_PREFIX_PATH``.

Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.learn.libsvm/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.learn.libsvm/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.

.. _bob: https://www.idiap.ch/software/bob
