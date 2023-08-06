/**
 * @author André Anjos <andre.anjos@idiap.ch>
 * @date Thu  3 Apr 18:47:12 2014 CEST
 *
 * @brief Binds color converters to python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include "utils.h"

static PyObject* PyBobIpColor_RgbToGray_Array(PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(3, 2, input_, output_)) return 0;

  output = output_.get();

  switch (input->type_num) {
    case NPY_UINT8:
      bob::ip::color::rgb_to_gray(
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint8_t,2>(output)
          );
      break;
    case NPY_UINT16:
      bob::ip::color::rgb_to_gray(
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(input),
          *PyBlitzArrayCxx_AsBlitz<uint16_t,2>(output)
          );
      break;
    case NPY_FLOAT64:
      bob::ip::color::rgb_to_gray(
          *PyBlitzArrayCxx_AsBlitz<double,3>(input),
          *PyBlitzArrayCxx_AsBlitz<double,2>(output)
          );
      break;
    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", PyBlitzArray_TypenumAsString(input->type_num));
      return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

static PyObject* PyBobIpColor_RgbToGray_Scalar(PyObject* args, PyObject* kwds) {

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
        uint8_t retval;
        bob::ip::color::rgb_to_gray_one(
            PyBlitzArrayCxx_AsCScalar<uint8_t>(r),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(g),
            PyBlitzArrayCxx_AsCScalar<uint8_t>(b),
            retval
            );
        return PyBlitzArrayCxx_FromCScalar(retval);
      }

    case NPY_UINT16:
      {
        uint16_t retval;
        bob::ip::color::rgb_to_gray_one(
            PyBlitzArrayCxx_AsCScalar<uint16_t>(r),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(g),
            PyBlitzArrayCxx_AsCScalar<uint16_t>(b),
            retval
            );
        return PyBlitzArrayCxx_FromCScalar(retval);
      }

    case NPY_FLOAT64:
      {
        double retval;
        bob::ip::color::rgb_to_gray_one(
            PyBlitzArrayCxx_AsCScalar<double>(r),
            PyBlitzArrayCxx_AsCScalar<double>(g),
            PyBlitzArrayCxx_AsCScalar<double>(b),
            retval
            );
        return PyBlitzArrayCxx_FromCScalar(retval);
      }

    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", Py_TYPE(r)->tp_name);
  }

  return 0;
}

PyObject* PyBobIpColor_RgbToGray (PyObject*, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1: //should pass an array
    case 2:
      return PyBobIpColor_RgbToGray_Array(args, kwds);

    case 3:
      return PyBobIpColor_RgbToGray_Scalar(args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - function requires 1, 2 or 3 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", nargs);

  }

  return 0;

}

static PyObject* PyBobIpColor_GrayToRgb_Array(PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(2, 3, input_, output_)) return 0;

  output = output_.get();

  switch (input->type_num) {
    case NPY_UINT8:
      bob::ip::color::gray_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<uint8_t,2>(input),
          *PyBlitzArrayCxx_AsBlitz<uint8_t,3>(output)
          );
      break;
    case NPY_UINT16:
      bob::ip::color::gray_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<uint16_t,2>(input),
          *PyBlitzArrayCxx_AsBlitz<uint16_t,3>(output)
          );
      break;
    case NPY_FLOAT64:
      bob::ip::color::gray_to_rgb(
          *PyBlitzArrayCxx_AsBlitz<double,2>(input),
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

static PyObject* PyBobIpColor_GrayToRgb_Scalar(PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"y", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* y = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &y)) return 0;

  int type_num = check_scalar("y", y);

  if (type_num == NPY_NOTYPE && PyErr_Occurred()) return 0;

  switch (type_num) {
    case NPY_UINT8:
      {
        uint8_t r, g, b;
        bob::ip::color::gray_to_rgb_one(PyBlitzArrayCxx_AsCScalar<uint8_t>(y), r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }
    case NPY_UINT16:
      {
        uint16_t r, g, b;
        bob::ip::color::gray_to_rgb_one(PyBlitzArrayCxx_AsCScalar<uint16_t>(y), r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }
    case NPY_FLOAT64:
      {
        double r, g, b;
        bob::ip::color::gray_to_rgb_one(PyBlitzArrayCxx_AsCScalar<double>(y), r, g, b);
        auto r_ = make_safe(PyBlitzArrayCxx_FromCScalar(r));
        auto g_ = make_safe(PyBlitzArrayCxx_FromCScalar(g));
        auto b_ = make_safe(PyBlitzArrayCxx_FromCScalar(b));
        return Py_BuildValue("(OOO)", r_.get(), g_.get(), b_.get());
      }
    default:
      PyErr_Format(PyExc_NotImplementedError, "function has no support for data type `%s', choose from uint8, uint16 or float64", Py_TYPE(y)->tp_name);
  }

  return 0;
}

PyObject* PyBobIpColor_GrayToRgb (PyObject*, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1: //should pass an array
      {
        PyObject* arg = 0; ///< borrowed (don't delete)
        if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
        else {
          PyObject* tmp = PyDict_Values(kwds);
          auto tmp_ = make_safe(tmp);
          arg = PyList_GET_ITEM(tmp, 0);
        }

        if (PyArray_CheckScalar(arg)) {
          return PyBobIpColor_GrayToRgb_Scalar(args, kwds);
        }
        //else, continues to the next case item
      }

    case 2:
      return PyBobIpColor_GrayToRgb_Array(args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - function requires 1 or 2 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", nargs);

  }

  return 0;

}
