/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Mon  7 Apr 14:50:46 2014 CEST
 *
 * @brief Binds point drawing operator to Python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */


#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>

#include "utils.h"

template <typename T>
static PyObject* inner_point (PyBlitzArrayObject* image,
    int y, int x, PyObject* color) {

  switch (image->ndim) {

    case 2:
      {
        T c;
        int ok = get_color1(color, c);
        if (!ok) return 0;

        try {
          bob::ip::draw::try_draw_point(*PyBlitzArrayCxx_AsBlitz<T,2>(image), y, x, c);
        }
        catch (std::exception& e) {
          PyErr_Format(PyExc_RuntimeError, "%s", e.what());
          return 0;
        }
        catch (...) {
          PyErr_SetString(PyExc_RuntimeError, "caught unknown exception while calling C++ bob::ip::draw::try_draw_point");
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
          bob::ip::draw::try_draw_point(*PyBlitzArrayCxx_AsBlitz<T,3>(image), y, x,
              boost::tuple<T,T,T>(r, g, b));
        }
        catch (std::exception& e) {
          PyErr_Format(PyExc_RuntimeError, "%s", e.what());
          return 0;
        }
        catch (...) {
          PyErr_SetString(PyExc_RuntimeError, "caught unknown exception while calling C++ bob::ip::draw::try_draw_point");
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

PyObject* PyBobIpDraw_TryPoint (PyObject*, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"image", "p", "color", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image = 0;
  Py_ssize_t y = 0;
  Py_ssize_t x = 0;
  PyObject* color = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&(nn)O", kwlist,
        &PyBlitzArray_OutputConverter, &image, &y, &x, &color)) return 0;

  //protects acquired resources through this scope
  auto image_ = make_safe(image);

  switch(image->type_num) {

    case NPY_UINT8:
      return inner_point<uint8_t>(image, y, x, color);

    case NPY_UINT16:
      return inner_point<uint16_t>(image, y, x, color);

    case NPY_FLOAT64:
      return inner_point<double>(image, y, x, color);

    default:
      PyErr_Format(PyExc_TypeError, "drawing operation does not support images with  data type `%s' (choose from uint8|uint16|float64)", PyBlitzArray_TypenumAsString(image->type_num));

  }

  return 0;
}
