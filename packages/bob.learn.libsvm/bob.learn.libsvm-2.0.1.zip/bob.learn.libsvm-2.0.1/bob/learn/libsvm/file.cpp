/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 14 Jan 2014 14:26:09 CET
 *
 * @brief Bindings for a Bob compatible LIBSVM-based Machine for SVMs
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_LIBSVM_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>
#include <bob.learn.libsvm/api.h>
#include <structmember.h>

/***********************************************
 * Implementation of Support Vector File class *
 ***********************************************/

PyDoc_STRVAR(s_file_str, BOB_EXT_MODULE_PREFIX ".File");

PyDoc_STRVAR(s_file_doc,
"File(path)\n\
\n\
Loads a given LIBSVM data file. The data file format, as\n\
defined on the library README is like this:\n\
\n\
.. code-block:: text\n\
\n\
   <label> <index1>:<value1> <index2>:<value2> ...\n\
   <label> <index1>:<value1> <index2>:<value2> ...\n\
   <label> <index1>:<value1> <index2>:<value2> ...\n\
   ...\n\
\n\
The labels are integer values, so are the indexes, starting\n\
from ``1`` (and not from zero as a C-programmer would expect).\n\
The values are floating point. Zero values are suppressed -\n\
LIBSVM uses a sparse format.\n\
\n\
Upon construction, objects of this class will inspect the input\n\
file so that the maximum sample size is computed. Once that job\n\
is performed, you can read the data in your own pace using the\n\
:py:meth:`read` method.\n\
\n\
This class is made available to you so you can input original\n\
LIBSVM files and convert them to another better supported\n\
representation. You cannot, from this object, save data or\n\
extend the current set.\n\
");

static int PyBobLearnLibsvmFile_init
(PyBobLearnLibsvmFileObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* filename = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist,
        &PyBobIo_FilenameConverter, &filename))
    return -1;

  auto filename_ = make_safe(filename);

#if PY_VERSION_HEX >= 0x03000000
  const char* c_filename = PyBytes_AS_STRING(filename);
#else
  const char* c_filename = PyString_AS_STRING(filename);
#endif

  try {
    self->cxx = new bob::learn::libsvm::File(c_filename);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static void PyBobLearnLibsvmFile_delete
(PyBobLearnLibsvmFileObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

int PyBobLearnLibsvmFile_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnLibsvmFile_Type));
}

PyDoc_STRVAR(s_shape_str, "shape");
PyDoc_STRVAR(s_shape_doc,
"The size of each sample in the file, as tuple with a single entry");

static PyObject* PyBobLearnLibsvmFile_getShape
(PyBobLearnLibsvmFileObject* self, void* /*closure*/) {
  return Py_BuildValue("(n)", self->cxx->shape());
}

PyDoc_STRVAR(s_samples_str, "samples");
PyDoc_STRVAR(s_samples_doc, "The number of samples in the file");

static PyObject* PyBobLearnLibsvmFile_getSamples
(PyBobLearnLibsvmFileObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->samples());
}

PyDoc_STRVAR(s_filename_str, "filename");
PyDoc_STRVAR(s_filename_doc, "The name of the file being read");

static PyObject* PyBobLearnLibsvmFile_getFilename
(PyBobLearnLibsvmFileObject* self, void* /*closure*/) {
  return Py_BuildValue("s", self->cxx->filename().c_str());
}

static PyGetSetDef PyBobLearnLibsvmFile_getseters[] = {
    {
      s_shape_str,
      (getter)PyBobLearnLibsvmFile_getShape,
      0,
      s_shape_doc,
      0
    },
    {
      s_samples_str,
      (getter)PyBobLearnLibsvmFile_getSamples,
      0,
      s_samples_doc,
      0
    },
    {
      s_filename_str,
      (getter)PyBobLearnLibsvmFile_getFilename,
      0,
      s_filename_doc,
      0
    },
    {0}  /* Sentinel */
};

#if PY_VERSION_HEX >= 0x03000000
#  define PYOBJECT_STR PyObject_Str
#else
#  define PYOBJECT_STR PyObject_Unicode
#endif

PyObject* PyBobLearnLibsvmFile_Repr(PyBobLearnLibsvmFileObject* self) {

  /**
   * Expected output:
   *
   * bob.learn.libsvm.File('filename')
   */

  PyObject* retval = PyUnicode_FromFormat("%s('%s')",
      Py_TYPE(self)->tp_name, self->cxx->filename().c_str());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyObject* PyBobLearnLibsvmFile_Str(PyBobLearnLibsvmFileObject* self) {

  /**
   * Expected output:
   *
   * bob.learn.libsvm.File('filename') <float64@(3, 4)>
   */

  PyObject* retval = PyUnicode_FromFormat("%s('%s')  <float64@(%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)>",
      Py_TYPE(self)->tp_name, self->cxx->filename().c_str(),
      self->cxx->samples(), self->cxx->shape());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyDoc_STRVAR(s_reset_str, "reset");
PyDoc_STRVAR(s_reset_doc,
"o.reset() -> None\n\
\n\
Resets the current file so it starts reading from the begin\n\
once more.\n\
");

PyObject* PyBobLearnLibsvmFile_reset(PyBobLearnLibsvmFileObject* self) {
  try {
    self->cxx->reset();
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot reset: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }
  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_good_str, "good");
PyDoc_STRVAR(s_good_doc,
"o.good() -> bool\n\
\n\
Returns if the file is in a good state for readout.\n\
It is ``True`` if the current file it has neither the\n\
``eof``, ``fail`` or ``bad`` bits set, whic means that\n\
next :py:meth:`read` operation may succeed.\n\
");

PyObject* PyBobLearnLibsvmFile_good(PyBobLearnLibsvmFileObject* self) {
  try {
    if (self->cxx->good()) Py_RETURN_TRUE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot check file: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }
  Py_RETURN_FALSE;
}

PyDoc_STRVAR(s_fail_str, "fail");
PyDoc_STRVAR(s_fail_doc,
"o.fail() -> bool\n\
\n\
Returns ``True`` if the file has a ``fail`` condition or\n\
``bad`` bit sets. It means the read operation has found a\n\
critical condition and you can no longer proceed in reading\n\
from the file. Note this is not the same as :py:meth:`eof`\n\
which informs if the file has ended, but no errors were found\n\
during the read operations.\n\
");

PyObject* PyBobLearnLibsvmFile_fail(PyBobLearnLibsvmFileObject* self) {
  try {
    if (self->cxx->fail()) Py_RETURN_TRUE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot check file: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }
  Py_RETURN_FALSE;
}

PyDoc_STRVAR(s_eof_str, "eof");
PyDoc_STRVAR(s_eof_doc,
"o.eof() -> bool\n\
\n\
Returns ``True`` if the file has reached its end. To start\n\
reading from the file again, you must call :py:meth:`reset`\n\
before another read operation may succeed.\n\
");

PyObject* PyBobLearnLibsvmFile_eof(PyBobLearnLibsvmFileObject* self) {
  try {
    if (self->cxx->eof()) Py_RETURN_TRUE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot check file: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }
  Py_RETURN_FALSE;
}

PyDoc_STRVAR(s_read_str, "read");
PyDoc_STRVAR(s_read_doc,
"o.read([values]) -> (int, array)\n\
\n\
Reads a single line from the file and returns a tuple\n\
containing the label and a numpy array of ``float64``\n\
elements. The :py:class:`numpy.ndarray` has a shape\n\
as defined by the :py:attr:`shape` attribute of\n\
the current file. If the file has finished, this method\n\
returns ``None`` instead.\n\
\n\
If the output array ``values`` is provided, it must be a\n\
64-bit float array with a shape matching the file shape as\n\
defined by :py:attr:`shape`. Providing an output\n\
array avoids constant memory re-allocation.\n\
\n\
");

static PyObject* PyBobLearnLibsvmFile_read
(PyBobLearnLibsvmFileObject* self, PyObject* args, PyObject* kwds) {

  // before doing anything, check file status and returns if that is the case
  if (!self->cxx->good()) Py_RETURN_NONE;

  static const char* const_kwlist[] = {"values", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* values = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&", kwlist,
        &PyBlitzArray_OutputConverter, &values
        )) return 0;

  //protects acquired resources through this scope
  auto values_ = make_xsafe(values);

  if (values && values->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for output array `values'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (values && values->ndim != 1) {
    PyErr_Format(PyExc_RuntimeError, "Output arrays should always be 1D but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions", values->ndim);
    return 0;
  }

  if (values && values->shape[0] != (Py_ssize_t)self->cxx->shape()) {
    PyErr_Format(PyExc_RuntimeError, "1D `values' array should have %" PY_FORMAT_SIZE_T "d elements matching the shape of this file, not %" PY_FORMAT_SIZE_T "d rows", self->cxx->shape(), values->shape[0]);
    return 0;
  }

  /** if ``values`` was not pre-allocated, do it now **/
  if (!values) {
    Py_ssize_t osize = self->cxx->shape();
    values = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &osize);
    values_ = make_safe(values);
  }

  /** all basic checks are done, can call the machine now **/
  int label = 0;

  try {
    auto bz = PyBlitzArrayCxx_AsBlitz<double,1>(values);
    bool ok = self->cxx->read_(label, *bz);
    if (!ok) Py_RETURN_NONE; ///< error condition or end-of-file
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot read data: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(values);
  return Py_BuildValue("iO",
      label,
      PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(values))
      );

}

PyDoc_STRVAR(s_read_all_str, "read_all");
PyDoc_STRVAR(s_read_all_doc,
"o.read_all([labels, [values]) -> (array, array)\n\
\n\
Reads all contents of the file into the output arrays\n\
``labels`` (used for storing each entry's label) and\n\
``values`` (used to store each entry's features).\n\
The array ``labels``, if provided, must be a 1D\n\
:py:class:`numpy.ndarray` with data type ``int64``,\n\
containing as many positions as entries in the file, as\n\
returned by the attribute :py:attr:`samples`. The\n\
array ``values``, if provided, must be a 2D array with\n\
data type ``float64``, as many rows as entries in the\n\
file and as many columns as features in each entry, as\n\
defined by the attribute :py:attr:`shape`.\n\
\n\
If the output arrays ``labels`` and/or ``values`` are not\n\
provided, they will be allocated internally and returned.\n\
\n\
.. note::\n\
\n\
   This method is intended to be used for reading the\n\
   whole contents of the input file. The file will be\n\
   reset as by calling :py:meth:`reset` before the\n\
   readout starts.\n\
\n\
");

static PyObject* PyBobLearnLibsvmFile_read_all
(PyBobLearnLibsvmFileObject* self, PyObject* args, PyObject* kwds) {

  // before doing anything, check file status and returns if that is the case
  if (!self->cxx->good()) Py_RETURN_NONE;

  static const char* const_kwlist[] = {"labels", "values", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* labels = 0;
  PyBlitzArrayObject* values = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&O&", kwlist,
        &PyBlitzArray_OutputConverter, &labels,
        &PyBlitzArray_OutputConverter, &values
        )) return 0;

  //protects acquired resources through this scope
  auto labels_ = make_xsafe(labels);
  auto values_ = make_xsafe(values);

  if (labels && labels->type_num != NPY_INT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit integer arrays for output array `labels'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (values && values->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for output array `values'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (labels && labels->ndim != 1) {
    PyErr_Format(PyExc_RuntimeError, "Output array `labels' should always be 1D but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions", labels->ndim);
    return 0;
  }

  if (values && values->ndim != 2) {
    PyErr_Format(PyExc_RuntimeError, "Output array `values' should always be 2D but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions", values->ndim);
    return 0;
  }

  if (labels && labels->shape[0] != (Py_ssize_t)self->cxx->samples()) {
    PyErr_Format(PyExc_RuntimeError, "1D `labels' array should have %" PY_FORMAT_SIZE_T "d elements matching the number of samples in this file, not %" PY_FORMAT_SIZE_T "d rows", self->cxx->samples(), labels->shape[0]);
    return 0;
  }

  if (values && values->shape[0] != (Py_ssize_t)self->cxx->samples()) {
    PyErr_Format(PyExc_RuntimeError, "2D `values' array should have %" PY_FORMAT_SIZE_T "d rows matching the number of samples in this file, not %" PY_FORMAT_SIZE_T "d rows", self->cxx->samples(), values->shape[0]);
    return 0;
  }

  if (values && values->shape[1] != (Py_ssize_t)self->cxx->shape()) {
    PyErr_Format(PyExc_RuntimeError, "2D `values' array should have %" PY_FORMAT_SIZE_T "d columns matching the shape of this file, not %" PY_FORMAT_SIZE_T "d rows", self->cxx->shape(), values->shape[0]);
    return 0;
  }

  /** if ``labels`` was not pre-allocated, do it now **/
  if (!labels) {
    Py_ssize_t osize = self->cxx->samples();
    labels = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_INT64, 1, &osize);
    labels_ = make_safe(labels);
  }

  /** if ``values`` was not pre-allocated, do it now **/
  if (!values) {
    Py_ssize_t osize[2];
    osize[0] = self->cxx->samples();
    osize[1] = self->cxx->shape();
    values = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 2, osize);
    values_ = make_safe(values);
  }

  /** all basic checks are done, can call the machine now **/
  try {
    self->cxx->reset();
    auto bzlab = PyBlitzArrayCxx_AsBlitz<int64_t,1>(labels);
    auto bzval = PyBlitzArrayCxx_AsBlitz<double,2>(values);
    blitz::Range all = blitz::Range::all();
    int k = 0;
    while (self->cxx->good()) {
      blitz::Array<double,1> v_ = (*bzval)(k, all);
      int label = 0;
      bool ok = self->cxx->read_(label, v_);
      if (ok) (*bzlab)(k) = label;
      ++k;
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot read data: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(labels);
  Py_INCREF(values);
  return Py_BuildValue("OO",
      PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(labels)),
      PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(values))
      );

}

static PyMethodDef PyBobLearnLibsvmFile_methods[] = {
  {
    s_reset_str,
    (PyCFunction)PyBobLearnLibsvmFile_reset,
    METH_NOARGS,
    s_reset_doc
  },
  {
    s_good_str,
    (PyCFunction)PyBobLearnLibsvmFile_good,
    METH_NOARGS,
    s_good_doc
  },
  {
    s_fail_str,
    (PyCFunction)PyBobLearnLibsvmFile_fail,
    METH_NOARGS,
    s_fail_doc
  },
  {
    s_eof_str,
    (PyCFunction)PyBobLearnLibsvmFile_eof,
    METH_NOARGS,
    s_eof_doc
  },
  {
    s_read_str,
    (PyCFunction)PyBobLearnLibsvmFile_read,
    METH_VARARGS|METH_KEYWORDS,
    s_read_doc
  },
  {
    s_read_all_str,
    (PyCFunction)PyBobLearnLibsvmFile_read_all,
    METH_VARARGS|METH_KEYWORDS,
    s_read_all_doc
  },
  {0} /* Sentinel */
};

static PyObject* PyBobLearnLibsvmFile_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnLibsvmFileObject* self =
    (PyBobLearnLibsvmFileObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyTypeObject PyBobLearnLibsvmFile_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_file_str,                                    /* tp_name */
    sizeof(PyBobLearnLibsvmFileObject),            /* tp_basicsize */
    0,                                             /* tp_itemsize */
    (destructor)PyBobLearnLibsvmFile_delete,       /* tp_dealloc */
    0,                                             /* tp_print */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_compare */
    (reprfunc)PyBobLearnLibsvmFile_Repr,           /* tp_repr */
    0,                                             /* tp_as_number */
    0,                                             /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    0,                                             /* tp_call */
    (reprfunc)PyBobLearnLibsvmFile_Str,            /* tp_str */
    0,                                             /* tp_getattro */
    0,                                             /* tp_setattro */
    0,                                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,      /* tp_flags */
    s_file_doc,                                    /* tp_doc */
    0,                                             /* tp_traverse */
    0,                                             /* tp_clear */
    0,                                             /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    0,                                             /* tp_iter */
    0,                                             /* tp_iternext */
    PyBobLearnLibsvmFile_methods,                  /* tp_methods */
    0,                                             /* tp_members */
    PyBobLearnLibsvmFile_getseters,                /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)PyBobLearnLibsvmFile_init,           /* tp_init */
    0,                                             /* tp_alloc */
    PyBobLearnLibsvmFile_new,                      /* tp_new */
};
