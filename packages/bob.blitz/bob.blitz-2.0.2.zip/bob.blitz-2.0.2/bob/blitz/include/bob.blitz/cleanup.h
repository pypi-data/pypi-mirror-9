/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 11 Dec 08:42:53 2013
 *
 * @brief Some C++ tricks to make our life dealing with Python references a bit
 * easier and other cleanup helpers.
 */

#ifndef BOB_BLITZ_CLEANUP_H
#define BOB_BLITZ_CLEANUP_H

#include <Python.h>
#include <boost/shared_ptr.hpp>
#include <numpy/arrayobject.h>

/**
 * Calls Py_DECREF(x) on the input object x. Usage pattern:
 *
 * PyObject* x = ... // builds x with a new python reference
 * auto protected_x = make_safe(x);
 *
 * After this point, no need to worry about DECREF'ing x anymore.
 * You can still use `x' inside your code, or protected_x.get().
 */
template <typename T> void __decref(T* p) { Py_DECREF(p); }
template <typename T> boost::shared_ptr<T> make_safe(T* o) {
  return boost::shared_ptr<T>(o, &__decref<T>);
}

/**
 * Calls Py_XDECREF(x) on the input object x. Usage pattern:
 *
 * PyObject* x = ... // builds x with a new python reference, x may be NULL
 * auto protected_x = make_xsafe(x);
 *
 * After this point, no need to worry about XDECREF'ing x anymore.
 * You can still use `x' inside your code, or protected_x.get(). Note
 * `x' may be NULL with this method.
 */
template <typename T> void __xdecref(T* p) { Py_XDECREF(p); }
template <typename T> boost::shared_ptr<T> make_xsafe(T* o) {
  return boost::shared_ptr<T>(o, &__xdecref<T>);
}

#endif /* BOB_BLITZ_CLEANUP_H */
