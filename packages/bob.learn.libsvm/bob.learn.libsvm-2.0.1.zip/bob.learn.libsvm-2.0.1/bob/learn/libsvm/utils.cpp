/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 28 Mar 13:08:40 2014 CET
 *
 * @brief Bindings for a Bob compatible LIBSVM-based Trainer for SVMs
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_LIBSVM_MODULE
#include <bob.blitz/cleanup.h>
#include <bob.learn.libsvm/api.h>

PyObject* PyBobLearnLibsvm_MachineTypeAsString(bob::learn::libsvm::machine_t s) {
  switch(s) {
    case bob::learn::libsvm::C_SVC:
      return Py_BuildValue("s", "C_SVC");
    case bob::learn::libsvm::NU_SVC:
      return Py_BuildValue("s", "NU_SVC");
    case bob::learn::libsvm::ONE_CLASS:
      return Py_BuildValue("s", "ONE_CLASS");
    case bob::learn::libsvm::EPSILON_SVR:
      return Py_BuildValue("s", "EPSILON_SVR");
    case bob::learn::libsvm::NU_SVR:
      return Py_BuildValue("s", "NU_SVR");
    default:
      PyErr_Format(PyExc_AssertionError, "illegal machine type (%d) - DEBUG ME", s);
      return 0;
  }
}

bob::learn::libsvm::machine_t PyBobLearnLibsvm_StringAsMachineType(PyObject* o) {

  //sane way to extract a string from an object w/o macros
  PyObject* args = Py_BuildValue("(O)", o);
  auto args_ = make_safe(args);
  const char* s = 0;
  if (!PyArg_ParseTuple(args, "s", &s)) return (bob::learn::libsvm::machine_t)-1;

  return PyBobLearnLibsvm_CStringAsMachineType(s);

}

bob::learn::libsvm::machine_t PyBobLearnLibsvm_CStringAsMachineType(const char* s) {

  static const char* available = "`C_SVC' or `NU_SVC'";

  std::string s_(s);

  if (s_ == "C_SVC") {
    return bob::learn::libsvm::C_SVC;
  }
  else if (s_ == "NU_SVC") {
    return bob::learn::libsvm::NU_SVC;
  }
  else if (s_ == "ONE_CLASS") {
    PyErr_Format(PyExc_NotImplementedError, "support for `%s' is not currently implemented by these bindings - choose from %s", s, available);
    return bob::learn::libsvm::ONE_CLASS;
  }
  else if (s_ == "EPSILON_SVR") {
    PyErr_Format(PyExc_NotImplementedError, "support for `%s' is not currently implemented by these bindings - choose from %s", s, available);
    return bob::learn::libsvm::EPSILON_SVR;
  }
  else if (s_ == "NU_SVR") {
    PyErr_Format(PyExc_NotImplementedError, "support for `%s' is not currently implemented by these bindings - choose from %s", s, available);
    return bob::learn::libsvm::NU_SVR;
  }

  PyErr_Format(PyExc_ValueError, "SVM type `%s' is not supported by these bindings - choose from %s", s, available);
  return (bob::learn::libsvm::machine_t)(-1);

}

PyObject* PyBobLearnLibsvm_KernelTypeAsString(bob::learn::libsvm::kernel_t s) {

  switch(s) {
    case bob::learn::libsvm::LINEAR:
      return Py_BuildValue("s", "LINEAR");
    case bob::learn::libsvm::POLY:
      return Py_BuildValue("s", "POLY");
    case bob::learn::libsvm::RBF:
      return Py_BuildValue("s", "RBF");
    case bob::learn::libsvm::SIGMOID:
      return Py_BuildValue("s", "SIGMOID");
    case bob::learn::libsvm::PRECOMPUTED:
      return Py_BuildValue("s", "PRECOMPUTED");
    default:
      // if you get to this point, an error occurred somewhere - corruption?
      PyErr_Format(PyExc_AssertionError, "illegal kernel type (%d) - DEBUG ME", s);
      return 0;
  }
}

bob::learn::libsvm::kernel_t PyBobLearnLibsvm_StringAsKernelType(PyObject* o) {

  //portable way to extract a string from an object w/o macros
  PyObject* args = Py_BuildValue("(O)", o);
  auto args_ = make_safe(args);
  const char* s = 0;
  if (!PyArg_ParseTuple(args, "s", &s)) return (bob::learn::libsvm::kernel_t)-1;

  return PyBobLearnLibsvm_CStringAsKernelType(s);

}

bob::learn::libsvm::kernel_t PyBobLearnLibsvm_CStringAsKernelType(const char* s) {

  static const char* available = "`LINEAR', `POLY', `RBF' or `SIGMOID'";

  std::string s_(s);

  if (s_ == "LINEAR") {
    return bob::learn::libsvm::LINEAR;
  }
  else if (s_ == "POLY") {
    return bob::learn::libsvm::POLY;
  }
  else if (s_ == "RBF") {
    return bob::learn::libsvm::RBF;
  }
  else if (s_ == "SIGMOID") {
    return bob::learn::libsvm::SIGMOID;
  }
  else if (s_ == "PRECOMPUTED") {
    PyErr_Format(PyExc_NotImplementedError, "support for `%s' kernels is not currently implemented by these bindings - choose from %s", s, available);
  }

  PyErr_Format(PyExc_ValueError, "SVM kernel type `%s' is not supported by these bindings - choose from %s", s, available);
  return (bob::learn::libsvm::kernel_t)(-1);

}
