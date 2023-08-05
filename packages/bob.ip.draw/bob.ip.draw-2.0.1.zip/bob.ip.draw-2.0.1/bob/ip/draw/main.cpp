/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri  4 Apr 15:02:59 2014 CEST
 *
 * @brief Bindings to bob::ip::draw
 */

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>

extern PyObject* PyBobIpDraw_Point(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_point = bob::extension::FunctionDoc(
    "point",

    "Draws a point in the given (gray-scale or color) image.",

    "This method can draw a point in either gray-scale (2D) or color images. "
    "Images have to be :py:class:`numpy.ndarray`'s with either ``uint8``, "
    "``uint16`` or ``float64`` data type. Trying to access outside the image "
    "range will raise a :py:class:`RuntimeError`.\n"
    "\n"
    "In case you pass a 2D array representing a gray-scale image, this function "
    "expects you pass a single scalar as a value for the input parameter "
    "``color``. In the case you pass a 3D array (color image), then the color "
    "parameter should be set to a tuple contanining 3 scalars representing the "
    "levels for each of the color components (red, green and blue)\n"
    "\n"
    "Color images are expected to be represented using the first dimension for "
    "the color planes: ``(3, height, width)``. Images are modified in place.\n"
    )

    .add_prototype("image, p, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p", "tuple", "a point, on the format ``(y, x)``, defining the location on the image that the pixel is going to be drawn.")
    .add_parameter("color", "scalar|tuple", "Color of the pixel. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

extern PyObject* PyBobIpDraw_TryPoint(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_try_point = bob::extension::FunctionDoc(
    "try_point",

    "Tries to draw a point in the given (gray-scale or color) image.",

    "This method tries to draw a point in either gray-scale (2D) or color "
    "images. If the point is out of bounds, it is simply ignored and not "
    "drawn. The input of this method is identical to the input of "
    ":py:func:`point`, in this module. See its help message for details."
    )

    .add_prototype("image, p, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p", "tuple", "a point, on the format ``(y, x)``, defining the location on the image that the pixel is going to be drawn.")
    .add_parameter("color", "scalar|tuple", "Color of the pixel. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

extern PyObject* PyBobIpDraw_Line(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_line = bob::extension::FunctionDoc(
    "line",

    "Draws a line between two points on the given image.",

    "This function is based on the Bresenham's line algorithm and is highly "
    "optimized to be able to draw lines very quickly. There is no floating "
    "point arithmetic nor multiplications and divisions involved. Only "
    "additions, subtractions and bit shifting operations are used.\n"
    "\n"
    "The line may go out of the image bounds in which case such points "
    "(lying outside the image boundary) are ignored.\n"
    "\n"
    "See also: http://en.wikipedia.org/wiki/Bresenham's_line_algorithm.\n"
    "\n"
    "This function can work with either gray-scale or color images. "
    "In case you pass a 2D array representing a gray-scale image, this function "
    "expects you pass a single scalar as a value for the input parameter "
    "``color``. In the case you pass a 3D array (color image), then the color "
    "parameter should be set to a tuple contanining 3 scalars representing the "
    "levels for each of the color components (red, green and blue)\n"
    "\n"

    )

    .add_prototype("image, p1, p2, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p1, p2", "tuple", "Points, on the format ``(y, x)``, defining the start and end of the line. Portions of the line outside the image range will be ignored.")
    .add_parameter("color", "scalar|tuple", "Color of the pixel. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

extern PyObject* PyBobIpDraw_Cross(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_cross = bob::extension::FunctionDoc(
    "cross",

    "Draws a cross in the given (gray-scale or color) image.",

    "This method can draw a cross-like set of lines resembling an ``x``, in "
    "either gray-scale (2D) or color images. The cross is centered on a given "
    "point ``p`` and will have the ``radius`` defined. Images have to be "
    ":py:class:`numpy.ndarray`'s with either ``uint8``, ``uint16`` or "
    "``float64`` data type. Trying to access outside the image range will "
    "raise a :py:class:`RuntimeError`.\n"
    "\n"
    "In case you pass a 2D array representing a gray-scale image, this function "
    "expects you pass a single scalar as a value for the input parameter "
    "``color``. In the case you pass a 3D array (color image), then the color "
    "parameter should be set to a tuple contanining 3 scalars representing the "
    "levels for each of the color components (red, green and blue)\n"
    "\n"
    "Color images are expected to be represented using the first dimension for "
    "the color planes: ``(3, height, width)``. Images are modified in place.\n"
    )

    .add_prototype("image, p, radius, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p", "tuple", "a point, on the format ``(y, x)``, defining the location on the image that the pixel is going to be drawn.")
    .add_parameter("radius", "int", "the value of the radius for the cross to be drawn, in pixels")
    .add_parameter("color", "scalar|tuple", "Color of the cross sign. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

extern PyObject* PyBobIpDraw_Plus(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_plus = bob::extension::FunctionDoc(
    "plus",

    "Draws a plus sign in the given (gray-scale or color) image.",

    "This method can draw a cross-like set of lines resembling an ``+``, in "
    "either gray-scale (2D) or color images. The cross is centered on a given "
    "point ``p`` and will have the ``radius`` defined. Images have to be "
    ":py:class:`numpy.ndarray`'s with either ``uint8``, ``uint16`` or "
    "``float64`` data type. Trying to access outside the image range will "
    "raise a :py:class:`RuntimeError`.\n"
    "\n"
    "In case you pass a 2D array representing a gray-scale image, this function "
    "expects you pass a single scalar as a value for the input parameter "
    "``color``. In the case you pass a 3D array (color image), then the color "
    "parameter should be set to a tuple contanining 3 scalars representing the "
    "levels for each of the color components (red, green and blue)\n"
    "\n"
    "Color images are expected to be represented using the first dimension for "
    "the color planes: ``(3, height, width)``. Images are modified in place.\n"
    )

    .add_prototype("image, p, radius, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p", "tuple", "a point, on the format ``(y, x)``, defining the location on the image that the pixel is going to be drawn.")
    .add_parameter("radius", "int", "the value of the radius for the cross to be drawn, in pixels")
    .add_parameter("color", "scalar|tuple", "Color of the cross sign. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

extern PyObject* PyBobIpDraw_Box(PyObject*, PyObject* args, PyObject* kwds);
static bob::extension::FunctionDoc s_box = bob::extension::FunctionDoc(
    "box",

    "Draws a box anchored at a point, with the given dimensions.",

    "This method draws a box, using the :py:func:`line` primitives, into the "
    "provided image. The box will be anchored at a given point, which refers "
    "to its upper-left corner and have a certain size, defined in terms of "
    "its height and width.\n"
    "\n"
    "The line may go out of the image bounds in which case such points "
    "(lying outside the image boundary) are ignored.\n"
    "\n"
    "See also: http://en.wikipedia.org/wiki/Bresenham's_line_algorithm.\n"
    "\n"
    "This function can work with either gray-scale or color images. "
    "In case you pass a 2D array representing a gray-scale image, this function "
    "expects you pass a single scalar as a value for the input parameter "
    "``color``. In the case you pass a 3D array (color image), then the color "
    "parameter should be set to a tuple contanining 3 scalars representing the "
    "levels for each of the color components (red, green and blue)\n"
    "\n"

    )

    .add_prototype("image, p, size, color")
    .add_parameter("image", "array (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(height, width)`` (for gray-scale images) or ``(3, height, width)`` (for color images)")
    .add_parameter("p", "tuple", "a point, on the format ``(y, x)``, defining the location on the image of the **upper-left** corner of the box.")
    .add_parameter("size", "tuple", "a tuple of integers on the format ``(height, width)`` indicating the size of the box.")
    .add_parameter("color", "scalar|tuple", "Color of the pixel. In case the input image is gray-scale (2D), this should be a single scalar. If the input image is colored (3D), then it should be a sequence containing 3 scalars, representing the levels of red, green and blue (in this order) of the pixel to be drawn. The type of scalars representing colors should match the pixel type in ``image``.")
    ;

static PyMethodDef module_methods[] = {
    {
      s_point.name(),
      (PyCFunction)PyBobIpDraw_Point,
      METH_VARARGS|METH_KEYWORDS,
      s_point.doc()
    },
    {
      s_try_point.name(),
      (PyCFunction)PyBobIpDraw_TryPoint,
      METH_VARARGS|METH_KEYWORDS,
      s_try_point.doc()
    },
    {
      s_line.name(),
      (PyCFunction)PyBobIpDraw_Line,
      METH_VARARGS|METH_KEYWORDS,
      s_line.doc()
    },
    {
      s_cross.name(),
      (PyCFunction)PyBobIpDraw_Cross,
      METH_VARARGS|METH_KEYWORDS,
      s_cross.doc()
    },
    {
      s_plus.name(),
      (PyCFunction)PyBobIpDraw_Plus,
      METH_VARARGS|METH_KEYWORDS,
      s_plus.doc()
    },
    {
      s_box.name(),
      (PyCFunction)PyBobIpDraw_Box,
      METH_VARARGS|METH_KEYWORDS,
      s_box.doc()
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Bob image drawing utilitiles");

#if PY_VERSION_HEX >= 0x03000000
static PyModuleDef module_definition = {
  PyModuleDef_HEAD_INIT,
  BOB_EXT_MODULE_NAME,
  module_docstr,
  -1,
  module_methods,
  0, 0, 0, 0
};
#endif

static PyObject* create_module (void) {

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m); ///< protects against early returns

  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0)
    return 0;

  /* imports bob.blitz C-API + dependencies */
  if (import_bob_blitz() < 0) return 0;

  Py_INCREF(m);
  return m;

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
