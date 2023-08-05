/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 25 Mar 2014 12:58:31 CET
 *
 * @brief C/C++ API for bob::machine
 */

#ifndef BOB_LEARN_LIBSVM_H
#define BOB_LEARN_LIBSVM_H

#include <Python.h>
#include <bob.learn.libsvm/config.h>
#include <bob.learn.libsvm/file.h>
#include <bob.learn.libsvm/machine.h>
#include <bob.learn.libsvm/trainer.h>

#define BOB_LEARN_LIBSVM_MODULE_PREFIX bob.learn.libsvm
#define BOB_LEARN_LIBSVM_MODULE_NAME _library

/*******************
 * C API functions *
 *******************/

/* Enum defining entries in the function table */
enum _PyBobLearnLibsvm_ENUM{
  PyBobLearnLibsvm_APIVersion_NUM = 0,
  // Bindings for bob.learn.libsvm.File
  PyBobLearnLibsvmFile_Type_NUM,
  PyBobLearnLibsvmFile_Check_NUM,
  // Bindings for bob.learn.libsvm.Machine
  PyBobLearnLibsvmMachine_Type_NUM,
  PyBobLearnLibsvmMachine_Check_NUM,
  PyBobLearnLibsvmMachine_NewFromMachine_NUM,
  // Bindings for bob.learn.libsvm.Trainer
  PyBobLearnLibsvmTrainer_Type_NUM,
  PyBobLearnLibsvmTrainer_Check_NUM,
  // Bindings to general utilities
  PyBobLearnLibsvm_MachineTypeAsString_NUM,
  PyBobLearnLibsvm_StringAsMachineType_NUM,
  PyBobLearnLibsvm_CStringAsMachineType_NUM,
  PyBobLearnLibsvm_KernelTypeAsString_NUM,
  PyBobLearnLibsvm_StringAsKernelType_NUM,
  PyBobLearnLibsvm_CStringAsKernelType_NUM,
  // Total number of C API pointers
  PyBobLearnLibsvm_API_pointers
};

/**************
 * Versioning *
 **************/

#define PyBobLearnLibsvm_APIVersion_TYPE int

/***************************************
 * Bindings for bob.learn.libsvm.File *
 ***************************************/

typedef struct {
  PyObject_HEAD
  bob::learn::libsvm::File* cxx;
} PyBobLearnLibsvmFileObject;

#define PyBobLearnLibsvmFile_Type_TYPE PyTypeObject

#define PyBobLearnLibsvmFile_Check_RET int
#define PyBobLearnLibsvmFile_Check_PROTO (PyObject* o)

/******************************************
 * Bindings for bob.learn.libsvm.Machine *
 ******************************************/

typedef struct {
  PyObject_HEAD
  bob::learn::libsvm::Machine* cxx;
} PyBobLearnLibsvmMachineObject;

#define PyBobLearnLibsvmMachine_Type_TYPE PyTypeObject

#define PyBobLearnLibsvmMachine_Check_RET int
#define PyBobLearnLibsvmMachine_Check_PROTO (PyObject* o)

#define PyBobLearnLibsvmMachine_NewFromMachine_RET PyObject*
#define PyBobLearnLibsvmMachine_NewFromMachine_PROTO (bob::learn::libsvm::Machine* m)

/******************************************
 * Bindings for bob.learn.libsvm.Trainer *
 ******************************************/

typedef struct {
  PyObject_HEAD
  bob::learn::libsvm::Trainer* cxx;
} PyBobLearnLibsvmTrainerObject;

#define PyBobLearnLibsvmTrainer_Type_TYPE PyTypeObject

#define PyBobLearnLibsvmTrainer_Check_RET int
#define PyBobLearnLibsvmTrainer_Check_PROTO (PyObject* o)

/*********************************
 * Bindings to general utilities *
 *********************************/

#define PyBobLearnLibsvm_MachineTypeAsString_RET PyObject*
#define PyBobLearnLibsvm_MachineTypeAsString_PROTO (bob::learn::libsvm::machine_t s)

#define PyBobLearnLibsvm_StringAsMachineType_RET bob::learn::libsvm::machine_t
#define PyBobLearnLibsvm_StringAsMachineType_PROTO (PyObject* o)

#define PyBobLearnLibsvm_CStringAsMachineType_RET bob::learn::libsvm::machine_t
#define PyBobLearnLibsvm_CStringAsMachineType_PROTO (const char* s)

#define PyBobLearnLibsvm_KernelTypeAsString_RET PyObject*
#define PyBobLearnLibsvm_KernelTypeAsString_PROTO (bob::learn::libsvm::kernel_t s)

#define PyBobLearnLibsvm_StringAsKernelType_RET bob::learn::libsvm::kernel_t
#define PyBobLearnLibsvm_StringAsKernelType_PROTO (PyObject* o)

#define PyBobLearnLibsvm_CStringAsKernelType_RET bob::learn::libsvm::kernel_t
#define PyBobLearnLibsvm_CStringAsKernelType_PROTO (const char* s)


#ifdef BOB_LEARN_LIBSVM_MODULE

  /* This section is used when compiling `bob.learn.libsvm' itself */

  /**************
   * Versioning *
   **************/

  extern int PyBobLearnLibsvm_APIVersion;

  /***************************************
   * Bindings for bob.learn.libsvm.File *
   ***************************************/

  extern PyBobLearnLibsvmFile_Type_TYPE PyBobLearnLibsvmFile_Type;

  PyBobLearnLibsvmFile_Check_RET PyBobLearnLibsvmFile_Check PyBobLearnLibsvmFile_Check_PROTO;

  /******************************************
   * Bindings for bob.learn.libsvm.Machine *
   ******************************************/

  extern PyBobLearnLibsvmMachine_Type_TYPE PyBobLearnLibsvmMachine_Type;

  PyBobLearnLibsvmMachine_Check_RET PyBobLearnLibsvmMachine_Check PyBobLearnLibsvmMachine_Check_PROTO;

  PyBobLearnLibsvmMachine_NewFromMachine_RET PyBobLearnLibsvmMachine_NewFromMachine PyBobLearnLibsvmMachine_NewFromMachine_PROTO;

  /******************************************
   * Bindings for bob.learn.libsvm.Trainer *
   ******************************************/

  extern PyBobLearnLibsvmTrainer_Type_TYPE PyBobLearnLibsvmTrainer_Type;

  PyBobLearnLibsvmTrainer_Check_RET PyBobLearnLibsvmTrainer_Check PyBobLearnLibsvmTrainer_Check_PROTO;

  /*********************************
   * Bindings to general utilities *
   *********************************/

  PyBobLearnLibsvm_MachineTypeAsString_RET PyBobLearnLibsvm_MachineTypeAsString PyBobLearnLibsvm_MachineTypeAsString_PROTO;

  PyBobLearnLibsvm_StringAsMachineType_RET PyBobLearnLibsvm_StringAsMachineType PyBobLearnLibsvm_StringAsMachineType_PROTO;

  PyBobLearnLibsvm_CStringAsMachineType_RET PyBobLearnLibsvm_CStringAsMachineType PyBobLearnLibsvm_CStringAsMachineType_PROTO;

  PyBobLearnLibsvm_KernelTypeAsString_RET PyBobLearnLibsvm_KernelTypeAsString PyBobLearnLibsvm_KernelTypeAsString_PROTO;

  PyBobLearnLibsvm_StringAsKernelType_RET PyBobLearnLibsvm_StringAsKernelType PyBobLearnLibsvm_StringAsKernelType_PROTO;

  PyBobLearnLibsvm_CStringAsKernelType_RET PyBobLearnLibsvm_CStringAsKernelType PyBobLearnLibsvm_CStringAsKernelType_PROTO;

#else

  /* This section is used in modules that use `bob.learn.libsvm's' C-API */

/************************************************************************
 * Macros to avoid symbol collision and allow for separate compilation. *
 * We pig-back on symbols already defined for NumPy and apply the same  *
 * set of rules here, creating our own API symbol names.                *
 ************************************************************************/

#  if defined(PY_ARRAY_UNIQUE_SYMBOL)
#    define BOB_LEARN_LIBSVM_MAKE_API_NAME_INNER(a) BOB_LEARN_LIBSVM_ ## a
#    define BOB_LEARN_LIBSVM_MAKE_API_NAME(a) BOB_LEARN_LIBSVM_MAKE_API_NAME_INNER(a)
#    define PyBobLearnLibsvm_API BOB_LEARN_LIBSVM_MAKE_API_NAME(PY_ARRAY_UNIQUE_SYMBOL)
#  endif

#  if defined(NO_IMPORT_ARRAY)
  extern void **PyBobLearnLibsvm_API;
#  else
#    if defined(PY_ARRAY_UNIQUE_SYMBOL)
  void **PyBobLearnLibsvm_API;
#    else
  static void **PyBobLearnLibsvm_API=NULL;
#    endif
#  endif

  /**************
   * Versioning *
   **************/

# define PyBobLearnLibsvm_APIVersion (*(PyBobLearnLibsvm_APIVersion_TYPE *)PyBobLearnLibsvm_API[PyBobLearnLibsvm_APIVersion_NUM])

  /***************************************
   * Bindings for bob.learn.libsvm.File *
   ***************************************/

# define PyBobLearnLibsvmFile_Type (*(PyBobLearnLibsvmFile_Type_TYPE *)PyBobLearnLibsvm_API[PyBobLearnLibsvmFile_Type_NUM])

# define PyBobLearnLibsvmFile_Check (*(PyBobLearnLibsvmFile_Check_RET (*)PyBobLearnLibsvmFile_Check_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvmFile_Check_NUM])

  /******************************************
   * Bindings for bob.learn.libsvm.Machine *
   ******************************************/

# define PyBobLearnLibsvmMachine_Type (*(PyBobLearnLibsvmMachine_Type_TYPE *)PyBobLearnLibsvm_API[PyBobLearnLibsvmMachine_Type_NUM])

# define PyBobLearnLibsvmMachine_Check (*(PyBobLearnLibsvmMachine_Check_RET (*)PyBobLearnLibsvmMachine_Check_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvmMachine_Check_NUM])

# define PyBobLearnLibsvmMachine_NewFromMachine (*(PyBobLearnLibsvmMachine_NewFromMachine_RET (*)PyBobLearnLibsvmMachine_NewFromMachine_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvmMachine_NewFromMachine_NUM])

  /******************************************
   * Bindings for bob.learn.libsvm.Trainer *
   ******************************************/

# define PyBobLearnLibsvmTrainer_Type (*(PyBobLearnLibsvmTrainer_Type_TYPE *)PyBobLearnLibsvm_API[PyBobLearnLibsvmTrainer_Type_NUM])

# define PyBobLearnLibsvmTrainer_Check (*(PyBobLearnLibsvmTrainer_Check_RET (*)PyBobLearnLibsvmTrainer_Check_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvmTrainer_Check_NUM])

  /*********************************
   * Bindings to general utilities *
   *********************************/

# define PyBobLearnLibsvm_MachineTypeAsString (*(PyBobLearnLibsvm_MachineTypeAsString_RET (*)PyBobLearnLibsvm_MachineTypeAsString_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_MachineTypeAsString_NUM])

# define PyBobLearnLibsvm_StringAsMachineType (*(PyBobLearnLibsvm_StringAsMachineType_RET (*)PyBobLearnLibsvm_StringAsMachineType_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_StringAsMachineType_NUM])

# define PyBobLearnLibsvm_CStringAsMachineType (*(PyBobLearnLibsvm_CStringAsMachineType_RET (*)PyBobLearnLibsvm_CStringAsMachineType_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_CStringAsMachineType_NUM])

# define PyBobLearnLibsvm_KernelTypeAsString (*(PyBobLearnLibsvm_KernelTypeAsString_RET (*)PyBobLearnLibsvm_KernelTypeAsString_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_KernelTypeAsString_NUM])

# define PyBobLearnLibsvm_StringAsKernelType (*(PyBobLearnLibsvm_StringAsKernelType_RET (*)PyBobLearnLibsvm_StringAsKernelType_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_StringAsKernelType_NUM])

# define PyBobLearnLibsvm_CStringAsKernelType (*(PyBobLearnLibsvm_CStringAsKernelType_RET (*)PyBobLearnLibsvm_CStringAsKernelType_PROTO) PyBobLearnLibsvm_API[PyBobLearnLibsvm_CStringAsKernelType_NUM])

# if !defined(NO_IMPORT_ARRAY)

  /**
   * Returns -1 on error, 0 on success. PyCapsule_Import will set an exception
   * if there's an error.
   */
  static int import_bob_learn_libsvm(void) {

    PyObject *c_api_object;
    PyObject *module;

    module = PyImport_ImportModule(BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_PREFIX) "." BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_NAME));

    if (module == NULL) return -1;

    c_api_object = PyObject_GetAttrString(module, "_C_API");

    if (c_api_object == NULL) {
      Py_DECREF(module);
      return -1;
    }

#   if PY_VERSION_HEX >= 0x02070000
    if (PyCapsule_CheckExact(c_api_object)) {
      PyBobLearnLibsvm_API = (void **)PyCapsule_GetPointer(c_api_object,
          PyCapsule_GetName(c_api_object));
    }
#   else
    if (PyCObject_Check(c_api_object)) {
      BobLearnLibsvm_API = (void **)PyCObject_AsVoidPtr(c_api_object);
    }
#   endif

    Py_DECREF(c_api_object);
    Py_DECREF(module);

    if (!BobLearnLibsvm_API) {
      PyErr_Format(PyExc_ImportError,
#   if PY_VERSION_HEX >= 0x02070000
          "cannot find C/C++ API capsule at `%s.%s._C_API'",
#   else
          "cannot find C/C++ API cobject at `%s.%s._C_API'",
#   endif
          BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_PREFIX),
          BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_NAME));
      return -1;
    }

    /* Checks that the imported version matches the compiled version */
    int imported_version = *(int*)PyBobLearnLibsvm_API[PyBobLearnLibsvm_APIVersion_NUM];

    if (BOB_LEARN_LIBSVM_API_VERSION != imported_version) {
      PyErr_Format(PyExc_ImportError, "%s.%s import error: you compiled against API version 0x%04x, but are now importing an API with version 0x%04x which is not compatible - check your Python runtime environment for errors", BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_PREFIX), BOOST_PP_STRINGIZE(BOB_LEARN_LIBSVM_MODULE_NAME), BOB_LEARN_LIBSVM_API_VERSION, imported_version);
      return -1;
    }

    /* If you get to this point, all is good */
    return 0;

  }

# endif //!defined(NO_IMPORT_ARRAY)

#endif /* BOB_LEARN_LIBSVM_MODULE */

#endif /* BOB_LEARN_LIBSVM_H */
