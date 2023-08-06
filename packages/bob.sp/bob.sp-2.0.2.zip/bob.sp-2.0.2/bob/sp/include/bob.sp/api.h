/**
 * @author Manuel Guenther <manuel.guenther@idiap.ch>
 * @date Wed Jul  2 16:41:38 CEST 2014
 *
 * @brief C/C++ API for bob.sp
 */

#ifndef BOB_SP_H
#define BOB_SP_H

/* Define Module Name and Prefix for other Modules
   Note: We cannot use BOB_EXT_* macros here, unfortunately */
#define BOB_SP_PREFIX    "bob.sp"
#define BOB_SP_FULL_NAME "bob.sp._library"

#include <Python.h>

#include <bob.sp/config.h>
#include "extrapolate.h"

#include <boost/shared_ptr.hpp>

/*******************
 * C API functions *
 *******************/

/* Enum defining entries in the function table */
enum _PyBobSp_ENUM{
  PyBobSp_APIVersion_NUM = 0,
  // bindings for bob.sp.BorderType
  PyBobSpExtrapolationBorder_Type_NUM,
  PyBobSpExtrapolationBorder_Converter_NUM,
  // Total number of C API pointers
  PyBobSp_API_pointers
};

#define PyBobSpExtrapolationBorder_Converter_PROTO (PyObject* o, bob::sp::Extrapolation::BorderType* b)

#ifdef BOB_SP_MODULE

  /* This section is used when compiling `bob.sp' itself */

  /**************
   * Versioning *
   **************/

  extern int PyBobSp_APIVersion;

  /**********************************
   * Bindings for bob.sp.BorderType *
   **********************************/

  extern PyTypeObject PyBobSpExtrapolationBorder_Type;
  int PyBobSpExtrapolationBorder_Converter PyBobSpExtrapolationBorder_Converter_PROTO;

  // create API
  void* PyBobSp_API[PyBobSp_API_pointers];

  void initialize_api(){
    /* exhaustive list of C APIs */
    PyBobSp_API[PyBobSp_APIVersion_NUM] = (void*)&PyBobSp_APIVersion;
    PyBobSp_API[PyBobSpExtrapolationBorder_Type_NUM] = (void*)&PyBobSpExtrapolationBorder_Type;
    PyBobSp_API[PyBobSpExtrapolationBorder_Converter_NUM] = (void*)PyBobSpExtrapolationBorder_Converter;
  }

#else // BOB_SP_MODULE

  /* This section is used in modules that use `bob.sp's' C-API */

#  if defined(NO_IMPORT_ARRAY)
  extern void **PyBobSp_API;
#  else
#    if defined(PY_ARRAY_UNIQUE_SYMBOL)
  void **PyBobSp_API;
#    else
  static void **PyBobSp_API=NULL;
#    endif
#  endif

  /**************
   * Versioning *
   **************/

# define PyBobSp_APIVersion (*(int *)PyBobSp_API[PyBobSp_APIVersion_NUM])

  /**********************************
   * Bindings for bob.sp.BorderType *
   **********************************/
# define PyBobSpExtrapolationBorder_Type (*(PyTypeObject *)PyBobSp_API[PyBobSpExtrapolationBorder_Type_NUM])
# define PyBobSpExtrapolationBorder_Converter (*(int (*)PyBobSpExtrapolationBorder_Converter_PROTO) PyBobSp_API[PyBobSpExtrapolationBorder_Converter_NUM])

# if !defined(NO_IMPORT_ARRAY)

  /**
   * Returns -1 on error, 0 on success.
   */
  static int import_bob_sp(void) {

    PyObject *c_api_object;
    PyObject *module;

    module = PyImport_ImportModule(BOB_SP_FULL_NAME);

    if (module == NULL) return -1;

    c_api_object = PyObject_GetAttrString(module, "_C_API");

    if (c_api_object == NULL) {
      Py_DECREF(module);
      return -1;
    }

#   if PY_VERSION_HEX >= 0x02070000
    if (PyCapsule_CheckExact(c_api_object)) {
      PyBobSp_API = (void **)PyCapsule_GetPointer(c_api_object, PyCapsule_GetName(c_api_object));
    }
#   else
    if (PyCObject_Check(c_api_object)) {
      PyBobSp_API = (void **)PyCObject_AsVoidPtr(c_api_object);
    }
#   endif

    Py_DECREF(c_api_object);
    Py_DECREF(module);

    if (!PyBobSp_API) {
      PyErr_SetString(PyExc_ImportError, "cannot find C/C++ API "
#   if PY_VERSION_HEX >= 0x02070000
          "capsule"
#   else
          "cobject"
#   endif
          " at `" BOB_SP_FULL_NAME "._C_API'");
      return -1;
    }

    /* Checks that the imported version matches the compiled version */
    int imported_version = *(int*)PyBobSp_API[PyBobSp_APIVersion_NUM];

    if (BOB_SP_API_VERSION != imported_version) {
      PyErr_Format(PyExc_ImportError, BOB_SP_FULL_NAME " import error: you compiled against API version 0x%04x, but are now importing an API with version 0x%04x which is not compatible - check your Python runtime environment for errors", BOB_SP_API_VERSION, imported_version);
      return -1;
    }

    /* If you get to this point, all is good */
    return 0;

  }

# endif //!defined(NO_IMPORT_ARRAY)

#endif /* BOB_SP_MODULE */

#endif /* BOB_IO_BASE_H */
