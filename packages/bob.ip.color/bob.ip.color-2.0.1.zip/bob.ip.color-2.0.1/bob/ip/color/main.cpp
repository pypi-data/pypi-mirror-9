/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri  4 Apr 15:02:59 2014 CEST
 *
 * @brief Bindings to bob::ip color converters
 */

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>

extern PyObject* PyBobIpColor_RgbToGray (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_rgb_to_gray = bob::extension::FunctionDoc(
    "rgb_to_gray",

    "Converts an RGB color-coded pixel or a full array (image) to grayscale",

    "This function converts an RGB color-coded pixel or a full RGB array to "
    "grayscale using the CCIR 601 (Kb = 0.114, Kr = 0.299) norm "
    "(http://www.fourcc.org/fccyvrgb.php). It returns only the gray value "
    "(Y component) in the desired data format. This method is more efficient "
    "than calling :py:func:`rgb_to_yuv` method just to extract the Y "
    "component.\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in RGB, in this order, with the specified "
    "``height`` and ``width``; or a set of 3 scalars defining the input R, G "
    "and B in a discrete way. The output array may be optionally provided. "
    "In such a case, it should be a 2D array with the same number of columns "
    "and rows as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the gray-scaled "
    "version for a pixel with the 3 discrete values for red, green and blue.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should be ``(height, width)``")
    .add_return("output", "array_like (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("r, g, b", "y")
    .add_parameter("r, g, b", "scalar (uint8|uint16|float64)", "Discrete pixel values for the red, green and blue channels")
    .add_return("y", "scalar (uint8|uint16|float64)", "A scalar is returned when this function is fed discrete RGB values. The type matches the input pixel values")
;

extern PyObject* PyBobIpColor_GrayToRgb (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_gray_to_rgb = bob::extension::FunctionDoc(
    "gray_to_rgb",

    "Converts a gray pixel or a full array (image) to RGB",

    "This function converts a gray pixel or a gray array representing an "
    "image to a monochrome colored equivalent. This method is implemented "
    "for completeness and is equivalent to replicating the Y pixel value "
    "over the three RGB bands.\n"
    "\n"
    "The input is expected to be either an array or a scalar. If you input "
    "an array, it is expected to assume the shape ``(height, width)``, "
    "representing an image encoded in gray scale, with the specified "
    "``height`` and ``width``. If you input a single scalar, it defines the "
    "value of Y in a discrete way.\n"
    "\n"
    "The output array may be optionally provided. In such a case, it should "
    "be a 3D array with the same number of columns and rows as the input, "
    "and have have the same data type. The number of color planes (first "
    "dimension) of such array should be ``3``. If an output array is not "
    "provided, one will be allocated internally. In any case, the output "
    "array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return a tuple with "
    "the 3 discrete values for red, green and blue.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> y = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 2D)", "Input array containing an image with the shape ``(height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 3D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should be ``(3, height, width)``")
    .add_return("output", "array (uint8|uint16|float64, 3D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("y", "r, g, b")
    .add_parameter("y", "scalar (uint8|uint16|float64)", "The gray-scale pixel scalar you wish to convert into an RGB tuple")
    .add_return("r, g, b", "scalar (uint8|uint16|float64)", "Discrete pixel values for the red, green and blue channels")
;

extern PyObject* PyBobIpColor_RgbToYuv (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_rgb_to_yuv = bob::extension::FunctionDoc(
    "rgb_to_yuv",

    "Converts an RGB color-coded pixel or a full array (image) to YUV",

    "This function converts an RGB color-coded pixel or a full RGB array to "
    "YUV (Y'CbCr) using the CCIR 601 (Kb = 0.114, Kr = 0.299) norm "
    "(http://www.fourcc.org/fccyvrgb.php).\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in RGB, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the YUV "
    "version for a pixel with the 3 discrete values for Y, U (Cb) and V (Cr). "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of R, G and B.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("r, g, b", "y, u, v")
    .add_parameter("r, g, b", "scalar (uint8|uint16|float64)", "Discrete pixel values for the red, green and blue channels")
    .add_return("y, u, v", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete RGB values. The types match the input pixel values")
;

extern PyObject* PyBobIpColor_YuvToRgb (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_yuv_to_rgb = bob::extension::FunctionDoc(
    "yuv_to_rgb",

    "Converts an YUV color-coded pixel or a full array (image) to RGB",

    "This function converts an YUV (Y'CbCr) array or color-coded pixel using "
    "the CCIR 601 (Kb = 0.114, Kr = 0.299) norm "
    "(http://www.fourcc.org/fccyvrgb.php) to RGB.\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in YUV, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the YUV "
    "version for a pixel with the 3 discrete values for red, green and blue. "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of Y, U and V.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("y, u, v", "r, g, b")
    .add_parameter("y, u, v", "scalar (uint8|uint16|float64)", "Discrete pixel values for Y, U (Cb) and V (Cr) channels")
    .add_return("r, g, b", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete YUV values. The types match the input pixel values")
;

extern PyObject* PyBobIpColor_RgbToHsv (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_rgb_to_hsv = bob::extension::FunctionDoc(
    "rgb_to_hsv",

    "Converts an RGB color-coded pixel or a full array (image) to HSV",

    "This function converts an RGB color-coded pixel or a full RGB array to "
    "HSV (http://en.wikipedia.org/wiki/HSL_and_HSV).\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in RGB, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the HSV "
    "version for a pixel with the 3 discrete values for H, S and V. "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of R, G and B.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("r, g, b", "h, s, v")
    .add_parameter("r, g, b", "scalar (uint8|uint16|float64)", "Discrete pixel values for the red, green and blue channels")
    .add_return("h, s, v", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete RGB values. The types match the input pixel values")
;

extern PyObject* PyBobIpColor_HsvToRgb (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_hsv_to_rgb = bob::extension::FunctionDoc(
    "hsv_to_rgb",

    "Converts an HSV color-coded pixel or a full array (image) to RGB",

    "This function converts an HSV array or color-coded pixel "
    "(http://en.wikipedia.org/wiki/HSL_and_HSV) to RGB.\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in HSV, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the HSV "
    "version for a pixel with the 3 discrete values for red, green and blue. "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of H, S and V.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("h, s, v", "r, g, b")
    .add_parameter("h, s, v", "scalar (uint8|uint16|float64)", "Discrete pixel values for H, S and V  channels")
    .add_return("r, g, b", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete HSV values. The types match the input pixel values")
;

extern PyObject* PyBobIpColor_RgbToHsl (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_rgb_to_hsl = bob::extension::FunctionDoc(
    "rgb_to_hsl",

    "Converts an RGB color-coded pixel or a full array (image) to HSL",

    "This function converts an RGB color-coded pixel or a full RGB array to "
    "HSL (http://en.wikipedia.org/wiki/HSL_and_HSL).\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in RGB, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the HSL "
    "version for a pixel with the 3 discrete values for H, S and L. "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of R, G and B.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("r, g, b", "h, s, l")
    .add_parameter("r, g, b", "scalar (uint8|uint16|float64)", "Discrete pixel values for the red, green and blue channels")
    .add_return("h, s, l", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete RGB values. The types match the input pixel values")
;

extern PyObject* PyBobIpColor_HslToRgb (PyObject*, PyObject*, PyObject*);
static bob::extension::FunctionDoc s_hsl_to_rgb = bob::extension::FunctionDoc(
    "hsl_to_rgb",

    "Converts an HSL color-coded pixel or a full array (image) to RGB",

    "This function converts an HSL array or color-coded pixel "
    "(http://en.wikipedia.org/wiki/HSL_and_HSL) to RGB.\n"
    "\n"
    "The input is expected to be either an array or scalars. If you input an "
    "array, it is expected to assume the shape ``(3, height, width)``, "
    "representing an image encoded in HSL, in this order, with the specified "
    "``height`` and ``width``. The output array may be optionally provided. "
    "In such a case, it should be a 3D array with the same dimensions "
    "as the input, and have have the same data type. If an output "
    "array is not provided, one will be allocated internally. In any case, "
    "the output array is always returned.\n"
    "\n"
    "If the input is of scalar type, this method will return the HSL "
    "version for a pixel with the 3 discrete values for red, green and blue. "
    "The input in this case should consist of 3 scalars defining the "
    "discrete values of H, S and L.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   If you provide python scalars, then you should provide 3 values that "
    "share the same scalar type. Type mixing will raise a "
    ":py:class:`TypeError` exception.\n"
    "\n"
    ".. note::\n"
    "\n"
    "   This method only supports arrays and scalars of the following data "
    "types:\n"
    "\n"
    "   * :py:class:`numpy.uint8`\n"
    "   * :py:class:`numpy.uint16`\n"
    "   * :py:class:`numpy.float64` (or the native python ``float``)\n"
    "   \n"
    "   To create an object with a scalar type that will be accepted by this "
    "   method, use a construction like the following:\n"
    "   \n"
    "   .. code-block:: python\n"
    "      \n"
    "      >> import numpy\n"
    "      >> r = numpy.uint8(32)"
    )

    .add_prototype("input, output", "output")
    .add_parameter("input", "array_like (uint8|uint16|float64, 3D)", "Input array containing an image with the shape ``(3, height, width)``")
    .add_parameter("output", "array (uint8|uint16|float64, 2D), optional", "Output array - if provided, should have matching data type to ``input``. The shape should match the ``input`` shape")
    .add_return("output", "array (uint8|uint16|float64, 2D)", "The ``output`` array is returned by the function. If one was not provided, a new one is allocated internally")

    .add_prototype("h, s, l", "r, g, b")
    .add_parameter("h, s, l", "scalar (uint8|uint16|float64)", "Discrete pixel values for H, S and L  channels")
    .add_return("r, g, b", "scalar (uint8|uint16|float64)", "Three scalars are returned when this function is fed discrete HSL values. The types match the input pixel values")
;

static PyMethodDef module_methods[] = {
    {
      s_rgb_to_gray.name(),
      (PyCFunction)PyBobIpColor_RgbToGray,
      METH_VARARGS|METH_KEYWORDS,
      s_rgb_to_gray.doc()
    },
    {
      s_gray_to_rgb.name(),
      (PyCFunction)PyBobIpColor_GrayToRgb,
      METH_VARARGS|METH_KEYWORDS,
      s_gray_to_rgb.doc()
    },
    {
      s_rgb_to_yuv.name(),
      (PyCFunction)PyBobIpColor_RgbToYuv,
      METH_VARARGS|METH_KEYWORDS,
      s_rgb_to_yuv.doc()
    },
    {
      s_yuv_to_rgb.name(),
      (PyCFunction)PyBobIpColor_YuvToRgb,
      METH_VARARGS|METH_KEYWORDS,
      s_yuv_to_rgb.doc()
    },
    {
      s_rgb_to_hsv.name(),
      (PyCFunction)PyBobIpColor_RgbToHsv,
      METH_VARARGS|METH_KEYWORDS,
      s_rgb_to_hsv.doc()
    },
    {
      s_hsv_to_rgb.name(),
      (PyCFunction)PyBobIpColor_HsvToRgb,
      METH_VARARGS|METH_KEYWORDS,
      s_hsv_to_rgb.doc()
    },
    {
      s_rgb_to_hsl.name(),
      (PyCFunction)PyBobIpColor_RgbToHsl,
      METH_VARARGS|METH_KEYWORDS,
      s_rgb_to_hsl.doc()
    },
    {
      s_hsl_to_rgb.name(),
      (PyCFunction)PyBobIpColor_HslToRgb,
      METH_VARARGS|METH_KEYWORDS,
      s_hsl_to_rgb.doc()
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Bob Image Processing Color Conversion");

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

  /* imports dependencies */
  if (import_bob_blitz() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  Py_INCREF(m);
  return m;

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
