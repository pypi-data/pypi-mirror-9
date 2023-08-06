/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Thu  3 Apr 18:47:12 2014 CEST
 *
 * @brief Binds color converters to python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include "utils.h"

static PyObject* PyBobIpColor_RgbToHsv_Array(PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(3, 3, input_, output_)) return 0;

  output = output_.get();

  switch (input->type_num) {
    case NPY_UINT8:
      bob::ip::color::rgb_to_hsv(
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(output)
          );
      break;
    case NPY_UINT16:
      bob::ip::color::rgb_to_hsv(
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(output)
          );
      break;
    case NPY_FLOAT64:
      bob::ip::color::rgb_to_hsv(
          *PyBlitzArrayCxx_AsBlitz<double,3>(input),
          *PyBlitzArrayCxx_AsBlitz<double,3>(output)
          );
      break;
    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", PyBlitzArray_TypenumAsString(input->type_num));
      return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

static PyObject* PyBobIpColor_RgbToHsv_Scalar(PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"r", "g", "b", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* r = 0;
  PyObject* g = 0;
  PyObject* b = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO", kwlist, &r, &g, &b)) return 0;

  int type_num = check_scalars("r", r, "g", g, "b", b);

  if (type_num == NPY_NOTYPE && PyErr_Occurred()) return 0;

  switch (type_num) {

    case NPY_UINT8:
      {
        uint8_t h;
        uint8_t s;
        uint8_t v;
        bob::ip::color::rgb_to_hsv_one(
            PyBlitzArrayCxx_AsCScalar<uint8_t>(r),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(g),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(b),
            h, s, v
            );
        auto h_ = make_safe(PyBlitzArrayCxx_FromCScalar(h));
        auto s_ = make_safe(PyBlitzArrayCxx_FromCScalar(s));
        auto v_ = make_safe(PyBlitzArrayCxx_FromCScalar(v));
        return Py_BuildValue("(OOO)", h_.get(), s_.get(), v_.get());
      }

    case NPY_UINT16:
      {
        uint16_t h;
        uint16_t s;
        uint16_t v;
        bob::ip::color::rgb_to_hsv_one(
            PyBlitzArrayCxx_AsCScalar<uint16_t>(r),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(g),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(b),
            h, s, v
            );
        auto h_ = make_safe(PyBlitzArrayCxx_FromCScalar(h));
        auto s_ = make_safe(PyBlitzArrayCxx_FromCScalar(s));
        auto v_ = make_safe(PyBlitzArrayCxx_FromCScalar(v));
        return Py_BuildValue("(OOO)", h_.get(), s_.get(), v_.get());
      }

    case NPY_FLOAT64:
      {
        double h;
        double s;
        double v;
        bob::ip::color::rgb_to_hsv_one(
            PyBlitzArrayCxx_AsCScalar<double>(r),
            PyBlitzArrayCxx_AsCScalar<double>(g),
            PyBlitzArrayCxx_AsCScalar<double>(b),
            h, s, v
            );
        auto h_ = make_safe(PyBlitzArrayCxx_FromCScalar(h));
        auto s_ = make_safe(PyBlitzArrayCxx_FromCScalar(s));
        auto v_ = make_safe(PyBlitzArrayCxx_FromCScalar(v));
        return Py_BuildValue("(OOO)", h_.get(), s_.get(), v_.get());
      }

    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", Py_TYPE(r)->tp_name);
  }

  return 0;
}

PyObject* PyBobIpColor_RgbToHsv (PyObject*, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1: //should pass an array
    case 2:
      return PyBobIpColor_RgbToHsv_Array(args, kwds);

    case 3:
      return PyBobIpColor_RgbToHsv_Scalar(args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - function requires 1, 2 or 3 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", nargs);

  }

  return 0;

}

static PyObject* PyBobIpColor_HsvToRgb_Array(PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(3, 3, input_, output_)) return 0;

  output = output_.get();

  switch (input->type_num) {
    case NPY_UINT8:
      bob::ip::color::hsv_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(output)
          );
      break;
    case NPY_UINT16:
      bob::ip::color::hsv_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(output)
          );
      break;
    case NPY_FLOAT64:
      bob::ip::color::hsv_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<double,3>(input),
          *PyBlitzArrayCxx_AsBlitz<double,3>(output)
          );
      break;
    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", PyBlitzArray_TypenumAsString(input->type_num));
      return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

static PyObject* PyBobIpColor_HsvToRgb_Scalar(PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"h", "s", "v", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* h = 0;
  PyObject* s = 0;
  PyObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOO", kwlist,
        &h, &s, &v)) return 0;

  int type_num = check_scalars("h", h, "s", s, "v", v);

  if (type_num == NPY_NOTYPE && PyErr_Occurred()) return 0;

  switch (type_num) {

    case NPY_UINT8:
      {
        uint8_t r, g, b;
        bob::ip::color::hsv_to_rgb_one(
            PyBlitzArrayCxx_AsCScalar<uint8_t>(h),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(s),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(v),
            r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }

    case NPY_UINT16:
      {
        uint16_t r, g, b;
        bob::ip::color::hsv_to_rgb_one(
            PyBlitzArrayCxx_AsCScalar<uint16_t>(h),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(s),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(v),
            r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }

    case NPY_FLOAT64:
      {
        double r, g, b;
        bob::ip::color::hsv_to_rgb_one(
            PyBlitzArrayCxx_AsCScalar<double>(h),
            PyBlitzArrayCxx_AsCScalar<double>(s),
            PyBlitzArrayCxx_AsCScalar<double>(v),
            r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }

    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", Py_TYPE(h)->tp_name);
  }

  return 0;
}

PyObject* PyBobIpColor_HsvToRgb (PyObject*, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1: //should pass an array
    case 2:
      return PyBobIpColor_HsvToRgb_Array(args, kwds);

    case 3:
      return PyBobIpColor_HsvToRgb_Scalar(args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - function requires 1, 2 or 3 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", nargs);

  }

  return 0;

}
