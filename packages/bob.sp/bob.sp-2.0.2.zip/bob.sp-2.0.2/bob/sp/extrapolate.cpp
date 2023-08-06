/**
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 30 Jan 17:13:00 2014 CET
 *
 * @brief Binds extrapolation to python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.sp/extrapolate.h>

PyDoc_STRVAR(s_border_str, BOB_EXT_MODULE_PREFIX ".BorderType");

PyDoc_STRVAR(s_border_doc,
"BorderType (C++ enumeration) - cannot be instantiated from Python\n\
\n\
Use of the values available in this class as input for ``BorderType``\n\
when required:\n\
\n\
  * Zero\n\
  * Constant\n\
  * NearestNeighbour\n\
  * Circular\n\
  * Mirror\n\
\n\
A dictionary containing all names and values available for this\n\
enumeration is available through the attribute ``entries``.\n\
"
);

extern PyTypeObject PyBobSpExtrapolationBorder_Type; ///< forward

static int insert_item_string(PyObject* dict, PyObject* entries,
    const char* key, Py_ssize_t value) {
  auto v = make_safe(Py_BuildValue("n", value));
  if (PyDict_SetItemString(dict, key, v.get()) < 0) return -1;
  return PyDict_SetItemString(entries, key, v.get());
}

static PyObject* create_enumerations() {
  auto retval = PyDict_New();
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  auto entries = PyDict_New();
  if (!entries) return 0;
  auto entries_ = make_safe(entries);

  if (insert_item_string(retval, entries, "Zero",
        bob::sp::Extrapolation::BorderType::Zero) < 0) return 0;
  if (insert_item_string(retval, entries, "Constant",
        bob::sp::Extrapolation::BorderType::Constant) < 0) return 0;
  if (insert_item_string(retval, entries, "NearestNeighbour",
        bob::sp::Extrapolation::BorderType::NearestNeighbour) < 0) return 0;
  if (insert_item_string(retval, entries, "Circular",
        bob::sp::Extrapolation::BorderType::Circular) < 0) return 0;
  if (insert_item_string(retval, entries, "Mirror",
        bob::sp::Extrapolation::BorderType::Mirror) < 0) return 0;

  if (PyDict_SetItemString(retval, "entries", entries) < 0) return 0;

  return Py_BuildValue("O", retval);
}

int PyBobSpExtrapolationBorder_Converter(PyObject* o,
    bob::sp::Extrapolation::BorderType* b) {

  Py_ssize_t v = PyNumber_AsSsize_t(o, PyExc_OverflowError);
  if (v == -1 && PyErr_Occurred()) return 0;
  bob::sp::Extrapolation::BorderType value =
    (bob::sp::Extrapolation::BorderType)v;

  switch (value) {
    case bob::sp::Extrapolation::BorderType::Zero:
    case bob::sp::Extrapolation::BorderType::Constant:
    case bob::sp::Extrapolation::BorderType::NearestNeighbour:
    case bob::sp::Extrapolation::BorderType::Circular:
    case bob::sp::Extrapolation::BorderType::Mirror:
      *b = value;
      return 1;
    default:
      PyErr_Format(PyExc_ValueError, "border parameter must be set to one of the integer values defined in `%s'", PyBobSpExtrapolationBorder_Type.tp_name);
  }

  return 0;

}

static int PyBobSpExtrapolationBorder_Init(PyObject* self, PyObject*, PyObject*) {

  PyErr_Format(PyExc_NotImplementedError, "cannot initialize C++ enumeration bindings `%s' - use one of the class' attached attributes instead", Py_TYPE(self)->tp_name);
  return -1;

}

PyTypeObject PyBobSpExtrapolationBorder_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_border_str,                             /* tp_name */
    sizeof(PyBobSpExtrapolationBorder_Type),  /* tp_basicsize */
    0,                                        /* tp_itemsize */
    0,                                        /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    0,                                        /* tp_call */
    0,                                        /* tp_str*/
    0,                                        /* tp_getattro*/
    0,                                        /* tp_setattro*/
    0,                                        /* tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags*/
    s_border_doc,                             /* tp_doc */
    0,		                                    /* tp_traverse */
    0,		                                    /* tp_clear */
    0,                                        /* tp_richcompare */
    0,		                                    /* tp_weaklistoffset */
    0,		                                    /* tp_iter */
    0,		                                    /* tp_iternext */
    0,                                        /* tp_methods */
    0,                                        /* tp_members */
    0,                                        /* tp_getset */
    0,                                        /* tp_base */
    create_enumerations(),                    /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    PyBobSpExtrapolationBorder_Init,          /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};

template <typename T> PyObject* inner_extrapolate (PyBlitzArrayObject* src,
    PyBlitzArrayObject* dst, bob::sp::Extrapolation::BorderType& border,
    PyObject* value) {

  //converts value into a proper scalar
  T c_value = 0;
  if (value) {
    c_value = PyBlitzArrayCxx_AsCScalar<T>(value);
    if (PyErr_Occurred()) return 0;
  }

  try {
    switch (src->ndim) {
      case 1:
        bob::sp::extrapolate(*PyBlitzArrayCxx_AsBlitz<T,1>(src),
            *PyBlitzArrayCxx_AsBlitz<T,1>(dst), border, c_value);
        break;
      case 2:
        bob::sp::extrapolate(*PyBlitzArrayCxx_AsBlitz<T,2>(src),
            *PyBlitzArrayCxx_AsBlitz<T,2>(dst), border, c_value);
        break;
      default:
        PyErr_Format(PyExc_TypeError, "extrapolation does not support arrays with %" PY_FORMAT_SIZE_T "d dimensions", src->ndim);
        return 0;
    }
  }
  catch (std::exception& e) {
    PyErr_Format(PyExc_RuntimeError, "%s", e.what());
    return 0;
  }

  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "caught unknown exception while calling C++ bob::spp::extrapolate");
    return 0;
  }

  Py_RETURN_NONE;

}

PyObject* extrapolate(PyObject*, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {
    "src",
    "dst",
    "border",
    "value",
    0 /* Sentinel */
  };
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* src = 0;
  PyBlitzArrayObject* dst = 0;
  bob::sp::Extrapolation::BorderType border = bob::sp::Extrapolation::Zero;
  PyObject* value = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&|O&O",
        kwlist,
        &PyBlitzArray_Converter, &src,
        &PyBlitzArray_OutputConverter, &dst,
        &PyBobSpExtrapolationBorder_Converter, &border,
        &value)) return 0;
  auto src_ = make_safe(src);
  auto dst_ = make_safe(dst);

  if (src->type_num != dst->type_num) {
    PyErr_Format(PyExc_TypeError, "source and destination arrays must have the same data types (src: `%s' != dst: `%s')",
        PyBlitzArray_TypenumAsString(src->type_num),
        PyBlitzArray_TypenumAsString(dst->type_num));
    return 0;
  }

  if (src->ndim != dst->ndim) {
    PyErr_Format(PyExc_TypeError, "source and destination arrays must have the same number of dimensions types (src: `%" PY_FORMAT_SIZE_T "d' != dst: `%" PY_FORMAT_SIZE_T "d')", src->ndim, dst->ndim);
    return 0;
  }

  if (src->ndim != 1 && src->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "source and destination arrays must have one or two dimensions, not `%" PY_FORMAT_SIZE_T "d", src->ndim);
    return 0;
  }

  switch (src->type_num) {
    case NPY_BOOL:
      return inner_extrapolate<bool>(src, dst, border, value);
    case NPY_INT8:
      return inner_extrapolate<int8_t>(src, dst, border, value);
    case NPY_INT16:
      return inner_extrapolate<int16_t>(src, dst, border, value);
    case NPY_INT32:
      return inner_extrapolate<int32_t>(src, dst, border, value);
    case NPY_INT64:
      return inner_extrapolate<int64_t>(src, dst, border, value);
    case NPY_UINT8:
      return inner_extrapolate<uint8_t>(src, dst, border, value);
    case NPY_UINT16:
      return inner_extrapolate<uint16_t>(src, dst, border, value);
    case NPY_UINT32:
      return inner_extrapolate<uint32_t>(src, dst, border, value);
    case NPY_UINT64:
      return inner_extrapolate<uint64_t>(src, dst, border, value);
    case NPY_FLOAT32:
      return inner_extrapolate<float>(src, dst, border, value);
    case NPY_FLOAT64:
      return inner_extrapolate<double>(src, dst, border, value);
    case NPY_COMPLEX64:
      return inner_extrapolate<std::complex<float>>(src, dst, border, value);
    case NPY_COMPLEX128:
      return inner_extrapolate<std::complex<double>>(src, dst, border, value);
    default:
      PyErr_Format(PyExc_TypeError, "extrapolation from `%s' (%d) is not supported", PyBlitzArray_TypenumAsString(src->type_num), src->type_num);
  }

  return 0;

}
