/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 29 Apr 09:26:02 2014 CEST
 *
 * @brief Bindings for Cost functions
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_MLP_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/defines.h>
#include <bob.learn.mlp/api.h>
#include <bob.learn.activation/api.h>
#include <structmember.h>
#include <boost/function.hpp>
#include <boost/bind.hpp>

/*************************************
 * Implementation of Cost base class *
 *************************************/

PyDoc_STRVAR(s_cost_str, BOB_EXT_MODULE_PREFIX ".Cost");

PyDoc_STRVAR(s_cost_doc,
"A base class for evaluating the performance cost.\n\
\n\
This is the base class for all concrete (C++ only) loss\n\
function implementations. You cannot instantiate objects\n\
of this type directly, use one of the derived classes.\n\
");

static int PyBobLearnCost_init
(PyBobLearnCostObject* self, PyObject* args, PyObject* kwds) {

  PyErr_Format(PyExc_NotImplementedError, "cannot instantiate objects of type `%s', use one of the derived classes", Py_TYPE(self)->tp_name);
  return -1;

}

int PyBobLearnCost_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnCost_Type));
}

static PyObject* PyBobLearnCost_RichCompare
(PyBobLearnCostObject* self, PyObject* other, int op) {

  if (!PyBobLearnCost_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobLearnCostObject*>(other);

  switch (op) {
    case Py_EQ:
      if (self->cxx->str() == other_->cxx->str()) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    case Py_NE:
      if (self->cxx->str() != other_->cxx->str()) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    default:
      Py_INCREF(Py_NotImplemented);
      return Py_NotImplemented;
  }

}

#if PY_VERSION_HEX >= 0x03000000
#  define PYOBJECT_STR PyObject_Str
#else
#  define PYOBJECT_STR PyObject_Unicode
#endif

PyObject* PyBobLearnCost_Repr(PyBobLearnCostObject* self) {

  /**
   * Expected output:
   *
   * <bob.learn.linear.Cost [...]>
   */

  auto retval = PyUnicode_FromFormat("<%s [act: %s]>",
        Py_TYPE(self)->tp_name, self->cxx->str().c_str());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyObject* PyBobLearnCost_Str(PyBobLearnCostObject* self) {
  return Py_BuildValue("s", self->cxx->str().c_str());
}

/**
 * Checks if a array `a1' and `a2' have a matching shape.
 */
static int have_same_shape (PyBlitzArrayObject* a1, PyBlitzArrayObject* a2) {

  if (a1->ndim != a2->ndim) return 0;

  for (Py_ssize_t k=0; k<a1->ndim; ++k) {
    if (a1->shape[k] != a2->shape[k]) return 0;
  }

  return 1;
}

static PyObject* apply_scalar(PyBobLearnCostObject* self, const char*,
    boost::function<double (double, double)> function,
    PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"output", "target", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  double output = 0.;
  double target = 0.;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "dd", kwlist,
        &output, &target)) return 0;

  return Py_BuildValue("d", function(output, target));

}

/**
 * Maps all elements of arr through function() into `result'
 */
static PyObject* apply_array(PyBobLearnCostObject* self, const char* fname,
    boost::function<double (double, double)> function,
    PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"output", "target", "result", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* output = 0;
  PyBlitzArrayObject* target = 0;
  PyBlitzArrayObject* result = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&|O&", kwlist,
        &PyBlitzArray_Converter, &output,
        &PyBlitzArray_Converter, &target,
        &PyBlitzArray_OutputConverter, &result
        )) return 0;

  //protects acquired resources through this scope
  auto output_ = make_safe(output);
  auto target_ = make_safe(target);
  auto result_ = make_xsafe(result);

  if (output->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 64-bit float arrays for input array `output'", Py_TYPE(self)->tp_name, fname);
    return 0;
  }

  if (target->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 64-bit float arrays for input array `target'", Py_TYPE(self)->tp_name, fname);
    return 0;
  }

  if (result && result->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s.%s' only supports 64-bit float arrays for output array `result'", Py_TYPE(self)->tp_name, fname);
    return 0;
  }

  if (!have_same_shape(output, target)) {
    PyErr_Format(PyExc_RuntimeError, "`%s.%s' requires input arrays `output' and `target' to have the same shape, but you provided arrays with different shapes", Py_TYPE(self)->tp_name, fname);
    return 0;
  }

  if (result && !have_same_shape(output, result)) {
    PyErr_Format(PyExc_RuntimeError, "`%s.%s' requires output array `result' to have the same shape as input arrays `output' and `target', but you provided arrays with different shapes", Py_TYPE(self)->tp_name, fname);
    return 0;
  }

  /** if ``result`` was not pre-allocated, do it now **/
  if (!result) {
    result = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, output->ndim, output->shape);
    result_ = make_safe(result);
  }

  switch (output->ndim) {
    case 1:
      {
        blitz::Array<double,1>& output_ =
          *PyBlitzArrayCxx_AsBlitz<double,1>(output);
        blitz::Array<double,1>& target_ =
          *PyBlitzArrayCxx_AsBlitz<double,1>(target);
        blitz::Array<double,1>& result_ =
          *PyBlitzArrayCxx_AsBlitz<double,1>(result);
        for (int k=0; k<output_.extent(0); ++k)
          result_(k) = function(output_(k), target_(k));
      }
      break;

    case 2:
      {
        blitz::Array<double,2>& output_ =
          *PyBlitzArrayCxx_AsBlitz<double,2>(output);
        blitz::Array<double,2>& target_ =
          *PyBlitzArrayCxx_AsBlitz<double,2>(target);
        blitz::Array<double,2>& result_ =
          *PyBlitzArrayCxx_AsBlitz<double,2>(result);
        for (int k=0; k<output_.extent(0); ++k)
          for (int l=0; l<output_.extent(1); ++l)
            result_(k,l) = function(output_(k,l), target_(k,l));
      }
      break;

    case 3:
      {
        blitz::Array<double,3>& output_ =
          *PyBlitzArrayCxx_AsBlitz<double,3>(output);
        blitz::Array<double,3>& target_ =
          *PyBlitzArrayCxx_AsBlitz<double,3>(target);
        blitz::Array<double,3>& result_ =
          *PyBlitzArrayCxx_AsBlitz<double,3>(result);
        for (int k=0; k<output_.extent(0); ++k)
          for (int l=0; l<output_.extent(1); ++l)
            for (int m=0; m<output_.extent(2); ++m)
              result_(k,l,m) = function(output_(k,l,m), target_(k,l,m));
      }
      break;

    case 4:
      {
        blitz::Array<double,4>& output_ =
          *PyBlitzArrayCxx_AsBlitz<double,4>(output);
        blitz::Array<double,4>& target_ =
          *PyBlitzArrayCxx_AsBlitz<double,4>(target);
        blitz::Array<double,4>& result_ =
          *PyBlitzArrayCxx_AsBlitz<double,4>(result);
        for (int k=0; k<output_.extent(0); ++k)
          for (int l=0; l<output_.extent(1); ++l)
            for (int m=0; m<output_.extent(2); ++m)
              for (int n=0; n<output_.extent(3); ++n)
                result_(k,l,m,n) = function(output_(k,l,m,n), target_(k,l,m,n));
      }
      break;

    default:
      PyErr_Format(PyExc_RuntimeError, "`%s.%s' only accepts 1, 2, 3 or 4-dimensional double arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, fname, output->ndim);
    return 0;

  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", result));

}

PyDoc_STRVAR(s_f_str, "f");
PyDoc_STRVAR(s_f_doc,
"o.f(output, target, [result]) -> result\n\
\n\
Computes the cost, given the current and expected outputs.\n\
\n\
Keyword arguments:\n\
\n\
output, ND array, float64 | scalar\n\
  Real output from the machine. May be a N-dimensional array\n\
  or a plain scalar.\n\
\n\
target, ND array, float64 | scalar\n\
  Target output you are training to achieve. The data type\n\
  and extents for this object must match that of ``target``.\n\
\n\
result (optional), ND array, float64\n\
  Where to place the result from the calculation. You can\n\
  pass this argument if the input are N-dimensional arrays.\n\
  Otherwise, it is an error to pass such a container. If the\n\
  inputs are arrays and an object for ``result`` is passed,\n\
  then its dimensions and data-type must match that of both\n\
  ``output`` and ``result``.\n\
\n\
Returns the cost as a scalar, if the input were scalars or\n\
as an array with matching size of ``output`` and ``target``\n\
otherwise.\n\
");

static PyObject* PyBobLearnCost_f
(PyBobLearnCostObject* self, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBob_NumberCheck(arg))
    return apply_scalar(self, s_f_str,
        boost::bind(&bob::learn::mlp::Cost::f, self->cxx, _1, _2), args, kwds);

  return apply_array(self, s_f_str,
      boost::bind(&bob::learn::mlp::Cost::f, self->cxx, _1, _2), args, kwds);

}

PyDoc_STRVAR(s_f_prime_str, "f_prime");
PyDoc_STRVAR(s_f_prime_doc,
"o.f_prime(output, target, [result]) -> result\n\
\n\
Computes the derivative of the cost w.r.t. output.\n\
\n\
Keyword arguments:\n\
\n\
output, ND array, float64 | scalar\n\
  Real output from the machine. May be a N-dimensional array\n\
  or a plain scalar.\n\
\n\
target, ND array, float64 | scalar\n\
  Target output you are training to achieve. The data type\n\
  and extents for this object must match that of ``target``.\n\
\n\
result (optional), ND array, float64\n\
  Where to place the result from the calculation. You can\n\
  pass this argument if the input are N-dimensional arrays.\n\
  Otherwise, it is an error to pass such a container. If the\n\
  inputs are arrays and an object for ``result`` is passed,\n\
  then its dimensions and data-type must match that of both\n\
  ``output`` and ``result``.\n\
\n\
Returns the cost as a scalar, if the input were scalars or\n\
as an array with matching size of ``output`` and ``target``\n\
otherwise.\n\
");

static PyObject* PyBobLearnCost_f_prime
(PyBobLearnCostObject* self, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBob_NumberCheck(arg))
    return apply_scalar(self, s_f_prime_str,
        boost::bind(&bob::learn::mlp::Cost::f_prime,
          self->cxx, _1, _2), args, kwds);

  return apply_array(self, s_f_prime_str,
      boost::bind(&bob::learn::mlp::Cost::f_prime,
        self->cxx, _1, _2), args, kwds);

}

PyDoc_STRVAR(s_error_str, "error");
PyDoc_STRVAR(s_error_doc,
"o.error(output, target, [result]) -> result\n\
\n\
Computes the back-propagated error for a given MLP ``output``\n\
layer.\n\
\n\
Computes the back-propagated error for a given MLP ``output``\n\
layer, given its activation function and outputs - i.e., the\n\
error back-propagated through the last layer neuron up to the\n\
synapse connecting the last hidden layer to the output layer.\n\
\n\
This implementation allows for optimization in the\n\
calculation of the back-propagated errors in cases where there\n\
is a possibility of mathematical simplification when using a\n\
certain combination of cost-function and activation. For\n\
example, using a ML-cost and a logistic activation function.\n\
\n\
Keyword arguments:\n\
\n\
output, ND array, float64 | scalar\n\
  Real output from the machine. May be a N-dimensional array\n\
  or a plain scalar.\n\
\n\
target, ND array, float64 | scalar\n\
  Target output you are training to achieve. The data type and\n\
  extents for this object must match that of ``target``.\n\
\n\
result (optional), ND array, float64\n\
  Where to place the result from the calculation. You can pass\n\
  this argument if the input are N-dimensional arrays.\n\
  Otherwise, it is an error to pass such a container. If the\n\
  inputs are arrays and an object for ``result`` is passed,\n\
  then its dimensions and data-type must match that of both\n\
  ``output`` and ``result``.\n\
\n\
Returns the cost as a scalar, if the input were scalars or as\n\
        an array with matching size of ``output`` and\n\
        ``target`` otherwise.\n\
");

static PyObject* PyBobLearnCost_error
(PyBobLearnCostObject* self, PyObject* args, PyObject* kwds) {

  PyObject* arg = 0; ///< borrowed (don't delete)
  if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
  else {
    PyObject* tmp = PyDict_Values(kwds);
    auto tmp_ = make_safe(tmp);
    arg = PyList_GET_ITEM(tmp, 0);
  }

  if (PyBob_NumberCheck(arg))
    return apply_scalar(self, s_error_str,
        boost::bind(&bob::learn::mlp::Cost::error, self->cxx, _1, _2), args, kwds);

  return apply_array(self, s_error_str,
      boost::bind(&bob::learn::mlp::Cost::error, self->cxx, _1, _2), args, kwds);

}

static PyMethodDef PyBobLearnCost_methods[] = {
  {
    s_f_str,
    (PyCFunction)PyBobLearnCost_f,
    METH_VARARGS|METH_KEYWORDS,
    s_f_doc
  },
  {
    s_f_prime_str,
    (PyCFunction)PyBobLearnCost_f_prime,
    METH_VARARGS|METH_KEYWORDS,
    s_f_prime_doc
  },
  {
    s_error_str,
    (PyCFunction)PyBobLearnCost_error,
    METH_VARARGS|METH_KEYWORDS,
    s_error_doc
  },
  {0} /* Sentinel */
};

static PyObject* PyBobLearnCost_new (PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnCostObject* self = (PyBobLearnCostObject*)type->tp_alloc(type, 0);

  self->cxx.reset();

  return reinterpret_cast<PyObject*>(self);

}

PyObject* PyBobLearnCost_NewFromCost (boost::shared_ptr<bob::learn::mlp::Cost> p) {

  PyBobLearnCostObject* retval = (PyBobLearnCostObject*)PyBobLearnCost_new(&PyBobLearnCost_Type, 0, 0);

  retval->cxx = p;

  return reinterpret_cast<PyObject*>(retval);

}

PyTypeObject PyBobLearnCost_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_cost_str,                               /* tp_name */
    sizeof(PyBobLearnCostObject),             /* tp_basicsize */
    0,                                        /* tp_itemsize */
    0,                                        /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    (reprfunc)PyBobLearnCost_Repr,            /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    (ternaryfunc)PyBobLearnCost_f,            /* tp_call */
    (reprfunc)PyBobLearnCost_Str,             /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    s_cost_doc,                               /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    (richcmpfunc)PyBobLearnCost_RichCompare,  /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PyBobLearnCost_methods,                   /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobLearnCost_init,            /* tp_init */
    0,                                        /* tp_alloc */
    PyBobLearnCost_new,                       /* tp_new */
};

PyDoc_STRVAR(s_squareerror_str, BOB_EXT_MODULE_PREFIX ".SquareError");

PyDoc_STRVAR(s_squareerror_doc,
"SquareError(actfun) -> new SquareError functor\n\
\n\
Calculates the Square-Error between output and target.\n\
\n\
The square error is defined as follows:\n\
\n\
.. math::\n\
   J = \\frac{(\\hat{y} - y)^2}{2}\n\
\n\
where :math:`\\hat{y}` is the output estimated by your machine and\n\
:math:`y` is the expected output.\n\
\n\
Keyword arguments:\n\
\n\
actfun\n\
  The activation function object used at the last layer\n\
\n\
");

static int PyBobLearnSquareError_init
(PyBobLearnSquareErrorObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"actfun", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* actfun = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnActivation_Type, &actfun)) return -1;

  try {
    auto _actfun = reinterpret_cast<PyBobLearnActivationObject*>(actfun);
    self->cxx.reset(new bob::learn::mlp::SquareError(_actfun->cxx));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
  }

  self->parent.cxx = self->cxx;

  if (PyErr_Occurred()) return -1;

  return 0;

}

static void PyBobLearnSquareError_delete
(PyBobLearnSquareErrorObject* self) {

  self->parent.cxx.reset();
  self->cxx.reset();
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyTypeObject PyBobLearnSquareError_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_squareerror_str,                        /*tp_name*/
    sizeof(PyBobLearnSquareErrorObject),      /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)PyBobLearnSquareError_delete, /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    0,                                        /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    0,                                        /*tp_call*/
    0,                                        /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    s_squareerror_doc,                        /* tp_doc */
    0,		                                    /* tp_traverse */
    0,		                                    /* tp_clear */
    0,                                        /* tp_richcompare */
    0,		                                    /* tp_weaklistoffset */
    0,		                                    /* tp_iter */
    0,		                                    /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobLearnSquareError_init,     /* tp_init */
};

PyDoc_STRVAR(s_crossentropyloss_str, BOB_EXT_MODULE_PREFIX ".CrossEntropyLoss");

PyDoc_STRVAR(s_crossentropyloss_doc,
"CrossEntropyLoss(actfun) -> new CrossEntropyLoss functor\n\
\n\
Calculates the Cross Entropy Loss between output and target.\n\
\n\
The cross entropy loss is defined as follows:\n\
\n\
.. math::\n\
   J = - y \\cdot \\log{(\\hat{y})} - (1-y) \\log{(1-\\hat{y})}\n\
\n\
where :math:`\\hat{y}` is the output estimated by your machine and\n\
:math:`y` is the expected output.\n\
\n\
Keyword arguments:\n\
\n\
actfun\n\
  The activation function object used at the last layer. If you\n\
  set this to :py:class:`bob.learn.activation.Logistic`, a\n\
  mathematical simplification is possible in which\n\
  ``backprop_error()`` can benefit increasing the numerical\n\
  stability of the training process. The simplification goes\n\
  as follows:\n\
  \n\
  .. math::\n\
     b = \\delta \\cdot \\varphi'(z)\n\
  \n\
  But, for the cross-entropy loss: \n\
  \n\
  .. math::\n\
     \\delta = \\frac{\\hat{y} - y}{\\hat{y}(1 - \\hat{y})}\n\
  \n\
  and :math:`\\varphi'(z) = \\hat{y} - (1 - \\hat{y})`, so:\n\
  \n\
  .. math::\n\
     b = \\hat{y} - y\n\
\n\
");

static int PyBobLearnCrossEntropyLoss_init
(PyBobLearnCrossEntropyLossObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"actfun", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* actfun = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobLearnActivation_Type, &actfun)) return -1;

  try {
    auto _actfun = reinterpret_cast<PyBobLearnActivationObject*>(actfun);
    self->cxx.reset(new bob::learn::mlp::CrossEntropyLoss(_actfun->cxx));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
  }

  self->parent.cxx = self->cxx;

  if (PyErr_Occurred()) return -1;

  return 0;

}

static void PyBobLearnCrossEntropyLoss_delete
(PyBobLearnCrossEntropyLossObject* self) {

  self->parent.cxx.reset();
  self->cxx.reset();
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyDoc_STRVAR(s_logistic_activation_str, "logistic_activation");
PyDoc_STRVAR(s_logistic_activation_doc,
"o.logistic_activation() -> bool\n\
\n\
Tells if this functor is set to operate together with a\n\
:py:class:`bob.learn.activation.Logistic` activation function.\n\
");

static PyObject* PyBobLearnCrossEntropyLoss_getLogisticActivation
(PyBobLearnCrossEntropyLossObject* self, void* /*closure*/) {
  if (self->cxx->logistic_activation()) Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

static PyGetSetDef PyBobLearnCrossEntropyLoss_getseters[] = {
    {
      s_logistic_activation_str,
      (getter)PyBobLearnCrossEntropyLoss_getLogisticActivation,
      0,
      s_logistic_activation_doc,
      0
    },
    {0}  /* Sentinel */
};

PyTypeObject PyBobLearnCrossEntropyLoss_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_crossentropyloss_str,                        /*tp_name*/
    sizeof(PyBobLearnCrossEntropyLossObject),      /*tp_basicsize*/
    0,                                             /*tp_itemsize*/
    (destructor)PyBobLearnCrossEntropyLoss_delete, /*tp_dealloc*/
    0,                                             /*tp_print*/
    0,                                             /*tp_getattr*/
    0,                                             /*tp_setattr*/
    0,                                             /*tp_compare*/
    0,                                             /*tp_repr*/
    0,                                             /*tp_as_number*/
    0,                                             /*tp_as_sequence*/
    0,                                             /*tp_as_mapping*/
    0,                                             /*tp_hash */
    0,                                             /*tp_call*/
    0,                                             /*tp_str*/
    0,                                             /*tp_getattro*/
    0,                                             /*tp_setattro*/
    0,                                             /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,      /*tp_flags*/
    s_crossentropyloss_doc,                        /* tp_doc */
    0,		                                         /* tp_traverse */
    0,		                                         /* tp_clear */
    0,                                             /* tp_richcompare */
    0,		                                         /* tp_weaklistoffset */
    0,		                                         /* tp_iter */
    0,		                                         /* tp_iternext */
    0,                                             /* tp_methods */
    0,                                             /* tp_members */
    PyBobLearnCrossEntropyLoss_getseters,          /* tp_getset */
    0,                                             /* tp_base */
    0,                                             /* tp_dict */
    0,                                             /* tp_descr_get */
    0,                                             /* tp_descr_set */
    0,                                             /* tp_dictoffset */
    (initproc)PyBobLearnCrossEntropyLoss_init,     /* tp_init */
};
