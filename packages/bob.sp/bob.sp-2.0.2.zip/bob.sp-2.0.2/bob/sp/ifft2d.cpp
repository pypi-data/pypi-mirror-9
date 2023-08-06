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
#include <bob.sp/FFT2D.h>

PyDoc_STRVAR(s_fft2d_str, BOB_EXT_MODULE_PREFIX ".IFFT2D");

PyDoc_STRVAR(s_fft2d_doc,
"IFFT2D(shape) -> new IFFT2D operator\n\
\n\
Calculates the inverse FFT of a 2D array/signal. Input and output\n\
arrays are 2D NumPy arrays of type ``complex128``.\n\
"
);

/**
 * Represents either an IFFT2D
 */
typedef struct {
  PyObject_HEAD
  bob::sp::IFFT2D* cxx;
} PyBobSpIFFT2DObject;

extern PyTypeObject PyBobSpIFFT2D_Type; //forward declaration

int PyBobSpIFFT2D_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobSpIFFT2D_Type));
}

static void PyBobSpIFFT2D_Delete (PyBobSpIFFT2DObject* o) {

  delete o->cxx;
  Py_TYPE(o)->tp_free((PyObject*)o);

}

static int PyBobSpIFFT2D_InitCopy
(PyBobSpIFFT2DObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobSpIFFT2D_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobSpIFFT2DObject*>(other);

  try {
    self->cxx = new bob::sp::IFFT2D(*(copy->cxx));
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

static int PyBobSpIFFT2D_InitShape(PyBobSpIFFT2DObject* self, PyObject *args,
    PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"height", "width", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t h = 0;
  Py_ssize_t w = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "nn", kwlist, &h, &w)) return -1;

  try {
    self->cxx = new bob::sp::IFFT2D(h, w);
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

static int PyBobSpIFFT2D_Init(PyBobSpIFFT2DObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:
      return PyBobSpIFFT2D_InitCopy(self, args, kwds);

    case 2:
      return PyBobSpIFFT2D_InitShape(self, args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 argument, but you provided %" PY_FORMAT_SIZE_T "d (see help)", Py_TYPE(self)->tp_name, nargs);

  }

  return -1;

}

static PyObject* PyBobSpIFFT2D_Repr(PyBobSpIFFT2DObject* self) {
  return
# if PY_VERSION_HEX >= 0x03000000
  PyUnicode_FromFormat
# else
  PyString_FromFormat
# endif
  ("%s(height=%zu, width=%zu)", Py_TYPE(self)->tp_name, self->cxx->getHeight(),
   self->cxx->getWidth());
}

static PyObject* PyBobSpIFFT2D_RichCompare (PyBobSpIFFT2DObject* self,
    PyObject* other, int op) {

  if (!PyBobSpIFFT2D_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobSpIFFT2DObject*>(other);

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

PyDoc_STRVAR(s_height_str, "height");
PyDoc_STRVAR(s_height_doc,
"The height of the output vector\n\
");

static PyObject* PyBobSpIFFT2D_GetHeight
(PyBobSpIFFT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getHeight());
}

static int PyBobSpIFFT2D_SetHeight
(PyBobSpIFFT2DObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBob_NumberCheck(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' height can only be set using a number, not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  Py_ssize_t len = PyNumber_AsSsize_t(o, PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setHeight(len);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `height' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_width_str, "width");
PyDoc_STRVAR(s_width_doc,
"The width of the output vector\n\
");

static PyObject* PyBobSpIFFT2D_GetWidth
(PyBobSpIFFT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getWidth());
}

static int PyBobSpIFFT2D_SetWidth
(PyBobSpIFFT2DObject* self, PyObject* o, void* /*closure*/) {

  if (!PyBob_NumberCheck(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' width can only be set using a number, not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  Py_ssize_t len = PyNumber_AsSsize_t(o, PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setWidth(len);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `width' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

PyDoc_STRVAR(s_shape_str, "shape");
PyDoc_STRVAR(s_shape_doc,
"A tuple that represents the size of the output vector\n\
");

static PyObject* PyBobSpIFFT2D_GetShape
(PyBobSpIFFT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("(nn)", self->cxx->getHeight(), self->cxx->getWidth());
}

static int PyBobSpIFFT2D_SetShape
(PyBobSpIFFT2DObject* self, PyObject* o, void* /*closure*/) {

  if (!PySequence_Check(o)) {
    PyErr_Format(PyExc_TypeError, "`%s' shape can only be set using tuples (or sequences), not `%s'", Py_TYPE(self)->tp_name, Py_TYPE(o)->tp_name);
    return -1;
  }

  PyObject* shape = PySequence_Tuple(o);
  auto shape_ = make_safe(shape);

  if (PyTuple_GET_SIZE(shape) != 2) {
    PyErr_Format(PyExc_RuntimeError, "`%s' shape can only be set using 2-position tuples (or sequences), not an %" PY_FORMAT_SIZE_T "d-position sequence", Py_TYPE(self)->tp_name, PyTuple_GET_SIZE(shape));
    return -1;
  }

  Py_ssize_t h = PyNumber_AsSsize_t(PyTuple_GET_ITEM(shape, 0), PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;
  Py_ssize_t w = PyNumber_AsSsize_t(PyTuple_GET_ITEM(shape, 1), PyExc_OverflowError);
  if (PyErr_Occurred()) return -1;

  try {
    self->cxx->setHeight(h);
    self->cxx->setWidth(w);
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

static PyGetSetDef PyBobSpIFFT2D_getseters[] = {
    {
      s_height_str,
      (getter)PyBobSpIFFT2D_GetHeight,
      (setter)PyBobSpIFFT2D_SetHeight,
      s_height_doc,
      0
    },
    {
      s_width_str,
      (getter)PyBobSpIFFT2D_GetWidth,
      (setter)PyBobSpIFFT2D_SetWidth,
      s_width_doc,
      0
    },
    {
      s_shape_str,
      (getter)PyBobSpIFFT2D_GetShape,
      (setter)PyBobSpIFFT2D_SetShape,
      s_shape_doc,
      0
    },
    {0}  /* Sentinel */
};

static PyObject* PyBobSpIFFT2D_Call
(PyBobSpIFFT2DObject* self, PyObject* args, PyObject* kwds) {

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

  if (input->type_num != NPY_COMPLEX128) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 128-bit complex (2x64-bit float) arrays for input array `input'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (output && output->type_num != NPY_COMPLEX128) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 128-bit complex (2x64-bit float) arrays for output array `output'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (input->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 2-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, input->ndim);
    return 0;
  }

  if (output && input->ndim != output->ndim) {
    PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching number of dimensions, but input array `input' has %" PY_FORMAT_SIZE_T "d dimensions while output array `output' has %" PY_FORMAT_SIZE_T "d dimensions", input->ndim, output->ndim);
    return 0;
  }

  if (output && output->shape[0] != (Py_ssize_t)self->cxx->getHeight()) {
    PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d rows matching `%s' output size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->getHeight(), Py_TYPE(self)->tp_name, output->shape[0]);
    return 0;
  }

  if (output && output->shape[1] != (Py_ssize_t)self->cxx->getWidth()) {
    PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d columns matching `%s' output size, not %" PY_FORMAT_SIZE_T "d elements", self->cxx->getWidth(), Py_TYPE(self)->tp_name, output->shape[1]);
    return 0;
  }

  /** if ``output`` was not pre-allocated, do it now **/
  if (!output) {
    Py_ssize_t size[2];
    size[0] = self->cxx->getHeight();
    size[1] = self->cxx->getWidth();
    output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_COMPLEX128, 2, size);
    output_ = make_safe(output);
  }

  /** all basic checks are done, can call the operator now **/
  try {
    self->cxx->operator()(*PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(input),
        *PyBlitzArrayCxx_AsBlitz<std::complex<double>,2>(output));
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

PyTypeObject PyBobSpIFFT2D_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_fft2d_str,                              /*tp_name*/
    sizeof(PyBobSpIFFT2DObject),              /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)PyBobSpIFFT2D_Delete,         /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    (reprfunc)PyBobSpIFFT2D_Repr,             /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    (ternaryfunc)PyBobSpIFFT2D_Call,          /* tp_call */
    (reprfunc)PyBobSpIFFT2D_Repr,             /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    s_fft2d_doc,                              /* tp_doc */
    0,		                                    /* tp_traverse */
    0,		                                    /* tp_clear */
    (richcmpfunc)PyBobSpIFFT2D_RichCompare,   /* tp_richcompare */
    0,		                                    /* tp_weaklistoffset */
    0,		                                    /* tp_iter */
    0,		                                    /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    PyBobSpIFFT2D_getseters,                  /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobSpIFFT2D_Init,             /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
