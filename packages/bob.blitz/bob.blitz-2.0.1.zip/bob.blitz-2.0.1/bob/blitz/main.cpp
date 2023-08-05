/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 01 Oct 2013 15:37:07 CEST
 *
 * @brief Pure python bindings for Blitz Arrays
 */

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#define BOB_BLITZ_MODULE
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>

static PyObject* PyBlitzArray_as_blitz(PyObject*, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"o", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* retval = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist, &PyBlitzArray_Converter, &retval)) return 0;

  return retval;

}

PyDoc_STRVAR(s_as_blitz_str, "as_blitz");
PyDoc_STRVAR(s_as_blitz__doc__,
"as_blitz(x) -> bob.blitz.array\n\
\n\
Converts any compatible python object into a shallow " BOB_EXT_MODULE_PREFIX ".array\n\
\n\
This function works by first converting the input object ``x`` into\n\
a :py:class:`numpy.ndarray` and then shallow wrapping that ``ndarray``\n\
into a new :py:class:`" BOB_EXT_MODULE_PREFIX ".array`. You can access the converted\n\
``ndarray`` using the returned value's ``base`` attribute. If the\n\
``ndarray`` cannot be shallow-wrapped, a :py:class:`ValueError` is\n\
raised.\n\
\n\
In the case the input object ``x`` is already a behaved (C-style,\n\
memory-aligned, contiguous) :py:class:`numpy.ndarray`, then this\n\
function only shallow wrap's it into a :py:class:`" BOB_EXT_MODULE_PREFIX ".array` skin.\n\
"
);

static PyMethodDef module_methods[] = {
    {
      s_as_blitz_str,
      (PyCFunction)PyBlitzArray_as_blitz,
      METH_VARARGS|METH_KEYWORDS,
      s_as_blitz__doc__
    },
    {0}  /* Sentinel */
};

int PyBlitzArray_APIVersion = BOB_BLITZ_API_VERSION;

PyDoc_STRVAR(module_docstr, "Blitz++ array definition and generic functions");

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

  PyBlitzArray_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBlitzArray_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m); ///< protects against early returns

  /* register version numbers and constants */
  if (PyModule_AddIntConstant(m, "__api_version__", BOB_BLITZ_API_VERSION) < 0)
    return 0;
  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0)
    return 0;

  /* register the type object to python */
  Py_INCREF(&PyBlitzArray_Type);
  if (PyModule_AddObject(m, "array", (PyObject *)&PyBlitzArray_Type) < 0) return 0;

  static void* PyBlitzArray_API[PyBlitzArray_API_pointers];

  /* exhaustive list of C APIs */
  PyBlitzArray_API[PyBlitzArray_APIVersion_NUM] = (void *)&PyBlitzArray_APIVersion;

  // Basic Properties and Checking
  PyBlitzArray_API[PyBlitzArray_Type_NUM] = (void *)&PyBlitzArray_Type;
  PyBlitzArray_API[PyBlitzArray_Check_NUM] = (void *)PyBlitzArray_Check;
  PyBlitzArray_API[PyBlitzArray_CheckNumpyBase_NUM] = (void *)PyBlitzArray_CheckNumpyBase;
  PyBlitzArray_API[PyBlitzArray_TYPE_NUM] = (void *)PyBlitzArray_TYPE;
  PyBlitzArray_API[PyBlitzArray_PyDTYPE_NUM] = (void *)PyBlitzArray_PyDTYPE;
  PyBlitzArray_API[PyBlitzArray_NDIM_NUM] = (void *)PyBlitzArray_NDIM;
  PyBlitzArray_API[PyBlitzArray_SHAPE_NUM] = (void *)PyBlitzArray_SHAPE;
  PyBlitzArray_API[PyBlitzArray_PySHAPE_NUM] = (void *)PyBlitzArray_PySHAPE;
  PyBlitzArray_API[PyBlitzArray_STRIDE_NUM] = (void *)PyBlitzArray_STRIDE;
  PyBlitzArray_API[PyBlitzArray_PySTRIDE_NUM] = (void *)PyBlitzArray_PySTRIDE;
  PyBlitzArray_API[PyBlitzArray_WRITEABLE_NUM] = (void *)PyBlitzArray_WRITEABLE;
  PyBlitzArray_API[PyBlitzArray_PyWRITEABLE_NUM] = (void *)PyBlitzArray_PyWRITEABLE;
  PyBlitzArray_API[PyBlitzArray_BASE_NUM] = (void *)PyBlitzArray_BASE;
  PyBlitzArray_API[PyBlitzArray_PyBASE_NUM] = (void *)PyBlitzArray_PyBASE;

  // Indexing
  PyBlitzArray_API[PyBlitzArray_GetItem_NUM] = (void *)PyBlitzArray_GetItem;
  PyBlitzArray_API[PyBlitzArray_SetItem_NUM] = (void *)PyBlitzArray_SetItem;

  // Construction and Destruction
  PyBlitzArray_API[PyBlitzArray_New_NUM] = (void *)PyBlitzArray_New;
  PyBlitzArray_API[PyBlitzArray_Delete_NUM] = (void *)PyBlitzArray_Delete;
  PyBlitzArray_API[PyBlitzArray_SimpleNew_NUM] = (void *)PyBlitzArray_SimpleNew;
  PyBlitzArray_API[PyBlitzArray_SimpleNewFromData_NUM] = (void *)PyBlitzArray_SimpleNewFromData;

  // From/To NumPy Converters
  PyBlitzArray_API[PyBlitzArray_AsNumpyArray_NUM] = (void *)PyBlitzArray_AsNumpyArray;
  PyBlitzArray_API[PyBlitzArray_FromNumpyArray_NUM] = (void *)PyBlitzArray_FromNumpyArray;
  PyBlitzArray_API[PyBlitzArray_NUMPY_WRAP_NUM] = (void *)PyBlitzArray_NUMPY_WRAP;

  // Converter Functions for PyArg_Parse* family
  PyBlitzArray_API[PyBlitzArray_Converter_NUM] = (void *)PyBlitzArray_Converter;
  PyBlitzArray_API[PyBlitzArray_BehavedConverter_NUM] = (void *)PyBlitzArray_BehavedConverter;
  PyBlitzArray_API[PyBlitzArray_OutputConverter_NUM] = (void *)PyBlitzArray_OutputConverter;
  PyBlitzArray_API[PyBlitzArray_IndexConverter_NUM] = (void *)PyBlitzArray_IndexConverter;
  PyBlitzArray_API[PyBlitzArray_TypenumConverter_NUM] = (void *)PyBlitzArray_TypenumConverter;

  // Utilities
  PyBlitzArray_API[PyBlitzArray_TypenumAsString_NUM] = (void *)PyBlitzArray_TypenumAsString;
  PyBlitzArray_API[PyBlitzArray_TypenumSize_NUM] = (void *)PyBlitzArray_TypenumSize;
  PyBlitzArray_API[PyBlitzArray_Cast_NUM] = (void *)PyBlitzArray_Cast;

#if PY_VERSION_HEX >= 0x02070000

  /* defines the PyCapsule */

  PyObject* c_api_object = PyCapsule_New((void *)PyBlitzArray_API,
      BOB_EXT_MODULE_PREFIX "." BOB_EXT_MODULE_NAME "._C_API", 0);

#else

  PyObject* c_api_object = PyCObject_FromVoidPtr((void *)PyBlitzArray_API, 0);

#endif

  if (!c_api_object) return 0;

  if (PyModule_AddObject(m, "_C_API", c_api_object) < 0) return 0;

  /* imports the NumPy C-API as well */
  import_array1(0);

  Py_INCREF(m);
  return m;

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
