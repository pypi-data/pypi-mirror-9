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
#include <bob.sp/DCT2D.h>

PyDoc_STRVAR(s_fft2d_str, BOB_EXT_MODULE_PREFIX ".DCT2D");

PyDoc_STRVAR(s_fft2d_doc,
"DCT2D(shape) -> new DCT2D operator\n\
\n\
Calculates the direct DCT of a 2D array/signal. Input and output\n\
arrays are 2D NumPy arrays of type ``float64``.\n\
"
);

/**
 * Represents either an DCT2D
 */
typedef struct {
  PyObject_HEAD
  bob::sp::DCT2D* cxx;
} PyBobSpDCT2DObject;

extern PyTypeObject PyBobSpDCT2D_Type; //forward declaration

int PyBobSpDCT2D_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobSpDCT2D_Type));
}

static void PyBobSpDCT2D_Delete (PyBobSpDCT2DObject* o) {

  delete o->cxx;
  Py_TYPE(o)->tp_free((PyObject*)o);

}

static int PyBobSpDCT2D_InitCopy
(PyBobSpDCT2DObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobSpDCT2D_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobSpDCT2DObject*>(other);

  try {
    self->cxx = new bob::sp::DCT2D(*(copy->cxx));
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

static int PyBobSpDCT2D_InitShape(PyBobSpDCT2DObject* self, PyObject *args,
    PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"height", "width", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t h = 0;
  Py_ssize_t w = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "nn", kwlist, &h, &w)) return -1;

  try {
    self->cxx = new bob::sp::DCT2D(h, w);
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

static int PyBobSpDCT2D_Init(PyBobSpDCT2DObject* self,
    PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:
      return PyBobSpDCT2D_InitCopy(self, args, kwds);

    case 2:
      return PyBobSpDCT2D_InitShape(self, args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 argument, but you provided %" PY_FORMAT_SIZE_T "d (see help)", Py_TYPE(self)->tp_name, nargs);

  }

  return -1;

}

static PyObject* PyBobSpDCT2D_Repr(PyBobSpDCT2DObject* self) {
  return
# if PY_VERSION_HEX >= 0x03000000
  PyUnicode_FromFormat
# else
  PyString_FromFormat
# endif
  ("%s(height=%zu, width=%zu)", Py_TYPE(self)->tp_name, self->cxx->getHeight(),
   self->cxx->getWidth());
}

static PyObject* PyBobSpDCT2D_RichCompare (PyBobSpDCT2DObject* self,
    PyObject* other, int op) {

  if (!PyBobSpDCT2D_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobSpDCT2DObject*>(other);

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

static PyObject* PyBobSpDCT2D_GetHeight
(PyBobSpDCT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getHeight());
}

static int PyBobSpDCT2D_SetHeight
(PyBobSpDCT2DObject* self, PyObject* o, void* /*closure*/) {

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

static PyObject* PyBobSpDCT2D_GetWidth
(PyBobSpDCT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("n", self->cxx->getWidth());
}

static int PyBobSpDCT2D_SetWidth
(PyBobSpDCT2DObject* self, PyObject* o, void* /*closure*/) {

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

static PyObject* PyBobSpDCT2D_GetShape
(PyBobSpDCT2DObject* self, void* /*closure*/) {
  return Py_BuildValue("(nn)", self->cxx->getHeight(), self->cxx->getWidth());
}

static int PyBobSpDCT2D_SetShape
(PyBobSpDCT2DObject* self, PyObject* o, void* /*closure*/) {

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

static PyGetSetDef PyBobSpDCT2D_getseters[] = {
    {
      s_height_str,
      (getter)PyBobSpDCT2D_GetHeight,
      (setter)PyBobSpDCT2D_SetHeight,
      s_height_doc,
      0
    },
    {
      s_width_str,
      (getter)PyBobSpDCT2D_GetWidth,
      (setter)PyBobSpDCT2D_SetWidth,
      s_width_doc,
      0
    },
    {
      s_shape_str,
      (getter)PyBobSpDCT2D_GetShape,
      (setter)PyBobSpDCT2D_SetShape,
      s_shape_doc,
      0
    },
    {0}  /* Sentinel */
};

static PyObject* PyBobSpDCT2D_Call
(PyBobSpDCT2DObject* self, PyObject* args, PyObject* kwds) {

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
    output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64, 2, size);
    output_ = make_safe(output);
  }

  /** all basic checks are done, can call the operator now **/
  try {
    self->cxx->operator()(*PyBlitzArrayCxx_AsBlitz<double,2>(input),
        *PyBlitzArrayCxx_AsBlitz<double,2>(output));
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

PyTypeObject PyBobSpDCT2D_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_fft2d_str,                              /*tp_name*/
    sizeof(PyBobSpDCT2DObject),               /*tp_basicsize*/
    0,                                        /*tp_itemsize*/
    (destructor)PyBobSpDCT2D_Delete,          /*tp_dealloc*/
    0,                                        /*tp_print*/
    0,                                        /*tp_getattr*/
    0,                                        /*tp_setattr*/
    0,                                        /*tp_compare*/
    (reprfunc)PyBobSpDCT2D_Repr,              /*tp_repr*/
    0,                                        /*tp_as_number*/
    0,                                        /*tp_as_sequence*/
    0,                                        /*tp_as_mapping*/
    0,                                        /*tp_hash */
    (ternaryfunc)PyBobSpDCT2D_Call,           /* tp_call */
    (reprfunc)PyBobSpDCT2D_Repr,              /*tp_str*/
    0,                                        /*tp_getattro*/
    0,                                        /*tp_setattro*/
    0,                                        /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    s_fft2d_doc,                              /* tp_doc */
    0,		                                    /* tp_traverse */
    0,		                                    /* tp_clear */
    (richcmpfunc)PyBobSpDCT2D_RichCompare,    /* tp_richcompare */
    0,		                                    /* tp_weaklistoffset */
    0,		                                    /* tp_iter */
    0,		                                    /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    PyBobSpDCT2D_getseters,                   /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobSpDCT2D_Init,              /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
