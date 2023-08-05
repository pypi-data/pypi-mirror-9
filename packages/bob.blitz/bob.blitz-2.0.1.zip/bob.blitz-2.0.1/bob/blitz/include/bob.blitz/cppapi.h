/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 10 Oct 16:02:58 2013
 *
 * @brief These are C++ extensions in the form of templates that are extras for
 * transforming C++ objects into our Pythonic blitz::Array<> layer.
 */

#ifndef BOB_BLITZ_CPP_API_H
#define BOB_BLITZ_CPP_API_H

#include <bob.blitz/capi.h>

#include <complex>
#include <blitz/array.h>
#include <stdint.h>
#include <stdexcept>
#include <typeinfo>

template <typename T> int PyBlitzArrayCxx_CToTypenum() {

  const std::type_info& ttype = typeid(T);

  if (ttype == typeid(bool))          return NPY_BOOL;
  else if (ttype == typeid(uint8_t))  return NPY_UINT8;
  else if (ttype == typeid(uint16_t)) return NPY_UINT16;
  else if (ttype == typeid(uint32_t)) return NPY_UINT32;
  else if (ttype == typeid(uint64_t)) return NPY_UINT64;
  else if (ttype == typeid(int8_t))   return NPY_INT8;
  else if (ttype == typeid(int16_t))  return NPY_INT16;
  else if (ttype == typeid(int32_t))  return NPY_INT32;
  else if (ttype == typeid(int64_t))  return NPY_INT64;
  else if (ttype == typeid(float))    return NPY_FLOAT32;
  else if (ttype == typeid(double))   return NPY_FLOAT64;
#ifdef NPY_FLOAT128
  else if (ttype == typeid(long double)) return NPY_FLOAT128;
#endif
  else if (ttype == typeid(std::complex<float>))  return NPY_COMPLEX64;
  else if (ttype == typeid(std::complex<double>)) return NPY_COMPLEX128;
#ifdef NPY_COMPLEX256
  else if (ttype == typeid(std::complex<long double>)) return NPY_COMPLEX256;
#endif
#ifdef __APPLE__
  else if (ttype == typeid(long)) {
    if (sizeof(long) == 4) return NPY_INT32;
    else return NPY_INT64;
  }
  else if (ttype == typeid(unsigned long)) {
    if (sizeof(unsigned long) == 4) return NPY_UINT32;
    else return NPY_UINT64;
  }
#endif

  // if you get to this point, the type is not supported
  PyErr_Format(PyExc_NotImplementedError, "c++ type to numpy type_num conversion unsupported for typeid.name() `%s'", typeid(T).name());
  return -1;

}

template <typename T> T PyBlitzArrayCxx_AsCScalar(PyObject* o) {

  int type_num = PyBlitzArrayCxx_CToTypenum<T>();
  if (PyErr_Occurred()) {
    T retval = 0;
    return retval;
  }

  // create a zero-dimensional array on the expected type
  PyArrayObject* zerodim =
    reinterpret_cast<PyArrayObject*>(PyArray_SimpleNew(0, 0, type_num));

  if (!zerodim) {
    T retval = 0;
    return retval;
  }

  int status = PyArray_SETITEM(zerodim,
      reinterpret_cast<char*>(PyArray_DATA(zerodim)), o);

  if (status != 0) {
    T retval = 0;
    return retval;
  }

  // note: this will decref `zerodim'
  PyObject* scalar=PyArray_Return(zerodim);

  if (!scalar) {
    T retval = 0;
    return retval;
  }

  T retval = 0;
  PyArray_ScalarAsCtype(scalar, &retval);
  Py_DECREF(scalar);
  return retval;
}

template <typename T> PyObject* PyBlitzArrayCxx_FromCScalar(T v) {

  PyArray_Descr* descr = 0;
  const std::type_info& ttype = typeid(T);

  if (ttype == typeid(bool))
    descr = PyArray_DescrFromType(NPY_BOOL);
  else if (ttype == typeid(uint8_t))
    descr = PyArray_DescrFromType(NPY_UINT8);
  else if (ttype == typeid(uint16_t))
    descr = PyArray_DescrFromType(NPY_UINT16);
  else if (ttype == typeid(uint32_t))
    descr = PyArray_DescrFromType(NPY_UINT32);
  else if (ttype == typeid(uint64_t))
    descr = PyArray_DescrFromType(NPY_UINT64);
  else if (ttype == typeid(int8_t))
    descr = PyArray_DescrFromType(NPY_INT8);
  else if (ttype == typeid(int16_t))
    descr = PyArray_DescrFromType(NPY_INT16);
  else if (ttype == typeid(int32_t))
    descr = PyArray_DescrFromType(NPY_INT32);
  else if (ttype == typeid(int64_t))
    descr = PyArray_DescrFromType(NPY_INT64);
  else if (ttype == typeid(float))
    descr = PyArray_DescrFromType(NPY_FLOAT32);
  else if (ttype == typeid(double))
    descr = PyArray_DescrFromType(NPY_FLOAT64);
#ifdef NPY_FLOAT128
  else if (ttype == typeid(long double))
    descr = PyArray_DescrFromType(NPY_FLOAT128);
#endif
  else if (ttype == typeid(std::complex<float>))
    descr = PyArray_DescrFromType(NPY_COMPLEX64);
  else if (ttype == typeid(std::complex<double>))
    descr = PyArray_DescrFromType(NPY_COMPLEX128);
#ifdef NPY_COMPLEX256
  else if (ttype == typeid(std::complex<long double>))
    descr = PyArray_DescrFromType(NPY_COMPLEX256);
#endif
#ifdef __APPLE__
  else if (ttype == typeid(long)) {
    if (sizeof(long) == 4) descr = PyArray_DescrFromType(NPY_INT32);
    else descr = PyArray_DescrFromType(NPY_INT64);
  }
  else if (ttype == typeid(unsigned long)) {
    if (sizeof(unsigned long) == 4) descr = PyArray_DescrFromType(NPY_UINT32);
    else descr = PyArray_DescrFromType(NPY_UINT64);
  }
#endif
  else {
    PyErr_Format(PyExc_NotImplementedError, "c++ value to numpy scalar conversion unsupported for typeid.name() == `%s'", typeid(T).name());
    return 0;
  }

  PyObject* retval = PyArray_Scalar(&v, descr, 0);
  Py_DECREF(descr);
  return retval;
}

template <typename T, int N>
int PyBlitzArrayCxx_IsBehaved(const blitz::Array<T,N>& a) {

  if(!a.isStorageContiguous()) return 0;

  for(int i=0; i<a.rank(); ++i) {
    if(!(a.isRankStoredAscending(i) && a.ordering(i)==a.rank()-1-i))
      return 0;
  }

  //if you get to this point, nothing else to-do rather than return true
  return 1;
}

template <typename T, int N>
PyObject* PyBlitzArrayCxx_NewFromConstArray(const blitz::Array<T,N>& a) {

  if (!PyBlitzArrayCxx_IsBehaved(a)) {
    PyErr_Format(PyExc_ValueError, "cannot convert C++ blitz::Array<%s,%d> which doesn't behave (memory contiguous, aligned, C-style) into a pythonic %s.array", PyBlitzArray_TypenumAsString(PyBlitzArrayCxx_CToTypenum<T>()), N, BOB_BLITZ_PREFIX);
    return 0;
  }

  try {

    PyTypeObject& tp = PyBlitzArray_Type;
    PyBlitzArrayObject* retval = (PyBlitzArrayObject*)PyBlitzArray_New(&tp, 0, 0);
    retval->bzarr = static_cast<void*>(new blitz::Array<T,N>(a));
    retval->data = const_cast<void*>(static_cast<const void*>(a.data()));
    retval->type_num = PyBlitzArrayCxx_CToTypenum<T>();
    retval->ndim = N;
    for (Py_ssize_t i=0; i<N; ++i) {
      retval->shape[i] = a.extent(i);
      retval->stride[i] = sizeof(T)*a.stride(i); ///in **bytes**
    }
    retval->writeable = 0;
    return reinterpret_cast<PyObject*>(retval);

  }

  catch (std::exception& e) {
    PyErr_Format(PyExc_RuntimeError, "caught exception while instantiating %s.array(@%d,'%s'): %s", BOB_BLITZ_PREFIX, N, PyBlitzArray_TypenumAsString(PyBlitzArrayCxx_CToTypenum<T>()), e.what());
  }

  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while instantiating %s.array(@%d,'%s')", BOB_BLITZ_PREFIX, N, PyBlitzArray_TypenumAsString(PyBlitzArrayCxx_CToTypenum<T>()));
  }

  /** some test code
  std::cout << "allocating array" << std::endl;
  boost::shared_ptr<blitz::Array<T,N>> retval(new blitz::Array<T,N>(tv_shape),
      &delete_array<T,N>);
  **/

  return 0;

}

template<typename T, int N>
PyObject* PyBlitzArrayCxx_NewFromArray(blitz::Array<T,N>& a) {

  PyObject* retval = PyBlitzArrayCxx_NewFromConstArray(a);

  if (!retval) return retval;

  reinterpret_cast<PyBlitzArrayObject*>(retval)->writeable = 1;

  return retval;
}

/**
 * Converts the given blitz::Array directly into a const numpy.ndarray that can be returned
 * @param array  The array to convert
 * @return A representation of the numpy.ndarray that can directly be returned (no Py_INCREF required)
 */
template<typename T, int N>
PyObject* PyBlitzArrayCxx_AsConstNumpy(const blitz::Array<T,N>& array){
  return PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(array));
}

/**
 * Converts the given blitz::Array directly into a numpy.ndarray that can be returned
 * @param array  The array to convert
 * @return A representation of the numpy.ndarray that can directly be returned (no Py_INCREF required)
 */
template<typename T, int N>
PyObject* PyBlitzArrayCxx_AsNumpy(blitz::Array<T,N>& array){
  return PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromArray(array));
}


template<typename T, int N>
blitz::Array<T,N>* PyBlitzArrayCxx_AsBlitz(PyBlitzArrayObject* o) {
  return reinterpret_cast<blitz::Array<T,N>*>(o->bzarr);
}


/**
 * Converts the given PyBlitzArrayObject into a blitz array,
 * performing consistency checks and sets the error flags in case of problems
 *
 * @note    This function might be a bit slower than you checking for the right type yourself.
 * @warning This function might return NULL, so **DON'T** dereference without checking!
 *
 * @param array  The python blitz array object to convert
 * @param name   The name of the object; this will be used to set an appropriate error message in case of problems
 * @return A representation of the numpy.ndarray that can directly be returned (no Py_INCREF required)
 */
template<typename T, int N>
blitz::Array<T,N>* PyBlitzArrayCxx_AsBlitz(PyBlitzArrayObject* array, const char* name) {

  // get the python type of the templated C++ type
  int type_num = PyBlitzArrayCxx_CToTypenum<T>();
  // perform the checks
  if (array->type_num != type_num || array->ndim != N){
    const char* type_num_name = PyBlitzArray_TypenumAsString(type_num);
    PyErr_Format(PyExc_TypeError, "The parameter '%s' only supports %dD arrays of type '%s'", name, N, type_num_name);
    return NULL;
  }
  // convert
  return PyBlitzArrayCxx_AsBlitz<T,N>(array);
}

#endif /* BOB_BLITZ_CPP_API_H */
