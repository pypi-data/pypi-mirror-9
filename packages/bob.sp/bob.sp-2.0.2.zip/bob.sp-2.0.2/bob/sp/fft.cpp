/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 13 Feb 2014 15:34:30 CET
 *
 * @brief Methods for quick FFT/IFFT calculation
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.sp/FFT1D.h>
#include <bob.sp/FFT2D.h>
#include <bob.sp/fftshift.h>

static int check_and_allocate(boost::shared_ptr<PyBlitzArrayObject>& input,
    boost::shared_ptr<PyBlitzArrayObject>& output) {

  if (input->type_num != NPY_COMPLEX128) {
    PyErr_SetString(PyExc_TypeError, "method only supports 128-bit complex (2x64-bit float) arrays for input array `input'");
    return 0;
  }

  if (output && output->type_num != NPY_COMPLEX128) {
    PyErr_SetString(PyExc_TypeError, "method only supports 128-bit complex (2x64-bit float) arrays for output array `output'");
    return 0;
  }

  if (input->ndim != 1 and input->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "method only accepts 1 or 2-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", input->ndim);
    return 0;
  }

  if (output && input->ndim != output->ndim) {
    PyErr_Format(PyExc_RuntimeError, "input and output arrays should have matching number of dimensions, but input array `input' has %" PY_FORMAT_SIZE_T "d dimensions while output array `output' has %" PY_FORMAT_SIZE_T "d dimensions", input->ndim, output->ndim);
    return 0;
  }

  if (output) {

    if (input->ndim == 1) {
      if (output->shape[0] != input->shape[0]) {
        PyErr_Format(PyExc_RuntimeError, "1D `output' array should have %" PY_FORMAT_SIZE_T "d elements matching output size, not %" PY_FORMAT_SIZE_T "d elements", input->shape[0], output->shape[0]);
        return 0;
      }
    }
    else { // input->ndim == 2
      if (output->shape[0] != input->shape[0]) {
        PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d rows matching input size, not %" PY_FORMAT_SIZE_T "d rows", input->shape[0], output->shape[0]);
        return 0;
      }
      if (output->shape[1] != input->shape[1]) {
        PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d columns matching input size, not %" PY_FORMAT_SIZE_T "d columns", input->shape[1], output->shape[1]);
        return 0;
      }
    }
  }

  else {

    auto tmp = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_COMPLEX128, input->ndim, input->shape);
    if (!tmp) return 0;
    output = make_safe(tmp);

  }

  return 1;

}

PyObject* fft(PyObject*, PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(input_, output_))
    return 0;

  output = output_.get();

  /** all basic checks are done, can call the operator now **/
  try {

    if (input->ndim == 1) {
      bob::sp::FFT1D op(input->shape[0]);
      op(*PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(output));
    }

    else { // input->ndim == 2
      bob::sp::FFT2D op(input->shape[0], input->shape[1]);
      op(*PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(output));
    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot operate on data: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}

PyObject* ifft(PyObject*, PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(input_, output_))
    return 0;

  output = output_.get();

  /** all basic checks are done, can call the operator now **/
  try {

    if (input->ndim == 1) {
      bob::sp::IFFT1D op(input->shape[0]);
      op(*PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(output));
    }

    else { // input->ndim == 2
      bob::sp::IFFT2D op(input->shape[0], input->shape[1]);
      op(*PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(output));
    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot operate on data: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}

PyObject* fftshift(PyObject*, PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(input_, output_))
    return 0;

  output = output_.get();

  /** all basic checks are done, can call the operator now **/
  try {

    if (input->ndim == 1) {
      bob::sp::fftshift(
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(output)
          );
    }

    else { // input->ndim == 2
      bob::sp::fftshift(
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(output)
          );
    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot operate on data: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}

PyObject* ifftshift(PyObject*, PyObject* args, PyObject* kwds) {

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

  if (!check_and_allocate(input_, output_))
    return 0;

  output = output_.get();

  /** all basic checks are done, can call the operator now **/
  try {

    if (input->ndim == 1) {
      bob::sp::ifftshift(
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,1>(output)
          );
    }

    else { // input->ndim == 2
      bob::sp::ifftshift(
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(input),
          *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(output)
          );
    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot operate on data: unknown exception caught");
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}
