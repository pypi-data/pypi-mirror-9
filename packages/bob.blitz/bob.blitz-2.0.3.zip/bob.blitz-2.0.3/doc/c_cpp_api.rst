.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 14:59:05 2013
..
.. Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland

===============
 C and C++ API
===============

This section includes information for using the pure C or C++ API for
manipulating :py:class:`bob.bob.blitz` objects in compiled code.

C API
-----

The C API of ``bob.blitz`` allows users to leverage from automatic converters
between :py:class:`numpy.ndarray` and :py:class:`bob.blitz.array` within their
own python extensions. To use the C API, clients should first, include the
header file ``<bob.blitz/capi.h>`` on their compilation units and then, make
sure to call once ``import_bob_blitz()`` at their module instantiation, as
explained at the `Python manual
<http://docs.python.org/2/extending/extending.html#using-capsules>`_.

Here is a dummy C example showing how to include the header and where to call
the import function:

.. code-block:: c++

   #include <bob.blitz/capi.h>

   PyMODINIT_FUNC initclient(void) {

     PyObject* m Py_InitModule("client", ClientMethods);

     if (!m) return;

     // imports dependencies
     if (import_bob_blitz() < 0) {
       PyErr_Print();
       PyErr_SetString(PyExc_ImportError, "cannot import module");
       return 0;
     }

     return m;
   }


Array Structure
===============

.. c:type:: PyBlitzArrayObject

   The basic array structure represents a ``bob.blitz.array`` instance from
   the C-side of the interpreter. You should **avoid direct access to the
   structure components** (it is presented just as an overview on the
   functionality). Instead, use the accessor methods described below.

   .. code-block:: c

      typedef struct {
        PyObject_HEAD
        void* bzarr;
        void* data;
        int type_num;
        Py_ssize_t ndim;
        Py_ssize_t shape[BLITZ_ARRAY_MAXDIMS];
        Py_ssize_t stride[BLITZ_ARRAY_MAXDIMS];
        int writeable;
        PyObject* base;

      } PyBlitzArrayObject;

   .. c:macro:: BLITZ_ARRAY_MAXDIMS

      The maximum number of dimensions supported by the current
      ``bob.blitz.array`` implementation.

   .. c:member:: void* bzarr

      This is a pointer that points to the allocated ``blitz::Array``
      structure. This pointer is cast to the proper type and number of
      dimensions when operations on the data are requested.

   .. c:member:: void* data

      A pointer to the data entry in the ``blitz::Array<>``. This is equivalent
      to the operation ``blitz::Array<>::data()``.

   .. c:member:: int type_num

      The numpy type number that is compatible with the elements of this
      array. It is a C representation of the C++ template parameter ``T``. Only
      some types are current supported, namely:

      =============================== ==================== ==================
         C/C++ type                      Numpy Enum            Notes
      =============================== ==================== ==================
       ``bool``                        ``NPY_BOOL``
       ``uint8_t``                     ``NPY_UINT8``
       ``uint16_t``                    ``NPY_UINT16``
       ``uint32_t``                    ``NPY_UINT32``
       ``uint64_t``                    ``NPY_UINT64``
       ``int8_t``                      ``NPY_INT8``
       ``int16_t``                     ``NPY_INT16``
       ``int32_t``                     ``NPY_INT32``
       ``int64_t``                     ``NPY_INT64``
       ``float``                       ``NPY_FLOAT32``
       ``double``                      ``NPY_FLOAT64``
       ``long double``                 ``NPY_FLOAT128``     Plat. Dependent
       ``std::complex<float>``         ``NPY_COMPLEX64``
       ``std::complex<double>``        ``NPY_COMPLEX128``
       ``std::complex<long double>``   ``NPY_COMPLEX256``   Plat. Dependent
      =============================== ==================== ==================

   .. c:member:: Py_ssize_t ndim

      The rank of the ``blitz::Array<>`` allocated on ``bzarr``.

   .. c:member:: Py_ssize_t shape[BLITZ_ARRAY_MAXDIMS]

      The shape of the ``blitz::Array<>`` allocated on ``bzarr``, in number of
      **elements** in each dimension.

   .. c:member:: Py_ssize_t stride[BLITZ_ARRAY_MAXDIMS]

      The strides of the ``blitz::Array<>`` allocated on ``bzarr``, in number
      of **bytes** to jump to read the next element in each dimensions.

   .. c:member:: int writeable

      Assumes the value of ``1`` (true), if the data is read-write. ``0`` is
      set otherwise.

   .. c:member:: PyObject* base

      If the memory pointed by the currently allocated ``blitz::Array<>``
      belongs to another Python object, the object is ``Py_INCREF()``'ed and a
      pointer is kept on this structure member.


Basic Properties and Checking
=============================

.. c:function:: int PyBlitzArray_Check(PyObject* o)

   Checks if the input object ``o`` is a ``PyBlitzArrayObject``. Returns ``1``
   if it is, and ``0`` otherwise.


.. c:function:: int PyBlitzArray_CheckNumpyBase(PyArrayObject* o)

   Checks if the input object ``o`` is a ``PyArrayObject`` (i.e. a
   :py:class:`numpy.ndarray`), if so, checks if the base of the object is set
   and that it corresponds to the current ``PyArrayObject`` shape and stride
   settings. If so, returns ``1``. It returns ``0`` otherwise.


.. c:function:: int PyBlitzArray_TYPE (PyBlitzArrayObject* o)

   Returns integral type number (as defined by the Numpy C-API) of elements
   in this blitz::Array<>. This is the formal method to query for
   ``o->type_num``.


.. c:function:: PyArray_Descr* PyBlitzArray_PyDTYPE (PyBlitzArrayObject* o)

   Returns a **new reference** to a numpy C-API ``PyArray_Descr*`` equivalent
   to the internal type element T.


.. c:function:: Py_ssize_t PyBlitzArray_NDIM (PyBlitzArrayObject* o)

   Returns the number of dimensions in a given ``bob.blitz.array``. This is
   the formal way to check for ``o->ndim``.


.. c:function:: Py_ssize_t* PyBlitzArray_SHAPE (PyBlitzArrayObject* o)

   Returns the C-stype shape for this blitz::Array<>. This is the formal method
   to query for ``o->shape``. The shape represents the number of elements in
   each dimension of the array.


.. c:function:: PyObject* PyBlitzArray_PySHAPE (PyBlitzArrayObject* o)

   Returns a **new reference** to a Python tuple holding a copy of the shape
   for the given array. The shape represents the number of elements in each
   dimension of the array.


.. c:function:: Py_ssize_t* PyBlitzArray_STRIDE (PyBlitzArrayObject* o)

   Returns the C-stype stride for this blitz::Array<>. This is the formal
   method to query for ``o->stride``. The strides in this object are
   represented in number of bytes and **not** in number of elements considering
   its ``type_num``. This is compatible with the :py:class:`numpy.ndarray`
   strategy.


.. c:function:: PyObject* PyBlitzArray_PySTRIDE (PyBlitzArrayObject* o)

   Returns a **new reference** to a Python tuple holding a copy of the strides
   for the given array. The strides in this object are represented in number of
   bytes and **not** in number of elements considering its ``type_num``. This
   is compatible with the :py:class:`numpy.ndarray` strategy.


.. c:function:: int PyBlitzArray_WRITEABLE (PyBlitzArrayObject* o)

   Returns ``1`` if the object is writeable, ``0`` otherwise. This is the
   formal way to check for ``o->writeable``.


.. c:function:: PyObject* PyBlitzArray_PyWRITEABLE (PyBlitzArrayObject* o)

   Returns ``True`` if the object is writeable, ``False`` otherwise.


.. c:function:: PyObject* PyBlitzArray_BASE (PyBlitzArrayObject* o)

   Returns a **borrowed reference** to the base of this object. The return
   value of this function may be ``NULL``.


.. c:function:: PyObject* PyBlitzArray_PyBASE (PyBlitzArrayObject* o)

   Returns a **new reference** to the base of this object. If the internal
   ``o->base`` is ``NULL``, then returns ``Py_None``. Use this when interfacing
   with the Python interpreter.


Indexing
========

.. c:function:: PyObject* PyBlitzArray_GetItem (PyBlitzArrayObject* o, Py_ssize_t* pos)

   Returns, as a PyObject, an item from the array. This will be a copy of the
   internal item. If you set it, it won't set the original array.  ``o`` should
   be the PyBlitzArrayObject to be queried. ``pos`` should be a C-style array
   indicating the precise position to fetch. It is considered to have the same
   number of entries as the current array shape.


.. c:function:: int PyBlitzArray_SetItem (PyBlitzArrayObject* o, Py_ssize_t* pos, PyObject* value)

   Sets an given position on the array using any Python or numpy scalar. ``o``
   should be the PyBlitzArrayObject to be set. ``pos`` should be a C-style
   array indicating the precise position to set and ``value``, the Python
   or numpy scalar to set the value to.


Construction and Destruction
============================

.. c:function:: PyObject* PyBlitzArray_New (PyTypeObject* type, PyObject *args, PyObject* kwds)

   Allocates memory and pre-initializes a ``PyBlitzArrayObject*`` object. This
   is the base allocator - seldomly used in user code.


.. c:function:: void PyBlitzArray_Delete (PyBlitzArrayObject* o)

   Completely deletes a ``PyBlitzArrayObject*`` and associated memory areas.
   This is the base deallocator - seldomly used in user code.


.. c:function:: PyObject* PyBlitzArray_SimpleNew (int typenum, Py_ssize_t ndim, Py_ssize_t* shape)

   Allocates a new ``bob.blitz`` with a given (supported) type and return it
   as a python object. ``typenum`` should be set to the numpy type number of
   the array type (e.g. ``NPY_FLOAT64``). ``ndim`` should be set to the total
   number of dimensions the array should have. ``shape`` should be set to the
   array shape.


.. c:function:: PyObject* PyBlitzArray_SimpleNewFromData (int type_num, Py_ssize_t ndim, Py_ssize_t* shape, Py_ssize_t* stride, void* data, int writeable)

   Allocates a new ``bob.blitz.array`` with a given (supported) type and
   return it as a python object. ``typenum`` should be set to the numpy type
   number of the array type (e.g. ``NPY_FLOAT64``). ``ndim`` should be set to
   the total number of dimensions the array should have. ``shape`` should be
   set to the array shape. ``stride`` should be set to the array stride in the
   numpy style (in number of bits). ``data`` should be a pointer to the begin
   of the data area. ``writeable`` indicates if the resulting array should be
   writeble (set it to ``1``), or read-only (set it to ``0``).

   The memory area pointed by ``data`` is stolen from the user, which should
   not delete it anymore.

.. c:function:: int PyBlitzArray_SimpleInit (PyBlitzArrayObject* arr, int typenum, Py_ssize_t ndim, Py_ssize_t* shape)

   Initializes the given ``PyBlitzArrayObject*`` with a new ``blitz::Array`` of the given typenum, dimensionality and shape.
   See :c:func:`PyBlitzArray_SimpleNew` for details on the parameters.
   This function does not check if the memory is already initialized.
   It returns 0 on success and -1 on failure.


To/From Numpy Converters
========================

.. c:function:: PyObject* PyBlitzArray_AsNumpyArray (PyBlitzArrayObject* o, PyArrayDescr* dtype)

   Creates a **shallow** copy of the given ``bob.blitz.array`` as a
   ``numpy.ndarray``. The argument ``dtype`` may be given, in which case
   if the current data type is not the same, then forces the creation of a copy
   conforming to the require data type, if possible. You may set ``dtype`` to
   ``NULL`` in case you don't mind the resulting data type.

   Returns a **new reference**.


.. c:function:: PyObject* PyBlitzArray_FromNumpyArray (PyObject* o)

   Creates a new ``bob.blitz.array`` from a ``numpy.ndarray`` object in a
   shallow manner.

   Returns a **new reference**.


.. c:function:: PyObject* PyBlitzArray_NUMPY_WRAP (PyObject* o)

   Creates a **shallow** copy of the given :py:class:`bob.blitz.array` as a
   :py:class:`numpy.ndarray`. This function is a shortcut replacement for
   :c:func:`PyBlitzArray_AsNumpyArray`. It can be used when the input object
   ``o`` is surely of type :c:type:`PyBlitzArrayObject`. It creates a wrapper
   :c:type:`PyArrayObject` that contains, as base, a **stolen** reference to
   the input object ``o``.

   It is designed like this so you can easily wrap **freshly** created objects
   of type :c:type:`PyBlitzArrayObject` as :c:type:`PyArrayObject`. It
   *assumes* the input object is of the right type and wrap-able as a
   :py:class:`numpy.ndarray`. It does not check the object ``base`` variable,
   assuming it is set to ``NULL`` (what is the case to freshly created
   :c:type:`PyBlitzArrayObject`'s). If you are not sure about the nature of
   ``o``, use the slower but safer :c:func:`PyBlitzArray_AsNumpyArray`.

   .. note::

      The value of ``o`` can be ``NULL``, in which case this function returns
      immediately, allowing you to propagate exceptions.


Converter Functions for PyArg_Parse* family
===========================================

.. c:function:: int PyBlitzArray_Converter(PyObject* o, PyBlitzArrayObject** a)

   This function is meant to be used with :c:func:`PyArg_ParseTupleAndKeywords`
   family of functions in the Python C-API. It converts an arbitrary input
   object into a ``PyBlitzArrayObject`` that can be used as input into another
   function.

   You should use this converter when you don't need to write-back into the
   input array. As any other standard Python converter, it returns a **new**
   reference to a ``PyBlitzArrayObject``.

   It works efficiently if the input array is already a
   :c:type:`PyBlitzArrayObject` or if it is a :c:type:`PyArrayObject` (i.e., a
   :py:class:``numpy.ndarray``), with a matching base which is a
   :c:type:`PyBlitzArrayObject`. Otherwise, it creates a new
   :c:type:`PyBlitzArrayObject` by first creating a :c:type:`PyArrayObject` and
   then shallow wrapping it with a :c:type:`PyBlitzArrayObject`.

   Returns 0 if an error is detected, 1 on success.

.. c:function:: int PyBlitzArray_BehavedConverter(PyObject* o, PyBlitzArrayObject** a)

   This function operates like :c:func:`PyBlitzArray_Converter`, excepts it
   guarantees that the returned (underlying) ``blitz::Array<>`` object is
   wrapped around a well-behaved :py:class:`numpy.ndarray` object (i.e.
   contiguous, memory-aligned, C-style).

   In the event the input object is already a :c:type:`PyBlitzArrayObject`,
   then a new reference to it is returned. It does not check, in this
   particular case, that the input object is well-behaved.

   Returns 0 if an error is detected, 1 on success.

.. c:function:: int PyBlitzArray_OutputConverter(PyObject* o, PyBlitzArrayObject** a)

   This function is meant to be used with :c:func:`PyArg_ParseTupleAndKeywords`
   family of functions in the Python C-API. It converts an arbitrary input
   object into a ``PyBlitzArrayObject`` that can be used as input/output or
   output into another function.

   You should use this converter when you need to write-back into the input
   array. The input type should be promptly convertible to a
   :py:class:`numpy.ndarray` as with :c:func:`PyArray_OutputConverter`. As any
   other standard Python converter, it returns a **new** reference to a
   ``PyBlitzArrayObject*``.

   Returns 0 if an error is detected, 1 on success.

.. c:function:: int PyBlitzArray_IndexConverter (PyObject* o, PyBlitzArrayObject** shape)

   Converts any compatible sequence into a C-array containing the shape
   information. The shape information and number of dimensions is stored on the
   previously allocated ``PyBlitzArrayObject*`` you should provide. This method
   is supposed to be used with ``PyArg_ParseTupleAndKeywords`` and derivatives.

   Parameters are:

   ``o``
     The input object to be converted into a C-shape

   ``shape``
     A preallocated (double) address for storing the shape value, on successful
     conversion

   Returns 0 if an error is detected, 1 on success.


.. c:function:: int PyBlitzArray_TypenumConverter (PyObject* o, int* type_num)

   Converts any compatible value into a Numpy integer type number. This method
   is supposed to be used with ``PyArg_ParseTupleAndKeywords`` and derivatives.

   Parameters are:

   ``o``
     The input object to be converted into a type number

   ``type_num``
      An address for storing the type number on successful conversion.

   Returns 0 if an error is detected, 1 on success.


Other Utilities
===============

.. c:function:: const char* PyBlitzArray_TypenumAsString (int typenum)

   Converts from numpy type_num to a string representation


.. c:function:: PyObject* PyBlitzArray_Cast (PyBlitzArrayObject* o, int typenum)

   Casts a given Blitz++ Array into another data type, returns a **new
   reference**. If the underlying Blitz++ Array is already of the given type,
   then just increments the reference counter and returns.

   If a problem is detected (e.g. the impossibility to cast to the desired
   type), then this function will return ``NULL``. You must check the return
   value and then take the appropriate action after calling this function.

   .. note::

      Casting, as operated by this function, may incur in precision loss
      between the originating type and the destination type.

C++ API
-------

The C++ API consists mostly of templated methods for manipulating the C++ type
``blitz::Array<>`` so as to convert ``PyObject*``'s from and to objects of that
type. To use the C++ API you must include the header file
``<bob.blitz/cppapi.h>`` and ``import_bob_blitz()`` on your module, as
explained on the C-API section of this document.

Basic Properties and Checking
=============================

.. cpp:function:: int PyBlitzArrayCxx_IsBehaved<T,N>(blitz::Array<T,N>& a)

   Tells if a ``blitz::Array<>`` is memory contiguous and C-style.


Construction and Destruction
============================

.. cpp:function:: PyObject* PyBlitzArrayCxx_NewFromConstArray<T,N>(const blitz::Array<T,N>& a)

   Builds a new read-only ``PyBlitzArrayObject`` from an existing Blitz++
   array, without copying the data. Returns a new reference.


.. cpp:function:: PyObject* PyBlitzArrayCxx_NewFromArray<T,N>(blitz::Array<T,N>& a)

   Builds a new writeable ``PyBlitzArrayObject`` from an existing Blitz++
   array, without copying the data. Returns a new reference.


.. cpp:function:: PyObject* PyBlitzArrayCxx_AsConstNumpy<T,N>(const blitz::Array<T,N>& a)

   Builds a new read-only :py:class:`numpy.ndarray` object from the given Blitz++ array
   without copying the data. Returns a new reference.

   In fact, it actually calls two of the above mentioned functions :cpp:func:`PyBlitzArrayCxx_NewFromConstArray` and :cpp:func:`PyBlitzArray_NUMPY_WRAP`:

   .. code-block:: c++

      PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromConstArray(a));


.. cpp:function:: PyObject* PyBlitzArrayCxx_AsNumpy<T,N>(blitz::Array<T,N>& a)

   Builds a new writeable :py:class:`numpy.ndarray` object from the given Blitz++ array
   without copying the data. Returns a new reference.

   In fact, it actually calls two of the above mentioned functions :cpp:func:`PyBlitzArrayCxx_NewFromArray` and :cpp:func:`PyBlitzArray_NUMPY_WRAP`:

   .. code-block:: c++

      PyBlitzArray_NUMPY_WRAP(PyBlitzArrayCxx_NewFromArray(a));



Other Utilities
===============

.. cpp:function:: blitz::Array<T,N>* PyBlitzArrayCxx_AsBlitz(PyBlitzArrayObject* o)

   Casts a ``PyBlitzArrayObject`` to a specific ``blitz::Array<>`` type. Notice
   this is a brute-force cast. You are responsible for checking if that it is
   correct.


.. cpp:function:: blitz::Array<T,N>* PyBlitzArrayCxx_AsBlitz(PyBlitzArrayObject* o, const char* name)

   Casts a ``PyBlitzArrayObject`` to a specific ``blitz::Array<>`` type after checking that the dimensions and the data type of the underlying :cpp:type:`PyBlitzArrayObject` fits to the template parameters.
   If the check fails, an Python error is set, using the given ``name`` parameter as the name of the object that was passed to the python function, **and** ``NULL`` **is returned**.
   Hence, please check the result of this function for ``NULL``:

   .. code-block:: c++

      // ...

      PyBlitzArrayObject* data;
      if (!PyArg_ParseTupleAndKeywords(..., data, ...))
        return NULL;

      // use safe reference counting
      auto _ = make_safe(data);

      // get the blitz array; returns NULL on failure
      blitz::Array<double,2>* array = PyBlitzArrayCxx_AsBlitz<double,2>(data, "data");

      // check for NULL
      if (!array)
        // The error message has already been set, so we can simply return NULL
        return NULL;

      // ...

   .. note:: If you need to check for several data types and/or dimensions, use the first version of this function and perform the checks by hand.

   .. note:: This version of the function might be slightly slower than the first version.


.. cpp:function:: int PyBlitzArrayCxx_CToTypenum<T>()

   Converts from C/C++ type to ndarray type_num.

   We cover only simple conversions (i.e., standard integers, floats and
   complex numbers only). If the input type is not convertible, an exception
   is set on the Python error stack. You must check ``PyErr_Occurred()`` after
   a call to this function to make sure things are OK and act accordingly.  For
   example:

   .. code-block:: c++

      int typenum = PyBlitzArrayCxx_CToTypenum<my_weird_type>(obj);
      if (PyErr_Occurred()) return 0; ///< propagate exception


.. cpp:function:: T PyBlitzArrayCxx_AsCScalar<T>(PyObject* o)

   Extraction API for **simple** types.

   We cover only simple conversions (i.e., standard integers, floats and
   complex numbers only). If the input object is not convertible to the given
   type, an exception is set on the Python error stack. You must check
   ``PyErr_Occurred()`` after a call to this function to make sure things are OK
   and act accordingly. For example:

   .. code-block:: c++

      auto z = extract<uint8_t>(obj);
      if (PyErr_Occurred()) return 0; ///< propagate exception

.. cpp:function:: PyBlitzArrayCxx_FromCScalar<T>(T v)

   Converts **simple** C types into numpy scalars

   We cover only simple conversions (i.e., standard integers, floats and
   complex numbers only). If the input object is not convertible to the given
   type, an exception is set on the Python error stack and ``0`` (``NULL``) is
   returned.
