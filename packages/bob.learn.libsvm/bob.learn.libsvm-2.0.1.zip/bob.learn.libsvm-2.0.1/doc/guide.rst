.. vim: set fileencoding=utf-8 :
.. consolidated by Andre Anjos <andre.anjos@idiap.ch>
.. Wed 26 Mar 2014 10:38:10 CET
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. testsetup::

  import os
  import numpy
  import bob.learn.libsvm

  def F(m, f):
    from pkg_resources import resource_filename
    return resource_filename(m, os.path.join('data', f))

  heart_model = F('bob.learn.libsvm', 'heart.svmmodel')

  svm = bob.learn.libsvm.Machine(heart_model)

  heart_data = F('bob.learn.libsvm', 'heart.svmdata')

  f = bob.learn.libsvm.File(heart_data)

======================================
 Support Vector Machines and Trainers
======================================

A **Support vector machine** (SVM) [1]_ is a very popular `supervised` learning
technique. |project| provides a bridge to `LIBSVM`_ which allows you to `train`
such a `machine` and use it for classification. This section contains a
tutorial on how to use |project|'s Pythonic bindings to LIBSVM. It starts by
introducing the support vector :py:class:`bob.learn.libsvm.Machine` followed
by the trainer usage.

Machines
--------

The functionality of this bridge includes loading and saving SVM data files and
machine models, which you can produce or download following the instructions
found on `LIBSVM`_'s home page. |project| bindings to `LIBSVM`_ **do not**
allow you to explicitly set the machine's internal values. You must use the
a trainer to create a machine first, as explained further down. Once you have
followed those instructions, you can come back to this point and follow the
remaining examples here.

.. note::

  Our current ``svm`` object was trained with the file called ``heart_scale``,
  distributed with `LIBSVM`_ and `available here
  <http://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/heart_scale>`_.
  This dataset proposes a binary classification problem (i.e., 2 classes of
  features to be discriminated). The number of features is 13.

Our extensions to `LIBSVM`_ also allows you to feed data through a
:py:class:`bob.learn.libsvm.Machine` using :py:class:`numpy.ndarray` objects
and collect results in that format. For the following lines, we assume you have
available a :py:class:`bob.learn.libsvm.Machine` named ``svm``. (For this
example, the variable ``svm`` was generated from the ``heart_scale`` dataset
using the application ``svm-train`` with default parameters). The ``shape``
attribute, indicates how many features a machine from this module can input and
how many it outputs (typically, just 1):

.. doctest::

  >>> svm.shape
  (13, 1)

To run a single example through the SVM, just use the ``()`` operator:

.. doctest::

  >> svm(numpy.ones((13,), 'float64'))
  1
  >> svm(numpy.ones((10,13), 'float64'))
  (1, 1, 1, 1, 1, 1, 1, 1, 1, 1)

Visit the documentation for :py:class:`bob.learn.libsvm.Machine` to find more
information about these bindings and methods you can call on such a machine.
Visit the documentation for :py:class:`bob.learn.libsvm.File` for information
on loading `LIBSVM`_ data files directly into python and producing
:py:class:`numpy.ndarray` objects.

Below is a quick example: Suppose the variable ``f`` contains an object of
type :py:class:`bob.learn.libsvm.File`. Then, you could read data (and labels)
from the file like this:

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> labels, data = f.read_all()
   >>> data = numpy.vstack(data) #creates a single 2D array

Then you can throw the data into the ``svm`` machine you trained earlier like
this:

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> predicted_labels = svm(data)

Training
--------

The training set for SVM's consists of a list of 2D `NumPy` arrays, one for
each class. The first dimension of each 2D `NumPy` array is the number of
training samples for the given class and the second dimension is the
dimensionality of the feature. For instance, let's consider the following
training set for a two class problem:

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> pos = numpy.array([[1,-1,1], [0.5,-0.5,0.5], [0.75,-0.75,0.8]], 'float64')
   >>> neg = numpy.array([[-1,1,-0.75], [-0.25,0.5,-0.8]], 'float64')
   >>> data = [pos,neg]
   >>> print(data) # doctest: +SKIP

.. note::

   Please note that in the above training set, the data is pre-scaled so
   features remain in the range between -1 and +1. libsvm, apparently, suggests
   you do that for all features. Our bindings to libsvm do not include scaling.
   If you want to implement that generically, please do it.

Then, an SVM [1]_ can be trained easily using the
:py:class:`bob.learn.libsvm.Trainer` class.

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> trainer = bob.learn.libsvm.Trainer()
   >>> machine = trainer.train(data) #ordering only affects labels

This returns a :py:class:`bob.learn.libsvm.Machine` which can later be used
for classification, as explained before.

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> predicted_label = machine(numpy.array([1.,-1.,1.]))
   >>> print(predicted_label)
   [1]

The `training` procedure allows setting several different options. For
instance, the default `kernel` is an `RBF`. If we would like a `linear SVM`
instead, this can be set before calling the
:py:meth:`bob.learn.libsvm.Trainer.train` method.

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> trainer.kernel_type = 'LINEAR'


Acknowledgements
----------------

As a final note, if you decide to use our `LIBSVM`_ bindings for your
publication, be sure to also cite:

.. code-block:: latex

  @article{CC01a,
   author  = {Chang, Chih-Chung and Lin, Chih-Jen},
   title   = {{LIBSVM}: A library for support vector machines},
   journal = {ACM Transactions on Intelligent Systems and Technology},
   volume  = {2},
   issue   = {3},
   year    = {2011},
   pages   = {27:1--27:27},
   note    = {Software available at \url{http://www.csie.ntu.edu.tw/~cjlin/libsvm}}
  }

.. Place here your external references
.. include:: links.rst
.. [1] http://en.wikipedia.org/wiki/Support_vector_machine
