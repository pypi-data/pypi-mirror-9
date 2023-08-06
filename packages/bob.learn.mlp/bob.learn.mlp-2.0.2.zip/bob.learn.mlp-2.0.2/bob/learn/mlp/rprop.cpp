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

/**************************************
 * Implementation of RProp trainer *
 **************************************/

PyDoc_STRVAR(s_trainer_str, BOB_EXT_MODULE_PREFIX ".RProp");

PyDoc_STRVAR(s_trainer_doc,
"RProp(batch_size, cost, [trainer, [train_biases]]) -> new RProp\n\
\n\
RProp(other) -> new RProp\n\
\n\
Sets an MLP to perform discrimination based on *RProp: A Direct\n\
Adaptive Method for Faster Backpropagation Learning: The RPROP\n\
Algorithm, by Martin Riedmiller and Heinrich Braun on IEEE\n\
International Conference on Neural Networks, pp. 586--591, 1993.*\n\
\n\
To create a new trainer, either pass the batch-size, cost functor,\n\
machine and a biases-training flag or another trainer you'd like\n\
the parameters copied from.\n\
\n\
.. note::\n\
   \n\
   RProp **is** a \"batch\" training algorithm. Do not try to set\n\
   batch_size to a value which is too low.\n\
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

static int PyBobLearnMLPRProp_init_discrete
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

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
      self->cxx = new bob::learn::mlp::RProp(batch_size, cost->cxx,
          *machine->cxx, PyObject_IsTrue(train_biases));
    }
    else if (machine) {
      self->cxx = new bob::learn::mlp::RProp(batch_size, cost->cxx,
          *machine->cxx);
    }
    else if (train_biases) {
      PyErr_Format(PyExc_RuntimeError, "cannot provide a flag for `train_biases' and do not provide a `machine' upon initialisation of type `%s'", Py_TYPE(self)->tp_name);
      return -1;
    }
    else {
      self->cxx = new bob::learn::mlp::RProp(batch_size, cost->cxx);
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

  self->parent.cxx = self->cxx;

  return 0;

}

static int PyBobLearnMLPRProp_init_copy
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnMLPRProp_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobLearnMLPRPropObject*>(other);

  try {
    self->cxx = new bob::learn::mlp::RProp(*(copy->cxx));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return -1;
  }

  self->parent.cxx = self->cxx;

  return 0;

}

static int PyBobLearnMLPRProp_init(PyBobLearnMLPRPropObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:

      return PyBobLearnMLPRProp_init_copy(self, args, kwds);

    default:

      return PyBobLearnMLPRProp_init_discrete(self, args, kwds);
  }

  return -1;

}

static void PyBobLearnMLPRProp_delete
(PyBobLearnMLPRPropObject* self) {

  self->parent.cxx = 0;
  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

int PyBobLearnMLPRProp_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnMLPRProp_Type));
}

static PyObject* PyBobLearnMLPRProp_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnMLPRPropObject* self = (PyBobLearnMLPRPropObject*)type->tp_alloc(type, 0);

  self->cxx = 0;
  self->parent.cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyDoc_STRVAR(s_eta_minus_str, "eta_minus");
PyDoc_STRVAR(s_eta_minus_doc,
"Learning de-enforcement parameter (defaults to ``0.5``)"
);

static PyObject* PyBobLearnMLPRProp_getEtaMinus
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getEtaMinus());
}

static int PyBobLearnMLPRProp_setEtaMinus
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setEtaMinus(value);
  return 0;

}

PyDoc_STRVAR(s_eta_plus_str, "eta_plus");
PyDoc_STRVAR(s_eta_plus_doc,
"Learning enforcement parameter (defaults to ``1.2``)"
);

static PyObject* PyBobLearnMLPRProp_getEtaPlus
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getEtaPlus());
}

static int PyBobLearnMLPRProp_setEtaPlus
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setEtaPlus(value);
  return 0;

}

PyDoc_STRVAR(s_delta_zero_str, "delta_zero");
PyDoc_STRVAR(s_delta_zero_doc,
"Initial weight update (defaults to ``0.1``)"
);

static PyObject* PyBobLearnMLPRProp_getDeltaZero
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getDeltaZero());
}

static int PyBobLearnMLPRProp_setDeltaZero
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setDeltaZero(value);
  return 0;

}

PyDoc_STRVAR(s_delta_min_str, "delta_min");
PyDoc_STRVAR(s_delta_min_doc,
"Minimal weight update (defaults to :math:`10^{-6}`)"
);

static PyObject* PyBobLearnMLPRProp_getDeltaMin
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getDeltaMin());
}

static int PyBobLearnMLPRProp_setDeltaMin
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setDeltaMin(value);
  return 0;

}

PyDoc_STRVAR(s_delta_max_str, "delta_max");
PyDoc_STRVAR(s_delta_max_doc,
"Maximal weight update (defaults to ``50.0``)"
);

static PyObject* PyBobLearnMLPRProp_getDeltaMax
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getDeltaMax());
}

static int PyBobLearnMLPRProp_setDeltaMax
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setDeltaMax(value);
  return 0;

}

PyDoc_STRVAR(s_previous_derivatives_str, "previous_derivatives");
PyDoc_STRVAR(s_previous_derivatives_doc,
"The derivatives of the cost w.r.t. to the specific\n\
**weights** of the network, from the previous training step.\n\
The derivatives are arranged to match the organization\n\
of weights of the machine being trained.");

static PyObject* PyBobLearnMLPRProp_getPreviousDerivatives
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getPreviousDerivatives());
}

static int PyBobLearnMLPRProp_setPreviousDerivatives
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,2>> bzvec;
  int retval = convert_tuple<2>(Py_TYPE(self)->tp_name,
      s_previous_derivatives_str, o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setPreviousDerivatives(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_previous_derivatives_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_previous_bias_derivatives_str, "previous_bias_derivatives");
PyDoc_STRVAR(s_previous_bias_derivatives_doc,
"The derivatives of the cost w.r.t. to the specific\n\
**biases** of the network, from the previous training step.\n\
The derivatives are arranged to match the organization\n\
of weights of the machine being trained.");

static PyObject* PyBobLearnMLPRProp_getPreviousBiasDerivatives
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return convert_vector<1>(self->cxx->getPreviousBiasDerivatives());
}

static int PyBobLearnMLPRProp_setPreviousBiasDerivatives
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,1>> bzvec;
  int retval = convert_tuple<1>(Py_TYPE(self)->tp_name,
      s_previous_bias_derivatives_str, o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setPreviousBiasDerivatives(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_previous_bias_derivatives_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_deltas_str, "deltas");
PyDoc_STRVAR(s_deltas_doc,
"Current settings for the weight update (:math:`\\Delta_{ij}(t)`)");

static PyObject* PyBobLearnMLPRProp_getDeltas
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getDeltas());
}

static int PyBobLearnMLPRProp_setDeltas
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,2>> bzvec;
  int retval = convert_tuple<2>(Py_TYPE(self)->tp_name, s_deltas_str, o, bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setDeltas(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_deltas_str);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_bias_deltas_str, "bias_deltas");
PyDoc_STRVAR(s_bias_deltas_doc,
"Current settings for the bias update (:math:`\\Delta_{ij}(t)`)");

static PyObject* PyBobLearnMLPRProp_getBiasDeltas
(PyBobLearnMLPRPropObject* self, void* /*closure*/) {
  return convert_vector<1>(self->cxx->getBiasDeltas());
}

static int PyBobLearnMLPRProp_setBiasDeltas
(PyBobLearnMLPRPropObject* self, PyObject* o, void* /*closure*/) {

  std::vector<blitz::Array<double,1>> bzvec;
  int retval = convert_tuple<1>(Py_TYPE(self)->tp_name, s_bias_deltas_str, o,
      bzvec);
  if (retval < 0) return retval;

  try {
    self->cxx->setBiasDeltas(bzvec);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `%s' of %s: unknown exception caught", Py_TYPE(self)->tp_name, s_bias_deltas_str);
    return -1;
  }

  return 0;

}

static PyGetSetDef PyBobLearnMLPRProp_getseters[] = {
    {
      s_eta_minus_str,
      (getter)PyBobLearnMLPRProp_getEtaMinus,
      (setter)PyBobLearnMLPRProp_setEtaMinus,
      s_eta_minus_doc,
      0
    },
    {
      s_eta_plus_str,
      (getter)PyBobLearnMLPRProp_getEtaPlus,
      (setter)PyBobLearnMLPRProp_setEtaPlus,
      s_eta_plus_doc,
      0
    },
    {
      s_delta_zero_str,
      (getter)PyBobLearnMLPRProp_getDeltaZero,
      (setter)PyBobLearnMLPRProp_setDeltaZero,
      s_delta_zero_doc,
      0
    },
    {
      s_delta_min_str,
      (getter)PyBobLearnMLPRProp_getDeltaMin,
      (setter)PyBobLearnMLPRProp_setDeltaMin,
      s_delta_min_doc,
      0
    },
    {
      s_delta_max_str,
      (getter)PyBobLearnMLPRProp_getDeltaMax,
      (setter)PyBobLearnMLPRProp_setDeltaMax,
      s_delta_max_doc,
      0
    },
    {
      s_previous_derivatives_str,
      (getter)PyBobLearnMLPRProp_getPreviousDerivatives,
      (setter)PyBobLearnMLPRProp_setPreviousDerivatives,
      s_previous_derivatives_doc,
      0
    },
    {
      s_previous_bias_derivatives_str,
      (getter)PyBobLearnMLPRProp_getPreviousBiasDerivatives,
      (setter)PyBobLearnMLPRProp_setPreviousBiasDerivatives,
      s_previous_bias_derivatives_doc,
      0
    },
    {
      s_deltas_str,
      (getter)PyBobLearnMLPRProp_getDeltas,
      (setter)PyBobLearnMLPRProp_setDeltas,
      s_deltas_doc,
      0
    },
    {
      s_bias_deltas_str,
      (getter)PyBobLearnMLPRProp_getBiasDeltas,
      (setter)PyBobLearnMLPRProp_setBiasDeltas,
      s_bias_deltas_doc,
      0
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(s_reset_str, "reset");
PyDoc_STRVAR(s_reset_doc,
"Re-initializes the whole training apparatus to start training\n\
a new machine. This will effectively reset previous derivatives\n\
to zero.");

static PyObject* PyBobLearnMLPRProp_reset (PyBobLearnMLPRPropObject* self) {

  self->cxx->reset();
  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_train_str, "train");
PyDoc_STRVAR(s_train_doc,
"o.train(machine, input, target) -> None\n\
\n\
Trains the MLP to perform discrimination using RProp\n\
\n\
Resilient Back-propagation (R-Prop) is an efficient algorithm for\n\
gradient descent with local adpatation of the weight updates, which\n\
adapts to the behaviour of the chosen error function.\n\
\n\
Concretely, this executes the following update rule for the weights\n\
(and biases, optionally) and respective :math:`\\Delta`'s (the\n\
current weight updates):\n\
\n\
.. math::\n\
   \n\
   \\Delta_{ij}(t) &= \\left\\{\n\
     \\begin{array}{l l}\n\
     \\text{min}(\\eta^+\\cdot\\Delta_{ij}(t-1), \\Delta_{\\text{max}}) & \\text{ if } \\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t-1)\\cdot\\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t) > 0\\\\\n\
     \\max(\\eta^-\\cdot\\Delta_{ij}(t-1), \\Delta_{\\text{min}}) & \\text{ if } \\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t-1)\\cdot\\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t) < 0\\\\\n\
     \\Delta_{ij}(t-1) & \\text{ otherwise}\n\
     \\end{array}\n\
   \\right. \\\\\n\
   \\Delta_{ij}w(t) &= \\left\\{\n\
     \\begin{array}{l l}\n\
     -\\Delta_{ij}(t) & \\text{ if } \\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t) > 0\\\\\n\
     +\\Delta_{ij}(t) & \\text{ if } \\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}(t) < 0\\\\\n\
     0 & \\text{ otherwise}\n\
     \\end{array}\n\
   \\right. \\\\\n\
   w_{ij}(t+1) &= w_{ij}(t) + \\Delta_{ij}(t)\n\
\n\
The following parameters are set *by default* and suggested by the article:\n\
\n\
.. math::\n\
   \n\
   0 < \\eta^- &< 1 < \\eta^+\\\\\n\
   \\eta^- &= 0.5\\\\\n\
   \\eta^+ &= 1.2\\\\\n\
   \\Delta_{0} &= 0.1\\\\\n\
   \\Delta_{\\text{min}} &= 10^{-6}\\\\\n\
   \\Delta_{\\text{max}} &= 50.0\n\
\n\
The training is executed outside the machine context, but uses all the\n\
current machine layout. The given machine is updated with new weights\n\
and biases at the end of the training that is performed a single time.\n\
Iterate as much as you want to refine the training.\n\
\n\
The machine given as input is checked for compatibility with the\n\
current initialized settings. If the two are not compatible, an\n\
exception is thrown.\n\
\n\
.. note::\n\
\n\
   In RProp, training is done in batches. You should set the batch\n\
   size adequately at class initialization or use setBatchSize().\n\
\n\
.. note::\n\
\n\
   The machine is not initialized randomly at each call to this\n\
   method. It is your task to call\n\
   :py:meth:`bob.learn.mlp.Machine.randomize` once at the machine\n\
   you want to train and then call this method as many times as you\n\
   think are necessary. This design allows for a training criteria\n\
   to be encoded outside the scope of this trainer and to this type\n\
   to focus only on applying the training when requested to.\n\
\n\
Keyword arguments:\n\
\n\
machine, :py:class:`bob.learn.mlp.Machine`\n\
   The machine that will be trained. You must have called\n\
   :py:meth:`bob.learn.mlp.Trainer.initialize` which a similarly\n\
   configured machine before being able to call this method, or an\n\
   exception may be thrown.\n\
\n\
input, array-like, 2D with ``float64`` as data type\n\
   A 2D :py:class:`numpy.ndarray` with 64-bit floats containing the\n\
   input data for the MLP to which this training step will be based\n\
   on. The matrix should be organized so each input (example) lies on\n\
   a single row of ``input``.\n\
\n\
target, array-like, 2D with ``float64`` as data type\n\
   A 2D :py:class:`numpy.ndarray` with 64-bit floats containing the\n\
   target data for the MLP to which this training step will be based\n\
   on. The matrix should be organized so each target lies on a single\n\
   row of ``target``, matching each input example in ``input``.\n\
\n\
");

static PyObject* PyBobLearnMLPRProp_train
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

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

  auto input_ = make_safe(input);
  auto target_ = make_safe(target);

  if (input->type_num != NPY_FLOAT64 || input->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (target->type_num != NPY_FLOAT64 || target->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `target'", Py_TYPE(self)->tp_name);
    return 0;
  }

  try {
    self->cxx->train(*machine->cxx,
        *PyBlitzArrayCxx_AsBlitz<double,2>(input),
        *PyBlitzArrayCxx_AsBlitz<double,2>(target)
        );
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot perform training-step for `%s': unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_previous_derivative_str, "set_previous_derivative");
PyDoc_STRVAR(s_set_previous_derivative_doc,
    "Sets the previous cost derivative for a given weight layer (index).");

static PyObject* PyBobLearnMLPRProp_setPreviousDerivativeOnLayer
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_previous_derivative_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setPreviousDerivative(*PyBlitzArrayCxx_AsBlitz<double,2>(array),
        layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set previous derivative at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_previous_bias_derivative_str, "set_previous_bias_derivative");
PyDoc_STRVAR(s_set_previous_bias_derivative_doc,
    "Sets the cost bias derivative for a given bias layer (index).");

static PyObject* PyBobLearnMLPRProp_setPreviousBiasDerivativeOnLayer
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 1D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_previous_bias_derivative_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setPreviousBiasDerivative(*PyBlitzArrayCxx_AsBlitz<double,1>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set previous bias derivative at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_delta_str, "set_delta");
PyDoc_STRVAR(s_set_delta_doc,
    "Sets the delta for a given weight layer.");

static PyObject* PyBobLearnMLPRProp_setDeltaOnLayer
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 2D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_delta_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setDelta(*PyBlitzArrayCxx_AsBlitz<double,2>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set delta at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_bias_delta_str, "set_bias_delta");
PyDoc_STRVAR(s_set_bias_delta_doc,
    "Sets the bias delta for a given bias layer.");

static PyObject* PyBobLearnMLPRProp_setBiasDeltaOnLayer
(PyBobLearnMLPRPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", "layer", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* array = 0;
  Py_ssize_t layer = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&n", kwlist,
        &PyBlitzArray_Converter, &array, &layer)) return 0;

  if (array->type_num != NPY_FLOAT64 || array->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 1D 64-bit float arrays for argument `array' (or any other object coercible to that), but you provided an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, s_set_bias_delta_str, array->ndim, PyBlitzArray_TypenumAsString(array->type_num));
    return 0;
  }

  try {
    self->cxx->setBiasDelta(*PyBlitzArrayCxx_AsBlitz<double,1>(array), layer);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot set bias delta at layer %" PY_FORMAT_SIZE_T "d for `%s': unknown exception caught", layer, Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_RETURN_NONE;

}

static PyMethodDef PyBobLearnMLPRProp_methods[] = {
  {
    s_reset_str,
    (PyCFunction)PyBobLearnMLPRProp_reset,
    METH_NOARGS,
    s_reset_doc,
  },
  {
    s_train_str,
    (PyCFunction)PyBobLearnMLPRProp_train,
    METH_VARARGS|METH_KEYWORDS,
    s_train_doc,
  },
  {
    s_set_previous_derivative_str,
    (PyCFunction)PyBobLearnMLPRProp_setPreviousDerivativeOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_previous_derivative_doc,
  },
  {
    s_set_previous_bias_derivative_str,
    (PyCFunction)PyBobLearnMLPRProp_setPreviousBiasDerivativeOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_previous_bias_derivative_doc,
  },
  {
    s_set_delta_str,
    (PyCFunction)PyBobLearnMLPRProp_setDeltaOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_delta_doc,
  },
  {
    s_set_bias_delta_str,
    (PyCFunction)PyBobLearnMLPRProp_setBiasDeltaOnLayer,
    METH_VARARGS|METH_KEYWORDS,
    s_set_bias_delta_doc,
  },
  {0} /* Sentinel */
};

PyTypeObject PyBobLearnMLPRProp_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_trainer_str,                            /* tp_name */
    sizeof(PyBobLearnMLPRPropObject),         /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)PyBobLearnMLPRProp_delete,    /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0, //(reprfunc)PyBobLearnMLPRProp_Repr,   /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0, //(reprfunc)PyBobLearnMLPRProp_Repr,   /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    s_trainer_doc,                            /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PyBobLearnMLPRProp_methods,               /* tp_methods */
    0,                                        /* tp_members */
    PyBobLearnMLPRProp_getseters,             /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobLearnMLPRProp_init,        /* tp_init */
    0,                                        /* tp_alloc */
    PyBobLearnMLPRProp_new,                   /* tp_new */
};
