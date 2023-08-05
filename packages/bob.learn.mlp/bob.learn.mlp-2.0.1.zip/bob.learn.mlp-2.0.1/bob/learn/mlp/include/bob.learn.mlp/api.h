/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 24 Apr 17:32:07 2014 CEST
 */

#ifndef BOB_LEARN_MLP_H
#define BOB_LEARN_MLP_H

#include <Python.h>
#include <boost/shared_ptr.hpp>
#include <bob.learn.mlp/config.h>

#include <bob.learn.mlp/machine.h>
#include <bob.learn.mlp/cost.h>
#include <bob.learn.mlp/square_error.h>
#include <bob.learn.mlp/cross_entropy.h>
#include <bob.learn.mlp/shuffler.h>
#include <bob.learn.mlp/trainer.h>
#include <bob.learn.mlp/backprop.h>
#include <bob.learn.mlp/rprop.h>

#define BOB_LEARN_MLP_MODULE_PREFIX bob.learn.mlp
#define BOB_LEARN_MLP_MODULE_NAME _library

/*******************
 * C API functions *
 *******************/

/* Enum defining entries in the function table */
enum _PyBobLearnMLP_ENUM {
  PyBobLearnMLP_APIVersion_NUM = 0,
  // Bindings for bob.learn.mlp.Machine
  PyBobLearnMLPMachine_Type_NUM,
  PyBobLearnMLPMachine_Check_NUM,
  // Bindings for bob.learn.mlp.Cost and variants
  PyBobLearnCost_Type_NUM,
  PyBobLearnCost_Check_NUM,
  PyBobLearnCost_NewFromCost_NUM,
  PyBobLearnSquareError_Type_NUM,
  PyBobLearnCrossEntropyLoss_Type_NUM,
  // Bindings for bob.learn.mlp.DataShuffler
  PyBobLearnDataShuffler_Type_NUM,
  PyBobLearnDataShuffler_Check_NUM,
  // Bindings for bob.learn.mlp.Trainer
  PyBobLearnMLPTrainer_Type_NUM,
  PyBobLearnMLPTrainer_Check_NUM,
  PyBobLearnMLPBackProp_Type_NUM,
  PyBobLearnMLPBackProp_Check_NUM,
  PyBobLearnMLPRProp_Type_NUM,
  PyBobLearnMLPRProp_Check_NUM,
  // Total number of C API pointers
  PyBobLearnMLP_API_pointers
};

/**************
 * Versioning *
 **************/

#define PyBobLearnMLP_APIVersion_TYPE int

/***************************************
 * Bindings for bob.learn.mlp.Machine *
 ***************************************/

typedef struct {
  PyObject_HEAD
  bob::learn::mlp::Machine* cxx;
} PyBobLearnMLPMachineObject;

#define PyBobLearnMLPMachine_Type_TYPE PyTypeObject

#define PyBobLearnMLPMachine_Check_RET int
#define PyBobLearnMLPMachine_Check_PROTO (PyObject* o)

typedef struct {
  PyObject_HEAD
  boost::shared_ptr<bob::learn::mlp::Cost> cxx;
} PyBobLearnCostObject;

#define PyBobLearnCost_Type_TYPE PyTypeObject

#define PyBobLearnCost_Check_RET int
#define PyBobLearnCost_Check_PROTO (PyObject* o)

#define PyBobLearnCost_NewFromCost_RET PyObject*
#define PyBobLearnCost_NewFromCost_PROTO (boost::shared_ptr<bob::learn::mlp::Cost>)

typedef struct {
  PyBobLearnCostObject parent;
  boost::shared_ptr<bob::learn::mlp::SquareError> cxx;
} PyBobLearnSquareErrorObject;

#define PyBobLearnSquareError_Type_TYPE PyTypeObject

typedef struct {
  PyBobLearnCostObject parent;
  boost::shared_ptr<bob::learn::mlp::CrossEntropyLoss> cxx;
} PyBobLearnCrossEntropyLossObject;

#define PyBobLearnCrossEntropyLoss_Type_TYPE PyTypeObject

typedef struct {
  PyObject_HEAD
  bob::learn::mlp::DataShuffler* cxx;
} PyBobLearnDataShufflerObject;

#define PyBobLearnDataShuffler_Type_TYPE PyTypeObject

#define PyBobLearnDataShuffler_Check_RET int
#define PyBobLearnDataShuffler_Check_PROTO (PyObject* o)

/***************************************
 * Bindings for bob.learn.mlp.Trainer *
 ***************************************/

typedef struct {
  PyObject_HEAD
  bob::learn::mlp::Trainer* cxx;
} PyBobLearnMLPTrainerObject;

#define PyBobLearnMLPTrainer_Type_TYPE PyTypeObject

#define PyBobLearnMLPTrainer_Check_RET int
#define PyBobLearnMLPTrainer_Check_PROTO (PyObject* o)

typedef struct {
  PyBobLearnMLPTrainerObject parent;
  bob::learn::mlp::BackProp* cxx;
} PyBobLearnMLPBackPropObject;

#define PyBobLearnMLPBackProp_Type_TYPE PyTypeObject

#define PyBobLearnMLPBackProp_Check_RET int
#define PyBobLearnMLPBackProp_Check_PROTO (PyObject* o)

typedef struct {
  PyBobLearnMLPTrainerObject parent;
  bob::learn::mlp::RProp* cxx;
} PyBobLearnMLPRPropObject;

#define PyBobLearnMLPRProp_Type_TYPE PyTypeObject

#define PyBobLearnMLPRProp_Check_RET int
#define PyBobLearnMLPRProp_Check_PROTO (PyObject* o)

#ifdef BOB_LEARN_MLP_MODULE

  /* This section is used when compiling `bob.learn.mlp' itself */

  /**************
   * Versioning *
   **************/

  extern int PyBobLearnMLP_APIVersion;

  /***************************************
   * Bindings for bob.learn.mlp.Machine *
   ***************************************/

  extern PyBobLearnMLPMachine_Type_TYPE PyBobLearnMLPMachine_Type;

  PyBobLearnMLPMachine_Check_RET PyBobLearnMLPMachine_Check PyBobLearnMLPMachine_Check_PROTO;

  /************************************
   * Bindings for bob.learn.mlp.Cost *
   ************************************/

  extern PyBobLearnCost_Type_TYPE PyBobLearnCost_Type;

  PyBobLearnCost_Check_RET PyBobLearnCost_Check PyBobLearnCost_Check_PROTO;

  extern PyBobLearnSquareError_Type_TYPE PyBobLearnSquareError_Type;

  extern PyBobLearnCrossEntropyLoss_Type_TYPE PyBobLearnCrossEntropyLoss_Type;

  PyBobLearnCost_NewFromCost_RET PyBobLearnCost_NewFromCost PyBobLearnCost_NewFromCost_PROTO;

  /********************************************
   * Bindings for bob.learn.mlp.DataShuffler *
   ********************************************/

  extern PyBobLearnDataShuffler_Type_TYPE PyBobLearnDataShuffler_Type;

  PyBobLearnDataShuffler_Check_RET PyBobLearnDataShuffler_Check PyBobLearnDataShuffler_Check_PROTO;

  /***************************************
   * Bindings for bob.learn.mlp.Trainer *
   ***************************************/

  extern PyBobLearnMLPTrainer_Type_TYPE PyBobLearnMLPTrainer_Type;

  PyBobLearnMLPTrainer_Check_RET PyBobLearnMLPTrainer_Check PyBobLearnMLPTrainer_Check_PROTO;

  extern PyBobLearnMLPBackProp_Type_TYPE PyBobLearnMLPBackProp_Type;

  PyBobLearnMLPBackProp_Check_RET PyBobLearnMLPBackProp_Check PyBobLearnMLPBackProp_Check_PROTO;

  extern PyBobLearnMLPRProp_Type_TYPE PyBobLearnMLPRProp_Type;

  PyBobLearnMLPRProp_Check_RET PyBobLearnMLPRProp_Check PyBobLearnMLPRProp_Check_PROTO;

#else

  /* This section is used in modules that use `bob.learn.mlp's' C-API */

/************************************************************************
 * Macros to avoid symbol collision and allow for separate compilation. *
 * We pig-back on symbols already defined for NumPy and apply the same  *
 * set of rules here, creating our own API symbol names.                *
 ************************************************************************/

#  if defined(PY_ARRAY_UNIQUE_SYMBOL)
#    define BOB_LEARN_MLP_MAKE_API_NAME_INNER(a) BOB_LEARN_MLP_ ## a
#    define BOB_LEARN_MLP_MAKE_API_NAME(a) BOB_LEARN_MLP_MAKE_API_NAME_INNER(a)
#    define PyBobLearnMLP_API BOB_LEARN_MLP_MAKE_API_NAME(PY_ARRAY_UNIQUE_SYMBOL)
#  endif

#  if defined(NO_IMPORT_ARRAY)
  extern void **PyBobLearnMLP_API;
#  else
#    if defined(PY_ARRAY_UNIQUE_SYMBOL)
  void **PyBobLearnMLP_API;
#    else
  static void **PyBobLearnMLP_API=NULL;
#    endif
#  endif

  /**************
   * Versioning *
   **************/

# define PyBobLearnMLP_APIVersion (*(PyBobLearnMLP_APIVersion_TYPE *)PyBobLearnMLP_API[PyBobLearnMLP_APIVersion_NUM])

  /***************************************
   * Bindings for bob.learn.mlp.Machine *
   ***************************************/

# define PyBobLearnMLPMachine_Type (*(PyBobLearnMLPMachine_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnMLPMachine_Type_NUM])

# define PyBobLearnMLPMachine_Check (*(PyBobLearnMLPMachine_Check_RET (*)PyBobLearnMLPMachine_Check_PROTO) PyBobLearnMLP_API[PyBobLearnMLPMachine_Check_NUM])

  /************************************
   * Bindings for bob.learn.mlp.Cost *
   ************************************/

# define PyBobLearnCost_Type (*(PyBobLearnCost_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnCost_Type_NUM])

# define PyBobLearnCost_Check (*(PyBobLearnCost_Check_RET (*)PyBobLearnCost_Check_PROTO) PyBobLearnMLP_API[PyBobLearnCost_Check_NUM])

# define PyBobLearnCost_NewFromCost (*(PyBobLearnCost_NewFromCost_RET (*)PyBobLearnCost_NewFromCost_PROTO) PyBobLearnMLP_API[PyBobLearnCost_NewFromCost_NUM])

# define PyBobLearnSquareError_Type (*(PyBobLearnSquareError_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnSquareError_Type_NUM])

# define PyBobLearnCrossEntropyLoss_Type (*(PyBobLearnCrossEntropyLoss_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnCrossEntropyLoss_Type_NUM])

  /********************************************
   * Bindings for bob.learn.mlp.DataShuffler *
   ********************************************/

# define PyBobLearnDataShuffler_Type (*(PyBobLearnDataShuffler_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnDataShuffler_Type_NUM])

# define PyBobLearnDataShuffler_Check (*(PyBobLearnDataShuffler_Check_RET (*)PyBobLearnDataShuffler_Check_PROTO) PyBobLearnMLP_API[PyBobLearnDataShuffler_Check_NUM])

  /***************************************
   * Bindings for bob.learn.mlp.Trainer *
   ***************************************/

# define PyBobLearnMLPTrainer_Type (*(PyBobLearnMLPTrainer_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnMLPTrainer_Type_NUM])

# define PyBobLearnMLPTrainer_Check (*(PyBobLearnMLPTrainer_Check_RET (*)PyBobLearnMLPTrainer_Check_PROTO) PyBobLearnMLP_API[PyBobLearnMLPTrainer_Check_NUM])

# define PyBobLearnMLPBackProp_Type (*(PyBobLearnMLPBackProp_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnMLPBackProp_Type_NUM])

# define PyBobLearnMLPBackProp_Check (*(PyBobLearnMLPBackProp_Check_RET (*)PyBobLearnMLPBackProp_Check_PROTO) PyBobLearnMLP_API[PyBobLearnMLPBackProp_Check_NUM])

# define PyBobLearnMLPRProp_Type (*(PyBobLearnMLPRProp_Type_TYPE *)PyBobLearnMLP_API[PyBobLearnMLPRProp_Type_NUM])

# define PyBobLearnMLPRProp_Check (*(PyBobLearnMLPRProp_Check_RET (*)PyBobLearnMLPRProp_Check_PROTO) PyBobLearnMLP_API[PyBobLearnMLPRProp_Check_NUM])

# if !defined(NO_IMPORT_ARRAY)

  /**
   * Returns -1 on error, 0 on success. PyCapsule_Import will set an exception
   * if there's an error.
   */
  static int import_bob_learn_mlp(void) {

    PyObject *c_api_object;
    PyObject *module;

    module = PyImport_ImportModule(BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_PREFIX) "." BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_NAME));

    if (module == NULL) return -1;

    c_api_object = PyObject_GetAttrString(module, "_C_API");

    if (c_api_object == NULL) {
      Py_DECREF(module);
      return -1;
    }

#   if PY_VERSION_HEX >= 0x02070000
    if (PyCapsule_CheckExact(c_api_object)) {
      PyBobLearnMLP_API = (void **)PyCapsule_GetPointer(c_api_object,
          PyCapsule_GetName(c_api_object));
    }
#   else
    if (PyCObject_Check(c_api_object)) {
      BobLearnMLP_API = (void **)PyCObject_AsVoidPtr(c_api_object);
    }
#   endif

    Py_DECREF(c_api_object);
    Py_DECREF(module);

    if (!BobLearnMLP_API) {
      PyErr_Format(PyExc_ImportError,
#   if PY_VERSION_HEX >= 0x02070000
          "cannot find C/C++ API capsule at `%s.%s._C_API'",
#   else
          "cannot find C/C++ API cobject at `%s.%s._C_API'",
#   endif
          BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_PREFIX),
          BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_NAME));
      return -1;
    }

    /* Checks that the imported version matches the compiled version */
    int imported_version = *(int*)PyBobLearnMLP_API[PyBobLearnMLP_APIVersion_NUM];

    if (BOB_LEARN_MLP_API_VERSION != imported_version) {
      PyErr_Format(PyExc_ImportError, "%s.%s import error: you compiled against API version 0x%04x, but are now importing an API with version 0x%04x which is not compatible - check your Python runtime environment for errors", BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_PREFIX), BOOST_PP_STRINGIZE(BOB_LEARN_MLP_MODULE_NAME), BOB_LEARN_MLP_API_VERSION, imported_version);
      return -1;
    }

    /* If you get to this point, all is good */
    return 0;

  }

# endif //!defined(NO_IMPORT_ARRAY)

#endif /* BOB_LEARN_MLP_MODULE */

#endif /* BOB_LEARN_MLP_H */
