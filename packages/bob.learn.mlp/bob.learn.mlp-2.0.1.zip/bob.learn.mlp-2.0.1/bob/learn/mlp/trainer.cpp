/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue  6 May 12:32:39 2014 CEST
 *
 * @brief Bindings for an MLP
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_MLP_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.learn.mlp/api.h>
#include <structmember.h>

#include "utils.h"

/****************************************
 * Implementation of base Trainer class *
 ****************************************/

PyDoc_STRVAR(s_trainer_str, BOB_EXT_MODULE_PREFIX ".Trainer");

PyDoc_STRVAR(s_trainer_doc,
"Trainer(batch_size, cost, [trainer, [train_biases]]) -> new Trainer\n\
\n\
Trainer(other) -> new Trainer\n\
\n\
The base python class for MLP trainers based on cost derivatives.\n\
\n\
You should use this class when you want to create your own MLP\n\
trainers and re-use the base infrastructured provided by this\n\
module, such as the computation of partial derivatives (using\n\
the :py:meth:`backward_step` method).\n\
\n\
To create a new trainer, either pass the batch-size, cost functor,\n\
machine and a biases-training flag or another trainer you'd like\n\
the parameters copied from.\n\
\n\
Keyword parameters:\n\
\n\
batch_size, int\n\
   The size of each batch used for the forward and backward steps.\n\
   If you set this to ``1``, then you are implementing stochastic\n\
   training.\n\
   \n\
   .. note::\n\
   \n\
      This setting affects the convergence.\n\
\n\
cost, :py:class:`bob.learn.mlp.Cost`\n\
   An object that can calculate the cost at every iteration.\n\
\n\
machine, :py:class:`bob.learn.mlp.Machine`\n\
   This parameter that will be used as a basis for this trainer's\n\
   internal properties (cache sizes, for instance).\n\
\n\
train_biases, bool\n\
   A boolean indicating if we should train the biases weights (set\n\
   it to ``True``) or not (set it to ``False``).\n\
\n\
other, :py:class:`bob.learn.mlp.Trainer`\n\
   Another trainer from which this new copy will get its properties\n\
   from. If you use this constructor than a new (deep) copy of the\n\
   trainer is created.\n\
\n\
");

static int PyBobLearnMLPTrainer_init_discrete
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {
    "batch_size",
    "cost",
    "machine",
    "train_biases",
    0
  };
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t batch_size = 0;
  PyBobLearnCostObject* cost = 0;
  PyBobLearnMLPMachineObject* machine = 0;
  PyObject* train_biases = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "nO!|O!O", kwlist,
        &batch_size,
        &PyBobLearnCost_Type, &cost,
        &PyBobLearnMLPMachine_Type, &machine,
        &train_biases)) return -1;

  try {
    if (machine && train_biases) {
      self->cxx = new bob::learn::mlp::Trainer(batch_size, cost->cxx,
          *machine->cxx, PyObject_IsTrue(train_biases));
    }
    else if (machine) {
      self->cxx = new bob::learn::mlp::Trainer(batch_size, cost->cxx,
          *machine->cxx);
    }
    else if (train_biases) {
      PyErr_Format(PyExc_RuntimeError, "cannot provide a flag for `train_biases' and do not provide a `machine' upon initialisation of type `%s'", Py_TYPE(self)->tp_name);
      return -1;
    }
    else {
      self->cxx = new bob::learn::mlp::Trainer(batch_size, cost->cxx);
    }
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

static int PyBobLearnMLPTrainer_init_copy
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnMLPTrainer_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobLearnMLPTrainerObject*>(other);

  try {
    self->cxx = new bob::learn::mlp::Trainer(*(copy->cxx));
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

static int PyBobLearnMLPTrainer_init(PyBobLearnMLPTrainerObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:

      return PyBobLearnMLPTrainer_init_copy(self, args, kwds);

    default:

      return PyBobLearnMLPTrainer_init_discrete(self, args, kwds);
  }

  return -1;

}

static void PyBobLearnMLPTrainer_delete
(PyBobLearnMLPTrainerObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

int PyBobLearnMLPTrainer_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnMLPTrainer_Type));
}

static PyObject* PyBobLearnMLPTrainer_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnMLPTrainerObject* self = (PyBobLearnMLPTrainerObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyDoc_STRVAR(s_batch_size_str, "batch_size");
PyDoc_STRVAR(s_batch_size_doc,
"How many examples should be fed each time through the network\n\
for testing or training. This number reflects the internal sizes\n\
of structures setup to accomodate the input and the output of\n\
the network.");

static PyObject* PyBobLearnMLPTrainer_getBatchSize
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getBatchSize());
}

static int PyBobLearnMLPTrainer_setBatchSize
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  Py_ssize_t value = PyNumber_AsSsize_t(o, PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;
  self->cxx->setBatchSize(value);
  return 0;

}

PyDoc_STRVAR(s_cost_object_str, "cost_object");
PyDoc_STRVAR(s_cost_object_doc,
"An object, derived from :py:class:`bob.learn.mlp.Cost` (e.g.\n\
:py:class:`bob.learn.mlp.SquareError` or \n\
:py:class:`bob.learn.mlp.CrossEntropyLoss`), that is used to evaluate\n\
the cost (a.k.a. *loss*) and the derivatives given the input, the\n\
target and the MLP structure.");

static PyObject* PyBobLearnMLPTrainer_getCostObject
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return PyBobLearnCost_NewFromCost(self->cxx->getCost());
}

static int PyBobLearnMLPTrainer_setCostObject
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBobLearnCost_Check(o)) {
    PyErr_Format(PyExc_TypeError, "%s.cost requires an object of type `Cost' (or an inherited type), not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  auto py = reinterpret_cast<PyBobLearnCostObject*>(o);
  self->cxx->setCost(py->cxx);
  return 0;

}

PyDoc_STRVAR(s_train_biases_str, "train_biases");
PyDoc_STRVAR(s_train_biases_doc,
"A flag, indicating if this trainer will adjust the biases\n\
of the network");

static PyObject* PyBobLearnMLPTrainer_getTrainBiases
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  if (self->cxx->getTrainBiases()) Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

static int PyBobLearnMLPTrainer_setTrainBiases
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {
  self->cxx->setTrainBiases(PyObject_IsTrue(o));
  return -1;
}

PyDoc_STRVAR(s_error_str, "error");
PyDoc_STRVAR(s_error_doc,
"The error (a.k.a. :math:`\\delta`'s) back-propagated through the\n\
network, given an input and a target.");

static PyObject* PyBobLearnMLPTrainer_getError
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getError());
}

static int PyBobLearnMLPTrainer_setError
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,2>> bzvec;
  int retval = convert_tuple<2>(Py_TYPE(self)->tp_name, s_error_str, o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setError(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_error_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_output_str, "output");
PyDoc_STRVAR(s_output_doc,
"The outputs of each neuron in the network");

static PyObject* PyBobLearnMLPTrainer_getOutput
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getOutput());
}

static int PyBobLearnMLPTrainer_setOutput
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,2>> bzvec;
  int retval = convert_tuple<2>(Py_TYPE(self)->tp_name, s_output_str, o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setOutput(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_output_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_derivatives_str, "derivatives");
PyDoc_STRVAR(s_derivatives_doc,
"The calculated derivatives of the cost w.r.t. to the specific\n\
**weights** of the network, organized to match the organization\n\
of weights of the machine being trained.");

static PyObject* PyBobLearnMLPTrainer_getDerivatives
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getDerivatives());
}

static int PyBobLearnMLPTrainer_setDerivatives
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,2>> bzvec;
  int retval = convert_tuple<2>(Py_TYPE(self)->tp_name, s_derivatives_str, o,
      bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setDerivatives(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_derivatives_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_bias_derivatives_str, "bias_derivatives");
PyDoc_STRVAR(s_bias_derivatives_doc,
"The calculated derivatives of the cost w.r.t. to the specific\n\
**biases** of the network, organized to match the organization\n\
of biases of the machine being trained.");

static PyObject* PyBobLearnMLPTrainer_getBiasDerivatives
(PyBobLearnMLPTrainerObject* self, void* /*closure*/) {
  return convert_vector<1>(self->cxx->getBiasDerivatives());
}

static int PyBobLearnMLPTrainer_setBiasDerivatives
(PyBobLearnMLPTrainerObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,1>> bzvec;
  int retval = convert_tuple<1>(Py_TYPE(self)->tp_name, s_bias_derivatives_str,
      o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setBiasDerivatives(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_bias_derivatives_str);
    return -1;
  }

  return 0;

}

static PyGetSetDef PyBobLearnMLPTrainer_getseters[] = {
    {
      s_batch_size_str,
      (getter)PyBobLearnMLPTrainer_getBatchSize,
      (setter)PyBobLearnMLPTrainer_setBatchSize,
      s_batch_size_doc,
      0
    },
    {
      s_cost_object_str,
      (getter)PyBobLearnMLPTrainer_getCostObject,
      (setter)PyBobLearnMLPTrainer_setCostObject,
      s_cost_object_doc,
      0
    },
    {
      s_train_biases_str,
      (getter)PyBobLearnMLPTrainer_getTrainBiases,
      (setter)PyBobLearnMLPTrainer_setTrainBiases,
      s_train_biases_doc,
      0
    },
    {
      s_error_str,
      (getter)PyBobLearnMLPTrainer_getError,
      (setter)PyBobLearnMLPTrainer_setError,
      s_error_doc,
      0
    },
    {
      s_output_str,
      (getter)PyBobLearnMLPTrainer_getOutput,
      (setter)PyBobLearnMLPTrainer_setOutput,
      s_output_doc,
      0
    },
    {
      s_derivatives_str,
      (getter)PyBobLearnMLPTrainer_getDerivatives,
      (setter)PyBobLearnMLPTrainer_setDerivatives,
      s_derivatives_doc,
      0
    },
    {
      s_bias_derivatives_str,
      (getter)PyBobLearnMLPTrainer_getBiasDerivatives,
      (setter)PyBobLearnMLPTrainer_setBiasDerivatives,
      s_bias_derivatives_doc,
      0
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(s_is_compatible_str, "is_compatible");
PyDoc_STRVAR(s_is_compatible_doc, "Checks if a given machine is compatible with inner settings");

static PyObject* PyBobLearnMLPTrainer_isCompatible
(PyBobLearnMLPTrainerObject* self, PyObject* o) {

  if (!PyBobLearnMLPMachine_Check(o)) {
    PyErr_Format(PyExc_TypeError, "`%s.%s()' requires a `%s' as input, not `%s'",
        Py_TYPE(self)->tp_name, s_is_compatible_str,
        PyBobLearnMLPMachine_Type.tp_name, Py_TYPE(o)->tp_name);
    return 0;
  }

  auto machine = reinterpret_cast<PyBobLearnMLPMachineObject*>(o);

  if (self->cxx->isCompatible(*machine->cxx)) Py_RETURN_TRUE;
  Py_RETURN_FALSE;

}

PyDoc_STRVAR(s_initialize_str, "initialize");
PyDoc_STRVAR(s_initialize_doc, "Initialize the trainer with the given machine");

static PyObject* PyBobLearnMLPTrainer_initialize
(PyBobLearnMLPTrainerObject* self, PyObject* o) {

  if (!PyBobLearnMLPMachine_Check(o)) {
    PyErr_Format(PyExc_TypeError, "`%s.%s()' requires a `%s' as input, not `%s'",
        Py_TYPE(self)->tp_name, s_initialize_str,
        PyBobLearnMLPMachine_Type.tp_name, Py_TYPE(o)->tp_name);
    return 0;
  }

  auto machine = reinterpret_cast<PyBobLearnMLPMachineObject*>(o);

  try {
    self->cxx->initialize(*machine->cxx);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot initialize `%s': unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_forward_step_str, "forward_step");
PyDoc_STRVAR(s_forward_step_doc, "Forwards a batch of data through the MLP and updates the internal buffers.");

static PyObject* PyBobLearnMLPTrainer_forwardStep
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"machine", "input", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBobLearnMLPMachineObject* machine = 0;
  PyBlitzArrayObject* input = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O&", kwlist,
        &PyBobLearnMLPMachine_Type, &machine,
        &PyBlitzArray_Converter, &input)) return 0;

  if (input->type_num != NPY_FLOAT64 || input->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  try {
    self->cxx->forward_step(*machine->cxx, *PyBlitzArrayCxx_AsBlitz<double,2>(input));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot perform forward-step for `%s': unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_backward_step_str, "backward_step");
PyDoc_STRVAR(s_backward_step_doc,
"Backwards a batch of data through the MLP and updates the\n\
internal buffers (errors and derivatives).");

static PyObject* PyBobLearnMLPTrainer_backwardStep
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"machine", "input", "target", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBobLearnMLPMachineObject* machine = 0;
  PyBlitzArrayObject* input = 0;
  PyBlitzArrayObject* target = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O&O&", kwlist,
        &PyBobLearnMLPMachine_Type, &machine,
        &PyBlitzArray_Converter, &input,
        &PyBlitzArray_Converter, &target)) return 0;

  if (input->type_num != NPY_FLOAT64 || input->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (target->type_num != NPY_FLOAT64 || target->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `target'", Py_TYPE(self)->tp_name);
    return 0;
  }

  try {
    self->cxx->backward_step(*machine->cxx,
        *PyBlitzArrayCxx_AsBlitz<double,2>(input),
        *PyBlitzArrayCxx_AsBlitz<double,2>(target)
        );
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot perform backward-step for `%s': unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_cost_str, "cost");
PyDoc_STRVAR(s_cost_doc,
"o.cost(target) -> float\n\
\n\
o.cost(machine, input, target) -> float\n\
\n\
Calculates the cost for a given target.\n\
\n\
The cost for a given target is defined as the sum of individual\n\
costs for every output in the current network, averaged over all\n\
the examples.\n\
\n\
You can use this function in two ways. Either by initially calling\n\
:py:meth:`forward_step` passing ``machine`` and ``input`` and then\n\
calling this method with just the ``target`` or passing all three\n\
objects in a single call. With the latter strategy, the\n\
:py:meth:`forward_step` will be called internally.\n\
\n\
This function returns a single scalar, of ``float`` type,\n\
representing the average cost for all input given the expected\n\
target.\n\
");

static PyObject* PyBobLearnMLPTrainer_cost
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  PyBobLearnMLPMachineObject* machine = 0;
  PyBlitzArrayObject* input = 0;
  PyBlitzArrayObject* target = 0;

  if (nargs == 1) {
    static const char* const_kwlist[] = {"target", 0};
    static char** kwlist = const_cast<char**>(const_kwlist);
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist,
          &PyBlitzArray_Converter, &target)) return 0;
  }
  else { //there must be three
    static const char* const_kwlist[] = {"machine", "input", "target", 0};
    static char** kwlist = const_cast<char**>(const_kwlist);
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O&O&", kwlist,
          &PyBobLearnMLPMachine_Type, &machine,
          &PyBlitzArray_Converter, &input,
          &PyBlitzArray_Converter, &target)) return 0;
  }

  /* Parses input arguments in a single shot */

  if ((machine && !input) || (input && !machine)) {
    PyErr_Format(PyExc_RuntimeError, "`%s.%s' expects that you either provide only the target (after a call to `forward_step') with a given machine and input or target, machine *and* input. You cannot provide a machine and not an input or vice-versa", Py_TYPE(self)->tp_name, s_cost_str);
    return 0;
  }

  if (input && (input->type_num != NPY_FLOAT64 || input->ndim != 2)) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `input' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_cost_str, input->ndim, PyBlitzArray_TypenumAsString(input->type_num));
    return 0;
  }

  if (target->type_num != NPY_FLOAT64 || target->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `target' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your target", Py_TYPE(self)->tp_name, s_cost_str, target->ndim, PyBlitzArray_TypenumAsString(target->type_num));
    return 0;
  }

  try {
    if (machine) {
      return Py_BuildValue("d", self->cxx->cost(*machine->cxx,
            *PyBlitzArrayCxx_AsBlitz<double,2>(input),
            *PyBlitzArrayCxx_AsBlitz<double,2>(target)));
    }
    else {
      return Py_BuildValue("d",
          self->cxx->cost(*PyBlitzArrayCxx_AsBlitz<double,2>(target)));
    }
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot estimate cost for `%s': unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  PyErr_Format(PyExc_RuntimeError, " `%s': unexpected condition - DEBUG ME", Py_TYPE(self)->tp_name);
  return 0;

}

PyDoc_STRVAR(s_hidden_layers_str, "hidden_layers");
PyDoc_STRVAR(s_hidden_layers_doc,
    "The number of hidden layers on the target machine.");

static PyObject* PyBobLearnMLPTrainer_hiddenLayers
(PyBobLearnMLPTrainerObject* self) {
  return Py_BuildValue("n", self->cxx->numberOfHiddenLayers());
}

PyDoc_STRVAR(s_set_error_str, "set_error");
PyDoc_STRVAR(s_set_error_doc, "Sets the error for a given layer in the network.");

static PyObject* PyBobLearnMLPTrainer_setErrorOnLayer
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_error_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setError(*PyBlitzArrayCxx_AsBlitz<double,2>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set error at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_output_str, "set_output");
PyDoc_STRVAR(s_set_output_doc, "Sets the output for a given layer in the network.");

static PyObject* PyBobLearnMLPTrainer_setOutputOnLayer
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_output_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setOutput(*PyBlitzArrayCxx_AsBlitz<double,2>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set output at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_derivative_str, "set_derivative");
PyDoc_STRVAR(s_set_derivative_doc,
    "Sets the cost derivative w.r.t. the **weights** for a given layer.");

static PyObject* PyBobLearnMLPTrainer_setDerivativeOnLayer
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_derivative_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setDerivative(*PyBlitzArrayCxx_AsBlitz<double,2>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set derivative at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_bias_derivative_str, "set_bias_derivative");
PyDoc_STRVAR(s_set_bias_derivative_doc,
    "Sets the cost derivative w.r.t. the **biases** for a given layer.");

static PyObject* PyBobLearnMLPTrainer_setBiasDerivativeOnLayer
(PyBobLearnMLPTrainerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 1D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_bias_derivative_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setBiasDerivative(*PyBlitzArrayCxx_AsBlitz<double,1>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set bias derivative at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

static PyMethodDef PyBobLearnMLPTrainer_methods[] = {
  {
    s_is_compatible_str,
    (PyCFunction)PyBobLearnMLPTrainer_isCompatible,
    METH_O,
    s_is_compatible_doc,
  },
  {
    s_initialize_str,
    (PyCFunction)PyBobLearnMLPTrainer_initialize,
    METH_O,
    s_initialize_doc,
  },
  {
    s_forward_step_str,
    (PyCFunction)PyBobLearnMLPTrainer_forwardStep,
    METH_VARARGS|METH_KEYWORDS,
    s_forward_step_doc,
  },
  {
    s_backward_step_str,
    (PyCFunction)PyBobLearnMLPTrainer_backwardStep,
    METH_VARARGS|METH_KEYWORDS,
    s_backward_step_doc,
  },
  {
    s_cost_str,
    (PyCFunction)PyBobLearnMLPTrainer_cost,
    METH_VARARGS|METH_KEYWORDS,
    s_cost_doc,
  },
  {
    s_hidden_layers_str,
    (PyCFunction)PyBobLearnMLPTrainer_hiddenLayers,
    METH_NOARGS,
    s_hidden_layers_doc,
  },
  {
    s_set_error_str,
    (PyCFunction)PyBobLearnMLPTrainer_setErrorOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_error_doc,
  },
  {
    s_set_output_str,
    (PyCFunction)PyBobLearnMLPTrainer_setOutputOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_output_doc,
  },
  {
    s_set_derivative_str,
    (PyCFunction)PyBobLearnMLPTrainer_setDerivativeOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_derivative_doc,
  },
  {
    s_set_bias_derivative_str,
    (PyCFunction)PyBobLearnMLPTrainer_setBiasDerivativeOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_bias_derivative_doc,
  },
  {0} /* Sentinel */
};

PyTypeObject PyBobLearnMLPTrainer_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_trainer_str,                                 /* tp_name */
    sizeof(PyBobLearnMLPTrainerObject),            /* tp_basicsize */
    0,                                             /* tp_itemsize */
    (destructor)PyBobLearnMLPTrainer_delete,       /* tp_dealloc */
    0,                                             /* tp_print */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_compare */
    0, //(reprfunc)PyBobLearnMLPTrainer_Repr,           /* tp_repr */
    0,                                             /* tp_as_number */
    0,                                             /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    0,                                             /* tp_call */
    0, //(reprfunc)PyBobLearnMLPTrainer_Repr,           /* tp_str */
    0,                                             /* tp_getattro */
    0,                                             /* tp_setattro */
    0,                                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,      /* tp_flags */
    s_trainer_doc,                                 /* tp_doc */
    0,                                             /* tp_traverse */
    0,                                             /* tp_clear */
    0,                                             /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    0,                                             /* tp_iter */
    0,                                             /* tp_iternext */
    PyBobLearnMLPTrainer_methods,                  /* tp_methods */
    0,                                             /* tp_members */
    PyBobLearnMLPTrainer_getseters,                /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)PyBobLearnMLPTrainer_init,           /* tp_init */
    0,                                             /* tp_alloc */
    PyBobLearnMLPTrainer_new,                      /* tp_new */
};
