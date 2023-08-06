/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 13 Dec 2013 12:35:59 CET
 *
 * @brief Bindings to bob::learn::mlp
 */

#define BOB_LEARN_MLP_MODULE
#include <bob.learn.mlp/api.h>

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>
#include <bob.learn.activation/api.h>
#include <bob.core/random_api.h>

PyDoc_STRVAR(s_unroll_str, "unroll");
PyDoc_STRVAR(s_unroll_doc,
"unroll(machine, [parameters]) -> parameters\n\
\n\
unroll(weights, biases, [parameters]) -> parameters\n\
\n\
Unroll the parameters (weights and biases) into a 64-bit float 1D array.\n\
\n\
This function will unroll the MLP machine weights and biases into a\n\
single 1D array of 64-bit floats. This procedure is useful for adapting\n\
generic optimization procedures for the task of training MLPs.\n\
\n\
Keyword parameters:\n\
\n\
machine, :py:class:`bob.learn.mlp.Machine`\n\
  An MLP that will have its weights and biases unrolled into a 1D array\n\
\n\
weights, sequence of 2D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  2D arrays of 64-bit floats representing the weights for the MLP you\n\
  wish to unroll.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
     \n\
     Other checks are disabled as this is considered an *expert* API.\n\
     If you plan to unroll the weights and biases on a\n\
     :py:class:`bob.learn.mlp.Machine`, notice that in a given\n\
     ``weights`` sequence, the number of outputs in layer ``k``\n\
     must match the number of inputs on layer ``k+1`` and the\n\
     number of biases on layer ``k``. In practice, you must assert\n\
     that ``weights[k].shape[1] == weights[k+1].shape[0]`` and.\n\
     that ``weights[k].shape[1] == bias[k].shape[0]``.\n\
\n\
biases, sequence of 1D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  1D arrays of 64-bit floats representing the biases for the MLP you\n\
  wish to unroll.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
\n\
parameters, 1D 64-bit float array\n\
  You may decide to pass the array in which the parameters will be\n\
  placed using this variable. In this case, the size of the vector\n\
  must match the total number of parameters available on the input\n\
  machine or discrete weights and biases. If you decided to omit\n\
  this parameter, then a vector with the appropriate size will be\n\
  allocated internally and returned.\n\
  \n\
  You can use py:func:`number_of_parameters` to calculate the total\n\
  length of the required ``parameters`` vector, in case you wish\n\
  to supply it.\n\
\n\
");

PyObject* unroll(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_roll_str, "roll");
PyDoc_STRVAR(s_roll_doc,
"roll(machine, parameters) -> parameters\n\
\n\
roll(weights, biases, parameters) -> parameters\n\
\n\
Roll the parameters (weights and biases) from a 64-bit float 1D array.\n\
\n\
This function will roll the MLP machine weights and biases from a\n\
single 1D array of 64-bit floats. This procedure is useful for adapting\n\
generic optimization procedures for the task of training MLPs.\n\
\n\
Keyword parameters:\n\
\n\
machine, :py:class:`bob.learn.mlp.Machine`\n\
  An MLP that will have its weights and biases rolled from a 1D array\n\
\n\
weights, sequence of 2D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  2D arrays of 64-bit floats representing the weights for the MLP you\n\
  wish to roll the parameters into using this argument.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
     \n\
     Other checks are disabled as this is considered an *expert* API.\n\
     If you plan to roll the weights and biases on a\n\
     :py:class:`bob.learn.mlp.Machine`, notice that in a given\n\
     ``weights`` sequence, the number of outputs in layer ``k``\n\
     must match the number of inputs on layer ``k+1`` and the\n\
     number of biases on layer ``k``. In practice, you must assert\n\
     that ``weights[k].shape[1] == weights[k+1].shape[0]`` and.\n\
     that ``weights[k].shape[1] == bias[k].shape[0]``.\n\
\n\
biases, sequence of 1D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  1D arrays of 64-bit floats representing the biases for the MLP you\n\
  wish to roll the parameters into.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
\n\
parameters, 1D 64-bit float array\n\
  You may decide to pass the array in which the parameters will be\n\
  placed using this variable. In this case, the size of the vector\n\
  must match the total number of parameters available on the input\n\
  machine or discrete weights and biases. If you decided to omit\n\
  this parameter, then a vector with the appropriate size will be\n\
  allocated internally and returned.\n\
  \n\
  You can use py:func:`number_of_parameters` to calculate the total\n\
  length of the required ``parameters`` vector, in case you wish\n\
  to supply it.\n\
\n\
");

PyObject* roll(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_number_of_parameters_str, "number_of_parameters");
PyDoc_STRVAR(s_number_of_parameters_doc,
"number_of_parameters(machine) -> scalar\n\
\n\
number_of_parameters(weights, biases) -> scalar\n\
\n\
Returns the total number of parameters in an MLP.\n\
\n\
Keyword parameters:\n\
\n\
machine, :py:class:`bob.learn.mlp.Machine`\n\
  Using the first call API, counts the total number of parameters in\n\
  an MLP.\n\
\n\
weights, sequence of 2D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  2D arrays of 64-bit floats representing the weights for the MLP you\n\
  wish to count the parameters from.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
     \n\
     Other checks are disabled as this is considered an *expert* API.\n\
     If you plan to unroll the weights and biases on a\n\
     :py:class:`bob.learn.mlp.Machine`, notice that in a given\n\
     ``weights`` sequence the number of outputs in layer ``k``\n\
     must match the number of inputs on layer ``k+1`` and the\n\
     number of bias on layer ``k``. In practice, you must assert\n\
     that ``weights[k].shape[1] == weights[k+1].shape[0]`` and.\n\
     that ``weights[k].shape[1] == bias[k].shape[0]``.\n\
\n\
biases, sequence of 1D 64-bit float arrays\n\
  If you choose the second calling strategy, then pass a sequence of\n\
  1D arrays of 64-bit floats representing the biases for the MLP you\n\
  wish to number_of_parameters the parameters into.\n\
  \n\
  .. note::\n\
     In this case, both this sequence and ``biases`` must have the\n\
     same length. This is the sole requirement.\n\
\n\
");

PyObject* number_of_parameters(PyObject*, PyObject* args, PyObject* kwds);

static PyMethodDef module_methods[] = {
  {
    s_unroll_str,
    (PyCFunction)unroll,
    METH_VARARGS|METH_KEYWORDS,
    s_unroll_doc
  },
  {
    s_roll_str,
    (PyCFunction)roll,
    METH_VARARGS|METH_KEYWORDS,
    s_roll_doc
  },
  {
    s_number_of_parameters_str,
    (PyCFunction)number_of_parameters,
    METH_VARARGS|METH_KEYWORDS,
    s_number_of_parameters_doc
  },
  {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "bob's multi-layer perceptron machine and trainers");

int PyBobLearnMLP_APIVersion = BOB_LEARN_MLP_API_VERSION;

#if PY_VERSION_HEX >= 0x03000000
static PyModuleDef module_definition = {
  PyModuleDef_HEAD_INIT,
  BOB_EXT_MODULE_NAME,
  module_docstr,
  -1,
  module_methods,
  0, 0, 0, 0
};
#endif

static PyObject* create_module (void) {

  PyBobLearnMLPMachine_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnMLPMachine_Type) < 0) return 0;

  PyBobLearnCost_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnCost_Type) < 0) return 0;

  PyBobLearnSquareError_Type.tp_base = &PyBobLearnCost_Type;
  if (PyType_Ready(&PyBobLearnSquareError_Type) < 0) return 0;

  PyBobLearnCrossEntropyLoss_Type.tp_base = &PyBobLearnCost_Type;
  if (PyType_Ready(&PyBobLearnCrossEntropyLoss_Type) < 0) return 0;

  PyBobLearnDataShuffler_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnDataShuffler_Type) < 0) return 0;

  PyBobLearnMLPTrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnMLPTrainer_Type) < 0) return 0;

  PyBobLearnMLPBackProp_Type.tp_base = &PyBobLearnMLPTrainer_Type;
  if (PyType_Ready(&PyBobLearnMLPBackProp_Type) < 0) return 0;

  PyBobLearnMLPRProp_Type.tp_base = &PyBobLearnMLPTrainer_Type;
  if (PyType_Ready(&PyBobLearnMLPRProp_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m);

  /* register some constants */
  if (PyModule_AddIntConstant(m, "__api_version__", BOB_LEARN_MLP_API_VERSION) < 0) return 0;
  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0) return 0;

  /* register the types to python */
  Py_INCREF(&PyBobLearnMLPMachine_Type);
  if (PyModule_AddObject(m, "Machine", (PyObject *)&PyBobLearnMLPMachine_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnCost_Type);
  if (PyModule_AddObject(m, "Cost", (PyObject *)&PyBobLearnCost_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnSquareError_Type);
  if (PyModule_AddObject(m, "SquareError", (PyObject *)&PyBobLearnSquareError_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnCrossEntropyLoss_Type);
  if (PyModule_AddObject(m, "CrossEntropyLoss", (PyObject *)&PyBobLearnCrossEntropyLoss_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnDataShuffler_Type);
  if (PyModule_AddObject(m, "DataShuffler", (PyObject *)&PyBobLearnDataShuffler_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnMLPTrainer_Type);
  if (PyModule_AddObject(m, "Trainer", (PyObject *)&PyBobLearnMLPTrainer_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnMLPBackProp_Type);
  if (PyModule_AddObject(m, "BackProp", (PyObject *)&PyBobLearnMLPBackProp_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnMLPRProp_Type);
  if (PyModule_AddObject(m, "RProp", (PyObject *)&PyBobLearnMLPRProp_Type) < 0) return 0;

  static void* PyBobLearnMLP_API[PyBobLearnMLP_API_pointers];

  /* exhaustive list of C APIs */

  /**************
   * Versioning *
   **************/

  PyBobLearnMLP_API[PyBobLearnMLP_APIVersion_NUM] = (void *)&PyBobLearnMLP_APIVersion;

  /***************************************
   * Bindings for bob.learn.mlp.Machine *
   ***************************************/

  PyBobLearnMLP_API[PyBobLearnMLPMachine_Type_NUM] = (void *)&PyBobLearnMLPMachine_Type;

  PyBobLearnMLP_API[PyBobLearnMLPMachine_Check_NUM] = (void *)&PyBobLearnMLPMachine_Check;

  /************************************
   * Bindings for bob.learn.mlp.Cost *
   ************************************/

  PyBobLearnMLP_API[PyBobLearnCost_Type_NUM] = (void *)&PyBobLearnCost_Type;

  PyBobLearnMLP_API[PyBobLearnCost_Check_NUM] = (void *)&PyBobLearnCost_Check;

  PyBobLearnMLP_API[PyBobLearnCost_NewFromCost_NUM] = (void *)&PyBobLearnCost_NewFromCost;

  PyBobLearnMLP_API[PyBobLearnSquareError_Type_NUM] = (void *)&PyBobLearnSquareError_Type;

  PyBobLearnMLP_API[PyBobLearnCrossEntropyLoss_Type_NUM] = (void *)&PyBobLearnCrossEntropyLoss_Type;

  /********************************************
   * Bindings for bob.learn.mlp.DataShuffler *
   ********************************************/

  PyBobLearnMLP_API[PyBobLearnDataShuffler_Type_NUM] = (void *)&PyBobLearnDataShuffler_Type;

  PyBobLearnMLP_API[PyBobLearnDataShuffler_Check_NUM] = (void *)&PyBobLearnDataShuffler_Check;

  /***************************************
   * Bindings for bob.learn.mlp.Trainer *
   ***************************************/

  PyBobLearnMLP_API[PyBobLearnMLPTrainer_Type_NUM] = (void *)&PyBobLearnMLPTrainer_Type;

  PyBobLearnMLP_API[PyBobLearnMLPTrainer_Check_NUM] = (void *)&PyBobLearnMLPTrainer_Check;

  PyBobLearnMLP_API[PyBobLearnMLPBackProp_Type_NUM] = (void *)&PyBobLearnMLPBackProp_Type;

  PyBobLearnMLP_API[PyBobLearnMLPBackProp_Check_NUM] = (void *)&PyBobLearnMLPBackProp_Check;

  PyBobLearnMLP_API[PyBobLearnMLPRProp_Type_NUM] = (void *)&PyBobLearnMLPRProp_Type;

  PyBobLearnMLP_API[PyBobLearnMLPRProp_Check_NUM] = (void *)&PyBobLearnMLPRProp_Check;

#if PY_VERSION_HEX >= 0x02070000

  /* defines the PyCapsule */

  PyObject* c_api_object = PyCapsule_New((void *)PyBobLearnMLP_API,
      BOB_EXT_MODULE_PREFIX "." BOB_EXT_MODULE_NAME "._C_API", 0);

#else

  PyObject* c_api_object = PyCObject_FromVoidPtr((void *)PyBobLearnMLP_API, 0);

#endif

  if (c_api_object) PyModule_AddObject(m, "_C_API", c_api_object);

  /* imports dependencies */
  if (import_bob_blitz() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  if (import_bob_io_base() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  if (import_bob_learn_activation() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  if (import_bob_core_random() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  return Py_BuildValue("O", m);

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
