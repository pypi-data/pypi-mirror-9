/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Mon  7 Apr 18:02:11 2014 CEST
 *
 * @brief Some utilities for color conversion
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <Python.h>
#include <bob.ip.draw/drawing.h>

/**
 * Returns and checks a single component color
 */
template <typename T> int get_color1(PyObject* o, T& v) {
  if (!PyArray_CheckScalar(o) && !PyNumber_Check(o)) {
    PyErr_Format(PyExc_TypeError, "drawing on a 2D image (gray-scale) requires a color which is a scalar, not `%s'", Py_TYPE(o)->tp_name);
    return 0;
  }
  v = PyBlitzArrayCxx_AsCScalar<T>(o);
  if (PyErr_Occurred()) return 0;
  return 1;
}

/**
 * Returns and checks 3 color components
 */
template <typename T> int get_color3(PyObject* o, T& r, T& g, T& b) {
  if (!PySequence_Check(o) || (PySequence_Fast_GET_SIZE(o) != 3)) {
    PyErr_Format(PyExc_TypeError, "drawing on a 3D image (colored) requires a color which is a sequence (tuple, list, etc) with 3 components");
    return 0;
  }
  int ok = get_color1(PySequence_Fast_GET_ITEM(o, 0), r);
  ok &= get_color1(PySequence_Fast_GET_ITEM(o, 1), g);
  ok &= get_color1(PySequence_Fast_GET_ITEM(o, 2), b);
  return ok;
}
