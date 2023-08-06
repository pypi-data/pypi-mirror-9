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
 * Implementation of BackProp trainer *
 **************************************/

PyDoc_STRVAR(s_trainer_str, BOB_EXT_MODULE_PREFIX ".BackProp");

PyDoc_STRVAR(s_trainer_doc,
"BackProp(batch_size, cost, [trainer, [train_biases]]) -> new BackProp\n\
\n\
BackProp(other) -> new BackProp\n\
\n\
Sets an MLP to perform discrimination based on vanilla error\n\
back-propagation as defined in \"Pattern Recognition and Machine\n\
Learning\" by C.M. Bishop, chapter 5 or else, \"Pattern\n\
Classification\" by Duda, Hart and Stork, chapter 6.\n\
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

static int PyBobLearnMLPBackProp_init_discrete
(PyBobLearnMLPBackPropObject* self, PyObject* args, PyObject* kwds) {

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
      self->cxx = new bob::learn::mlp::BackProp(batch_size, cost->cxx,
          *machine->cxx, PyObject_IsTrue(train_biases));
    }
    else if (machine) {
      self->cxx = new bob::learn::mlp::BackProp(batch_size, cost->cxx,
          *machine->cxx);
    }
    else if (train_biases) {
      PyErr_Format(PyExc_RuntimeError, "cannot provide a flag for `train_biases' and do not provide a `machine' upon initialisation of type `%s'", Py_TYPE(self)->tp_name);
      return -1;
    }
    else {
      self->cxx = new bob::learn::mlp::BackProp(batch_size, cost->cxx);
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

static int PyBobLearnMLPBackProp_init_copy
(PyBobLearnMLPBackPropObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnMLPBackProp_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobLearnMLPBackPropObject*>(other);

  try {
    self->cxx = new bob::learn::mlp::BackProp(*(copy->cxx));
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

static int PyBobLearnMLPBackProp_init(PyBobLearnMLPBackPropObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:

      return PyBobLearnMLPBackProp_init_copy(self, args, kwds);

    default:

      return PyBobLearnMLPBackProp_init_discrete(self, args, kwds);
  }

  return -1;

}

static void PyBobLearnMLPBackProp_delete
(PyBobLearnMLPBackPropObject* self) {

  self->parent.cxx = 0;
  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

int PyBobLearnMLPBackProp_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnMLPBackProp_Type));
}

static PyObject* PyBobLearnMLPBackProp_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnMLPBackPropObject* self = (PyBobLearnMLPBackPropObject*)type->tp_alloc(type, 0);

  self->cxx = 0;
  self->parent.cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyDoc_STRVAR(s_learning_rate_str, "learning_rate");
PyDoc_STRVAR(s_learning_rate_doc,
"The learning rate (:math:`\\alpha`) to be used for the\n\
back-propagation (defaults to ``0.1``)."
);

static PyObject* PyBobLearnMLPBackProp_getLearningRate
(PyBobLearnMLPBackPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getLearningRate());
}

static int PyBobLearnMLPBackProp_setLearningRate
(PyBobLearnMLPBackPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setLearningRate(value);
  return 0;

}

PyDoc_STRVAR(s_momentum_str, "momentum");
PyDoc_STRVAR(s_momentum_doc,
"The momentum (:math:`\\mu`) to be used for the back-propagation.\n\
This value allows for some *memory* on previous weight updates to\n\
be used for the next update (defaults to ``0.0``).");

static PyObject* PyBobLearnMLPBackProp_getMomentum
(PyBobLearnMLPBackPropObject* self, void* /*closure*/) {
  return Py_BuildValue("d", self->cxx->getMomentum());
}

static int PyBobLearnMLPBackProp_setMomentum
(PyBobLearnMLPBackPropObject* self, PyObject* o, void* /*closure*/) {

  double value = PyFloat_AsDouble(o);
  if (PyErr_Occurred()) return -1;
  self->cxx->setMomentum(value);
  return 0;

}

PyDoc_STRVAR(s_previous_derivatives_str, "previous_derivatives");
PyDoc_STRVAR(s_previous_derivatives_doc,
"The derivatives of the cost w.r.t. to the specific\n\
**weights** of the network, from the previous training step.\n\
The derivatives are arranged to match the organization\n\
of weights of the machine being trained.");

static PyObject* PyBobLearnMLPBackProp_getPreviousDerivatives
(PyBobLearnMLPBackPropObject* self, void* /*closure*/) {
  return convert_vector<2>(self->cxx->getPreviousDerivatives());
}

static int PyBobLearnMLPBackProp_setPreviousDerivatives
(PyBobLearnMLPBackPropObject* self, PyObject* o, void* /*closure*/) {

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

static PyObject* PyBobLearnMLPBackProp_getPreviousBiasDerivatives
(PyBobLearnMLPBackPropObject* self, void* /*closure*/) {
  return convert_vector<1>(self->cxx->getPreviousBiasDerivatives());
}

static int PyBobLearnMLPBackProp_setPreviousBiasDerivatives
(PyBobLearnMLPBackPropObject* self, PyObject* o, void* /*closure*/) {

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

static PyGetSetDef PyBobLearnMLPBackProp_getseters[] = {
    {
      s_learning_rate_str,
      (getter)PyBobLearnMLPBackProp_getLearningRate,
      (setter)PyBobLearnMLPBackProp_setLearningRate,
      s_learning_rate_doc,
      0
    },
    {
      s_momentum_str,
      (getter)PyBobLearnMLPBackProp_getMomentum,
      (setter)PyBobLearnMLPBackProp_setMomentum,
      s_momentum_doc,
      0
    },
    {
      s_previous_derivatives_str,
      (getter)PyBobLearnMLPBackProp_getPreviousDerivatives,
      (setter)PyBobLearnMLPBackProp_setPreviousDerivatives,
      s_previous_derivatives_doc,
      0
    },
    {
      s_previous_bias_derivatives_str,
      (getter)PyBobLearnMLPBackProp_getPreviousBiasDerivatives,
      (setter)PyBobLearnMLPBackProp_setPreviousBiasDerivatives,
      s_previous_bias_derivatives_doc,
      0
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(s_reset_str, "reset");
PyDoc_STRVAR(s_reset_doc,
"Re-initializes the whole training apparatus to start training\n\
a new machine. This will effectively reset previous derivatives\n\
to zero.");

static PyObject* PyBobLearnMLPBackProp_reset (PyBobLearnMLPBackPropObject* self) {

  self->cxx->reset();
  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_train_str, "train");
PyDoc_STRVAR(s_train_doc,
"o.train(machine, input, target) -> None\n\
\n\
Trains the MLP to perform discrimination using error back-propagation\n\
\n\
Call this method to train the MLP to perform discrimination using\n\
back-propagation with (optional) momentum. Concretely, this executes\n\
the following update rule for the weights (and biases, optionally):\n\
\n\
.. math::\n\
   :nowrap:\n\
   \n\
   \\begin{align}\n\
     \\theta_j(t+1) & = & \\theta_j - [ (1-\\mu)\\Delta\\theta_j(t) + \\mu\\Delta\\theta_j(t-1) ] \\\\\n\
     \\Delta\\theta_j(t) & = & \\alpha\\frac{1}{N}\\sum_{i=1}^{N}\\frac{\\partial J(x_i; \\theta)}{\\partial \\theta_j}\n\
    \\end{align}\n\
\n\
The training is executed outside the machine context, but uses all\n\
the current machine layout. The given machine is updated with new\n\
weights and biases at the end of the training that is performed a single\n\
time.\n\
\n\
You must iterate (in Python) as much as you want to refine the training.\n\
\n\
The machine given as input is checked for compatibility with the current\n\
initialized settings. If the two are not compatible, an exception is\n\
thrown.\n\
\n\
.. note::\n\
   \n\
   In BackProp, training is done in batches. You should set the batch\n\
   size properly at class initialization or use setBatchSize().\n\
\n\
.. note::\n\
   \n\
   The machine is **not** initialized randomly at each call to this\n\
   method. It is your task to call\n\
   :py:meth:`bob.learn.mlp.Machine.randomize` once at the machine\n\
   you want to train and then call this method as many times as you\n\
   think is necessary. This design allows for a *stopping criteria*\n\
   to be encoded outside the scope of this trainer and for this method\n\
   to only focus on applying the training when requested to.\n\
   Stochastic training can be executed by setting the ``batch_size``\n\
   to 1.\n\
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

static PyObject* PyBobLearnMLPBackProp_train
(PyBobLearnMLPBackPropObject* self, PyObject* args, PyObject* kwds) {

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

static PyMethodDef PyBobLearnMLPBackProp_methods[] = {
  {
    s_reset_str,
    (PyCFunction)PyBobLearnMLPBackProp_reset,
    METH_NOARGS,
    s_reset_doc,
  },
  {
    s_train_str,
    (PyCFunction)PyBobLearnMLPBackProp_train,
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
  {0} /* Sentinel */
};

PyTypeObject PyBobLearnMLPBackProp_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_trainer_str,                                 /* tp_name */
    sizeof(PyBobLearnMLPBackPropObject),           /* tp_basicsize */
    0,                                             /* tp_itemsize */
    (destructor)PyBobLearnMLPBackProp_delete,      /* tp_dealloc */
    0,                                             /* tp_print */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_compare */
    0, //(reprfunc)PyBobLearnMLPBackProp_Repr,     /* tp_repr */
    0,                                             /* tp_as_number */
    0,                                             /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    0,                                             /* tp_call */
    0, //(reprfunc)PyBobLearnMLPBackProp_Repr,     /* tp_str */
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
    PyBobLearnMLPBackProp_methods,                 /* tp_methods */
    0,                                             /* tp_members */
    PyBobLearnMLPBackProp_getseters,               /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)PyBobLearnMLPBackProp_init,          /* tp_init */
    0,                                             /* tp_alloc */
    PyBobLearnMLPBackProp_new,                     /* tp_new */
};
