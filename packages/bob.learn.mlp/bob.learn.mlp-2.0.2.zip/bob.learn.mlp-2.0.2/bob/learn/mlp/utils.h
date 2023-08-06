/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue  6 May 12:32:39 2014 CEST
 *
 * @brief Shared utilities
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_UTILS_H
#define BOB_LEARN_MLP_UTILS_H

#define BOB_LEARN_MLP_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.learn.mlp/api.h>

/**
 * Converts a vector of blitz::Array<double,N> into a python iterable over
 * arrays.
 *
 * Returns NULL if a problem occurs, the PyObject* resulting from the
 * conversion if all is good.
 */
template <int N>
PyObject* convert_vector(const std::vector<blitz::Array<double,N>>& v) {
  PyObject* retval = PyTuple_New(v.size());
  auto retval_ = make_safe(retval);
  if (!retval) return 0;
  for (unsigned int k=0; k<v.size(); ++k) {
    auto arr = PyBlitzArrayCxx_NewFromConstArray(v[k]);
    if (!arr) return 0;
    PyTuple_SET_ITEM(retval, k, PyBlitzArray_NUMPY_WRAP(arr));
  }
  return Py_BuildValue("O", retval);
}

/**
 * Converts an iterable of pythonic arrays into a vector of
 * blitz::Array<double,N>, checking for errors.
 *
 * Returns -1 if a problem occurs, 0 if all is good.
 */
template <int N>
int convert_tuple(const char* name, const char* attr,
    PyObject* o, std::vector<blitz::Array<double,N>>& seq) {

  if (!PyIter_Check(o) && !PySequence_Check(o)) {
    PyErr_Format(PyExc_TypeError, "parameter `%s' of `%s' requires an iterable, but you passed `%s' which does not implement the iterator protocol", name, attr, Py_TYPE(o)->tp_name);
    return -1;
  }

  /* Checks and converts all entries */
  std::vector<boost::shared_ptr<PyBlitzArrayObject>> seq_;

  PyObject* iterator = PyObject_GetIter(o);
  if (!iterator) return -1;
  auto iterator_ = make_safe(iterator);

  while (PyObject* item = PyIter_Next(iterator)) {
    auto item_ = make_safe(item);

    PyBlitzArrayObject* bz = 0;

    if (!PyBlitzArray_Converter(item, &bz)) {
      PyErr_Format(PyExc_TypeError, "`%s' (while reading `%s') could not convert object of type `%s' at position %" PY_FORMAT_SIZE_T "d of input sequence into an array - check your input", name, attr, Py_TYPE(item)->tp_name, seq.size());
      return -1;
    }

    if (bz->ndim != N || bz->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for parameter `%s' (or any other object coercible to that), but at position %" PY_FORMAT_SIZE_T "d I have found an object with %" PY_FORMAT_SIZE_T "d dimensions and with type `%s' which is not compatible - check your input", name, attr, seq.size(), bz->ndim, PyBlitzArray_TypenumAsString(bz->type_num));
      Py_DECREF(bz);
      return -1;
    }

    seq_.push_back(make_safe(bz)); ///< prevents data deletion
    seq.push_back(*PyBlitzArrayCxx_AsBlitz<double,N>(bz)); ///< only a view!
  }

  if (PyErr_Occurred()) return -1;

  return 0;
}

#endif /* BOB_LEARN_MLP_UTILS_H */
