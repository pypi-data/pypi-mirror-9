/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 21 May 12:08:40 2014 CEST
 *
 * @brief Bindings to roll/unroll
 */


#define BOB_LEARN_MLP_MODULE
#include <bob.learn.mlp/api.h>
#include <bob.learn.mlp/roll.h>
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>

#include "utils.h"

static PyObject* unroll_from_machine(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"machine", "parameters", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* machine = 0;
  PyBlitzArrayObject* parameters = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!|O&", kwlist,
        &PyBobLearnMLPMachine_Type, &machine,
        &PyBlitzArray_OutputConverter, &parameters
        )) return 0;

  auto machine_ = reinterpret_cast<PyBobLearnMLPMachineObject*>(machine);
  auto parameters_ = make_xsafe(parameters);
  Py_ssize_t nb_parameters =
    bob::learn::mlp::detail::getNbParameters(*machine_->cxx);

  if (parameters) {

    if (parameters->type_num != NPY_FLOAT64 ||
        parameters->ndim != 1 ||
        parameters->shape[0] != nb_parameters) {
      PyErr_Format(PyExc_TypeError, "function only supports 1D 64-bit float arrays with shape (%" PY_FORMAT_SIZE_T "d,) for output array `parameters', but you passed a %" PY_FORMAT_SIZE_T"dD %s array with shape (%" PY_FORMAT_SIZE_T "d,)", nb_parameters, parameters->ndim, PyBlitzArray_TypenumAsString(parameters->type_num), parameters->shape[0]);
      return 0;
    }

  }

  else {

    //allocate space for the parameters
    parameters = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &nb_parameters);
    if (!parameters) return 0;
    parameters_ = make_safe(parameters);

  }

  /** all basic checks are done, can execute the function now **/
  try {
    bob::learn::mlp::unroll(*machine_->cxx,
        *PyBlitzArrayCxx_AsBlitz<double,1>(parameters));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot unroll machine parameters: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", parameters));

}

static PyObject* unroll_from_values(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"weights", "biases", "parameters", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* weights = 0;
  PyObject* biases = 0;
  PyBlitzArrayObject* parameters = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO|O&", kwlist,
        &weights, &biases,
        &PyBlitzArray_OutputConverter, &parameters
        )) return 0;

  auto parameters_ = make_xsafe(parameters);

  //converts weights and biases
  std::vector<blitz::Array<double,2>> weights_;
  int status = convert_tuple<2>("unroll", "weights", weights, weights_);
  if (status < 0) return 0;

  std::vector<blitz::Array<double,1>> biases_;
  status = convert_tuple<1>("unroll", "biases", biases, biases_);
  if (status < 0) return 0;

  //checks
  if (weights_.size() != biases_.size()) {
    PyErr_Format(PyExc_RuntimeError, "unroll, when applied to individual weights and biases, requires these iterables to have the same length but len(weights) = %" PY_FORMAT_SIZE_T"d != len(biases) = %" PY_FORMAT_SIZE_T "d", weights_.size(), biases_.size());
    return 0;
  }

  /** we don't check to provide a fast path
  for (Py_ssize_t k=0; k<weights_.size(); ++k) {

    if (weights_[k].extent(1) != biases_[k].extent(0)) {
      Py_ssize_t cols = weights_[k].extent(1);
      Py_ssize_t elems = biases_[k].extent(0);
      PyErr_Format(PyExc_RuntimeError, "unroll, when applied to individual weights and biases, requires these iterables to have the same length and that the number of columns in each weight matrix matches the number of biases for the same layer, but in layer %" PY_FORMAT_SIZE_T "d, the weight matrix has %" PY_FORMAT_SIZE_T "d columns and the bias vector has %" PY_FORMAT_SIZE_T "d elements", k, cols, elems);
      return 0;
    }

    if (k < (weights_.size()-1)) {
      if (weights_[k].extent(1) != weights_[k+1].extent(0)) {
        Py_ssize_t cols = weights_[k].extent(1);
        Py_ssize_t rows = weights_[k+1].extent(0);
        PyErr_Format(PyExc_RuntimeError, "unroll, when applied to individual weights and biases, requires that weights of successive layers have matching number of inputs and outputs, but the weight matrix in layer %" PY_FORMAT_SIZE_T "d, has %" PY_FORMAT_SIZE_T "d columns (outputs) and in layer %" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d rows (inputs)", k, cols, k+1, rows);
        return 0;
      }
    }

  }
  **/

  Py_ssize_t nb_parameters =
    bob::learn::mlp::detail::getNbParameters(weights_, biases_);

  if (parameters) {

    if (parameters->type_num != NPY_FLOAT64 ||
        parameters->ndim != 1 ||
        parameters->shape[0] != nb_parameters) {
      PyErr_Format(PyExc_TypeError, "function only supports 1D 64-bit float arrays with shape (%" PY_FORMAT_SIZE_T "d,) for output array `parameters', but you passed a %" PY_FORMAT_SIZE_T"dD %s array with shape (%" PY_FORMAT_SIZE_T "d,)", nb_parameters, parameters->ndim, PyBlitzArray_TypenumAsString(parameters->type_num), parameters->shape[0]);
      return 0;
    }

  }

  else {

    //allocate space for the parameters
    parameters = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &nb_parameters);
    if (!parameters) return 0;
    parameters_ = make_safe(parameters);

  }

  /** all basic checks are done, can execute the function now **/
  try {
    bob::learn::mlp::unroll(weights_, biases_,
        *PyBlitzArrayCxx_AsBlitz<double,1>(parameters));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot unroll machine parameters: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", parameters));

}

PyObject* unroll(PyObject*, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBobLearnMLPMachine_Check(arg)) return unroll_from_machine(args, kwds);
  return unroll_from_values(args, kwds);

}

static PyObject* roll_to_machine(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"machine", "parameters", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* machine = 0;
  PyBlitzArrayObject* parameters = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!O&", kwlist,
        &PyBobLearnMLPMachine_Type, &machine,
        &PyBlitzArray_Converter, &parameters
        )) return 0;

  auto machine_ = reinterpret_cast<PyBobLearnMLPMachineObject*>(machine);
  auto parameters_ = make_safe(parameters);
  Py_ssize_t nb_parameters =
    bob::learn::mlp::detail::getNbParameters(*machine_->cxx);

  if (parameters->type_num != NPY_FLOAT64 ||
      parameters->ndim != 1 ||
      parameters->shape[0] != nb_parameters) {
    PyErr_Format(PyExc_TypeError, "function only supports 1D 64-bit float arrays with shape (%" PY_FORMAT_SIZE_T "d,) for input array `parameters', but you passed a %" PY_FORMAT_SIZE_T"dD %s array with shape (%" PY_FORMAT_SIZE_T "d,)", nb_parameters, parameters->ndim, PyBlitzArray_TypenumAsString(parameters->type_num), parameters->shape[0]);
    return 0;
  }

  /** all basic checks are done, can execute the function now **/
  try {
    bob::learn::mlp::roll(*machine_->cxx,
        *PyBlitzArrayCxx_AsBlitz<double,1>(parameters));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot roll machine parameters: unknown exception caught");
    return 0;
  }

  Py_RETURN_NONE;

}

static PyObject* roll_to_values(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"weights", "biases", "parameters", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* weights = 0;
  PyObject* biases = 0;
  PyBlitzArrayObject* parameters = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO&", kwlist,
        &weights, &biases,
        &PyBlitzArray_Converter, &parameters
        )) return 0;

  auto parameters_ = make_safe(parameters);

  //converts weights and biases
  std::vector<blitz::Array<double,2>> weights_;
  int status = convert_tuple<2>("roll", "weights", weights, weights_);
  if (status < 0) return 0;

  std::vector<blitz::Array<double,1>> biases_;
  status = convert_tuple<1>("roll", "biases", biases, biases_);
  if (status < 0) return 0;

  //checks
  if (weights_.size() != biases_.size()) {
    PyErr_Format(PyExc_RuntimeError, "roll, when applied to individual weights and biases, requires these iterables to have the same length but len(weights) = %" PY_FORMAT_SIZE_T"d != len(biases) = %" PY_FORMAT_SIZE_T "d", weights_.size(), biases_.size());
    return 0;
  }

  /** we don't check to provide a fast path
  for (Py_ssize_t k=0; k<weights_.size(); ++k) {

    if (weights_[k].extent(1) != biases_[k].extent(0)) {
      Py_ssize_t cols = weights_[k].extent(1);
      Py_ssize_t elems = biases_[k].extent(0);
      PyErr_Format(PyExc_RuntimeError, "roll, when applied to individual weights and biases, requires these iterables to have the same length and that the number of columns in each weight matrix matches the number of biases for the same layer, but in layer %" PY_FORMAT_SIZE_T "d, the weight matrix has %" PY_FORMAT_SIZE_T "d columns and the bias vector has %" PY_FORMAT_SIZE_T "d elements", k, cols, elems);
      return 0;
    }

    if (k < (weights_.size()-1)) {
      if (weights_[k].extent(1) != weights_[k+1].extent(0)) {
        Py_ssize_t cols = weights_[k].extent(1);
        Py_ssize_t rows = weights_[k+1].extent(0);
        PyErr_Format(PyExc_RuntimeError, "roll, when applied to individual weights and biases, requires that weights of successive layers have matching number of inputs and outputs, but the weight matrix in layer %" PY_FORMAT_SIZE_T "d, has %" PY_FORMAT_SIZE_T "d columns (outputs) and in layer %" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d rows (inputs)", k, cols, k+1, rows);
        return 0;
      }
    }

  }
  **/

  Py_ssize_t nb_parameters =
    bob::learn::mlp::detail::getNbParameters(weights_, biases_);

  if (parameters->type_num != NPY_FLOAT64 ||
      parameters->ndim != 1 ||
      parameters->shape[0] != nb_parameters) {
    PyErr_Format(PyExc_TypeError, "function only supports 1D 64-bit float arrays with shape (%" PY_FORMAT_SIZE_T "d,) for input array `parameters', but you passed a %" PY_FORMAT_SIZE_T"dD %s array with shape (%" PY_FORMAT_SIZE_T "d,)", nb_parameters, parameters->ndim, PyBlitzArray_TypenumAsString(parameters->type_num), parameters->shape[0]);
    return 0;
  }

  /** all basic checks are done, can execute the function now **/
  try {
    bob::learn::mlp::roll(weights_, biases_,
        *PyBlitzArrayCxx_AsBlitz<double,1>(parameters));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot roll machine parameters: unknown exception caught");
    return 0;
  }

  Py_RETURN_NONE;

}

PyObject* roll(PyObject*, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBobLearnMLPMachine_Check(arg)) return roll_to_machine(args, kwds);
  return roll_to_values(args, kwds);

}

static PyObject* nb_param_from_machine(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"machine", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* machine = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnMLPMachine_Type, &machine)) return 0;

  auto machine_ = reinterpret_cast<PyBobLearnMLPMachineObject*>(machine);
  return Py_BuildValue("n",
      bob::learn::mlp::detail::getNbParameters(*machine_->cxx));

}

static PyObject* nb_param_from_values(PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"weights", "biases", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* weights = 0;
  PyObject* biases = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
        &weights, &biases)) return 0;

  //converts weights and biases
  std::vector<blitz::Array<double,2>> weights_;
  int status = convert_tuple<2>("unroll", "weights", weights, weights_);
  if (status < 0) return 0;

  std::vector<blitz::Array<double,1>> biases_;
  status = convert_tuple<1>("unroll", "biases", biases, biases_);
  if (status < 0) return 0;

  //checks
  if (weights_.size() != biases_.size()) {
    PyErr_Format(PyExc_RuntimeError, "unroll, when applied to individual weights and biases, requires these iterables to have the same length but len(weights) = %" PY_FORMAT_SIZE_T"d != len(biases) = %" PY_FORMAT_SIZE_T "d", weights_.size(), biases_.size());
    return 0;
  }

  /** we don't check to provide a fast path
  for (Py_ssize_t k=0; k<weights_.size(); ++k) {

    if (weights_[k].extent(1) != biases_[k].extent(0)) {
      Py_ssize_t cols = weights_[k].extent(1);
      Py_ssize_t elems = biases_[k].extent(0);
      PyErr_Format(PyExc_RuntimeError, "MLP parameter counting, when applied to individual weights and biases, requires these iterables to have the same length and that the number of columns in each weight matrix matches the number of biases for the same layer, but in layer %" PY_FORMAT_SIZE_T "d, the weight matrix has %" PY_FORMAT_SIZE_T "d columns and the bias vector has %" PY_FORMAT_SIZE_T "d elements", k, cols, elems);
      return 0;
    }

    if (k < (weights_.size()-1)) {
      if (weights_[k].extent(1) != weights_[k+1].extent(0)) {
        Py_ssize_t cols = weights_[k].extent(1);
        Py_ssize_t rows = weights_[k+1].extent(0);
        PyErr_Format(PyExc_RuntimeError, "MLP parameter counting, when applied to individual weights and biases, requires that weights of successive layers have matching number of inputs and outputs, but the weight matrix in layer %" PY_FORMAT_SIZE_T "d, has %" PY_FORMAT_SIZE_T "d columns (outputs) and in layer %" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d rows (inputs)", k, cols, k+1, rows);
        return 0;
      }
    }

  }
  **/

  return Py_BuildValue("n",
      bob::learn::mlp::detail::getNbParameters(weights_, biases_));

}

PyObject* number_of_parameters(PyObject*, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBobLearnMLPMachine_Check(arg)) return nb_param_from_machine(args, kwds);
  return nb_param_from_values(args, kwds);

}
