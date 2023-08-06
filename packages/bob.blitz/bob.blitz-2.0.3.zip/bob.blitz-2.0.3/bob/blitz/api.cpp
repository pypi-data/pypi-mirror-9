/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue  1 Oct 13:52:57 2013
 *
 * @brief Implements some constructions exported to all modules
 */

#define BOB_BLITZ_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/defines.h>
#include <algorithm>

/*******************
 * Non-API Helpers *
 *******************/

/**
 * Correct for integer types
 */
static int fix_integer_type_num_inner(bool sign, int nbits) {
  switch (nbits) {
    case 8:
      return sign ? NPY_INT8 : NPY_UINT8;
    case 16:
      return sign ? NPY_INT16 : NPY_UINT16;
    case 32:
      return sign ? NPY_INT32 : NPY_UINT32;
    case 64:
      return sign ? NPY_INT64 : NPY_UINT64;
    default:
      break;
  }

  PyErr_Format(PyExc_NotImplementedError, "no support for integer type with %d bits", nbits);
  return -1;
}

/**
 * Correct for type numbers which are not necessarily bound to one of the
 * supported type numbers.
 */
static int fix_integer_type_num(int type_num) {

  switch(type_num) {
    case NPY_BYTE:
      return fix_integer_type_num_inner(true, NPY_BITSOF_CHAR);
    case NPY_SHORT:
      return fix_integer_type_num_inner(true, NPY_BITSOF_SHORT);
    case NPY_INT:
      return fix_integer_type_num_inner(true, NPY_BITSOF_INT);
    case NPY_LONG:
      return fix_integer_type_num_inner(true, NPY_BITSOF_LONG);
    case NPY_LONGLONG:
      return fix_integer_type_num_inner(true, NPY_BITSOF_LONGLONG);
    case NPY_UBYTE:
      return fix_integer_type_num_inner(false, NPY_BITSOF_CHAR);
    case NPY_USHORT:
      return fix_integer_type_num_inner(false, NPY_BITSOF_SHORT);
    case NPY_UINT:
      return fix_integer_type_num_inner(false, NPY_BITSOF_INT);
    case NPY_ULONG:
      return fix_integer_type_num_inner(false, NPY_BITSOF_LONG);
    case NPY_ULONGLONG:
      return fix_integer_type_num_inner(false, NPY_BITSOF_LONGLONG);
    default:
      break;
  }

  return type_num;
}

/*********************************
 * Basic Properties and Checking *
 *********************************/

int PyBlitzArray_Check(PyObject* o) {
  if (!o) return 0;
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBlitzArray_Type));
}

int PyBlitzArray_CheckNumpyBase(PyArrayObject* o) {
  if (!PyArray_BASE(o)) return 0;

  if (!PyBlitzArray_Check(PyArray_BASE(o))) return 0;

  PyBlitzArrayObject* bo = reinterpret_cast<PyBlitzArrayObject*>(PyArray_BASE(o));

  if (PyArray_DESCR(o)->type_num != bo->type_num) return 0;

  if (PyArray_NDIM(o) != bo->ndim) return 0;

  for (Py_ssize_t i=0; i<bo->ndim; ++i)
    if (bo->shape[i] != PyArray_DIMS(o)[i]) return 0;

  return 1;
}

int PyBlitzArray_TYPE (PyBlitzArrayObject* o) {
  return o->type_num;
}

PyArray_Descr* PyBlitzArray_PyDTYPE (PyBlitzArrayObject* o) {
  PyArray_Descr* retval = PyArray_DescrFromType(o->type_num);
  if (retval) Py_INCREF(reinterpret_cast<PyObject*>(retval));
  return retval;
}

Py_ssize_t PyBlitzArray_NDIM (PyBlitzArrayObject* o) {
  return o->ndim;
}

Py_ssize_t* PyBlitzArray_SHAPE (PyBlitzArrayObject* o) {
  return o->shape;
}

PyObject* PyBlitzArray_PySHAPE (PyBlitzArrayObject* o) {
  PyObject* retval = PyTuple_New(o->ndim);
  if (!retval) return retval;
  for (Py_ssize_t i = 0; i != o->ndim; ++i) {
#if PY_VERSION_HEX >= 0x03000000
    PyTuple_SET_ITEM(retval, i, PyLong_FromSsize_t(o->shape[i]));
#else
    PyTuple_SET_ITEM(retval, i, PyInt_FromSsize_t(o->shape[i]));
#endif
  }
  return retval;
}

Py_ssize_t* PyBlitzArray_STRIDE (PyBlitzArrayObject* o) {
  return o->stride;
}

PyObject* PyBlitzArray_PySTRIDE (PyBlitzArrayObject* o) {
  PyObject* retval = PyTuple_New(o->ndim);
  if (!retval) return retval;
  for (Py_ssize_t i = 0; i != o->ndim; ++i) {
#if PY_VERSION_HEX >= 0x03000000
    PyTuple_SET_ITEM(retval, i, PyLong_FromSsize_t(o->stride[i]));
#else
    PyTuple_SET_ITEM(retval, i, PyInt_FromSsize_t(o->stride[i]));
#endif
  }
  return retval;
}

int PyBlitzArray_WRITEABLE(PyBlitzArrayObject* o) {
  return o->writeable;
}

PyObject* PyBlitzArray_PyWRITEABLE(PyBlitzArrayObject* o) {
  if (o->writeable) Py_RETURN_TRUE;
  Py_RETURN_FALSE;
}

PyObject* PyBlitzArray_BASE(PyBlitzArrayObject* o) {
  return o->base;
}

PyObject* PyBlitzArray_PyBASE(PyBlitzArrayObject* o) {
  if (o->base) {
    Py_INCREF(o->base);
    return o->base;
  }
  Py_RETURN_NONE;
}

/************
 * Indexing *
 ************/

template <typename T>
PyObject* getitem_inner(PyBlitzArrayObject* o, Py_ssize_t* pos) {

  Py_ssize_t tmp[BOB_BLITZ_MAXDIMS];

  /* Fix negative indexes and check ranges */
  for (Py_ssize_t i=0; i<o->ndim; ++i) {
    tmp[i] = pos[i];
    if (tmp[i] < 0) tmp[i] += o->shape[i];
    if (tmp[i] < 0 || tmp[i] >= o->shape[i]) {
      PyErr_Format(PyExc_IndexError, "%s(@%" PY_FORMAT_SIZE_T "d,'%s') position %" PY_FORMAT_SIZE_T "d is out of range: %" PY_FORMAT_SIZE_T "d not in [0,%" PY_FORMAT_SIZE_T "d[", Py_TYPE(o)->tp_name, o->ndim, PyBlitzArray_TypenumAsString(o->type_num), i, pos[i], o->shape[i]);
      return 0;
    }
  }

  /* If you get to this point, then you known the indexing is fine */

  switch (o->ndim) {

    case 1:
      {
        T& val = (*reinterpret_cast<blitz::Array<T,1>*>(o->bzarr))((int)tmp[0]);
        return PyArray_Scalar(&val, PyArray_DescrFromType(o->type_num), 0);
      }

    case 2:
      {
        T& val = (*reinterpret_cast<blitz::Array<T,2>*>(o->bzarr))((int)tmp[0], (int)tmp[1]);
        return PyArray_Scalar(&val, PyArray_DescrFromType(o->type_num), 0);
      }

    case 3:
      {
        T& val = (*reinterpret_cast<blitz::Array<T,3>*>(o->bzarr))((int)tmp[0], (int)tmp[1], (int)tmp[2]);
        return PyArray_Scalar(&val, PyArray_DescrFromType(o->type_num), 0);
      }

    case 4:
      {
        T& val = (*reinterpret_cast<blitz::Array<T,2>*>(o->bzarr))((int)tmp[0], (int)tmp[1], (int)tmp[2], (int)tmp[3]);
        return PyArray_Scalar(&val, PyArray_DescrFromType(o->type_num), 0);
      }

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot index %s(@%" PY_FORMAT_SIZE_T "d,'%s'): this number of dimensions is outside the range of supported dimensions [1,%d]", Py_TYPE(o)->tp_name, o->ndim, PyBlitzArray_TypenumAsString(o->type_num), BOB_BLITZ_MAXDIMS); return 0;
  }
}

PyObject* PyBlitzArray_GetItem(PyBlitzArrayObject* o, Py_ssize_t* pos) {

  switch (o->type_num) {

    case NPY_BOOL:
      return getitem_inner<bool>(o, pos);

    case NPY_INT8:
      return getitem_inner<int8_t>(o, pos);

    case NPY_INT16:
      return getitem_inner<int16_t>(o, pos);

    case NPY_INT32:
      return getitem_inner<int32_t>(o, pos);

    case NPY_INT64:
      return getitem_inner<int64_t>(o, pos);

    case NPY_UINT8:
      return getitem_inner<uint8_t>(o, pos);

    case NPY_UINT16:
      return getitem_inner<uint16_t>(o, pos);

    case NPY_UINT32:
      return getitem_inner<uint32_t>(o, pos);

    case NPY_UINT64:
      return getitem_inner<uint64_t>(o, pos);

    case NPY_FLOAT32:
      return getitem_inner<float>(o, pos);

    case NPY_FLOAT64:
      return getitem_inner<double>(o, pos);

#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      return getitem_inner<long double>(o, pos);

#endif

    case NPY_COMPLEX64:
      return getitem_inner<std::complex<float>>(o, pos);

    case NPY_COMPLEX128:
      return getitem_inner<std::complex<double>>(o, pos);

#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      return getitem_inner<std::complex<long double>>(o, pos);

#endif

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot index %s(@%" PY_FORMAT_SIZE_T "d,T) with T being a data type with an unsupported numpy type number = %d", Py_TYPE(o)->tp_name, o->ndim, o->type_num);
      return 0;

  }

}

/**
 * Sets a given item from the blitz::Array<>
 */
template <typename T>
int setitem_inner(PyBlitzArrayObject* o, Py_ssize_t* pos, PyObject* value) {

  Py_ssize_t tmp[BOB_BLITZ_MAXDIMS];

  /* Fix negative indexes and check ranges */
  for (Py_ssize_t i=0; i<o->ndim; ++i) {
    tmp[i] = pos[i];
    if (tmp[i] < 0) tmp[i] += o->shape[i];
    if (tmp[i] < 0 || tmp[i] >= o->shape[i]) {
      PyErr_Format(PyExc_IndexError, "array index (tmpition %" PY_FORMAT_SIZE_T "d) is out of range: %" PY_FORMAT_SIZE_T "d not in [0,%" PY_FORMAT_SIZE_T "d[", i, pos[i], o->shape[i]);
      return -1;
    }
  }

  /* If you get to this point, then you known the indexing is fine */

  switch (o->ndim) {

    case 1:
      {
        T c_value = PyBlitzArrayCxx_AsCScalar<T>(value);
        if (PyErr_Occurred()) return -1;
        (*reinterpret_cast<blitz::Array<T,1>*>(o->bzarr))((int)tmp[0]) = c_value;
        return 0;
      }

    case 2:
      {
        T c_value = PyBlitzArrayCxx_AsCScalar<T>(value);
        if (PyErr_Occurred()) return -1;
        (*reinterpret_cast<blitz::Array<T,2>*>(o->bzarr))((int)tmp[0], (int)tmp[1]) = c_value;
        return 0;
      }

    case 3:
      {
        T c_value = PyBlitzArrayCxx_AsCScalar<T>(value);
        if (PyErr_Occurred()) return -1;
        (*reinterpret_cast<blitz::Array<T,3>*>(o->bzarr))((int)tmp[0], (int)tmp[1], (int)tmp[2]) = c_value;
        return 0;
      }

    case 4:
      {
        T c_value = PyBlitzArrayCxx_AsCScalar<T>(value);
        if (PyErr_Occurred()) return -1;
        (*reinterpret_cast<blitz::Array<T,4>*>(o->bzarr))((int)tmp[0], (int)tmp[1], (int)tmp[2], (int)tmp[3]) = c_value;
        return 0;
      }

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot set item on %s(@%" PY_FORMAT_SIZE_T "d,'%s'): this number of dimensions is outside the range of supported dimensions [1,%d]", Py_TYPE(o)->tp_name, o->ndim, PyBlitzArray_TypenumAsString(o->type_num), BOB_BLITZ_MAXDIMS);
      return -1;
  }

}

int PyBlitzArray_SetItem(PyBlitzArrayObject* o, Py_ssize_t* pos, PyObject* value) {

  if (!o->writeable) {
    PyErr_Format(PyExc_RuntimeError, "cannot set item on read-only %s(@%" PY_FORMAT_SIZE_T "d,%s) ", Py_TYPE(o)->tp_name, o->ndim, PyBlitzArray_TypenumAsString(o->type_num));
    return -1;
  }

  switch (o->type_num) {

    case NPY_BOOL:
      return setitem_inner<bool>(o, pos, value);

    case NPY_INT8:
      return setitem_inner<int8_t>(o, pos, value);

    case NPY_INT16:
      return setitem_inner<int16_t>(o, pos, value);

    case NPY_INT32:
      return setitem_inner<int32_t>(o, pos, value);

    case NPY_INT64:
      return setitem_inner<int64_t>(o, pos, value);

    case NPY_UINT8:
      return setitem_inner<uint8_t>(o, pos, value);

    case NPY_UINT16:
      return setitem_inner<uint16_t>(o, pos, value);

    case NPY_UINT32:
      return setitem_inner<uint32_t>(o, pos, value);

    case NPY_UINT64:
      return setitem_inner<uint64_t>(o, pos, value);

    case NPY_FLOAT32:
      return setitem_inner<float>(o, pos, value);

    case NPY_FLOAT64:
      return setitem_inner<double>(o, pos, value);

#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      return setitem_inner<long double>(o, pos, value);

#endif

    case NPY_COMPLEX64:
      return setitem_inner<std::complex<float>>(o, pos, value);

    case NPY_COMPLEX128:
      return setitem_inner<std::complex<double>>(o, pos, value);

#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      return setitem_inner<std::complex<long double>>(o, pos, value);

#endif

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot set item on %s(@%" PY_FORMAT_SIZE_T "d,T) with T being a data type with an unsupported numpy type number = %d", Py_TYPE(o)->tp_name, o->ndim, o->type_num);
      return -1;

  }

}

/********************************
 * Construction and Destruction *
 ********************************/

PyObject* PyBlitzArray_New(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBlitzArrayObject* self = (PyBlitzArrayObject*)type->tp_alloc(type, 0);

  self->bzarr = 0;
  self->data = 0;
  self->type_num = NPY_NOTYPE;
  self->ndim = 0;
  self->writeable = 0;
  self->base = 0;

  return reinterpret_cast<PyObject*>(self);
}

template<typename T> void deallocate_inner(PyBlitzArrayObject* o) {

  switch (o->ndim) {

    case 1:
      delete reinterpret_cast<blitz::Array<T,1>*>(o->bzarr);
      break;

    case 2:
      delete reinterpret_cast<blitz::Array<T,2>*>(o->bzarr);
      break;

    case 3:
      delete reinterpret_cast<blitz::Array<T,3>*>(o->bzarr);
      break;

    case 4:
      delete reinterpret_cast<blitz::Array<T,4>*>(o->bzarr);
      break;

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot deallocate %s(@%" PY_FORMAT_SIZE_T "d,%s>, this number of dimensions is outside the range of supported dimensions [1,%d]", Py_TYPE(o)->tp_name, o->ndim, PyBlitzArray_TypenumAsString(o->type_num), BOB_BLITZ_MAXDIMS);
      return;
  }

  Py_XDECREF(o->base);
  Py_TYPE(o)->tp_free((PyObject*)o);
}

void PyBlitzArray_Delete (PyBlitzArrayObject* o) {

  if (!o->bzarr) {
    //shortcut
    Py_XDECREF(o->base);
    Py_TYPE(o)->tp_free((PyObject*)o);
    return;
  }

  switch (o->type_num) {

    case NPY_BOOL:
      return deallocate_inner<bool>(o);

    case NPY_INT8:
      return deallocate_inner<int8_t>(o);

    case NPY_INT16:
      return deallocate_inner<int16_t>(o);

    case NPY_INT32:
      return deallocate_inner<int32_t>(o);

    case NPY_INT64:
      return deallocate_inner<int64_t>(o);

    case NPY_UINT8:
      return deallocate_inner<uint8_t>(o);

    case NPY_UINT16:
      return deallocate_inner<uint16_t>(o);

    case NPY_UINT32:
      return deallocate_inner<uint32_t>(o);

    case NPY_UINT64:
      return deallocate_inner<uint64_t>(o);

    case NPY_FLOAT32:
      return deallocate_inner<float>(o);

    case NPY_FLOAT64:
      return deallocate_inner<double>(o);

#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      return deallocate_inner<long double>(o);

#endif

    case NPY_COMPLEX64:
      return deallocate_inner<std::complex<float>>(o);

    case NPY_COMPLEX128:
      return deallocate_inner<std::complex<double>>(o);

#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      return deallocate_inner<std::complex<long double>>(o);

#endif

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot deallocate %s(@%" PY_FORMAT_SIZE_T "d,T) with T having an unsupported numpy type number of %d", Py_TYPE(o)->tp_name, o->ndim, o->type_num);
      return;

  }

}

template<typename T, int N>
int simplenew_2(PyBlitzArrayObject* arr, int type_num, Py_ssize_t ndim, Py_ssize_t* shape) {

  try {

    blitz::TinyVector<int,N> tv_shape;
    for (int i=0; i<N; ++i) tv_shape(i) = shape[i];
    auto bz = new blitz::Array<T,N>(tv_shape);
    arr->bzarr = static_cast<void*>(bz);
    arr->data = bz->data();
    arr->type_num = type_num;
    arr->ndim = ndim;
    for (Py_ssize_t i=0; i<N; ++i) {
      arr->shape[i] = shape[i];
      arr->stride[i] = sizeof(T)*bz->stride(i); ///in **bytes**
    }
    arr->writeable = 1;
    return 0;
  }

  catch (std::exception& e) {
    PyErr_Format(PyExc_RuntimeError, "caught exception while instantiating %s(@%" PY_FORMAT_SIZE_T "d,'%s'): %s", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num), e.what());
  }

  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while instantiating %s(@%" PY_FORMAT_SIZE_T "d,'%s')", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num));
  }

  /** some test code
  std::cout << "allocating array" << std::endl;
  std::shared_ptr<blitz::Array<T,N>> retval(new blitz::Array<T,N>(tv_shape),
      &delete_array<T,N>);
  **/

  return -1;

}

template<typename T>
int simplenew_1(PyBlitzArrayObject* arr, int type_num, Py_ssize_t ndim, Py_ssize_t* shape) {
  switch (ndim) {

    case 1:
      return simplenew_2<T,1>(arr, type_num, ndim, shape);

    case 2:
      return simplenew_2<T,2>(arr, type_num, ndim, shape);

    case 3:
      return simplenew_2<T,3>(arr, type_num, ndim, shape);

    case 4:
      return simplenew_2<T,4>(arr, type_num, ndim, shape);

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot allocate %s(@%" PY_FORMAT_SIZE_T "d,'%s'): this number of dimensions is outside the range of supported dimensions [1,%d]", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num), BOB_BLITZ_MAXDIMS);
      return -1;
  }

}

// Initializes the given arr with new data of the desired size
// No check is performed, so old data is simply overwritten!
// Returns 0 on success and -1 on failure
int PyBlitzArray_SimpleInit(PyBlitzArrayObject* arr, int type_num, Py_ssize_t ndim, Py_ssize_t* shape) {

  if (!arr){
    PyErr_Format(PyExc_RuntimeError, "PyBlitzArray_SimpleInit: Cannot fill an array pointing to NULL.");
    return -1;
  }

  type_num = fix_integer_type_num(type_num);

  switch (type_num) {

    case NPY_BOOL:
      return simplenew_1<bool>(arr, type_num, ndim, shape);

    case NPY_INT8:
      return simplenew_1<int8_t>(arr, type_num, ndim, shape);

    case NPY_INT16:
      return simplenew_1<int16_t>(arr, type_num, ndim, shape);

    case NPY_INT32:
      return simplenew_1<int32_t>(arr, type_num, ndim, shape);

    case NPY_INT64:
      return simplenew_1<int64_t>(arr, type_num, ndim, shape);

    case NPY_UINT8:
      return simplenew_1<uint8_t>(arr, type_num, ndim, shape);

    case NPY_UINT16:
      return simplenew_1<uint16_t>(arr, type_num, ndim, shape);

    case NPY_UINT32:
      return simplenew_1<uint32_t>(arr, type_num, ndim, shape);

    case NPY_UINT64:
      return simplenew_1<uint64_t>(arr, type_num, ndim, shape);

    case NPY_FLOAT32:
      return simplenew_1<float>(arr, type_num, ndim, shape);

    case NPY_FLOAT64:
      return simplenew_1<double>(arr, type_num, ndim, shape);

#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      return simplenew_1<long double>(arr, type_num, ndim, shape);

#endif

    case NPY_COMPLEX64:
      return simplenew_1<std::complex<float>>(arr, type_num, ndim, shape);

    case NPY_COMPLEX128:
      return simplenew_1<std::complex<double>>(arr, type_num, ndim, shape);

#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      return simplenew_1<std::complex<long double>>(arr, type_num, ndim, shape);

#endif

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot create %s(@%" PY_FORMAT_SIZE_T "d,T) with T having an unsupported numpy type number of %d", PyBlitzArray_Type.tp_name, ndim, type_num);
      return -1;

  }

}

// Creates and returns a new PyBlitzArrayObject with the desired size
PyObject* PyBlitzArray_SimpleNew (int type_num, Py_ssize_t ndim, Py_ssize_t* shape) {

  PyBlitzArrayObject* retval = (PyBlitzArrayObject*)PyBlitzArray_New(&PyBlitzArray_Type, 0, 0);

  auto retval_ = make_safe(retval);

  if (PyBlitzArray_SimpleInit(retval, type_num, ndim, shape) != 0)
    return 0;

  return Py_BuildValue("O", retval);

}


// N.B.: cannot use lambdas with very old versions of gcc
struct stride_sorter {
  Py_ssize_t* _s;
  stride_sorter(Py_ssize_t* s) { _s = s; }
  bool operator() (int i1, int i2) { return _s[i1] <= _s[i2]; }
};

template <int N>
void stride_order(Py_ssize_t* s, blitz::TinyVector<int,N>& tv) {

  for (int i=0; i<N; ++i) tv[i] = i;
  int* idx = tv.data();
  std::sort(idx, idx+N, stride_sorter(s));

}

template<typename T, int N>
PyObject* simplenewfromdata_2(int type_num, Py_ssize_t ndim,
    Py_ssize_t* shape, Py_ssize_t* stride, void* data, int writeable) {

  try {

    blitz::TinyVector<int,N> tv_shape;
    blitz::TinyVector<int,N> tv_stride;
    for (int i=0; i<N; ++i) {
      tv_shape(i) = shape[i];
      tv_stride(i) = stride[i]/sizeof(T); ///< from **bytes**
    }
    PyBlitzArrayObject* retval = (PyBlitzArrayObject*)PyBlitzArray_New(&PyBlitzArray_Type, 0, 0);

    //get the storage right
    blitz::TinyVector<bool,N> ascending;
    ascending = true;
    blitz::TinyVector<int,N> ordering;
    stride_order(stride, ordering);
    blitz::GeneralArrayStorage<N> storage(ordering, ascending);

    auto bz = new blitz::Array<T,N>(reinterpret_cast<T*>(data), tv_shape, tv_stride, blitz::neverDeleteData, storage);
    retval->bzarr = static_cast<void*>(bz);
    retval->data = data;
    retval->type_num = type_num;
    retval->ndim = ndim;
    for (Py_ssize_t i=0; i<N; ++i) {
      retval->shape[i] = shape[i];
      retval->stride[i] = stride[i];
    }
    retval->writeable = writeable ? 1 : 0;
    return reinterpret_cast<PyObject*>(retval);

  }

  catch (std::exception& e) {
    PyErr_Format(PyExc_RuntimeError, "caught exception while instantiating %s(@%" PY_FORMAT_SIZE_T "d,'%s'): %s", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num), e.what());
  }

  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while instantiating %s(@%" PY_FORMAT_SIZE_T "d,'%s')", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num));
  }

  /** some test code
  std::cout << "allocating array" << std::endl;
  std::shared_ptr<blitz::Array<T,N>> retval(new blitz::Array<T,N>(tv_shape),
      &delete_array<T,N>);
  **/

  return 0;

}

template<typename T>
PyObject* simplenewfromdata_1(int type_num, Py_ssize_t ndim,
    Py_ssize_t* shape, Py_ssize_t* stride, void* data, int writeable) {

  switch (ndim) {

    case 1:
      return simplenewfromdata_2<T,1>(type_num, ndim, shape, stride, data, writeable);

    case 2:
      return simplenewfromdata_2<T,2>(type_num, ndim, shape, stride, data, writeable);

    case 3:
      return simplenewfromdata_2<T,3>(type_num, ndim, shape, stride, data, writeable);

    case 4:
      return simplenewfromdata_2<T,4>(type_num, ndim, shape, stride, data, writeable);

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot allocate %s(@%" PY_FORMAT_SIZE_T "d,'%s'): this number of dimensions is outside the range of supported dimensions [1,%d]", PyBlitzArray_Type.tp_name, ndim, PyBlitzArray_TypenumAsString(type_num), BOB_BLITZ_MAXDIMS);
      return 0;
  }

}

PyObject* PyBlitzArray_SimpleNewFromData (int type_num, Py_ssize_t ndim,
    Py_ssize_t* shape, Py_ssize_t* stride, void* data, int writeable) {

  type_num = fix_integer_type_num(type_num);

  switch (type_num) {

    case NPY_BOOL:
      return simplenewfromdata_1<bool>(type_num, ndim, shape, stride, data, writeable);

    case NPY_INT8:
      return simplenewfromdata_1<int8_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_INT16:
      return simplenewfromdata_1<int16_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_INT32:
      return simplenewfromdata_1<int32_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_INT64:
      return simplenewfromdata_1<int64_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_UINT8:
      return simplenewfromdata_1<uint8_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_UINT16:
      return simplenewfromdata_1<uint16_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_UINT32:
      return simplenewfromdata_1<uint32_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_UINT64:
      return simplenewfromdata_1<uint64_t>(type_num, ndim, shape, stride, data, writeable);

    case NPY_FLOAT32:
      return simplenewfromdata_1<float>(type_num, ndim, shape, stride, data, writeable);

    case NPY_FLOAT64:
      return simplenewfromdata_1<double>(type_num, ndim, shape, stride, data, writeable);

#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      return simplenewfromdata_1<long double>(type_num, ndim, shape, stride, data, writeable);

#endif

    case NPY_COMPLEX64:
      return simplenewfromdata_1<std::complex<float>>(type_num, ndim, shape, stride, data, writeable);

    case NPY_COMPLEX128:
      return simplenewfromdata_1<std::complex<double>>(type_num, ndim, shape, stride, data, writeable);

#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      return simplenewfromdata_1<std::complex<long double>>(type_num, ndim, shape, stride, data, writeable);

#endif

    default:
      PyErr_Format(PyExc_NotImplementedError, "cannot create %s(@%" PY_FORMAT_SIZE_T "d,T) with T having an unsupported numpy type number of %d", PyBlitzArray_Type.tp_name, ndim, type_num);
      return 0;

  }

}

/****************************
 * From/To NumPy Converters *
 ****************************/

PyObject* PyBlitzArray_AsNumpyArray(PyBlitzArrayObject* o, PyArray_Descr* newtype) {

  // if o->base is a numpy array, return it
  if (o->base && PyArray_Check(o->base)) {
    if (newtype) return PyArray_FromArray(reinterpret_cast<PyArrayObject*>(o->base), newtype,
#       if NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
        NPY_ARRAY_FORCECAST
#       else
        NPY_FORCECAST
#       endif
        );
    Py_INCREF(o->base);
    return o->base;
  }

  // creates an ndarray from the blitz::Array<>.data()
  PyArray_Descr* dtype = PyArray_DescrFromType(o->type_num); //borrowed
  PyObject* retval = PyArray_NewFromDescr(&PyArray_Type,
      dtype,
      o->ndim, o->shape, o->stride, o->data,
#     if NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
      NPY_ARRAY_CARRAY,
#     else
      NPY_CARRAY,
#     endif
      0);

  if (!retval) return 0;

  // link this object with the returned numpy ndarray

#if NPY_FEATURE_VERSION < NUMPY17_API /* NumPy C-API version >= 1.7 */
  PyArray_BASE(reinterpret_cast<PyArrayObject*>(retval)) = reinterpret_cast<PyObject*>(o);
#else
  if (PyArray_SetBaseObject(reinterpret_cast<PyArrayObject*>(retval), reinterpret_cast<PyObject*>(o)) != 0) {
    Py_DECREF(retval);
    return 0;
  }
#endif
  Py_INCREF(reinterpret_cast<PyObject*>(o));

  // if newtype was specified and the types are not equivalent, cast
  if (newtype && !PyArray_EquivTypenums(newtype->type_num, o->type_num)) {
    PyObject* new_retval = PyArray_FromArray(reinterpret_cast<PyArrayObject*>(retval),
        newtype,
#       if NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
        NPY_ARRAY_FORCECAST
#       else
        NPY_FORCECAST
#       endif
        );
    Py_DECREF(retval);
    retval = new_retval;
  }

  return retval;

}

static int ndarray_behaves (PyArrayObject* o) {

  if (!PyArray_Check(o)) return 0;

  PyArrayObject* ao = reinterpret_cast<PyArrayObject*>(o);

  // checks if the array is C-style and memory aligned
  if (!PyArray_ISBEHAVED_RO(ao)) return 0;

  // checks if the number of dimensions is supported
  if (PyArray_NDIM(ao) < 1 || PyArray_NDIM(ao) > BOB_BLITZ_MAXDIMS) return 0;

  // checks if the type number if supported
  switch(fix_integer_type_num(PyArray_DESCR(ao)->type_num)) {
    case NPY_BOOL:
    case NPY_UINT8:
    case NPY_UINT16:
    case NPY_UINT32:
    case NPY_UINT64:
    case NPY_INT8:
    case NPY_INT16:
    case NPY_INT32:
    case NPY_INT64:
    case NPY_FLOAT32:
    case NPY_FLOAT64:
#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
#endif
    case NPY_COMPLEX64:
    case NPY_COMPLEX128:
#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
#endif
      break;
    default:
      return 0;
  }

  // if you get to this point, you can only return yes
  return 1;
}

PyObject* PyBlitzArray_FromNumpyArray(PyArrayObject* o) {

  // is numpy.ndarray wrapped around a blitz.array
  if (PyBlitzArray_CheckNumpyBase(o)) {
    Py_INCREF(PyArray_BASE(o));
    return PyArray_BASE(o);
  }

  if (!ndarray_behaves(o)) {
    PyErr_Format(PyExc_ValueError, "cannot convert `%s' which doesn't behave (memory contiguous, aligned, C-style, minimum 1 and up to %d dimensions) into a `%s'", Py_TYPE(o)->tp_name, BOB_BLITZ_MAXDIMS, PyBlitzArray_Type.tp_name);
    return 0;
  }

  PyObject* retval = PyBlitzArray_SimpleNewFromData(
      PyArray_DESCR(o)->type_num,
      PyArray_NDIM(o),
      PyArray_DIMS(o),
      PyArray_STRIDES(o),
      PyArray_DATA(o),
#     if NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
      PyArray_FLAGS(o) & NPY_ARRAY_WRITEABLE
#     else
      PyArray_FLAGS(o) & NPY_WRITEABLE
#     endif
      );

  if (!retval) return 0;

  PyObject* pyo = reinterpret_cast<PyObject*>(o);
  reinterpret_cast<PyBlitzArrayObject*>(retval)->base = pyo;
  Py_INCREF(pyo);

  return retval;

}

PyObject* PyBlitzArray_NUMPY_WRAP(PyObject* bz) {

  if (!bz) return bz;

  PyBlitzArrayObject* o = reinterpret_cast<PyBlitzArrayObject*>(bz);

  // creates an ndarray from the blitz::Array<>.data()
  PyArray_Descr* dtype = PyArray_DescrFromType(o->type_num); //borrowed
  PyObject* retval = PyArray_NewFromDescr(&PyArray_Type,
      dtype,
      o->ndim, o->shape, o->stride, o->data,
#     if NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
      NPY_ARRAY_CARRAY,
#     else
      NPY_CARRAY,
#     endif
      0);

  if (!retval) return 0;

  // link this object with the returned numpy ndarray

#if NPY_FEATURE_VERSION < NUMPY17_API /* NumPy C-API version >= 1.7 */
  PyArray_BASE(reinterpret_cast<PyArrayObject*>(retval)) = bz;
#else
  if (PyArray_SetBaseObject(reinterpret_cast<PyArrayObject*>(retval), bz) != 0) {
    Py_DECREF(retval);
    return 0;
  }
#endif

  return retval;

}

/***********************************************
 * Converter Functions for PyArg_Parse* family *
 ***********************************************/

int PyBlitzArray_Converter(PyObject* o, PyBlitzArrayObject** a) {

  // is already a bob.blitz.array
  if (PyBlitzArray_Check(o)) {
    *a = reinterpret_cast<PyBlitzArrayObject*>(o);
    Py_INCREF(*a);
    return 1;
  }

  // is numpy.ndarray wrapped around a bob.blitz.array
  if (PyArray_Check(o)) {
    PyArrayObject* arr = reinterpret_cast<PyArrayObject*>(o);
    if (PyBlitzArray_CheckNumpyBase(arr)) {
      *a = reinterpret_cast<PyBlitzArrayObject*>(PyArray_BASE(arr));
      Py_INCREF(*a);
      return 1;
    }
  }

  // run the normal converter
  PyObject* ao = 0;
  if (!PyArray_Converter(o, &ao)) {
    PyErr_Print();
    PyErr_Format(PyExc_ValueError, "cannot convert argument to `%s' - prefix conversion to numpy.ndarray failed", Py_TYPE(*a)->tp_name);
    return 0;
  }

  PyObject* retval = PyBlitzArray_FromNumpyArray(reinterpret_cast<PyArrayObject*>(ao));
  Py_DECREF(ao);

  *a = reinterpret_cast<PyBlitzArrayObject*>(retval);

  return (*a) ? 1 : 0;

}

int PyBlitzArray_OutputConverter(PyObject* o, PyBlitzArrayObject** a) {

  // is already a bob.blitz.array
  if (PyBlitzArray_Check(o)) {
    *a = reinterpret_cast<PyBlitzArrayObject*>(o);
    Py_INCREF(o);
    return 1;
  }

  // is numpy.ndarray wrapped around a bob.blitz.array
  if (PyArray_Check(o)) {
    PyArrayObject* arr = reinterpret_cast<PyArrayObject*>(o);
    if (PyBlitzArray_CheckNumpyBase(arr)) {
      *a = reinterpret_cast<PyBlitzArrayObject*>(PyArray_BASE(arr));
      Py_INCREF(*a);
      return 1;
    }
  }

  // run the numpy output converter, hope it works
  PyArrayObject* ao = 0;
  if (!PyArray_OutputConverter(o, &ao)) {
    PyErr_Print();
    PyErr_Format(PyExc_ValueError, "cannot convert argument to %s - prefix conversion to numpy.ndarray failed", Py_TYPE(o)->tp_name);
    return 0;
  }

  PyObject* retval = PyBlitzArray_FromNumpyArray(ao);

  // note: as the numpy c-api manual states, if the input object to
  // PyArray_OutputConverter() responds 'true' to PyArray_Check(), then
  // its reference count is not incremented. Therefore, we only need
  // to DECREF this guy if it is PyArray_Check() is 'false'.
  if (!PyArray_Check(o)) {
    Py_DECREF(ao);
  }

  *a = reinterpret_cast<PyBlitzArrayObject*>(retval);

  return (*a) ? 1 : 0;

}

int PyBlitzArray_BehavedConverter(PyObject* o, PyBlitzArrayObject** a) {

  // is already a bob.blitz.array
  // TODO: Don't we check in these conditions?
  if (PyBlitzArray_Check(o)) {
    *a = reinterpret_cast<PyBlitzArrayObject*>(o);
    Py_INCREF(*a);
    return 1;
  }

  // is numpy.ndarray wrapped around a bob.blitz.array
  if (PyArray_Check(o)) {
    PyArrayObject* arr = reinterpret_cast<PyArrayObject*>(o);
    if (PyArray_ISCARRAY_RO(arr) && PyBlitzArray_CheckNumpyBase(arr)) {
      *a = reinterpret_cast<PyBlitzArrayObject*>(PyArray_BASE(arr));
      Py_INCREF(*a);
      return 1;
    }
  }

  // run the normal converter
  PyObject* ao = 0;
  if (!PyArray_Converter(o, &ao)) {
    PyErr_Print();
    PyErr_Format(PyExc_ValueError, "cannot convert argument to %s - prefix conversion to numpy.ndarray failed", Py_TYPE(o)->tp_name);
    return 0;
  }

  PyArrayObject* arr = reinterpret_cast<PyArrayObject*>(ao);

  // check if array is behaved
  if (!PyArray_ISCARRAY_RO(arr)) { //copies and discard non-behaved
    PyObject* tmp = PyArray_NewCopy(arr, NPY_ANYORDER);
    Py_DECREF(ao);
    ao = tmp;
    arr = reinterpret_cast<PyArrayObject*>(ao);
  }

  PyObject* retval = PyBlitzArray_FromNumpyArray(arr);
  Py_DECREF(ao);

  *a = reinterpret_cast<PyBlitzArrayObject*>(retval);

  return (*a) ? 1 : 0;

}

int PyBlitzArray_IndexConverter(PyObject* o, PyBlitzArrayObject** shape) {

  if (PyBob_NumberCheck(o)) {
    (*shape)->ndim = 1;
    (*shape)->shape[0] = PyNumber_AsSsize_t(o, PyExc_OverflowError);
    if (PyErr_Occurred()) return 0;
    if ((*shape)->shape[0] < 0) {
      PyErr_Format(PyExc_ValueError, "index/shape values should be >=0; %" PY_FORMAT_SIZE_T "d is invalid", (*shape)->shape[0]);
      return 0;
    }
    return 1;
  }

  /* The other option is to have it as a sequence */
  if (!PySequence_Check(o)) {
    PyErr_SetString(PyExc_TypeError, "shape/index must be a sequence of integers");
    return 0;
  }

  (*shape)->ndim = PySequence_Size(o);

  if ((*shape)->ndim == 0 || (*shape)->ndim > BOB_BLITZ_MAXDIMS) {
    PyErr_Format(PyExc_TypeError, "shape/index must be a sequence with at least 1 and at most %d element(s) (you passed a sequence with %" PY_FORMAT_SIZE_T "d elements)", BOB_BLITZ_MAXDIMS, (*shape)->ndim);
    return 0;
  }

  for (Py_ssize_t i=0; i<(*shape)->ndim; ++i) {
    PyObject* item = PySequence_GetItem(o, i);
    if (!item) return 0;
    if (!PyBob_NumberCheck(item)) {
      PyErr_Format(PyExc_ValueError, "element %" PY_FORMAT_SIZE_T "d from shape/index sequence should be an number (coercible to integer)", i);
      Py_DECREF(item);
      return 0;
    }
    (*shape)->shape[i] = PyNumber_AsSsize_t(item, PyExc_OverflowError);
    if (PyErr_Occurred()) {
      PyErr_Print();
      PyErr_Format(PyExc_TypeError, "error extracting a size from element %" PY_FORMAT_SIZE_T "d of input shape/index sequence", i);
      Py_DECREF(item);
      return 0;
    }
    if ((*shape)->shape[0] < 0) {
      PyErr_Format(PyExc_ValueError, "shape/index values should be >=0; %" PY_FORMAT_SIZE_T "d is an invalid value at position %" PY_FORMAT_SIZE_T "d of input sequence", (*shape)->shape[0], i);
      Py_DECREF(item);
      return 0;
    }
  }

  return 1;
}

int PyBlitzArray_TypenumConverter(PyObject* o, int* type_num) {

  PyArray_Descr* dtype = 0;
  if (!PyArray_DescrConverter2(o, &dtype)) return 0; ///< (*dtype) is borrowed
  (*type_num) = dtype->type_num;

  switch (fix_integer_type_num(*type_num)) {
    case NPY_BOOL:
    case NPY_UINT8:
    case NPY_UINT16:
    case NPY_UINT32:
    case NPY_UINT64:
    case NPY_INT8:
    case NPY_INT16:
    case NPY_INT32:
    case NPY_INT64:
    case NPY_FLOAT32:
    case NPY_FLOAT64:
#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
#endif
    case NPY_COMPLEX64:
    case NPY_COMPLEX128:
#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
#endif
      break;
    default:
    {
      PyErr_Format(PyExc_NotImplementedError, "no support for using type number %d in %s", (*type_num), Py_TYPE(o)->tp_name);
      return 0;
    }
  }

  /* At this point, you know everything went well */
  return 1;
}

/*************
 * Utilities *
 *************/

/**
 * A simple implementation of the function below. It returns type names such as
 * "numpy.uint64" instead of just "uint64". The type name is also associated to
 * an object which may vanish - so, not that safe.
 */
/**
const char* PyBlitzArray_TypenumAsString (int type_num) {
  PyArray_Descr* dtype = PyArray_DescrFromType(type_num); ///< new reference
  if (!dtype) return 0;
  const char* retval = dtype->typeobj->tp_name;
  Py_DECREF(dtype);
  return retval;
}
*/

const char* PyBlitzArray_TypenumAsString (int type_num) {

  type_num = fix_integer_type_num(type_num);

  switch (type_num) {

    case NPY_BOOL:
      {
        static char s[] = "bool";
        return s;
      }
    case NPY_UINT8:
      {
        static char s[] = "uint8";
        return s;
      }
    case NPY_UINT16:
      {
        static char s[] = "uint16";
        return s;
      }
    case NPY_UINT32:
      {
        static char s[] = "uint32";
        return s;
      }
    case NPY_UINT64:
      {
        static char s[] = "uint64";
        return s;
      }
    case NPY_INT8:
      {
        static char s[] = "int8";
        return s;
      }
    case NPY_INT16:
      {
        static char s[] = "int16";
        return s;
      }
    case NPY_INT32:
      {
        static char s[] = "int32";
        return s;
      }
    case NPY_INT64:
      {
        static char s[] = "int64";
        return s;
      }
    case NPY_FLOAT32:
      {
        static char s[] = "float32";
        return s;
      }
    case NPY_FLOAT64:
      {
        static char s[] = "float64";
        return s;
      }
#ifdef NPY_FLOAT128
    case NPY_FLOAT128:
      {
        static char s[] = "float128";
        return s;
      }
#endif
    case NPY_COMPLEX64:
      {
        static char s[] = "complex64";
        return s;
      }
    case NPY_COMPLEX128:
      {
        static char s[] = "complex128";
        return s;
      }
#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256:
      {
        static char s[] = "complex256";
        return s;
      }
#endif
    default:
      {
        static char s[] = "unsupported";
        return s;
      }
  }

}

size_t PyBlitzArray_TypenumSize (int type_num) {

  PyArray_Descr* dtype = PyArray_DescrFromType(type_num); ///< new reference
  if (!dtype) return 0;
  size_t retval = dtype->elsize;
  Py_DECREF(dtype);
  return retval;

}

PyObject* PyBlitzArray_Cast (PyBlitzArrayObject* o, int type_num) {
  if (o->type_num == type_num) {
    auto pyo = (PyObject*)o;
    Py_INCREF(pyo);
    return pyo;
  }

  //non-matching type has been found, just cast using the NumPy C-API
  PyObject* npy = PyBlitzArray_AsNumpyArray(o, PyArray_DescrFromType(type_num));
  if (!npy) return 0;
  PyObject* retval = PyBlitzArray_FromNumpyArray((PyArrayObject*)npy);
  Py_DECREF(npy);
  return retval;
}
