/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 24 Apr 17:34:44 2014 CEST
 *
 * @brief Bindings for an MLP
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_MLP_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>
#include <bob.learn.activation/api.h>
#include <bob.learn.mlp/api.h>
#include <bob.core/random_api.h>
#include <structmember.h>

/****************************************
 * Implementation of Machine base class *
 ****************************************/

PyDoc_STRVAR(s_machine_str, BOB_EXT_MODULE_PREFIX ".Machine");

PyDoc_STRVAR(s_machine_doc,
"Machine(shape)\n\
Machine(config)\n\
Machine(other)\n\
\n\
A Multi-layer Perceptron Machine.\n\
\n\
An MLP Machine is a representation of a Multi-Layer Perceptron.\n\
This implementation is feed-forward and fully-connected. The\n\
implementation allows setting of input normalization values and\n\
a global activation function. References to fully-connected\n\
feed-forward networks:\n\
\n\
  Bishop's Pattern Recognition and Machine Learning, Chapter 5.\n\
  Figure 5.1 shows what is programmed.\n\
\n\
MLPs normally are multi-layered systems, with 1 or more hidden\n\
layers. As a special case, this implementation also supports\n\
connecting the input directly to the output by means of a single\n\
weight matrix. This is equivalent of a\n\
:py:class:`bob.learn.linear.Machine`, with the advantage it can\n\
be trained by trainers defined in this package.\n\
\n\
An MLP can be constructed in different ways. In the first form,\n\
the user specifies the machine shape as sequence (e.g. a tuple).\n\
The sequence should contain the number of inputs (first element),\n\
number of outputs (last element) and the number of neurons in\n\
each hidden layer (elements between the first and last element\n\
of given tuple). The activation function will be set to\n\
hyperbolic tangent. The machine is remains **uninitialized**.\n\
In the second form the user passes a pre-opened HDF5 file\n\
pointing to the machine information to be loaded in memory.\n\
Finally, in the last form (copy constructor), the user passes\n\
another :py:class:`Machine` that will be fully copied.\n\
");

static int PyBobLearnMLPMachine_init_sizes
(PyBobLearnMLPMachineObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"shape", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* shape = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist,
        &shape)) return -1;

  /* Iterate and extracts the shape */
  std::vector<size_t> cxx_shape;

  PyObject* iterator = PyObject_GetIter(shape);
  if (!iterator) return -1;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);
    Py_ssize_t value = PyNumber_AsSsize_t(item, PyExc_OverflowError);
    if (PyErr_Occurred()) return -1;
    cxx_shape.push_back(value);
  }

  try {
    self->cxx = new bob::learn::mlp::Machine(cxx_shape);
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

static int PyBobLearnMLPMachine_init_hdf5(PyBobLearnMLPMachineObject* self,
    PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"config", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* config = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobIoHDF5File_Type, &config)) return -1;

  auto h5f = reinterpret_cast<PyBobIoHDF5FileObject*>(config);

  try {
    self->cxx = new bob::learn::mlp::Machine(*(h5f->f));
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

static int PyBobLearnMLPMachine_init_copy
(PyBobLearnMLPMachineObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnMLPMachine_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobLearnMLPMachineObject*>(other);

  try {
    self->cxx = new bob::learn::mlp::Machine(*(copy->cxx));
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

static int PyBobLearnMLPMachine_init(PyBobLearnMLPMachineObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:

      {

        PyObject* arg = 0; ///< borrowed (don't delete)
        if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
        else {
          PyObject* tmp = PyDict_Values(kwds);
          auto tmp_ = make_safe(tmp);
          arg = PyList_GET_ITEM(tmp, 0);
        }

        if (PyBobIoHDF5File_Check(arg)) {
          return PyBobLearnMLPMachine_init_hdf5(self, args, kwds);
        }

        if (PyBobLearnMLPMachine_Check(arg)) {
          return PyBobLearnMLPMachine_init_copy(self, args, kwds);
        }

        if (PyIter_Check(arg) || PySequence_Check(arg)) {
          return PyBobLearnMLPMachine_init_sizes(self, args, kwds);
        }

        PyErr_Format(PyExc_TypeError, "cannot initialize `%s' with `%s' (see help)", Py_TYPE(self)->tp_name, Py_TYPE(arg)->tp_name);

      }

      break;

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 argument, but you provided %" PY_FORMAT_SIZE_T "d (see help)", Py_TYPE(self)->tp_name, nargs);

  }

  return -1;

}

static void PyBobLearnMLPMachine_delete
(PyBobLearnMLPMachineObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

int PyBobLearnMLPMachine_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnMLPMachine_Type));
}

static PyObject* PyBobLearnMLPMachine_RichCompare
(PyBobLearnMLPMachineObject* self, PyObject* other, int op) {

  if (!PyBobLearnMLPMachine_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobLearnMLPMachineObject*>(other);

  switch (op) {
    case Py_EQ:
      if (self->cxx->operator==(*other_->cxx)) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    case Py_NE:
      if (self->cxx->operator!=(*other_->cxx)) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    default:
      Py_INCREF(Py_NotImplemented);
      return Py_NotImplemented;
  }

}

PyDoc_STRVAR(s_weights_str, "weights");
PyDoc_STRVAR(s_weights_doc,
"Weight matrix to which the input is projected to. The output\n\
of the project is fed subject to bias and activation before\n\
being output.\n\
");

static PyObject* PyBobLearnMLPMachine_getWeights
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {

  const std::vector<blitz::Array<double, 2>>& weights = self->cxx->getWeights();
  PyObject* retval = PyTuple_New(weights.size());
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  int k=0;
  for (auto i=weights.begin(); i!=weights.end(); ++i, ++k) {
    PyObject* tmp = PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(*i));
    if (!tmp) return 0;
    PyTuple_SET_ITEM(retval, k, tmp);
  }

  Py_INCREF(retval);
  return retval;

}

static int PyBobLearnMLPMachine_setWeights (PyBobLearnMLPMachineObject* self,
    PyObject* weights, void* /*closure*/) {

  if (PyNumber_Check(weights)) {
    double v = PyFloat_AsDouble(weights);
    if (PyErr_Occurred()) return -1;
    self->cxx->setWeights(v);
    return 0;
  }

  if (!PyIter_Check(weights) && !PySequence_Check(weights)) {
    PyErr_Format(PyExc_TypeError, "setting attribute `weights' of `%s' requires either a float or an iterable, but you passed `%s' which does not implement the iterator protocol", Py_TYPE(self)->tp_name, Py_TYPE(weights)->tp_name);
    return -1;
  }

  /* Checks and converts all entries */
  std::vector<blitz::Array<double,2> > weights_seq;
  std::vector<boost::shared_ptr<PyBlitzArrayObject>> weights_seq_;

  PyObject* iterator = PyObject_GetIter(weights);
  if (!iterator) return -1;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);

    PyBlitzArrayObject* bz = 0;

    if (!PyBlitzArray_Converter(item, &bz)) {
      PyErr_Format(PyExc_TypeError, "`%s' could not convert object of type `%s' at position %" PY_FORMAT_SIZE_T "d of input sequence into an array - check your input", Py_TYPE(self)->tp_name, Py_TYPE(item)->tp_name, weights_seq.size());
      return -1;
    }

    if (bz->ndim != 2 || bz->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for attribute `weights' (or any other object coercible to that), but at position %" PY_FORMAT_SIZE_T "d I have found an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, weights_seq.size(), bz->ndim, PyBlitzArray_TypenumAsString(bz->type_num));
      Py_DECREF(bz);
      return -1;
    }

    weights_seq_.push_back(make_safe(bz)); ///< prevents data deletion
    weights_seq.push_back(*PyBlitzArrayCxx_AsBlitz<double,2>(bz)); ///< only a view!
  }

  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setWeights(weights_seq);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `weights' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_biases_str, "biases");
PyDoc_STRVAR(s_biases_doc,
"Bias to the output units of this linear machine, to be added\n\
to the output before activation.\n\
");

static PyObject* PyBobLearnMLPMachine_getBiases
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {

  const std::vector<blitz::Array<double, 1>>& biases = self->cxx->getBiases();
  PyObject* retval = PyTuple_New(biases.size());
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  int k=0;
  for (auto i=biases.begin(); i!=biases.end(); ++i, ++k) {
    PyObject* tmp = PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(*i));
    if (!tmp) return 0;
    PyTuple_SET_ITEM(retval, k, tmp);
  }

  Py_INCREF(retval);
  return retval;

}

static int PyBobLearnMLPMachine_setBiases (PyBobLearnMLPMachineObject* self,
    PyObject* biases, void* /*closure*/) {

  if (PyNumber_Check(biases)) {
    double v = PyFloat_AsDouble(biases);
    if (PyErr_Occurred()) return -1;
    self->cxx->setBiases(v);
    return 0;
  }

  if (!PyIter_Check(biases) && !PySequence_Check(biases)) {
    PyErr_Format(PyExc_TypeError, "setting attribute `biases' of `%s' requires either a float or an iterable, but you passed `%s' which does not implement the iterator protocol", Py_TYPE(self)->tp_name, Py_TYPE(biases)->tp_name);
    return -1;
  }

  /* Checks and converts all entries */
  std::vector<blitz::Array<double,1> > biases_seq;
  std::vector<boost::shared_ptr<PyBlitzArrayObject>> biases_seq_;

  PyObject* iterator = PyObject_GetIter(biases);
  if (!iterator) return -1;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);

    PyBlitzArrayObject* bz = 0;

    if (!PyBlitzArray_Converter(item, &bz)) {
      PyErr_Format(PyExc_TypeError, "`%s' could not convert object of type `%s' at position %" PY_FORMAT_SIZE_T "d of input sequence into an array - check your input", Py_TYPE(self)->tp_name, Py_TYPE(item)->tp_name, biases_seq.size());
      return -1;
    }

    if (bz->ndim != 1 || bz->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays for attribute `biases' (or any other object coercible to that), but at position %" PY_FORMAT_SIZE_T "d I have found an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, biases_seq.size(), bz->ndim, PyBlitzArray_TypenumAsString(bz->type_num));
      Py_DECREF(bz);
      return -1;
    }

    biases_seq_.push_back(make_safe(bz)); ///< prevents data deletion
    biases_seq.push_back(*PyBlitzArrayCxx_AsBlitz<double,1>(bz)); ///< only a view!
  }

  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setBiases(biases_seq);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `biases' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_input_subtract_str, "input_subtract");
PyDoc_STRVAR(s_input_subtract_doc,
"Input subtraction factor, before feeding data through the\n\
weight matrix W. The subtraction is the first applied\n\
operation in the processing chain - by default, it is set to\n\
0.0.\n\
");

static PyObject* PyBobLearnMLPMachine_getInputSubtraction
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {
  return PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(self->cxx->getInputSubtraction()));
}

static int PyBobLearnMLPMachine_setInputSubtraction
(PyBobLearnMLPMachineObject* self, PyObject* o, void* /*closure*/) {

  if (PyNumber_Check(o)) {
    double v = PyFloat_AsDouble(o);
    if (PyErr_Occurred()) return -1;
    self->cxx->setInputSubtraction(v);
    return 0;
  }

  PyBlitzArrayObject* input_subtract = 0;
  if (!PyBlitzArray_Converter(o, &input_subtract)) return -1;
  auto input_subtract_ = make_safe(input_subtract);

  if (input_subtract->type_num != NPY_FLOAT64 || input_subtract->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports either a single florat or 64-bit floats 1D arrays for property array `input_subtract'", Py_TYPE(self)->tp_name);
    return -1;
  }

  try {
    self->cxx->setInputSubtraction(*PyBlitzArrayCxx_AsBlitz<double,1>(input_subtract));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `input_subtract' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_input_divide_str, "input_divide");
PyDoc_STRVAR(s_input_divide_doc,
"Input division factor, before feeding data through the\n\
weight matrix W. The division is applied just after\n\
subtraction - by default, it is set to 1.0.\n\
");

static PyObject* PyBobLearnMLPMachine_getInputDivision
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {
  return PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(self->cxx->getInputDivision()));
}

static int PyBobLearnMLPMachine_setInputDivision (PyBobLearnMLPMachineObject* self,
    PyObject* o, void* /*closure*/) {

  if (PyNumber_Check(o)) {
    double v = PyFloat_AsDouble(o);
    if (PyErr_Occurred()) return -1;
    self->cxx->setInputDivision(v);
    return 0;
  }

  PyBlitzArrayObject* input_divide = 0;
  if (!PyBlitzArray_Converter(o, &input_divide)) return -1;
  auto input_divide_ = make_safe(input_divide);

  if (input_divide->type_num != NPY_FLOAT64 || input_divide->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports either a single float or 64-bit floats 1D arrays for property array `input_divide'", Py_TYPE(self)->tp_name);
    return -1;
  }

  try {
    self->cxx->setInputDivision(*PyBlitzArrayCxx_AsBlitz<double,1>(input_divide));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `input_divide' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_shape_str, "shape");
PyDoc_STRVAR(s_shape_doc,
"A tuple that represents the size of the input vector\n\
followed by the size of the output vector in the format\n\
``(input, output)``.\n\
");

static PyObject* PyBobLearnMLPMachine_getShape
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {

  PyObject* retval = PyTuple_New(self->cxx->numOfHiddenLayers() + 2);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  //fills in all the layers
  Py_ssize_t k = 0;

  PyTuple_SET_ITEM(retval, k++, Py_BuildValue("n", self->cxx->inputSize()));

  auto biases = self->cxx->getBiases();
  for (auto i=biases.begin(); i!=biases.end(); ++i, ++k) {
    PyTuple_SET_ITEM(retval, k, Py_BuildValue("n", i->extent(0)));
  }

  Py_INCREF(retval);
  return retval;
}

static int PyBobLearnMLPMachine_setShape
(PyBobLearnMLPMachineObject* self, PyObject* o, void* /*closure*/) {

  if (!PySequence_Check(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' shape can only be set using sequences, not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  /* Iterate and extracts the shape */
  std::vector<size_t> cxx_shape;

  PyObject* iterator = PyObject_GetIter(o);
  if (!iterator) return -1;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);
    Py_ssize_t value = PyNumber_AsSsize_t(item, PyExc_OverflowError);
    if (PyErr_Occurred()) return -1;
    cxx_shape.push_back(value);
  }

  try {
    self->cxx->resize(cxx_shape);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `shape' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_hidden_activation_str, "hidden_activation");
PyDoc_STRVAR(s_hidden_activation_doc,
"The hidden neurons activation function - by default, the\n\
hyperbolic tangent function. The current implementation only\n\
allows setting one global value for all hidden layers.\n\
");

static PyObject* PyBobLearnMLPMachine_getHiddenActivation
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {
  return PyBobLearnActivation_NewFromActivation(self->cxx->getHiddenActivation());
}

static int PyBobLearnMLPMachine_setHiddenActivation
(PyBobLearnMLPMachineObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBobLearnActivation_Check(o)) {
    PyErr_Format(PyExc_TypeError, "%s hidden activation requires an object of type `Activation' (or an inherited type), not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  auto py = reinterpret_cast<PyBobLearnActivationObject*>(o);
  self->cxx->setHiddenActivation(py->cxx);
  return 0;

}

PyDoc_STRVAR(s_output_activation_str, "output_activation");
PyDoc_STRVAR(s_output_activation_doc,
"The output activation function - by default, the hyperbolic\n\
tangent function. The output provided by the output activation\n\
function is passed, unchanged, to the user.\n\
");

static PyObject* PyBobLearnMLPMachine_getOutputActivation
(PyBobLearnMLPMachineObject* self, void* /*closure*/) {
  return PyBobLearnActivation_NewFromActivation(self->cxx->getOutputActivation());
}

static int PyBobLearnMLPMachine_setOutputActivation
(PyBobLearnMLPMachineObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBobLearnActivation_Check(o)) {
    PyErr_Format(PyExc_TypeError, "%s output activation requires an object of type `Activation' (or an inherited type), not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  auto py = reinterpret_cast<PyBobLearnActivationObject*>(o);
  self->cxx->setOutputActivation(py->cxx);
  return 0;

}

static PyGetSetDef PyBobLearnMLPMachine_getseters[] = {
    {
      s_weights_str,
      (getter)PyBobLearnMLPMachine_getWeights,
      (setter)PyBobLearnMLPMachine_setWeights,
      s_weights_doc,
      0
    },
    {
      s_biases_str,
      (getter)PyBobLearnMLPMachine_getBiases,
      (setter)PyBobLearnMLPMachine_setBiases,
      s_biases_doc,
      0
    },
    {
      s_input_subtract_str,
      (getter)PyBobLearnMLPMachine_getInputSubtraction,
      (setter)PyBobLearnMLPMachine_setInputSubtraction,
      s_input_subtract_doc,
      0
    },
    {
      s_input_divide_str,
      (getter)PyBobLearnMLPMachine_getInputDivision,
      (setter)PyBobLearnMLPMachine_setInputDivision,
      s_input_divide_doc,
      0
    },
    {
      s_shape_str,
      (getter)PyBobLearnMLPMachine_getShape,
      (setter)PyBobLearnMLPMachine_setShape,
      s_shape_doc,
      0
    },
    {
      s_hidden_activation_str,
      (getter)PyBobLearnMLPMachine_getHiddenActivation,
      (setter)PyBobLearnMLPMachine_setHiddenActivation,
      s_hidden_activation_doc,
      0
    },
    {
      s_output_activation_str,
      (getter)PyBobLearnMLPMachine_getOutputActivation,
      (setter)PyBobLearnMLPMachine_setOutputActivation,
      s_output_activation_doc,
      0
    },
    {0}  /* Sentinel */
};

#if PY_VERSION_HEX >= 0x03000000
#  define PYOBJECT_STR PyObject_Str
#else
#  define PYOBJECT_STR PyObject_Unicode
#endif

PyObject* PyBobLearnMLPMachine_Repr(PyBobLearnMLPMachineObject* self) {

  /**
   * Expected output:
   *
   * <bob.learn.linear.MLP float64@(3, 5, 2) [hidden: f(z) = tanh(z), out: f(z) = * tanh(z)]>
   */

  auto weights = make_safe(PyBobLearnMLPMachine_getWeights(self, 0));
  if (!weights) return 0;
  auto dtype = make_safe(PyObject_GetAttrString(weights.get(), "dtype"));
  auto dtype_str = make_safe(PYOBJECT_STR(dtype.get()));
  auto shape = make_safe(PyObject_GetAttrString(weights.get(), "shape"));
  auto shape_str = make_safe(PyObject_Str(shape.get()));

  PyObject* retval = 0;

  auto hidden = self->cxx->getHiddenActivation()->str();
  auto output = self->cxx->getOutputActivation()->str();

  if (hidden == output) {
    retval = PyUnicode_FromFormat("<%s %s@%s [act: %s]>",
        Py_TYPE(self)->tp_name, dtype_str.get(), shape_str.get(),
        hidden.c_str());
  }
  else {
    retval = PyUnicode_FromFormat("<%s %s@%s [act: %s]>",
        Py_TYPE(self)->tp_name, dtype_str.get(), shape_str.get(),
        hidden.c_str(), output.c_str());
  }

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyDoc_STRVAR(s_forward_str, "forward");
PyDoc_STRVAR(s_forward_doc,
"o.forward(input, [output]) -> array\n\
\n\
Projects ``input`` through its internal structure. If\n\
``output`` is provided, place output there instead of allocating\n\
a new array.\n\
\n\
The ``input`` (and ``output``) arrays can be either 1D or 2D\n\
64-bit float arrays. If one provides a 1D array, the ``output``\n\
array, if provided, should also be 1D, matching the output size\n\
of this machine. If one provides a 2D array, it is considered a\n\
set of vertically stacked 1D arrays (one input per row) and a\n\
2D array is produced or expected in ``output``. The ``output``\n\
array in this case shall have the same number of rows as the\n\
``input`` array and as many columns as the output size for this\n\
machine.\n\
\n\
.. note::\n\
\n\
   This method only accepts 64-bit float arrays as input or\n\
   output.\n\
\n");

static PyObject* PyBobLearnMLPMachine_forward
(PyBobLearnMLPMachineObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"input", "output", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* input = 0;
  PyBlitzArrayObject* output = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|O&", kwlist,
        &PyBlitzArray_Converter, &input,
        &PyBlitzArray_OutputConverter, &output
        )) return 0;

  //protects acquired resources through this scope
  auto input_ = make_safe(input);
  auto output_ = make_xsafe(output);

  if (input->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (output && output->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for output array `output'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (input->ndim < 1 || input->ndim > 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 1 or 2-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, input->ndim);
    return 0;
  }

  if (output && input->ndim != output->ndim) {
    PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching number of dimensions, but input array `input' has %" PY_FORMAT_SIZE_T "d dimensions while output array `output' has %" PY_FORMAT_SIZE_T "d dimensions", input->ndim, output->ndim);
    return 0;
  }

  if (input->ndim == 1) {
    if (input->shape[0] != (Py_ssize_t)self->cxx->inputSize()) {
      PyErr_Format(PyExc_RuntimeError, "1D `input' array should have %" PY_FORMAT_SIZE_T "d elements matching `%s' input size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->inputSize(), Py_TYPE(self)->tp_name, input->shape[0]);
      return 0;
    }
    if (output && output->shape[0] != (Py_ssize_t)self->cxx->outputSize()) {
      PyErr_Format(PyExc_RuntimeError, "1D `output' array should have %" PY_FORMAT_SIZE_T "d elements matching `%s' output size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->outputSize(), Py_TYPE(self)->tp_name, output->shape[0]);
      return 0;
    }
  }
  else {
    if (input->shape[1] != (Py_ssize_t)self->cxx->inputSize()) {
      PyErr_Format(PyExc_RuntimeError, "2D `input' array should have %" PY_FORMAT_SIZE_T "d columns, matching `%s' input size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->inputSize(), Py_TYPE(self)->tp_name, input->shape[1]);
      return 0;
    }
    if (output && output->shape[1] != (Py_ssize_t)self->cxx->outputSize()) {
      PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d columns matching `%s' output size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->outputSize(), Py_TYPE(self)->tp_name, output->shape[1]);
      return 0;
    }
    if (output && input->shape[0] != output->shape[0]) {
      PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d rows matching `input' size, not %" PY_FORMAT_SIZE_T "d rows", input->shape[0], output->shape[0]);
      return 0;
    }
  }

  /** if ``output`` was not pre-allocated, do it now **/
  if (!output) {
    Py_ssize_t osize[2];
    if (input->ndim == 1) {
      osize[0] = self->cxx->outputSize();
    }
    else {
      osize[0] = input->shape[0];
      osize[1] = self->cxx->outputSize();
    }
    output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, input->ndim, osize);
    if (!output) return 0;
    output_ = make_safe(output);
  }

  /** all basic checks are done, can call the machine now **/
  try {
    if (input->ndim == 1) {
      self->cxx->forward_(*PyBlitzArrayCxx_AsBlitz<double,1>(input),
          *PyBlitzArrayCxx_AsBlitz<double,1>(output));
    }
    else {
      auto bzin = PyBlitzArrayCxx_AsBlitz<double,2>(input);
      auto bzout = PyBlitzArrayCxx_AsBlitz<double,2>(output);
      blitz::Range all = blitz::Range::all();
      for (int k=0; k<bzin->extent(0); ++k) {
        blitz::Array<double,1> i_ = (*bzin)(k, all);
        blitz::Array<double,1> o_ = (*bzout)(k, all);
        self->cxx->forward_(i_, o_); ///< no need to re-check
      }
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot forward data: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

PyDoc_STRVAR(s_load_str, "load");
PyDoc_STRVAR(s_load_doc,
"o.load(f) -> None\n\
\n\
Loads itself from a :py:class:`bob.io.HDF5File`\n\
\n\
");

static PyObject* PyBobLearnMLPMachine_Load
(PyBobLearnMLPMachineObject* self, PyObject* f) {

  if (!PyBobIoHDF5File_Check(f)) {
    PyErr_Format(PyExc_TypeError, "`%s' cannot load itself from `%s', only from an HDF5 file", Py_TYPE(self)->tp_name, Py_TYPE(f)->tp_name);
    return 0;
  }

  auto h5f = reinterpret_cast<PyBobIoHDF5FileObject*>(f);

  try {
    self->cxx->load(*h5f->f);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot read data from file `%s' (at group `%s'): unknown exception caught", h5f->f->filename().c_str(),
        h5f->f->cwd().c_str());
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_save_str, "save");
PyDoc_STRVAR(s_save_doc,
"o.save(f) -> None\n\
\n\
Saves itself at a :py:class:`bob.io.HDF5File`\n\
\n\
");

static PyObject* PyBobLearnMLPMachine_Save
(PyBobLearnMLPMachineObject* self, PyObject* f) {

  if (!PyBobIoHDF5File_Check(f)) {
    PyErr_Format(PyExc_TypeError, "`%s' cannot write itself to `%s', only to an HDF5 file", Py_TYPE(self)->tp_name, Py_TYPE(f)->tp_name);
    return 0;
  }

  auto h5f = reinterpret_cast<PyBobIoHDF5FileObject*>(f);

  try {
    self->cxx->save(*h5f->f);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "`%s' cannot write data to file `%s' (at group `%s'): unknown exception caught", Py_TYPE(self)->tp_name,
        h5f->f->filename().c_str(), h5f->f->cwd().c_str());
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_is_similar_to_str, "is_similar_to");
PyDoc_STRVAR(s_is_similar_to_doc,
"o.is_similar_to(other, [r_epsilon=1e-5, [a_epsilon=1e-8]]) -> bool\n\
\n\
Compares this MLP with the ``other`` one to be approximately the same.\n\
\n\
The optional values ``r_epsilon`` and ``a_epsilon`` refer to the\n\
relative and absolute precision for the ``weights``, ``biases``\n\
and any other values internal to this machine.\n\
\n\
");

static PyObject* PyBobLearnMLPMachine_IsSimilarTo
(PyBobLearnMLPMachineObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", "r_epsilon", "a_epsilon", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;
  double r_epsilon = 1.e-5;
  double a_epsilon = 1.e-8;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|dd", kwlist,
        &PyBobLearnMLPMachine_Type, &other,
        &r_epsilon, &a_epsilon)) return 0;

  auto other_ = reinterpret_cast<PyBobLearnMLPMachineObject*>(other);

  if (self->cxx->is_similar_to(*other_->cxx, r_epsilon, a_epsilon))
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;

}

PyDoc_STRVAR(s_randomize_str, "randomize");
PyDoc_STRVAR(s_randomize_doc,
"o.randomize([lower_bound, [upper_bound, [rng]]]) -> None\n\
\n\
Resets parameters of this MLP using a random number generator.\n\
\n\
Sets all weights and biases of this MLP, with random values\n\
between :math:`[-0.1, 0.1)` as advised in textbooks.\n\nValues\n\
are drawn using ``boost::uniform_real`` class. The seed is\n\
picked using a time-based algorithm. Different calls spaced\n\
of at least 10 microseconds (machine clock) will be seeded\n\
differently. If lower and upper bound values are given, then\n\
new parameters are taken from ``[lower_bound, upper_bound)``,\n\
according to the ``boost::random`` documentation. The user may\n\
also pass the random number generator to be used. This allows\n\
you to set the seed to a specific value before randomizing\n\
the MLP parameters. If not set, this method will use an\n\
internal random number generator with a seed which is based\n\
on the current time.\n\
");

static PyObject* PyBobLearnMLPMachine_Randomize
(PyBobLearnMLPMachineObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"lower_bound", "upper_bound", "rng", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  double lower_bound = -0.1;
  double upper_bound = 0.1;
  PyBoostMt19937Object* rng = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|ddO!", kwlist,
        &lower_bound, &upper_bound, &PyBoostMt19937_Type, &rng)) return 0;

  if (rng) {
    self->cxx->randomize(*rng->rng, lower_bound, upper_bound);
  }
  else {
    self->cxx->randomize(lower_bound, upper_bound);
  }

  Py_RETURN_NONE;

}

static PyMethodDef PyBobLearnMLPMachine_methods[] = {
  {
    s_forward_str,
    (PyCFunction)PyBobLearnMLPMachine_forward,
    METH_VARARGS|METH_KEYWORDS,
    s_forward_doc
  },
  {
    s_load_str,
    (PyCFunction)PyBobLearnMLPMachine_Load,
    METH_O,
    s_load_doc
  },
  {
    s_save_str,
    (PyCFunction)PyBobLearnMLPMachine_Save,
    METH_O,
    s_save_doc
  },
  {
    s_is_similar_to_str,
    (PyCFunction)PyBobLearnMLPMachine_IsSimilarTo,
    METH_VARARGS|METH_KEYWORDS,
    s_is_similar_to_doc
  },
  {
    s_randomize_str,
    (PyCFunction)PyBobLearnMLPMachine_Randomize,
    METH_VARARGS|METH_KEYWORDS,
    s_randomize_doc
  },
  {0} /* Sentinel */
};

static PyObject* PyBobLearnMLPMachine_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnMLPMachineObject* self =
    (PyBobLearnMLPMachineObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyTypeObject PyBobLearnMLPMachine_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_machine_str,                                 /* tp_name */
    sizeof(PyBobLearnMLPMachineObject),            /* tp_basicsize */
    0,                                             /* tp_itemsize */
    (destructor)PyBobLearnMLPMachine_delete,       /* tp_dealloc */
    0,                                             /* tp_print */
    0,                                             /* tp_getattr */
    0,                                             /* tp_setattr */
    0,                                             /* tp_compare */
    (reprfunc)PyBobLearnMLPMachine_Repr,           /* tp_repr */
    0,                                             /* tp_as_number */
    0,                                             /* tp_as_sequence */
    0,                                             /* tp_as_mapping */
    0,                                             /* tp_hash */
    (ternaryfunc)PyBobLearnMLPMachine_forward,     /* tp_call */
    (reprfunc)PyBobLearnMLPMachine_Repr,           /* tp_str */
    0,                                             /* tp_getattro */
    0,                                             /* tp_setattro */
    0,                                             /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,      /* tp_flags */
    s_machine_doc,                                 /* tp_doc */
    0,                                             /* tp_traverse */
    0,                                             /* tp_clear */
    (richcmpfunc)PyBobLearnMLPMachine_RichCompare, /* tp_richcompare */
    0,                                             /* tp_weaklistoffset */
    0,                                             /* tp_iter */
    0,                                             /* tp_iternext */
    PyBobLearnMLPMachine_methods,                  /* tp_methods */
    0,                                             /* tp_members */
    PyBobLearnMLPMachine_getseters,                /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)PyBobLearnMLPMachine_init,           /* tp_init */
    0,                                             /* tp_alloc */
    PyBobLearnMLPMachine_new,                      /* tp_new */
};
