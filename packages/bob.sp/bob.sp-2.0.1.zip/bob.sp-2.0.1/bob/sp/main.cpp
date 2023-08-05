/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 25 Oct 16:54:55 2013
 *
 * @brief Bindings to bob::sp
 */

#define BOB_SP_MODULE
#include <bob.sp/api.h>

int PyBobSp_APIVersion = BOB_SP_API_VERSION;

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>

extern PyTypeObject PyBobSpFFT1D_Type;
extern PyTypeObject PyBobSpIFFT1D_Type;
extern PyTypeObject PyBobSpFFT2D_Type;
extern PyTypeObject PyBobSpIFFT2D_Type;
extern PyTypeObject PyBobSpDCT1D_Type;
extern PyTypeObject PyBobSpIDCT1D_Type;
extern PyTypeObject PyBobSpDCT2D_Type;
extern PyTypeObject PyBobSpIDCT2D_Type;
extern PyTypeObject PyBobSpExtrapolationBorder_Type;
extern PyTypeObject PyBobSpQuantization_Type;

PyDoc_STRVAR(s_extrapolate_str, "extrapolate");
PyDoc_STRVAR(s_extrapolate_doc,
"extrapolate(src, dst, [[border=" BOB_EXT_MODULE_PREFIX ".BorderType.Zero], value=0.]) -> None\n\
\n\
Extrapolates values in the given array using the specified border\n\
type. Works for 1 or 2D input arrays. The parameter ``value`` is\n\
only used if the border type is set to\n\
:py:attr:`" BOB_EXT_MODULE_PREFIX ".BorderType.Constant`. It is,\n\
by default, set to ``0.``, or the equivalent on the datatype passed\n\
as input. For example, ``False``, if the input is boolean and\n\
0+0j, if it is complex.\n\
");
PyObject* extrapolate(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_fft_str, "fft");
PyDoc_STRVAR(s_fft_doc,
"fft(src, [dst]) -> array\n\
\n\
Computes the direct Fast Fourier Transform of a 1D or 2D\n\
array/signal of type ``complex128``. Allocates a new output\n\
array if ``dst`` is not provided. If it is, then it must\n\
be of the same type and shape as ``src``.\n\
\n\
Parameters:\n\
\n\
src\n\
  [array] A 1 or 2-dimensional array of type ``complex128``\n\
  in which the FFT operation will be performed.\n\
\n\
dst\n\
  [array, optional] A 1 or 2-dimensional array of type\n\
  ``complex128`` and matching dimensions to ``src`` in\n\
  which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``complex128``, containing the FFT of\n\
the input signal.\n\
");
PyObject* fft(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_ifft_str, "ifft");
PyDoc_STRVAR(s_ifft_doc,
"ifft(src, [dst]) -> array\n\
\n\
Computes the inverse Fast Fourier Transform of a 1D or 2D\n\
transform of type ``complex128``. Allocates a new output\n\
array if ``dst`` is not provided. If it is, then it must\n\
be of the same type and shape as ``src``.\n\
\n\
Parameters:\n\
\n\
src\n\
  [array] A 1 or 2-dimensional array of type ``complex128``\n\
  in which the inverse FFT operation will be performed.\n\
\n\
dst\n\
  [array, optional] A 1 or 2-dimensional array of type\n\
  ``complex128`` and matching dimensions to ``src`` in\n\
  which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``complex128``, containing the inverse\n\
FFT of the input transform.\n\
");
PyObject* ifft(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_fftshift_str, "fftshift");
PyDoc_STRVAR(s_fftshift_doc,
"fftshift(src, [dst]) -> array\n\
\n\
If a 1D complex128 array is passed, inverses the two halves\n\
of that array and returns the result as a new array. If a 2D\n\
``complex128`` array is passed, swaps the four quadrants of\n\
the array and returns the result as a new array.\n\
\n\
Parameters:\n\
\n\
src\n\
[array] A 1 or 2-dimensional array of type ``complex128``\n\
with the signal to be shifted.\n\
\n\
dst\n\
[array, optional] A 1 or 2-dimensional array of type\n\
``complex128`` and matching dimensions to ``src`` in\n\
which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``complex128``, containing the shifted\n\
version of theinput.\n\
");
PyObject* fftshift(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_ifftshift_str, "ifftshift");
PyDoc_STRVAR(s_ifftshift_doc,
"ifftshift(src, [dst]) -> array\n\
\n\
This method undoes what :py:meth:`fftshift` does. It accepts\n\
1 or 2-dimensional arrays of type ``complex128``.\n\
\n\
Parameters:\n\
\n\
src\n\
[array] A 1 or 2-dimensional array of type ``complex128``\n\
with the signal to be shifted.\n\
\n\
dst\n\
[array, optional] A 1 or 2-dimensional array of type\n\
``complex128`` and matching dimensions to ``src`` in\n\
which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``complex128``, containing the shifted\n\
version of theinput.\n\
");
PyObject* ifftshift(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_dct_str, "dct");
PyDoc_STRVAR(s_dct_doc,
"dct(src, [dst]) -> array\n\
\n\
Computes the direct Discrete Cosine Transform of a 1D or 2D\n\
array/signal of type ``float64``. Allocates a new output\n\
array if ``dst`` is not provided. If it is, then it must\n\
be of the same type and shape as ``src``.\n\
\n\
Parameters:\n\
\n\
src\n\
  [array] A 1 or 2-dimensional array of type ``float64``\n\
  in which the DCT operation will be performed.\n\
\n\
dst\n\
  [array, optional] A 1 or 2-dimensional array of type\n\
  ``float64`` and matching dimensions to ``src`` in\n\
  which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``float64``, containing the DCT of\n\
the input signal.\n\
");
PyObject* dct(PyObject*, PyObject* args, PyObject* kwds);

PyDoc_STRVAR(s_idct_str, "idct");
PyDoc_STRVAR(s_idct_doc,
"idct(src, [dst]) -> array\n\
\n\
Computes the inverse Discrete Cosinte Transform of a 1D or 2D\n\
transform of type ``float64``. Allocates a new output\n\
array if ``dst`` is not provided. If it is, then it must\n\
be of the same type and shape as ``src``.\n\
\n\
Parameters:\n\
\n\
src\n\
  [array] A 1 or 2-dimensional array of type ``float64``\n\
  in which the inverse DCT operation will be performed.\n\
\n\
dst\n\
  [array, optional] A 1 or 2-dimensional array of type\n\
  ``float64`` and matching dimensions to ``src`` in\n\
  which the result of the operation will be stored.\n\
\n\
Returns a 1 or 2-dimensional array, of the same dimension\n\
as ``src``, of type ``float64``, containing the inverse\n\
DCT of the input transform.\n\
");
PyObject* idct(PyObject*, PyObject* args, PyObject* kwds);

static PyMethodDef module_methods[] = {
    {
      s_extrapolate_str,
      (PyCFunction)extrapolate,
      METH_VARARGS|METH_KEYWORDS,
      s_extrapolate_doc
    },
    {
      s_fft_str,
      (PyCFunction)fft,
      METH_VARARGS|METH_KEYWORDS,
      s_fft_doc
    },
    {
      s_ifft_str,
      (PyCFunction)ifft,
      METH_VARARGS|METH_KEYWORDS,
      s_ifft_doc
    },
    {
      s_fftshift_str,
      (PyCFunction)fftshift,
      METH_VARARGS|METH_KEYWORDS,
      s_fftshift_doc
    },
    {
      s_ifftshift_str,
      (PyCFunction)ifftshift,
      METH_VARARGS|METH_KEYWORDS,
      s_ifftshift_doc
    },
    {
      s_dct_str,
      (PyCFunction)dct,
      METH_VARARGS|METH_KEYWORDS,
      s_dct_doc
    },
    {
      s_idct_str,
      (PyCFunction)idct,
      METH_VARARGS|METH_KEYWORDS,
      s_idct_doc
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Bob signal processing toolkit");

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

  PyBobSpFFT1D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpFFT1D_Type) < 0) return 0;

  PyBobSpIFFT1D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpIFFT1D_Type) < 0) return 0;

  PyBobSpFFT2D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpFFT2D_Type) < 0) return 0;

  PyBobSpIFFT2D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpIFFT2D_Type) < 0) return 0;

  PyBobSpDCT1D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpDCT1D_Type) < 0) return 0;

  PyBobSpIDCT1D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpIDCT1D_Type) < 0) return 0;

  PyBobSpDCT2D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpDCT2D_Type) < 0) return 0;

  PyBobSpIDCT2D_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpIDCT2D_Type) < 0) return 0;

  PyBobSpExtrapolationBorder_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpExtrapolationBorder_Type) < 0) return 0;

  PyBobSpQuantization_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobSpQuantization_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m); ///< protects against early returns

  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0)
    return 0;

  /* register the types to python */
  Py_INCREF(&PyBobSpFFT1D_Type);
  if (PyModule_AddObject(m, "FFT1D", (PyObject *)&PyBobSpFFT1D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpIFFT1D_Type);
  if (PyModule_AddObject(m, "IFFT1D", (PyObject *)&PyBobSpIFFT1D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpFFT2D_Type);
  if (PyModule_AddObject(m, "FFT2D", (PyObject *)&PyBobSpFFT2D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpIFFT2D_Type);
  if (PyModule_AddObject(m, "IFFT2D", (PyObject *)&PyBobSpIFFT2D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpDCT1D_Type);
  if (PyModule_AddObject(m, "DCT1D", (PyObject *)&PyBobSpDCT1D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpIDCT1D_Type);
  if (PyModule_AddObject(m, "IDCT1D", (PyObject *)&PyBobSpIDCT1D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpDCT2D_Type);
  if (PyModule_AddObject(m, "DCT2D", (PyObject *)&PyBobSpDCT2D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpIDCT2D_Type);
  if (PyModule_AddObject(m, "IDCT2D", (PyObject *)&PyBobSpIDCT2D_Type) < 0) return 0;

  Py_INCREF(&PyBobSpExtrapolationBorder_Type);
  if (PyModule_AddObject(m, "BorderType", (PyObject *)&PyBobSpExtrapolationBorder_Type) < 0) return 0;

  Py_INCREF(&PyBobSpQuantization_Type);
  if (PyModule_AddObject(m, "Quantization", (PyObject *)&PyBobSpQuantization_Type) < 0) return 0;

  // initialize the PyBobSp_API
  initialize_api();

#if PY_VERSION_HEX >= 0x02070000

  /* defines the PyCapsule */

  PyObject* c_api_object = PyCapsule_New((void *)PyBobSp_API, BOB_EXT_MODULE_PREFIX "." BOB_EXT_MODULE_NAME "._C_API", 0);

#else

  PyObject* c_api_object = PyCObject_FromVoidPtr((void *)PyBobSp_API, 0);

#endif

  if (!c_api_object) return 0;

  if (PyModule_AddObject(m, "_C_API", c_api_object) < 0) return 0;

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
