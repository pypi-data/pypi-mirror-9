/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Tue  8 Apr 09:34:47 2014 CEST
 *
 * @brief Binds box drawing operator to Python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>

#include "utils.h"

template <typename T>
static PyObject* inner_box (PyBlitzArrayObject* image,
    Py_ssize_t y, Py_ssize_t x, Py_ssize_t h, Py_ssize_t w, PyObject* color) {

  switch (image->ndim) {

    case 2:
      {
        T c;
        int ok = get_color1(color, c);
        if (!ok) return 0;

        try {
          bob::ip::draw::draw_box(*PyBlitzArrayCxx_AsBlitz<T,2>(image), y, x,
              h, w, c);
        }
        catch (std::exception& e) {
          PyErr_Format(PyExc_RuntimeError, "%s", e.what());
          return 0;
        }
        catch (...) {
          PyErr_SetString(PyExc_RuntimeError, "caught unknown exception while calling C++ bob::ip::draw::draw_box");
          return 0;
        }

      }
      break;

    case 3:
      {
        T r, g, b;
        int ok = get_color3(color, r, g, b);
        if (!ok) return 0;

        try {
          bob::ip::draw::draw_box(*PyBlitzArrayCxx_AsBlitz<T,3>(image), y, x,
              h, w, boost::tuple<T,T,T>(r, g, b));
        }
        catch (std::exception& e) {
          PyErr_Format(PyExc_RuntimeError, "%s", e.what());
          return 0;
        }
        catch (...) {
          PyErr_SetString(PyExc_RuntimeError, "caught unknown exception while calling C++ bob::ip::draw::draw_box");
          return 0;
        }

      }
      break;

    default:
      PyErr_Format(PyExc_TypeError, "drawing operation does not support images with %" PY_FORMAT_SIZE_T "d dimensions (1 or 3 only)", image->ndim);
      return 0;

  }

  Py_RETURN_NONE;

}

PyObject* PyBobIpDraw_Box (PyObject*, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"image", "p", "size", "color", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image = 0;
  Py_ssize_t y, x, h, w;
  PyObject* color = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&(nn)(nn)O", kwlist,
        &PyBlitzArray_OutputConverter, &image,
        &y, &x, &h, &w, &color)) return 0;

  //protects acquired resources through this scope
  auto image_ = make_safe(image);

  switch(image->type_num) {

    case NPY_UINT8:
      return inner_box<uint8_t>(image, y, x, h, w, color);

    case NPY_UINT16:
      return inner_box<uint16_t>(image, y, x, h, w, color);

    case NPY_FLOAT64:
      return inner_box<double>(image, y, x, h, w, color);

    default:
      PyErr_Format(PyExc_TypeError, "drawing operation does not support images with  data type `%s' (choose from uint8|uint16|float64)", PyBlitzArray_TypenumAsString(image->type_num));

  }

  return 0;
}
