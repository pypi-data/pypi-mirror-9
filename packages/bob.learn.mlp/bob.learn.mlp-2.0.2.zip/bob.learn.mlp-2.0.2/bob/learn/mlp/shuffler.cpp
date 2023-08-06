/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 29 Apr 2014 16:16:59 CEST
 *
 * @brief Bindings for the data shuffler
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_MLP_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.learn.mlp/api.h>
#include <bob.core/random_api.h>
#include <structmember.h>

/*********************************************
 * Implementation of DataShuffler base class *
 *********************************************/

PyDoc_STRVAR(s_shuffler_str, BOB_EXT_MODULE_PREFIX ".DataShuffler");

PyDoc_STRVAR(s_shuffler_doc,
"DataShuffler(data, target) -> New DataShuffler\n\
\n\
Serves data from a training set, in a random way.\n\
\n\
Objects of this class are capable of being populated with data\n\
from one or multiple classes and matching target values. Once\n\
setup, the shuffer can randomly select a number of vectors and\n\
accompaning targets for the different classes, filling up user\n\
containers.\n\
\n\
Data shufflers are particular useful for training neural networks.\n\
\n\
Keyword arguments:\n\
\n\
data, sequence of array-like 2D float64\n\
  The input data are divided into sets corresponding to the\n\
  elements of each input class. Within the class array, each\n\
  row is expected to correspond to one observation of that class.\n\
\n\
target, sequence of array-like 1D float64\n\
  The target arrays correspond to the targets for each of the\n\
  input arrays. The number of targets must match the number of\n\
  2D array objects given in ``data``.\n\
\n");

static int PyBobLearnDataShuffler_init
(PyBobLearnDataShufflerObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"data", "target", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* data = 0;
  PyObject* target = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OO", kwlist,
        &data, &target)) return -1;

  /* Check lengths */
  Py_ssize_t data_length = PyObject_Length(data);
  if (data_length == -1) return -1;
  Py_ssize_t target_length = PyObject_Length(target);
  if (target_length == -1) return -1;

  if (data_length < 2) {
    PyErr_Format(PyExc_RuntimeError, "`%s' requires an iterable for parameter `data' leading to, at least, two entries (representing two classes), but you have passed something that has only %" PY_FORMAT_SIZE_T "d entries", Py_TYPE(self)->tp_name, data_length);
    return 0;
  }

  if (target_length != data_length) {
    PyErr_Format(PyExc_RuntimeError, "`%s' requires an iterable for parameter `target' leading to the same number of targets (%" PY_FORMAT_SIZE_T "d) as data arrays, but you have passed something that has only %" PY_FORMAT_SIZE_T "d entries", Py_TYPE(self)->tp_name, data_length, target_length);
    return 0;
  }

  /* Checks and converts all data entries */
  std::vector<blitz::Array<double,2> > data_seq;
  std::vector<boost::shared_ptr<PyBlitzArrayObject>> data_seq_;

  PyObject* iterator = PyObject_GetIter(data);
  if (!iterator) return 0;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);

    PyBlitzArrayObject* bz = 0;

    if (!PyBlitzArray_Converter(item, &bz)) {
      PyErr_Format(PyExc_TypeError, "`%s' could not convert object of type `%s' at position %" PY_FORMAT_SIZE_T "d of input sequence `data' into an array - check your input", Py_TYPE(self)->tp_name, Py_TYPE(item)->tp_name, data_seq.size());
      return 0;
    }

    if (bz->ndim != 2 || bz->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input sequence `data' (or any other object coercible to that), but at position %" PY_FORMAT_SIZE_T "d I have found an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, data_seq.size(), bz->ndim, PyBlitzArray_TypenumAsString(bz->type_num));
      Py_DECREF(bz);
      return 0;
    }

    data_seq_.push_back(make_safe(bz)); ///< prevents data deletion
    data_seq.push_back(*PyBlitzArrayCxx_AsBlitz<double,2>(bz)); ///< only a view!
  }

  if (PyErr_Occurred()) return 0;

  /* Checks and converts all target entries */
  std::vector<blitz::Array<double,1>> target_seq;
  std::vector<boost::shared_ptr<PyBlitzArrayObject>> target_seq_;

  iterator = PyObject_GetIter(target);
  if (!iterator) return 0;
  iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);

    PyBlitzArrayObject* bz = 0;

    if (!PyBlitzArray_Converter(item, &bz)) {
      PyErr_Format(PyExc_TypeError, "`%s' could not convert object of type `%s' at position %" PY_FORMAT_SIZE_T "d of input sequence `target' into an array - check your input", Py_TYPE(self)->tp_name, Py_TYPE(item)->tp_name, target_seq.size());
      return 0;
    }

    if (bz->ndim != 1 || bz->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays for input sequence `target' (or any other object coercible to that), but at position %" PY_FORMAT_SIZE_T "d I have found an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", Py_TYPE(self)->tp_name, target_seq.size(), bz->ndim, PyBlitzArray_TypenumAsString(bz->type_num));
      Py_DECREF(bz);
      return 0;
    }

    target_seq_.push_back(make_safe(bz)); ///< prevents target deletion
    target_seq.push_back(*PyBlitzArrayCxx_AsBlitz<double,1>(bz)); ///< only a view!
  }

  if (PyErr_Occurred()) return 0;

  // proceed to object initialization
  try {
    self->cxx = new bob::learn::mlp::DataShuffler(data_seq, target_seq);
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

int PyBobLearnDataShuffler_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnDataShuffler_Type));
}


static void PyBobLearnDataShuffler_delete(PyBobLearnDataShufflerObject* self) {
  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

PyDoc_STRVAR(s_draw_str, "draw");
PyDoc_STRVAR(s_draw_doc,
"o.draw([n, [data, [target, [rng]]]]) -> (data, target)\n\
\n\
Draws a random number of data-target pairs from the input data.\n\
\n\
This method will draw a given number ``n`` of data-target pairs\n\
from the input data, randomly. You can specific the destination\n\
containers ``data`` and ``target`` which, if provided, must be 2D\n\
arrays of type `float64`` with as many rows as ``n`` and as\n\
many columns as the data and target widths provided upon\n\
construction.\n\
\n\
If ``n`` is not specified, than that value is taken from the\n\
number of rows in either ``data`` or ``target``, whichever is\n\
provided. It is an error not to provide one of ``data``,\n\
``target`` or ``n``.\n\
\n\
If a random generator ``rng`` is provided, it must of the type\n\
:py:class:`bob.core.random.mt19937`. In this case, the shuffler\n\
is going to use this generator instead of its internal one. This\n\
mechanism is useful for repeating draws in case of tests.\n\
\n\
Independently if ``data`` and/or ``target`` is provided, this\n\
function will always return a tuple containing the ``data`` and\n\
``target`` arrays with the random data picked from the user\n\
input. If either ``data`` or ``target`` are not provided by\n\
the user, then they are created internally and returned.\n\
");

static PyObject* PyBobLearnDataShuffler_Call
(PyBobLearnDataShufflerObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"n", "data", "target", "rng", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t n = 0;
  PyBlitzArrayObject* data = 0;
  PyBlitzArrayObject* target = 0;
  PyBoostMt19937Object* rng = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|nO&O&O!", kwlist,
        &n,
        &PyBlitzArray_OutputConverter, &data,
        &PyBlitzArray_OutputConverter, &target,
        &PyBoostMt19937_Type, &rng
        )) return 0;

  //protects acquired resources through this scope
  auto data_ = make_xsafe(data);
  auto target_ = make_xsafe(target);

  //checks data and target first
  if (data) {
    if (data->ndim != 2 || data->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' functor requires you pass a 2D array with 64-bit floats for input `data', but you passed a %" PY_FORMAT_SIZE_T "dD array with `%s' data type", Py_TYPE(self)->tp_name, data->ndim, PyBlitzArray_TypenumAsString(data->type_num));
      return 0;
    }
    if (data->shape[1] != (Py_ssize_t)self->cxx->getDataWidth()) {
      PyErr_Format(PyExc_RuntimeError, "`%s' functor requires you pass a 2D array with %" PY_FORMAT_SIZE_T "d columns for input `data', but you passed an array with %" PY_FORMAT_SIZE_T "d columns instead", Py_TYPE(self)->tp_name, self->cxx->getDataWidth(), data->shape[1]);
      return 0;
    }
  }

  if (target) {
    if (target->ndim != 2 || target->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' functor requires you pass a 2D array with 64-bit floats for input `target', but you passed a %" PY_FORMAT_SIZE_T "dD array with `%s' target type", Py_TYPE(self)->tp_name, target->ndim, PyBlitzArray_TypenumAsString(target->type_num));
      return 0;
    }
    if (target->shape[1] != (Py_ssize_t)self->cxx->getTargetWidth()) {
      PyErr_Format(PyExc_RuntimeError, "`%s' functor requires you pass a 2D array with %" PY_FORMAT_SIZE_T "d columns for input `target', but you passed an array with %" PY_FORMAT_SIZE_T "d columns instead", Py_TYPE(self)->tp_name, self->cxx->getDataWidth(), target->shape[1]);
      return 0;
    }
  }

  if (data && target) {
    //make sure that the number of rows match
    if (data->shape[0] != target->shape[0]) {
      PyErr_Format(PyExc_RuntimeError, "`%s' functor requires you pass 2D arrays for both `data' and `target' with the same number of rows, but `data' has %" PY_FORMAT_SIZE_T "d rows and `target' has %" PY_FORMAT_SIZE_T "d rows instead", Py_TYPE(self)->tp_name, data->shape[0], target->shape[0]);
      return 0;
    }
  }

  Py_ssize_t array_length = 0;
  if (data) array_length = data->shape[0];
  if (target) array_length = target->shape[0];

  if (n && array_length) {
    if (n != array_length) {
      PyErr_Format(PyExc_RuntimeError, "`%s' functor requires you pass 2D arrays for both `data' and `target' with the same number of rows. If a value for `n' is passed, it should match the number of rows in both `data' and `target', but `data' and/or `target' have %" PY_FORMAT_SIZE_T "d rows and `n' is set to %" PY_FORMAT_SIZE_T "d instead - tip: you don't need to specific `n' in this case", Py_TYPE(self)->tp_name, array_length, n);
      return 0;
    }
  }

  if (!n && !array_length) {
    PyErr_Format(PyExc_RuntimeError, "`%s' functor expects you either pass `n', for the number of samples to return or `data' and/or `target' arrays to be filled, but you passed neither.", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (!n) n = array_length;

  //allocates data, if not already there
  if (!data) {
    Py_ssize_t shape[2];
    shape[0] = n;
    shape[1] = self->cxx->getDataWidth();
    data = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 2, shape);
    if (!data) return 0;
    data_ = make_safe(data);
  }

  //allocates target, if not already there
  if (!target) {
    Py_ssize_t shape[2];
    shape[0] = n;
    shape[1] = self->cxx->getTargetWidth();
    target = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 2, shape);
    if (!target) return 0;
    target_ = make_safe(target);
  }

  //all good, now call the shuffler
  try {
    if (rng) {
      self->cxx->operator()(
          *rng->rng,
          *PyBlitzArrayCxx_AsBlitz<double,2>(data),
          *PyBlitzArrayCxx_AsBlitz<double,2>(target)
          );
    }
    else {
      self->cxx->operator()(
          *PyBlitzArrayCxx_AsBlitz<double,2>(data),
          *PyBlitzArrayCxx_AsBlitz<double,2>(target)
          );
    }
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot call object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return 0;
  }

  //and finally we return...
  return Py_BuildValue("NN",
      PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", data)),
      PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", target))
      );

}

PyDoc_STRVAR(s_stdnorm_str, "stdnorm");
PyDoc_STRVAR(s_stdnorm_doc,
"o.stdnorm() -> (mean, stddev)\n\
\n\
Returns the standard normalisation parameters (mean and std. deviation)\n\
for the input data. Returns a tuple ``(mean, stddev)``, which are 1D\n\
float64 arrays with as many entries as ``o.data_width``.");

static PyObject* PyBobLearnDataShuffler_GetStdNorm
(PyBobLearnDataShufflerObject* self) {

  //allocates output vectors, secure them
  Py_ssize_t shape = self->cxx->getDataWidth();
  auto mean = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &shape);
  if (!mean) return 0;
  auto std = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &shape);
  if (!std) return 0;

  self->cxx->getStdNorm(*PyBlitzArrayCxx_AsBlitz<double,1>(mean),
      *PyBlitzArrayCxx_AsBlitz<double,1>(std));

  return Py_BuildValue("NN",
      PyBlitzArray_NUMPY_WRAP((PyObject*)mean),
      PyBlitzArray_NUMPY_WRAP((PyObject*)std)
  );

}

static PyMethodDef PyBobLearnDataShuffler_methods[] = {
  {
    s_draw_str,
    (PyCFunction)PyBobLearnDataShuffler_Call,
    METH_VARARGS|METH_KEYWORDS,
    s_draw_doc
  },
  {
    s_stdnorm_str,
    (PyCFunction)PyBobLearnDataShuffler_GetStdNorm,
    METH_NOARGS,
    s_stdnorm_doc
  },
  {0} /* Sentinel */
};

PyDoc_STRVAR(s_data_width_str, "data_width");
PyDoc_STRVAR(s_data_width_doc,
"The number of features (i.e. the *width*) of each data vector");

static PyObject* PyBobLearnDataShuffler_dataWidth
(PyBobLearnDataShufflerObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getDataWidth());
}

PyDoc_STRVAR(s_target_width_str, "target_width");
PyDoc_STRVAR(s_target_width_doc,
"The number of components (i.e. the *width*) of target vectors");

static PyObject* PyBobLearnDataShuffler_targetWidth
(PyBobLearnDataShufflerObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getTargetWidth());
}

PyDoc_STRVAR(s_auto_stdnorm_str, "auto_stdnorm");
PyDoc_STRVAR(s_auto_stdnorm_doc,
"Defines if we use or not automatic standard (Z) normalisation");

static PyObject* PyBobLearnDataShuffler_getAutoStdNorm
(PyBobLearnDataShufflerObject* self, void* /*closure*/) {
  if (self->cxx->getAutoStdNorm()) Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

static int PyBobLearnDataShuffler_setAutoStdNorm
(PyBobLearnDataShufflerObject* self, PyObject* o, void* /*closure*/) {
  self->cxx->setAutoStdNorm(PyObject_IsTrue(o));
  return 0;
}

static PyGetSetDef PyBobLearnDataShuffler_getseters[] = {
    {
      s_data_width_str,
      (getter)PyBobLearnDataShuffler_dataWidth,
      0,
      s_data_width_doc,
      0
    },
    {
      s_target_width_str,
      (getter)PyBobLearnDataShuffler_targetWidth,
      0,
      s_target_width_doc,
      0
    },
    {
      s_auto_stdnorm_str,
      (getter)PyBobLearnDataShuffler_getAutoStdNorm,
      (setter)PyBobLearnDataShuffler_setAutoStdNorm,
      s_auto_stdnorm_doc,
      0
    },
    {0}  /* Sentinel */
};

PyTypeObject PyBobLearnDataShuffler_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_shuffler_str,                           /* tp_name */
    sizeof(PyBobLearnDataShufflerObject),     /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)PyBobLearnDataShuffler_delete,/* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    (ternaryfunc)PyBobLearnDataShuffler_Call, /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    s_shuffler_doc,                           /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PyBobLearnDataShuffler_methods,           /* tp_methods */
    0,                                        /* tp_members */
    PyBobLearnDataShuffler_getseters,         /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobLearnDataShuffler_init,    /* tp_init */
};
