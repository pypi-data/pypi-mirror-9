/**
 * @date Mon Jun 20 11:47:58 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Python bindings to statistical methods
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/defines.h>
#include <bob.sp/DCT1D.h>

PyDoc_STRVAR(s_fft1d_str, BOB_EXT_MODULE_PREFIX ".IDCT1D");

PyDoc_STRVAR(s_fft1d_doc,
"IDCT1D(shape) -> new IDCT1D operator\n\
\n\
Calculates the inverse DCT of a 1D array/signal. Input and output\n\
arrays are 1D NumPy arrays of type ``float64``.\n\
"
);

/**
 * Represents either an IDCT1D
 */
typedef struct {
  PyObject_HEAD
  bob::sp::IDCT1D* cxx;
} PyBobSpIDCT1DObject;

extern PyTypeObject PyBobSpIDCT1D_Type; //forward declaration

int PyBobSpIDCT1D_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobSpIDCT1D_Type));
}

static void PyBobSpIDCT1D_Delete (PyBobSpIDCT1DObject* o) {

  delete o->cxx;
  Py_TYPE(o)->tp_free((PyObject*)o);

}

static int PyBobSpIDCT1D_InitCopy
(PyBobSpIDCT1DObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobSpIDCT1D_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobSpIDCT1DObject*>(other);

  try {
    self->cxx = new bob::sp::IDCT1D(*(copy->cxx));
    if (!self->cxx) {
      PyErr_Format(PyExc_MemoryError, "cannot create new object of type `%s' - no more memory", Py_TYPE(self)->tp_name);
      return -1;
    }
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

static int PyBobSpIDCT1D_InitShape(PyBobSpIDCT1DObject* self, PyObject *args,
    PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"length", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t length = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &length)) return -1;

  try {
    self->cxx = new bob::sp::IDCT1D(length);
    if (!self->cxx) {
      PyErr_Format(PyExc_MemoryError, "cannot create new object of type `%s' - no more memory", Py_TYPE(self)->tp_name);
      return -1;
    }
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0; ///< SUCCESS

}

static int PyBobSpIDCT1D_Init(PyBobSpIDCT1DObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:

      {

        PyObject* arg = 0; ///< borrowed (don't delete)
        if (PyTuple_Size(args)) arg = PyTuple_GET_ITEM(args, 0);
        else {
          PyObject* tmp = PyDict_Values(kwds);
          auto tmp_ = make_safe(tmp);
          arg = PyList_GET_ITEM(tmp, 0);
        }

        if (PyBob_NumberCheck(arg)) {
          return PyBobSpIDCT1D_InitShape(self, args, kwds);
        }

        if (PyBobSpIDCT1D_Check(arg)) {
          return PyBobSpIDCT1D_InitCopy(self, args, kwds);
        }

        PyErr_Format(PyExc_TypeError, "cannot initialize `%s' with `%s' (see help)", Py_TYPE(self)->tp_name, Py_TYPE(arg)->tp_name);

      }

      break;

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 argument, but you provided %" PY_FORMAT_SIZE_T "d (see help)", Py_TYPE(self)->tp_name, nargs);

  }

  return -1;

}

static PyObject* PyBobSpIDCT1D_Repr(PyBobSpIDCT1DObject* self) {
  return
# if PY_VERSION_HEX >= 0x03000000
  PyUnicode_FromFormat
# else
  PyString_FromFormat
# endif
  ("%s(length=%zu)", Py_TYPE(self)->tp_name, self->cxx->getLength());
}

static PyObject* PyBobSpIDCT1D_RichCompare (PyBobSpIDCT1DObject* self,
    PyObject* other, int op) {

  if (!PyBobSpIDCT1D_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobSpIDCT1DObject*>(other);

  switch (op) {
    case Py_EQ:
      if (self->cxx->operator==(*other_->cxx)) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    case Py_NE:
      if (self->cxx->operator!=(*other_->cxx)) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    default:
      Py_INCREF(Py_NotImplemented);
      return Py_NotImplemented;
  }

}

PyDoc_STRVAR(s_length_str, "length");
PyDoc_STRVAR(s_length_doc,
"The length of the output vector\n\
");

static PyObject* PyBobSpIDCT1D_GetLength
(PyBobSpIDCT1DObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getLength());
}

static int PyBobSpIDCT1D_SetLength
(PyBobSpIDCT1DObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBob_NumberCheck(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' length can only be set using a number, not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  Py_ssize_t len = PyNumber_AsSsize_t(o, PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setLength(len);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `length' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_shape_str, "shape");
PyDoc_STRVAR(s_shape_doc,
"A tuple that represents the size of the output vector\n\
");

static PyObject* PyBobSpIDCT1D_GetShape
(PyBobSpIDCT1DObject* self, void* /*closure*/) {
  return Py_BuildValue("(n)", self->cxx->getLength());
}

static int PyBobSpIDCT1D_SetShape
(PyBobSpIDCT1DObject* self, PyObject* o, void* /*closure*/) {

  if (!PySequence_Check(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' shape can only be set using tuples (or sequences), not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  PyObject* shape = PySequence_Tuple(o);
  auto shape_ = make_safe(shape);

  if (PyTuple_GET_SIZE(shape) != 1) {
    PyErr_Format(PyExc_RuntimeError, "`%s' shape can only be set using 1-position tuples (or sequences), not an %" PY_FORMAT_SIZE_T "d-position sequence", Py_TYPE(self)->tp_name, PyTuple_GET_SIZE(shape));
    return -1;
  }

  Py_ssize_t len = PyNumber_AsSsize_t(PyTuple_GET_ITEM(shape, 0), PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setLength(len);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `shape' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static PyGetSetDef PyBobSpIDCT1D_getseters[] = {
    {
      s_length_str,
      (getter)PyBobSpIDCT1D_GetLength,
      (setter)PyBobSpIDCT1D_SetLength,
      s_length_doc,
      0
    },
    {
      s_shape_str,
      (getter)PyBobSpIDCT1D_GetShape,
      (setter)PyBobSpIDCT1D_SetShape,
      s_shape_doc,
      0
    },
    {0}  /* Sentinel */
};

static PyObject* PyBobSpIDCT1D_Call
(PyBobSpIDCT1DObject* self, PyObject* args, PyObject* kwds) {

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

  if (input->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (output && output->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 64-bit float arrays for output array `output'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (input->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 1-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, input->ndim);
    return 0;
  }

  if (output && input->ndim != output->ndim) {
    PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching number of dimensions, but input array `input' has %" PY_FORMAT_SIZE_T "d dimensions while output array `output' has %" PY_FORMAT_SIZE_T "d dimensions", input->ndim, output->ndim);
    return 0;
  }

  if (output && output->shape[0] != (Py_ssize_t)self->cxx->getLength()) {
    PyErr_Format(PyExc_RuntimeError, "1D `output' array should have %" PY_FORMAT_SIZE_T "d elements matching `%s' output size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->getLength(), Py_TYPE(self)->tp_name, output->shape[0]);
    return 0;
  }

  /** if ``output`` was not pre-allocated, do it now **/
  if (!output) {
    Py_ssize_t length = self->cxx->getLength();
    output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 1, &length);
    output_ = make_safe(output);
  }

  /** all basic checks are done, can call the operator now **/
  try {
    self->cxx->operator()(*PyBlitzArrayCxx_AsBlitz<double,1>(input),
        *PyBlitzArrayCxx_AsBlitz<double,1>(output));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot operate on data: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}

PyTypeObject PyBobSpIDCT1D_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_fft1d_str,                              /*tp_name*/
    sizeof(PyBobSpIDCT1DObject),              /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)PyBobSpIDCT1D_Delete,         /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    (reprfunc)PyBobSpIDCT1D_Repr,             /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    (ternaryfunc)PyBobSpIDCT1D_Call,          /* tp_call */
    (reprfunc)PyBobSpIDCT1D_Repr,             /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    s_fft1d_doc,                              /* tp_doc */
    0,		                                    /* tp_traverse */
    0,		                                    /* tp_clear */
    (richcmpfunc)PyBobSpIDCT1D_RichCompare,   /* tp_richcompare */
    0,		                                    /* tp_weaklistoffset */
    0,		                                    /* tp_iter */
    0,		                                    /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    PyBobSpIDCT1D_getseters,                  /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobSpIDCT1D_Init,             /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
