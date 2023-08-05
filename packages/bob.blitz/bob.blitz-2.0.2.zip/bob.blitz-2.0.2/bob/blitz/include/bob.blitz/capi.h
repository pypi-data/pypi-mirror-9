/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue  8 Oct 08:19:28 2013
 *
 * @brief Defines the bob.blitz C-API
 *
 * This module allows somebody else, externally to this package, to include the
 * bob.blitz C-API functionality on their own package. Because the API is
 * compiled with a Python module (named `bob.blitz`), we need to dig it out
 * from there and bind it to the following C-API members. We do this using a
 * PyCObject/PyCapsule module as explained in:
 * http://docs.python.org/2/extending/extending.html#using-capsules.
 */

#ifndef BOB_BLITZ_C_API_H
#define BOB_BLITZ_C_API_H

#ifdef __cplusplus
extern "C" {
#endif

#include <Python.h>
#include <numpy/arrayobject.h>

/* Define Module Name and Prefix for other Modules
   Note: We cannot use BOB_EXT_* macros here, unfortunately */
#define BOB_BLITZ_PREFIX    "bob.blitz"
#define BOB_BLITZ_FULL_NAME "bob.blitz._library"

/* Define API version */
#define BOB_BLITZ_API_VERSION 0x0201

/* Maximum number of dimensions supported at this library */
#define BOB_BLITZ_MAXDIMS 4

/* Type definition for PyBlitzArrayObject */
typedef struct {
  PyObject_HEAD

  /* Type-specific fields go here. */
  void* bzarr; ///< blitz array container
  void* data; ///< a pointer to the internal data buffer
  int type_num; ///< numpy type number of elements
  Py_ssize_t ndim; ///< number of dimensions
  Py_ssize_t shape[BOB_BLITZ_MAXDIMS]; ///< shape
  Py_ssize_t stride[BOB_BLITZ_MAXDIMS]; ///< strides
  int writeable; ///< 1 if data is writeable, 0 otherwise

  /* Base pointer, if the memory of this object is coming from elsewhere */
  PyObject* base;

} PyBlitzArrayObject;

/* C-API of some Numpy versions we may support */
#define NUMPY17_API 0x00000007
#define NUMPY16_API 0x00000006
#define NUMPY14_API 0x00000004

/*******************
 * C API functions *
 *******************/

/* Enum defining entries in the function table */
enum _PyBlitzArray_ENUM{
  PyBlitzArray_APIVersion_NUM = 0,
  // Basic Properties and Checking
  PyBlitzArray_Type_NUM,
  PyBlitzArray_Check_NUM,
  PyBlitzArray_CheckNumpyBase_NUM,
  PyBlitzArray_TYPE_NUM,
  PyBlitzArray_PyDTYPE_NUM,
  PyBlitzArray_NDIM_NUM,
  PyBlitzArray_SHAPE_NUM,
  PyBlitzArray_PySHAPE_NUM,
  PyBlitzArray_STRIDE_NUM,
  PyBlitzArray_PySTRIDE_NUM,
  PyBlitzArray_WRITEABLE_NUM,
  PyBlitzArray_PyWRITEABLE_NUM,
  PyBlitzArray_BASE_NUM,
  PyBlitzArray_PyBASE_NUM,
  // Indexing
  PyBlitzArray_GetItem_NUM,
  PyBlitzArray_SetItem_NUM,
  PyBlitzArray_New_NUM,
  PyBlitzArray_Delete_NUM,
  PyBlitzArray_SimpleNew_NUM,
  PyBlitzArray_SimpleNewFromData_NUM,
  PyBlitzArray_SimpleInit_NUM,
  // From/To NumPy Converters
  PyBlitzArray_AsNumpyArray_NUM,
  PyBlitzArray_FromNumpyArray_NUM,
  PyBlitzArray_NUMPY_WRAP_NUM,
  // Converter Functions for PyArg_Parse* family
  PyBlitzArray_Converter_NUM,
  PyBlitzArray_BehavedConverter_NUM,
  PyBlitzArray_OutputConverter_NUM,
  PyBlitzArray_IndexConverter_NUM,
  PyBlitzArray_TypenumConverter_NUM,
  // Utilities
  PyBlitzArray_TypenumAsString_NUM,
  PyBlitzArray_TypenumSize_NUM,
  PyBlitzArray_Cast_NUM,
  /* Total number of C API pointers */
  PyBlitzArray_API_pointers
};

/**************
 * Versioning *
 **************/

#define PyBlitzArray_APIVersion_TYPE int

/*********************************
 * Basic Properties and Checking *
 *********************************/

#define PyBlitzArray_Type_TYPE PyTypeObject

#define PyBlitzArray_Check_RET int
#define PyBlitzArray_Check_PROTO (PyObject* o)

#define PyBlitzArray_CheckNumpyBase_RET int
#define PyBlitzArray_CheckNumpyBase_PROTO (PyArrayObject* o)

#define PyBlitzArray_TYPE_RET int
#define PyBlitzArray_TYPE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_PyDTYPE_RET PyArray_Descr*
#define PyBlitzArray_PyDTYPE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_NDIM_RET Py_ssize_t
#define PyBlitzArray_NDIM_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_SHAPE_RET Py_ssize_t*
#define PyBlitzArray_SHAPE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_PySHAPE_RET PyObject*
#define PyBlitzArray_PySHAPE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_STRIDE_RET Py_ssize_t*
#define PyBlitzArray_STRIDE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_PySTRIDE_RET PyObject*
#define PyBlitzArray_PySTRIDE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_WRITEABLE_RET int
#define PyBlitzArray_WRITEABLE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_PyWRITEABLE_RET PyObject*
#define PyBlitzArray_PyWRITEABLE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_BASE_RET PyObject*
#define PyBlitzArray_BASE_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_PyBASE_RET PyObject*
#define PyBlitzArray_PyBASE_PROTO (PyBlitzArrayObject* o)


/************
 * Indexing *
 ************/

#define PyBlitzArray_GetItem_RET PyObject*
#define PyBlitzArray_GetItem_PROTO (PyBlitzArrayObject* o, Py_ssize_t* pos)

#define PyBlitzArray_SetItem_RET int
#define PyBlitzArray_SetItem_PROTO (PyBlitzArrayObject* o, Py_ssize_t* pos, PyObject* value)

/********************************
 * Construction and Destruction *
 ********************************/

#define PyBlitzArray_New_RET PyObject*
#define PyBlitzArray_New_PROTO (PyTypeObject* type, PyObject *args, PyObject* kwds)

#define PyBlitzArray_Delete_RET void
#define PyBlitzArray_Delete_PROTO (PyBlitzArrayObject* o)

#define PyBlitzArray_SimpleNew_RET PyObject*
#define PyBlitzArray_SimpleNew_PROTO (int typenum, Py_ssize_t ndim, Py_ssize_t* shape)

#define PyBlitzArray_SimpleNewFromData_RET PyObject*
#define PyBlitzArray_SimpleNewFromData_PROTO (int typenum, Py_ssize_t ndim, Py_ssize_t* shape, Py_ssize_t* stride, void* data, int writeable)

#define PyBlitzArray_SimpleInit_RET int
#define PyBlitzArray_SimpleInit_PROTO (PyBlitzArrayObject* o, int typenum, Py_ssize_t ndim, Py_ssize_t* shape)

/****************************
 * From/To NumPy Converters *
 ****************************/

#define PyBlitzArray_AsNumpyArray_RET PyObject*
#define PyBlitzArray_AsNumpyArray_PROTO (PyBlitzArrayObject* o, PyArray_Descr* dtype)

#define PyBlitzArray_FromNumpyArray_RET PyObject*
#define PyBlitzArray_FromNumpyArray_PROTO (PyArrayObject* o)

#define PyBlitzArray_NUMPY_WRAP_RET PyObject*
#define PyBlitzArray_NUMPY_WRAP_PROTO (PyObject* o)

/***********************************************
 * Converter Functions for PyArg_Parse* family *
 ***********************************************/

#define PyBlitzArray_Converter_RET int
#define PyBlitzArray_Converter_PROTO (PyObject* o, PyBlitzArrayObject** a)

#define PyBlitzArray_BehavedConverter_RET int
#define PyBlitzArray_BehavedConverter_PROTO (PyObject* o, PyBlitzArrayObject** a)

#define PyBlitzArray_OutputConverter_RET int
#define PyBlitzArray_OutputConverter_PROTO (PyObject* o, PyBlitzArrayObject** a)

#define PyBlitzArray_IndexConverter_RET int
#define PyBlitzArray_IndexConverter_PROTO (PyObject* o, PyBlitzArrayObject** shape)

#define PyBlitzArray_TypenumConverter_RET int
#define PyBlitzArray_TypenumConverter_PROTO (PyObject* o, int* type_num)

/*************
 * Utilities *
 *************/

#define PyBlitzArray_TypenumAsString_RET const char*
#define PyBlitzArray_TypenumAsString_PROTO (int typenum)

#define PyBlitzArray_TypenumSize_RET size_t
#define PyBlitzArray_TypenumSize_PROTO (int typenum)

#define PyBlitzArray_Cast_RET PyObject*
#define PyBlitzArray_Cast_PROTO (PyBlitzArrayObject* o, int typenum)


#ifdef BOB_BLITZ_MODULE

  /* This section is used when compiling `bob.blitz' itself */

  extern int PyBlitzArray_APIVersion;

  /*********************************
   * Basic Properties and Checking *
   *********************************/

  extern PyBlitzArray_Type_TYPE PyBlitzArray_Type;

  PyBlitzArray_Check_RET PyBlitzArray_Check PyBlitzArray_Check_PROTO;

  PyBlitzArray_CheckNumpyBase_RET PyBlitzArray_CheckNumpyBase PyBlitzArray_CheckNumpyBase_PROTO;

  PyBlitzArray_TYPE_RET PyBlitzArray_TYPE PyBlitzArray_TYPE_PROTO;

  PyBlitzArray_PyDTYPE_RET PyBlitzArray_PyDTYPE PyBlitzArray_PyDTYPE_PROTO;

  PyBlitzArray_NDIM_RET PyBlitzArray_NDIM PyBlitzArray_NDIM_PROTO;

  PyBlitzArray_SHAPE_RET PyBlitzArray_SHAPE PyBlitzArray_SHAPE_PROTO;

  PyBlitzArray_PySHAPE_RET PyBlitzArray_PySHAPE PyBlitzArray_PySHAPE_PROTO;

  PyBlitzArray_STRIDE_RET PyBlitzArray_STRIDE PyBlitzArray_STRIDE_PROTO;

  PyBlitzArray_PySTRIDE_RET PyBlitzArray_PySTRIDE PyBlitzArray_PySTRIDE_PROTO;

  PyBlitzArray_WRITEABLE_RET PyBlitzArray_WRITEABLE PyBlitzArray_WRITEABLE_PROTO;

  PyBlitzArray_PyWRITEABLE_RET PyBlitzArray_PyWRITEABLE PyBlitzArray_PyWRITEABLE_PROTO;

  PyBlitzArray_BASE_RET PyBlitzArray_BASE PyBlitzArray_BASE_PROTO;

  PyBlitzArray_PyBASE_RET PyBlitzArray_PyBASE PyBlitzArray_PyBASE_PROTO;

/************
 * Indexing *
 ************/

  PyBlitzArray_GetItem_RET PyBlitzArray_GetItem PyBlitzArray_GetItem_PROTO;

  PyBlitzArray_SetItem_RET PyBlitzArray_SetItem PyBlitzArray_SetItem_PROTO;


/********************************
 * Construction and Destruction *
 ********************************/

  PyBlitzArray_New_RET PyBlitzArray_New PyBlitzArray_New_PROTO;

  PyBlitzArray_Delete_RET PyBlitzArray_Delete PyBlitzArray_Delete_PROTO;

  PyBlitzArray_SimpleNew_RET PyBlitzArray_SimpleNew PyBlitzArray_SimpleNew_PROTO;

  PyBlitzArray_SimpleNewFromData_RET PyBlitzArray_SimpleNewFromData PyBlitzArray_SimpleNewFromData_PROTO;

  PyBlitzArray_SimpleInit_RET PyBlitzArray_SimpleInit PyBlitzArray_SimpleInit_PROTO;

/****************************
 * From/To NumPy Converters *
 ****************************/

  PyBlitzArray_AsNumpyArray_RET PyBlitzArray_AsNumpyArray PyBlitzArray_AsNumpyArray_PROTO;

  PyBlitzArray_FromNumpyArray_RET PyBlitzArray_FromNumpyArray PyBlitzArray_FromNumpyArray_PROTO;

  PyBlitzArray_NUMPY_WRAP_RET PyBlitzArray_NUMPY_WRAP PyBlitzArray_NUMPY_WRAP_PROTO;

/***********************************************
 * Converter Functions for PyArg_Parse* family *
 ***********************************************/

  PyBlitzArray_Converter_RET PyBlitzArray_Converter PyBlitzArray_Converter_PROTO;

  PyBlitzArray_BehavedConverter_RET PyBlitzArray_BehavedConverter PyBlitzArray_BehavedConverter_PROTO;

  PyBlitzArray_OutputConverter_RET PyBlitzArray_OutputConverter PyBlitzArray_OutputConverter_PROTO;

  PyBlitzArray_IndexConverter_RET PyBlitzArray_IndexConverter PyBlitzArray_IndexConverter_PROTO;

  PyBlitzArray_TypenumConverter_RET PyBlitzArray_TypenumConverter PyBlitzArray_TypenumConverter_PROTO;

/*************
 * Utilities *
 *************/

  PyBlitzArray_TypenumAsString_RET PyBlitzArray_TypenumAsString PyBlitzArray_TypenumAsString_PROTO;

  PyBlitzArray_TypenumSize_RET PyBlitzArray_TypenumSize PyBlitzArray_TypenumSize_PROTO;

  PyBlitzArray_Cast_RET PyBlitzArray_Cast PyBlitzArray_Cast_PROTO;

#else

#  if defined(NO_IMPORT_ARRAY)
  extern void **PyBlitzArray_API;
#  else
#    if defined(PY_ARRAY_UNIQUE_SYMBOL)
  void **PyBlitzArray_API;
#    else
  static void **PyBlitzArray_API=NULL;
#    endif
#  endif

#define PyBlitzArray_APIVersion (*(PyBlitzArray_APIVersion_TYPE *)PyBlitzArray_API[PyBlitzArray_APIVersion_NUM])

/*********************************
 * Basic Properties and Checking *
 *********************************/

#define PyBlitzArray_Type (*(PyBlitzArray_Type_TYPE *)PyBlitzArray_API[PyBlitzArray_Type_NUM])

#define PyBlitzArray_Check (*(PyBlitzArray_Check_RET (*)PyBlitzArray_Check_PROTO) PyBlitzArray_API[PyBlitzArray_Check_NUM])

#define PyBlitzArray_CheckNumpyBase (*(PyBlitzArray_CheckNumpyBase_RET (*)PyBlitzArray_CheckNumpyBase_PROTO) PyBlitzArray_API[PyBlitzArray_CheckNumpyBase_NUM])

#define PyBlitzArray_TYPE (*(PyBlitzArray_TYPE_RET (*)PyBlitzArray_TYPE_PROTO) PyBlitzArray_API[PyBlitzArray_TYPE_NUM])

#define PyBlitzArray_PyDTYPE (*(PyBlitzArray_PyDTYPE_RET (*)PyBlitzArray_PyDTYPE_PROTO) PyBlitzArray_API[PyBlitzArray_PyDTYPE_NUM])

#define PyBlitzArray_NDIM (*(PyBlitzArray_NDIM_RET (*)PyBlitzArray_NDIM_PROTO) PyBlitzArray_API[PyBlitzArray_NDIM_NUM])

#define PyBlitzArray_SHAPE (*(PyBlitzArray_SHAPE_RET (*)PyBlitzArray_SHAPE_PROTO) PyBlitzArray_API[PyBlitzArray_SHAPE_NUM])

#define PyBlitzArray_PySHAPE (*(PyBlitzArray_PySHAPE_RET (*)PyBlitzArray_PySHAPE_PROTO) PyBlitzArray_API[PyBlitzArray_PySHAPE_NUM])

#define PyBlitzArray_STRIDE (*(PyBlitzArray_STRIDE_RET (*)PyBlitzArray_STRIDE_PROTO) PyBlitzArray_API[PyBlitzArray_STRIDE_NUM])

#define PyBlitzArray_PySTRIDE (*(PyBlitzArray_PySTRIDE_RET (*)PyBlitzArray_PySTRIDE_PROTO) PyBlitzArray_API[PyBlitzArray_PySTRIDE_NUM])

#define PyBlitzArray_WRITEABLE (*(PyBlitzArray_WRITEABLE_RET (*)PyBlitzArray_WRITEABLE_PROTO) PyBlitzArray_API[PyBlitzArray_WRITEABLE_NUM])

#define PyBlitzArray_PyWRITEABLE (*(PyBlitzArray_PyWRITEABLE_RET (*)PyBlitzArray_PyWRITEABLE_PROTO) PyBlitzArray_API[PyBlitzArray_PyWRITEABLE_NUM])

#define PyBlitzArray_BASE (*(PyBlitzArray_BASE_RET (*)PyBlitzArray_BASE_PROTO) PyBlitzArray_API[PyBlitzArray_BASE_NUM])

#define PyBlitzArray_PyBASE (*(PyBlitzArray_PyBASE_RET (*)PyBlitzArray_PyBASE_PROTO) PyBlitzArray_API[PyBlitzArray_PyBASE_NUM])

/************
 * Indexing *
 ************/

#define PyBlitzArray_GetItem (*(PyBlitzArray_GetItem_RET (*)PyBlitzArray_GetItem_PROTO) PyBlitzArray_API[PyBlitzArray_GetItem_NUM])

#define PyBlitzArray_SetItem (*(PyBlitzArray_SetItem_RET (*)PyBlitzArray_SetItem_PROTO) PyBlitzArray_API[PyBlitzArray_SetItem_NUM])

/********************************
 * Construction and Destruction *
 ********************************/

#define PyBlitzArray_New (*(PyBlitzArray_New_RET (*)PyBlitzArray_New_PROTO) PyBlitzArray_API[PyBlitzArray_New_NUM])

#define PyBlitzArray_Delete (*(PyBlitzArray_Delete_RET (*)PyBlitzArray_Delete_PROTO) PyBlitzArray_API[PyBlitzArray_Delete_NUM])

#define PyBlitzArray_SimpleNew (*(PyBlitzArray_SimpleNew_RET (*)PyBlitzArray_SimpleNew_PROTO) PyBlitzArray_API[PyBlitzArray_SimpleNew_NUM])

#define PyBlitzArray_SimpleNewFromData (*(PyBlitzArray_SimpleNewFromData_RET (*)PyBlitzArray_SimpleNewFromData_PROTO) PyBlitzArray_API[PyBlitzArray_SimpleNewFromData_NUM])

#define PyBlitzArray_SimpleInit (*(PyBlitzArray_SimpleInit_RET (*)PyBlitzArray_SimpleInit_PROTO) PyBlitzArray_API[PyBlitzArray_SimpleInit_NUM])

/****************************
 * From/To NumPy Converters *
 ****************************/

#define PyBlitzArray_AsNumpyArray (*(PyBlitzArray_AsNumpyArray_RET (*)PyBlitzArray_AsNumpyArray_PROTO) PyBlitzArray_API[PyBlitzArray_AsNumpyArray_NUM])

#define PyBlitzArray_FromNumpyArray (*(PyBlitzArray_FromNumpyArray_RET (*)PyBlitzArray_FromNumpyArray_PROTO) PyBlitzArray_API[PyBlitzArray_FromNumpyArray_NUM])

#define PyBlitzArray_NUMPY_WRAP (*(PyBlitzArray_NUMPY_WRAP_RET (*)PyBlitzArray_NUMPY_WRAP_PROTO) PyBlitzArray_API[PyBlitzArray_NUMPY_WRAP_NUM])

/***********************************************
 * Converter Functions for PyArg_Parse* family *
 ***********************************************/

#define PyBlitzArray_Converter (*(PyBlitzArray_Converter_RET (*)PyBlitzArray_Converter_PROTO) PyBlitzArray_API[PyBlitzArray_Converter_NUM])

#define PyBlitzArray_BehavedConverter (*(PyBlitzArray_BehavedConverter_RET (*)PyBlitzArray_BehavedConverter_PROTO) PyBlitzArray_API[PyBlitzArray_BehavedConverter_NUM])

#define PyBlitzArray_OutputConverter (*(PyBlitzArray_OutputConverter_RET (*)PyBlitzArray_OutputConverter_PROTO) PyBlitzArray_API[PyBlitzArray_OutputConverter_NUM])

#define PyBlitzArray_IndexConverter (*(PyBlitzArray_IndexConverter_RET (*)PyBlitzArray_IndexConverter_PROTO) PyBlitzArray_API[PyBlitzArray_IndexConverter_NUM])

#define PyBlitzArray_TypenumConverter (*(PyBlitzArray_TypenumConverter_RET (*)PyBlitzArray_TypenumConverter_PROTO) PyBlitzArray_API[PyBlitzArray_TypenumConverter_NUM])

/*************
 * Utilities *
 *************/

#define PyBlitzArray_TypenumAsString (*(PyBlitzArray_TypenumAsString_RET (*)PyBlitzArray_TypenumAsString_PROTO) PyBlitzArray_API[PyBlitzArray_TypenumAsString_NUM])

#define PyBlitzArray_TypenumSize (*(PyBlitzArray_TypenumSize_RET (*)PyBlitzArray_TypenumSize_PROTO) PyBlitzArray_API[PyBlitzArray_TypenumSize_NUM])

#define PyBlitzArray_Cast (*(PyBlitzArray_Cast_RET (*)PyBlitzArray_Cast_PROTO) PyBlitzArray_API[PyBlitzArray_Cast_NUM])

# if !defined(NO_IMPORT_ARRAY)

  /**
   * Returns -1 on error, 0 on success.
   */
  static int import_bob_blitz(void) {

    PyObject *c_api_object;
    PyObject *module;

    module = PyImport_ImportModule(BOB_BLITZ_FULL_NAME);

    if (module == NULL) return -1;

    c_api_object = PyObject_GetAttrString(module, "_C_API");

    if (c_api_object == NULL) {
      Py_DECREF(module);
      return -1;
    }

#   if PY_VERSION_HEX >= 0x02070000
    if (PyCapsule_CheckExact(c_api_object)) {
      PyBlitzArray_API = (void **)PyCapsule_GetPointer(c_api_object,
          PyCapsule_GetName(c_api_object));
    }
#   else
    if (PyCObject_Check(c_api_object)) {
      PyBlitzArray_API = (void **)PyCObject_AsVoidPtr(c_api_object);
    }
#   endif

    Py_DECREF(c_api_object);
    Py_DECREF(module);

    if (!PyBlitzArray_API) {
      PyErr_SetString(PyExc_ImportError, "cannot find C/C++ API "
#   if PY_VERSION_HEX >= 0x02070000
          "capsule"
#   else
          "cobject"
#   endif
          " at `" BOB_BLITZ_FULL_NAME "._C_API'");
      return -1;
    }

    /* Checks that the imported version matches the compiled version */
    int imported_version = *(int*)PyBlitzArray_API[PyBlitzArray_APIVersion_NUM];

    if (BOB_BLITZ_API_VERSION != imported_version) {
      PyErr_Format(PyExc_RuntimeError, BOB_BLITZ_FULL_NAME " import error: you compiled against API version 0x%x, but are now importing an API with version 0x%x which is not compatible - check your Python runtime environment for errors", BOB_BLITZ_API_VERSION, imported_version);
      return -1;
    }

    /* Imports the numpy C-API */
    import_array1(-1);

    /* If you get to this point, all is good */
    return 0;

  }
# endif // !defined(NO_IMPORT_ARRAY)

#endif // BOB_BLITZ_MODULE

#ifdef __cplusplus
} // extern "C"
#endif

#endif /* BOB_BLITZ_C_API_H */
