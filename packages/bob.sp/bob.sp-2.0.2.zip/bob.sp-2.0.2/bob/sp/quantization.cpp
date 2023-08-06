/**
 * @author Ivana Chingovska <ivana.chingovska@idiap.ch>
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 Jan 14:26:40 2014
 *
 * @brief Support for quantization at our signal processing toolbox.
 *
 * @todo Use enumerations (see example in "extrapolate.cpp") instead of strings
 * as return value for `quantization_type'.
 *
 * @todo Clean-up: initialization code is pretty tricky. There are different
 * ways to initialize the functor which are pretty much disjoint. Maybe these
 * should be different types?
 *
 * @todo Extend: quantization class does not support generic input array.
 * Limited to uint16 and uint8. Output is always in uint32. Ideally, the output
 * should be dependent on the range the user wants to use. Input should be
 * arbitrary.
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.sp/Quantization.h>

PyDoc_STRVAR(s_quantization_str, BOB_EXT_MODULE_PREFIX ".Quantization");

PyDoc_STRVAR(s_quantization_doc,
"Quantization(dtype, [rounding=False, [num_levels=-1, [min_level=None, [max_level=None]]]])\n\
Quantization(quantization_table)\n\
Quantization(other)\n\
\n\
Functor to quantize 1D or 2D signals into different number of\n\
levels. At the moment, only ``uint8`` and ``uint16`` data\n\
types are supported. The output array returned by this functor\n\
will always have a ``uint32`` data type.\n\
\n\
Parameters:\n\
\n\
dtype\n\
  (numpy.dtype) The data type of arrays that are going to be **input**\n\
  by this functor. Currently supported values are ``uint8`` and\n\
  ``uint16``.\n\
\n\
rounding\n\
  (bool) If set to ``True`` (defaults to ``False``), performs\n\
  Matlab-like uniform quantization with rounding (see\n\
  http://www.mathworks.com/matlabcentral/newsreader/view_thread/275291).\n\
\n\
num_levels\n\
  (int) the number of quantization levels. The default is the total\n\
  number of discrete values permitted by the data type. For example,\n\
  ``uint8`` allows for 256 levels.\n\
\n\
min_level\n\
  (scalar) Input values smaller than or equal to this value are\n\
  scaled to this value prior to quantization. As a result, they\n\
  will be scaled in the lowest quantization level. The data type\n\
  of this scalar should be coercible to the datatype of the input.\n\
\n\
max_level\n\
  (scalar) Input values higher than this value are scaled to this\n\
  value prior to quantization. As a result, they will be scaled in\n\
  the highest qunatization level. The data type of this scalar\n\
  should be coercible to the datatype of the input.\n\
\n\
quantization_table\n\
  (array) A 1-dimensional array matching the data type of ``input``\n\
  containing user-specified thresholds for the quantization. If\n\
  Each element corresponds to the lower boundary of the particular\n\
  quantization level. Eg. ``array([ 0,  5, 10])`` means quantization\n\
  in 3 levels. Input values in the range :math:`[0,4]` will be quantized\n\
  to level 0, input values in the range :math:`[5,9]` will be\n\
  quantized to level 1 and input values in the range\n\
  :math:`[10-\\text{max}]` will be quantized to level 2.\n\
\n\
other\n\
  (Quantization) You can also initialize a Quantization object\n\
  by passing another Quantization object as constructor parameter.\n\
  This will create a deep-copy of this Quantization object.\n\
\n\
Once this object has been created, it can be used through its ``()``\n\
operator, by passing ``input`` and ``output`` parameters:\n\
\n\
input\n\
  (array) a 1 or 2-dimensional ``uint8`` or ``uint16`` array of any\n\
  size.\n\
\n\
output\n\
  (array) The array where to store the output. This array should\n\
  have the same dimensions of the input array, but have data type\n\
  ``uint32``. If this array is not provided, a new one is allocated\n\
  internally and returned.\n\
\n\
"
);

/**
 * Represents either a bob::sp::Quantization<T> object
 */
typedef struct {
  PyObject_HEAD
  int type_num;
  boost::shared_ptr<void> cxx;
} PyBobSpQuantizationObject;

extern PyTypeObject PyBobSpQuantization_Type; //forward declaration

int PyBobSpQuantization_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobSpQuantization_Type));
}

static void PyBobSpQuantization_Delete (PyBobSpQuantizationObject* self) {

  self->cxx.reset();
  Py_TYPE(self)->tp_free((PyObject*)self);

}

static int PyBobSpQuantization_InitCopy
(PyBobSpQuantizationObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"other", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* other = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kwlist,
        &PyBobSpQuantization_Type, &other)) return -1;

  auto copy = reinterpret_cast<PyBobSpQuantizationObject*>(other);

  try {
    self->type_num = copy->type_num;
    switch (self->type_num) {
      case NPY_UINT8:
        self->cxx.reset(new bob::sp::Quantization<uint8_t>(*boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(copy->cxx)));
      case NPY_UINT16:
        self->cxx.reset(new bob::sp::Quantization<uint16_t>(*boost::static_pointer_cast<bob::sp::Quantization<uint16_t>>(copy->cxx)));
      default:
        PyErr_Format(PyExc_TypeError, "`%s' only accepts `uint8' or `uint16' as data types (not `%s')", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(copy->type_num));
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

template <typename T> int initialize(PyBobSpQuantizationObject* self,
    bob::sp::quantization::QuantizationType type, Py_ssize_t levels,
    PyObject* min, PyObject* max) {

  // calculates all missing elements:
  T c_min = std::numeric_limits<T>::min();
  if (min) {
    c_min = PyBlitzArrayCxx_AsCScalar<T>(min);
    if (PyErr_Occurred()) return -1;
  }

  T c_max = std::numeric_limits<T>::max();
  if (max) {
    c_max = PyBlitzArrayCxx_AsCScalar<T>(max);
    if (PyErr_Occurred()) return -1;
  }

  if (levels <= 0) levels = c_max - c_min + 1;

  try {
    self->cxx.reset(new bob::sp::Quantization<T>(type, levels, c_min, c_max));
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

static int PyBobSpQuantization_InitDiscrete(PyBobSpQuantizationObject* self,
    PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {
    "dtype",
    "rounding",
    "num_levels",
    "min_level",
    "max_level",
    0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  int type_num = NPY_NOTYPE;
  PyObject* rounding = 0;
  Py_ssize_t levels = -1;
  PyObject* min = 0;
  PyObject* max = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|O!nOO", kwlist,
        &PyBlitzArray_TypenumConverter, &type_num,
        &PyBool_Type, &rounding,
        &levels,
        &min,
        &max
        )) return -1;

  if (type_num != NPY_UINT8 && type_num != NPY_UINT16) {
  }

  bob::sp::quantization::QuantizationType rounding_enum =
    bob::sp::quantization::UNIFORM;
  if (rounding) {
    rounding_enum = PyObject_IsTrue(rounding)?bob::sp::quantization::UNIFORM_ROUNDING:bob::sp::quantization::UNIFORM;
  }

  self->type_num = type_num;
  switch (type_num) {
    case NPY_UINT8:
      return initialize<uint8_t>(self, rounding_enum, levels, min, max);
    case NPY_UINT16:
      return initialize<uint16_t>(self, rounding_enum, levels, min, max);
    default:
      PyErr_Format(PyExc_TypeError, "`%s' only accepts `uint8' or `uint16' as data types (not `%s')", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(type_num));
  }

  return -1; ///< FAIULRE
}

static int PyBobSpQuantization_InitTable(PyBobSpQuantizationObject* self,
    PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"quantization_table", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* table = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist,
        &PyBlitzArray_Converter, &table)) return -1;

  auto table_ = make_safe(table);

  if (table->ndim != 1) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 1-dimensional arrays as quantization table (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, table->ndim);
    return -1;
  }

  if (table->type_num != NPY_UINT8 && table->type_num != NPY_UINT16) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 1-dimensional `uint8' or `uint16' arrays as quantization tables (not `%s' arrays)", Py_TYPE(self)->tp_name,
        PyBlitzArray_TypenumAsString(table->type_num));
    return -1;
  }

  try {
    self->type_num = table->type_num;
    if (table->type_num == NPY_UINT8) {
      self->cxx.reset(new bob::sp::Quantization<uint8_t>(*PyBlitzArrayCxx_AsBlitz<uint8_t,1>(table)));
    }
    else {
      self->cxx.reset(new bob::sp::Quantization<uint16_t>(*PyBlitzArrayCxx_AsBlitz<uint16_t,1>(table)));
    }
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

static int PyBobSpQuantization_Init(PyBobSpQuantizationObject* self,
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

        if (PyBlitzArray_Check(arg) || PyArray_Check(arg)) {
          return PyBobSpQuantization_InitTable(self, args, kwds);
        }
        else if (PyBobSpQuantization_Check(arg)) {
          return PyBobSpQuantization_InitCopy(self, args, kwds);
        }
        else {
          return PyBobSpQuantization_InitDiscrete(self, args, kwds);
        }

        PyErr_Format(PyExc_TypeError, "cannot initialize `%s' with `%s' (see help)", Py_TYPE(self)->tp_name, Py_TYPE(arg)->tp_name);

      }

      break;

    case 2:
    case 3:
    case 4:
    case 5:
      return PyBobSpQuantization_InitDiscrete(self, args, kwds);

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1, 2, 3, 4 or 5 arguments for initialization, but you provided %" PY_FORMAT_SIZE_T "d (see help)", Py_TYPE(self)->tp_name, nargs);

  }

  return -1;

}

PyDoc_STRVAR(s_dtype_str, "dtype");
PyDoc_STRVAR(s_dtype_doc,
"(numpy.dtype) The data type of arrays that are going to be **input**\n\
by this functor. Currently supported values are ``uint8`` and\n\
``uint16``.\n\
");

static PyObject* PyBobSpQuantization_GetDtype
(PyBobSpQuantizationObject* self, void* /*closure*/) {
  PyArray_Descr* retval = PyArray_DescrFromType(self->type_num);
  if (retval) Py_INCREF(reinterpret_cast<PyObject*>(retval));
  return reinterpret_cast<PyObject*>(retval);
}

PyDoc_STRVAR(s_quantization_type_str, "quantization_type");
PyDoc_STRVAR(s_quantization_type_doc,
"(str) Possible values of this parameter:\n\
\n\
uniform\n\
  uniform quantization of the input signal within the range\n\
  between ``min_level`` and ``max_level``\n\
\n\
uniform_rounding\n\
  same as ``uniform`` above, but implemented in a similar way\n\
  to Matlab quantization\n\
  (see http://www.mathworks.com/matlabcentral/newsreader/view_thread/275291);\n\
\n\
user_spec\n\
  quantization according to user-specified quantization table\n\
  of thresholds.\n\
");

static PyObject* PyBobSpQuantization_GetQuantizationType
(PyBobSpQuantizationObject* self, void* /*closure*/) {
  bob::sp::quantization::QuantizationType type;

  switch(self->type_num) {
    case NPY_UINT8:
      type = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getType();
      break;
    case NPY_UINT16:
      type = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getType();
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  switch(type) {
    case bob::sp::quantization::UNIFORM:
      return Py_BuildValue("s", "uniform");
    case bob::sp::quantization::UNIFORM_ROUNDING:
      return Py_BuildValue("s", "uniform_rounding");
    case bob::sp::quantization::USER_SPEC:
      return Py_BuildValue("s", "user_spec");
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with quantization method == `%d' -- DEBUG ME", Py_TYPE(self)->tp_name, (int)type);
  }

  return 0;
}

PyDoc_STRVAR(s_num_levels_str, "num_levels");
PyDoc_STRVAR(s_num_levels_doc,
"(int) the number of quantization levels. The default is the total\n\
number of discrete values permitted by the data type. For example,\n\
``uint8`` allows for 256 levels.\n\
");

static PyObject* PyBobSpQuantization_GetNumLevels
(PyBobSpQuantizationObject* self, void* /*closure*/) {

  Py_ssize_t v;

  switch(self->type_num) {
    case NPY_UINT8:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getNumLevels();
      break;
    case NPY_UINT16:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getNumLevels();
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  return Py_BuildValue("n", v);

}

PyDoc_STRVAR(s_min_level_str, "min_level");
PyDoc_STRVAR(s_min_level_doc,
"Input values smaller than or equal to this value are\n\
scaled to this value prior to quantization. As a result, they\n\
will be scaled in the lowest quantization level. The data type\n\
of this scalar should be coercible to the datatype of the input.\n\
");

static PyObject* PyBobSpQuantization_GetMinLevel
(PyBobSpQuantizationObject* self, void* /*closure*/) {

  int v;

  switch(self->type_num) {
    case NPY_UINT8:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getMinLevel();
      break;
    case NPY_UINT16:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getMinLevel();
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  return Py_BuildValue("i", v);

}

PyDoc_STRVAR(s_max_level_str, "max_level");
PyDoc_STRVAR(s_max_level_doc,
"(scalar) Input values higher than this value are scaled to this\n\
value prior to quantization. As a result, they will be scaled in\n\
the highest qunatization level. The data type of this scalar\n\
should be coercible to the datatype of the input.\n\
");

static PyObject* PyBobSpQuantization_GetMaxLevel
(PyBobSpQuantizationObject* self, void* /*closure*/) {

  int v;

  switch(self->type_num) {
    case NPY_UINT8:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getMaxLevel();
      break;
    case NPY_UINT16:
      v = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getMaxLevel();
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  return Py_BuildValue("i", v);

}

PyDoc_STRVAR(s_quantization_table_str, "quantization_table");
PyDoc_STRVAR(s_quantization_table_doc,
"(array) A 1-dimensional array matching the data type of ``input``\n\
containing user-specified thresholds for the quantization. If\n\
Each element corresponds to the lower boundary of the particular\n\
quantization level. Eg. ``array([ 0,  5, 10])`` means quantization\n\
in 3 levels. Input values in the range :math:`[0,4]` will be quantized\n\
to level 0, input values in the range :math:`[5,9]` will be\n\
quantized to level 1 and input values in the range\n\
:math:`[10-\\text{max}]` will be quantized to level 2.\n\
");

static PyObject* PyBobSpQuantization_GetQuantizationTable
(PyBobSpQuantizationObject* self, void* /*closure*/) {

  PyObject* retval;

  switch(self->type_num) {
    case NPY_UINT8:
      retval = PyBlitzArrayCxx_NewFromConstArray(boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->getThresholds());
      break;
    case NPY_UINT16:
      retval = PyBlitzArrayCxx_NewFromConstArray(boost::static_pointer_cast<bob::sp::Quantization<uint16_t>>(self->cxx)->getThresholds());
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  if (!retval) return 0;

  return PyBlitzArray_NUMPY_WRAP(retval);

}

static PyGetSetDef PyBobSpQuantization_getseters[] = {
    {
      s_dtype_str,
      (getter)PyBobSpQuantization_GetDtype,
      0,
      s_dtype_doc,
      0
    },
    {
      s_quantization_type_str,
      (getter)PyBobSpQuantization_GetQuantizationType,
      0,
      s_quantization_type_doc,
      0
    },
    {
      s_num_levels_str,
      (getter)PyBobSpQuantization_GetNumLevels,
      0,
      s_num_levels_doc,
      0
    },
    {
      s_min_level_str,
      (getter)PyBobSpQuantization_GetMinLevel,
      0,
      s_min_level_doc,
      0
    },
    {
      s_max_level_str,
      (getter)PyBobSpQuantization_GetMaxLevel,
      0,
      s_max_level_doc,
      0
    },
    {
      s_quantization_table_str,
      (getter)PyBobSpQuantization_GetQuantizationTable,
      0,
      s_quantization_table_doc,
      0
    },
    {0}  /* Sentinel */
};

template <typename T>
static void call(PyBobSpQuantizationObject* self,
    PyBlitzArrayObject* input, PyBlitzArrayObject* output) {

  auto op = boost::static_pointer_cast<bob::sp::Quantization<T>>(self->cxx);

  switch(input->ndim) {
    case 1:
      op->operator()(*PyBlitzArrayCxx_AsBlitz<T,1>(input),
          *PyBlitzArrayCxx_AsBlitz<uint32_t,1>(output));
      break;
    case 2:
      op->operator()(*PyBlitzArrayCxx_AsBlitz<T,2>(input),
          *PyBlitzArrayCxx_AsBlitz<uint32_t,2>(output));
      break;
    default:
      throw std::runtime_error("don't know how to cope with Quantization object with unknown dtype -- DEBUG ME");
  }

}

static PyObject* PyBobSpQuantization_Call
(PyBobSpQuantizationObject* self, PyObject* args, PyObject* kwds) {

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

  if (self->type_num != input->type_num) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports `%s' arrays for `input', not `%s'", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num),
        PyBlitzArray_TypenumAsString(input->type_num));
    return 0;
  }

  if (output && output->type_num != NPY_UINT32) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports `uint32' arrays for `output', not `%s'", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(output->type_num));
    return 0;
  }

  if (input->ndim < 1 || input->ndim > 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only accepts 1 or 2-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, input->ndim);
    return 0;
  }

  if (output && input->ndim != output->ndim) {
    PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching number of dimensions, but input array `input' has %" PY_FORMAT_SIZE_T "d dimensions while output array `output' has %" PY_FORMAT_SIZE_T "d dimensions", input->ndim, output->ndim);
    return 0;
  }

  if (input->ndim == 1) {
    if (output && output->shape[0] != input->shape[0]) {
      PyErr_Format(PyExc_RuntimeError, "1D `output' array should have %" PY_FORMAT_SIZE_T "d elements matching `%s' input size, not %" PY_FORMAT_SIZE_T "d elements", input->shape[0], Py_TYPE(self)->tp_name, output->shape[0]);
      return 0;
    }
  }
  else {
    if (output && output->shape[1] != input->shape[1]) {
      PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d columns matching input size, not %" PY_FORMAT_SIZE_T "d columns", input->shape[1], output->shape[1]);
      return 0;
    }
    if (output && input->shape[0] != output->shape[0]) {
      PyErr_Format(PyExc_RuntimeError, "2D `output' array should have %" PY_FORMAT_SIZE_T "d rows matching `input' size, not %" PY_FORMAT_SIZE_T "d rows", input->shape[0], output->shape[0]);
      return 0;
    }
  }

  /** if ``output`` was not pre-allocated, do it now **/
  if (!output) {
    output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_UINT32,
        input->ndim, input->shape);
    output_ = make_safe(output);
  }

  /** all basic checks are done, can call the functor now **/
  try {
    switch (self->type_num) {
      case NPY_UINT8:
        call<uint8_t>(self, input, output);
        break;
      case NPY_UINT16:
        call<uint16_t>(self, input, output);
        break;
      default:
        PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
        return 0;
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot forward data: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", output));

}

PyDoc_STRVAR(s_quantization_level_str, "quantization_level");
PyDoc_STRVAR(s_quantization_level_doc,
"Calculates the quantization level for a single input value,\n\
given the current threshold table.\n\
");

static PyObject* PyBobSpQuantization_QuantizationLevel
(PyBobSpQuantizationObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"input", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* input = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &input)) return 0;

  int output;

  switch (self->type_num) {
    case NPY_UINT8:
      {
        auto c_input = PyBlitzArrayCxx_AsCScalar<uint8_t>(input);
        if (PyErr_Occurred()) return 0;
        output = boost::static_pointer_cast<bob::sp::Quantization<uint8_t>>(self->cxx)->quantization_level(c_input);
      }
      break;
    case NPY_UINT16:
      {
        auto c_input = PyBlitzArrayCxx_AsCScalar<uint16_t>(input);
        if (PyErr_Occurred()) return 0;
        output = boost::static_pointer_cast<bob::sp::Quantization<uint16_t>>(self->cxx)->quantization_level(c_input);
      }
      break;
    default:
      PyErr_Format(PyExc_RuntimeError, "don't know how to cope with `%s' object with dtype == `%s' -- DEBUG ME", Py_TYPE(self)->tp_name, PyBlitzArray_TypenumAsString(self->type_num));
      return 0;
  }

  return Py_BuildValue("n", output);

}

static PyMethodDef PyBobSpQuantization_methods[] = {
  {
    s_quantization_level_str,
    (PyCFunction)PyBobSpQuantization_QuantizationLevel,
    METH_VARARGS|METH_KEYWORDS,
    s_quantization_level_doc,
  },
  {0} /* Sentinel */
};

PyTypeObject PyBobSpQuantization_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_quantization_str,                       /* tp_name */
    sizeof(PyBobSpQuantizationObject),        /* tp_basicsize */
    0,                                        /* tp_itemsize */
    (destructor)PyBobSpQuantization_Delete,   /* tp_dealloc */
    0,                                        /* tp_print */
    0,                                        /* tp_getattr */
    0,                                        /* tp_setattr */
    0,                                        /* tp_compare */
    0,                                        /* tp_repr */
    0,                                        /* tp_as_number */
    0,                                        /* tp_as_sequence */
    0,                                        /* tp_as_mapping */
    0,                                        /* tp_hash */
    (ternaryfunc)PyBobSpQuantization_Call,    /* tp_call */
    0,                                        /* tp_str */
    0,                                        /* tp_getattro */
    0,                                        /* tp_setattro */
    0,                                        /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    s_quantization_doc,                       /* tp_doc */
    0,                                        /* tp_traverse */
    0,                                        /* tp_clear */
    0,                                        /* tp_richcompare */
    0,                                        /* tp_weaklistoffset */
    0,                                        /* tp_iter */
    0,                                        /* tp_iternext */
    PyBobSpQuantization_methods,              /* tp_methods */
    0,                                        /* tp_members */
    PyBobSpQuantization_getseters,            /* tp_getset */
    0,                                        /* tp_base */
    0,                                        /* tp_dict */
    0,                                        /* tp_descr_get */
    0,                                        /* tp_descr_set */
    0,                                        /* tp_dictoffset */
    (initproc)PyBobSpQuantization_Init,       /* tp_init */
    0,                                        /* tp_alloc */
    0,                                        /* tp_new */
};
