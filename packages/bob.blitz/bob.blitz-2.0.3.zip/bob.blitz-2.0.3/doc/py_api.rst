.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 17:41:52 2013
..
.. Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

.. testsetup:: blitztest

   import bob.blitz
   import numpy

============
 User Guide
============

You can build a new :py:class:`bob.blitz.array` using one of two possible ways:

1. Use the array constructor:

   .. doctest:: blitztest
      :options: +NORMALIZE_WHITESPACE

      >>> bob.blitz.array((2,3), float)
      bob.blitz.array((2,3),'float64')


  You should pass the array shape and a dtype convertible object that would
  identify the type of elements the array will contain. Arrays built this way
  are uninitialized:

   .. doctest:: blitztest
      :options: +NORMALIZE_WHITESPACE +ELLIPSIS

      >>> a = bob.blitz.array((2,), 'uint8')
      >>> a[0] # doctest: +SKIP
      145

2. Use the :py:func:`bob.blitz.as_blitz` generic converter. This function takes any
   object that is convertible to a :py:class:`numpy.ndarray`, convert it to a
   behaved (C-order, memory aligned and contiguous) :py:class:`numpy.ndarray` and then
   shallow copy it as a new :py:class:`bob.blitz.array`:

   .. doctest:: blitztest

      >>> import bob.blitz
      >>> a = bob.blitz.as_blitz(range(5))
      >>> print(a)
      [0 1 2 3 4]
      >>> a.dtype
      dtype('int...')


   The shallow copied ``ndarray`` remains visible through the returned object's
   ``base`` attribute:

   .. doctest:: blitztest

      >>> a.base
      array([0, 1, 2, 3, 4])
      >>> type(a.base)
      <... 'numpy.ndarray'>

   Because this is a shallow copy, any modifications done in any of the two
   arrays will be reflected in the other:

   .. doctest:: blitztest

      >>> a.base[3] = 67
      >>> print(a)
      [ 0  1  2 67  4]

You can get and set the individual values on :py:class:`bob.blitz.array` objects,
using the normal python indexing operatiors ``[]``:

.. doctest:: blitztest

   >>> a = bob.blitz.array(2, 'float64')
   >>> a[0] = 3.2
   >>> a[1] = 6.14
   >>> print(a)
   [ 3.2   6.14]
   >>> t = a[1]
   >>> print(t)
   6.14

You can convert :py:class:`bob.blitz.array` objects into either (shallow)
:py:class:`numpy.ndarray` copies using :py:meth:`bob.blitz.array.as_ndarray`.

.. doctest:: blitztest

   >>> a = bob.blitz.array(2, complex)
   >>> a[0] = complex(3,4)
   >>> a[1] = complex(2,2)
   >>> npy = a.as_ndarray()
   >>> print(npy)
   [ 3.+4.j  2.+2.j]
   >>> id(npy.base) == id(a)
   True
   >>> print(npy.flags.owndata)
   False

You can detach the :py:class:`numpy.ndarray` from the
:py:class:`bob.blitz.array`, by issuing a standard numpy copy:

.. doctest:: blitztest

   >>> npy_copy = npy.copy()
   >>> npy_copy.base is None
   True
   >>> print(npy_copy.flags.owndata)
   True

You can use :py:class:`bob.blitz.array` anywhere a :py:class:`numpy.ndarray` is
expected.  In this case, :py:mod:`numpy` checks for the existence of an
``__array__`` method on the passed object and if that is available, calls it to
get an array representation for the object. For :py:class:`bob.blitz.array`, the
:py:meth:`bob.blitz.array.__array__` method chooses the fastest possible
conversion path to generate a :py:class:`numpy.ndarray`.

.. doctest:: blitztest

   >>> a = bob.blitz.array(2, float)
   >>> a[0] = 3
   >>> a[1] = 4
   >>> print(numpy.mean(a))
   3.5

Reference
---------

This section includes information for using the pure Python API of
:py:class:`bob.blitz.array`. It is mainly intended as a test layer for the C and C++
API.

.. autoclass:: bob.blitz.array

.. autofunction:: bob.blitz.as_blitz
