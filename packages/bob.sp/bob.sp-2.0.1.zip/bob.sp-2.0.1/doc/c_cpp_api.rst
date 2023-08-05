.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Wed Jul  2 18:22:11 CEST 2014

=======
 C API
=======

The C API of ``bob::sp`` allows users to leverage from automatic converters for classes in :py:class:`bob.sp`.
To use the C API, you should first include the header file ``<bob.sp/api.h>`` on their compilation units and then make sure to call once ``import_bob_sp()`` at their module instantiation, as explained at the `Python manual <http://docs.python.org/2/extending/extending.html#using-capsules>`__.

Here is a dummy C example showing how to include the header and where to call the import function:

.. code-block:: c++

   #include <bob.sp/api.h>

   PyMODINIT_FUNC initclient(void) {

     PyObject* m Py_InitModule("client", ClientMethods);

     if (!m) return;

     /* imports dependencies */
     if (import_bob_blitz() < 0) {
       PyErr_Print();
       PyErr_SetString(PyExc_ImportError, "cannot import extension");
       return 0;
     }

     if (import_bob_sp() < 0) {
       PyErr_Print();
       PyErr_SetString(PyExc_ImportError, "cannot import extension");
       return 0;
     }

   }


BorderType Interface
--------------------
.. c:var:: PyObject* PyBobSpExtrapolationBorder_Type

   An enumeration type that defines several ways to handle the border of an image during convolution.

.. c:function:: PyBobSpExtrapolationBorder_Converter(PyObject*, bob::sp::Extrapolation::BorderType*)

   This function is meant to be used with :c:func:`PyArg_ParseTupleAndKeywords` family of functions in the Python C-API.
   It converts an arbitrary input object into a ``bob::sp::Extrapolation::BorderType`` object.

   Returns 0 if an error is detected, 1 on success.


.. include:: links.rst

