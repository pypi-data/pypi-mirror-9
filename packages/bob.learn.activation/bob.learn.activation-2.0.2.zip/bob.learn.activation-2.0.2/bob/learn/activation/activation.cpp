/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 10 Jan 2014 14:26:25 CET
 *
 * @brief Python bindings for bob::learn::activation
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#define BOB_LEARN_ACTIVATION_MODULE
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/defines.h>
#include <bob.learn.activation/api.h>
#include <bob.io.base/api.h>
#include <bob.learn.activation/Activation.h>
#include <boost/bind.hpp>
#include <boost/function.hpp>
#include <structmember.h>

/*******************************************
 * Implementation of Activation base class *
 *******************************************/

PyDoc_STRVAR(s_activation_str, BOB_EXT_MODULE_PREFIX ".Activation");

PyDoc_STRVAR(s_activation_doc,
"Base class for activation functors.\n\
\n\
.. warning::\n\
\n\
   You cannot instantiate an object of this type directly, you must\n\
   use it through one of the inherited types.\n\
\n\
.. warning::\n\
\n\
   You cannot create classes in Python that derive from this one and\n\
   expect them to work fine with the C++ code, as no hook is\n\
   implemented as of this time to allow for this. You must create\n\
   a class that inherits from the C++\n\
   :cpp:type:`bob::learn::activation::Activation` in C++ and then bind it to\n\
   Python like we have done for the classes available in these\n\
   bindings.\n\
\n\
");

static PyObject* PyBobLearnActivation_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobLearnActivationObject* self =
    (PyBobLearnActivationObject*)type->tp_alloc(type, 0);

  self->cxx.reset();

  return reinterpret_cast<PyObject*>(self);

}

PyObject* PyBobLearnActivation_NewFromActivation
(boost::shared_ptr<bob::learn::activation::Activation> a) {

  PyBobLearnActivationObject* retval = (PyBobLearnActivationObject*)PyBobLearnActivation_new(&PyBobLearnActivation_Type, 0, 0);

  retval->cxx = a;

  return Py_BuildValue("N", retval);

}

static void PyBobLearnActivation_delete (PyBobLearnActivationObject* self) {

  self->cxx.reset();
  Py_TYPE(self)->tp_free((PyObject*)self);

}

static int PyBobLearnActivation_init(PyBobLearnActivationObject* self,
    PyObject*, PyObject*) {

  PyErr_Format(PyExc_NotImplementedError, "cannot initialize object of base type `%s' - use one of the inherited classes", Py_TYPE(self)->tp_name);
  return -1;

}

/**
 * Maps all elements of arr through function() into retval
 */
static int apply(boost::function<double (double)> function,
    PyBlitzArrayObject* z, PyBlitzArrayObject* res) {

  if (z->ndim == 1) {
    auto z_ = PyBlitzArrayCxx_AsBlitz<double,1>(z);
    auto res_ = PyBlitzArrayCxx_AsBlitz<double,1>(res);
    for (int k=0; k<z_->extent(0); ++k)
      res_->operator()(k) = function(z_->operator()(k));
    return 1;
  }

  else if (z->ndim == 2) {
    auto z_ = PyBlitzArrayCxx_AsBlitz<double,2>(z);
    auto res_ = PyBlitzArrayCxx_AsBlitz<double,2>(res);
    for (int k=0; k<z_->extent(0); ++k)
      for (int l=0; l<z_->extent(1); ++l)
        res_->operator()(k,l) = function(z_->operator()(k,l));
    return 1;
  }

  else if (z->ndim == 3) {
    auto z_ = PyBlitzArrayCxx_AsBlitz<double,3>(z);
    auto res_ = PyBlitzArrayCxx_AsBlitz<double,3>(res);
    for (int k=0; k<z_->extent(0); ++k)
      for (int l=0; l<z_->extent(1); ++l)
        for (int m=0; m<z_->extent(2); ++m)
          res_->operator()(k,l,m) = function(z_->operator()(k,l,m));
    return 1;
  }

  else if (z->ndim == 4) {
    auto z_ = PyBlitzArrayCxx_AsBlitz<double,4>(z);
    auto res_ = PyBlitzArrayCxx_AsBlitz<double,4>(res);
    for (int k=0; k<z_->extent(0); ++k)
      for (int l=0; l<z_->extent(1); ++l)
        for (int m=0; m<z_->extent(2); ++m)
          for (int n=0; n<z_->extent(3); ++n)
            res_->operator()(k,l,m,n) = function(z_->operator()(k,l,m,n));
    return 1;
  }

  return 0;

}

static PyObject* PyBobLearnActivation_call1(PyBobLearnActivationObject* self,
    double (bob::learn::activation::Activation::*method) (double) const,
    PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"z", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* z = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &z)) return 0;

  //note: object z is borrowed

  if (PyBlitzArray_Check(z) || PyArray_Check(z)) {

    PyBlitzArrayObject* z_converted = 0;
    if (!PyBlitzArray_Converter(z, &z_converted)) return 0;
    auto z_converted_ = make_safe(z_converted);

    if (z_converted->type_num != NPY_FLOAT64) {
      PyErr_Format(PyExc_TypeError, "`%s' function only supports 64-bit float arrays for input array `z'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (z_converted->ndim < 1 || z_converted->ndim > 4) {
      PyErr_Format(PyExc_TypeError, "`%s' function only accepts 1, 2, 3 or 4-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, z_converted->ndim);
      return 0;
    }

    // creates output array
    PyObject* res = PyBlitzArray_SimpleNew(NPY_FLOAT64, z_converted->ndim,
        z_converted->shape);
    auto res_ = make_safe(res);

    // processes the data
    int ok = apply(boost::bind(method, self->cxx, _1),
        z_converted, reinterpret_cast<PyBlitzArrayObject*>(res));

    if (!ok) {
      PyErr_Format(PyExc_RuntimeError, "unexpected error occurred applying `%s' to input array (DEBUG ME)", Py_TYPE(self)->tp_name);
      return 0;
    }

    return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", res));

  }

  else if (PyBob_NumberCheck(z)) {

    PyObject* z_float = PyNumber_Float(z);
    auto z_float_ = make_safe(z_float);
    auto bound_method = boost::bind(method, self->cxx, _1);
    double res_c = bound_method(PyFloat_AsDouble(z_float));
    return PyFloat_FromDouble(res_c);

  }

  PyErr_Format(PyExc_TypeError, "`%s' is not capable to process input objects of type `%s'", Py_TYPE(self)->tp_name, Py_TYPE(z)->tp_name);
  return 0;

}

static PyObject* PyBobLearnActivation_call2(PyBobLearnActivationObject* self,
    double (bob::learn::activation::Activation::*method) (double) const,
    PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"z", "res", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* z = 0;
  PyBlitzArrayObject* res = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&", kwlist,
        &PyBlitzArray_Converter, &z,
        &PyBlitzArray_OutputConverter, &res
        )) return 0;

  //protects acquired resources through this scope
  auto z_ = make_safe(z);
  auto res_ = make_safe(res);

  if (z->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' function only supports 64-bit float arrays for input array `z'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (res->type_num != NPY_FLOAT64) {
    PyErr_Format(PyExc_TypeError, "`%s' function only supports 64-bit float arrays for output array `res'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (z->ndim < 1 || z->ndim > 4) {
    PyErr_Format(PyExc_TypeError, "`%s' function only accepts 1, 2, 3 or 4-dimensional arrays (not %" PY_FORMAT_SIZE_T "dD arrays)", Py_TYPE(self)->tp_name, z->ndim);
    return 0;
  }

  if (z->ndim != res->ndim) {
    PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching number of dimensions, but input array `z' has %" PY_FORMAT_SIZE_T "d dimensions while output array `res' has %" PY_FORMAT_SIZE_T "d dimensions", z->ndim, res->ndim);
    return 0;
  }

  for (Py_ssize_t i=0; i<z->ndim; ++i) {

    if (z->shape[i] != res->shape[i]) {
      PyErr_Format(PyExc_RuntimeError, "Input and output arrays should have matching sizes, but dimension %" PY_FORMAT_SIZE_T "d of input array `z' has %" PY_FORMAT_SIZE_T "d positions while output array `res' has %" PY_FORMAT_SIZE_T "d positions", i, z->shape[i], res->shape[i]);
      return 0;
    }

  }

  //at this point all checks are done, we can proceed into calling C++
  int ok = apply(boost::bind(method, self->cxx, _1), z, res);

  if (!ok) {
    PyErr_Format(PyExc_RuntimeError, "unexpected error occurred applying C++ `%s' to input array (DEBUG ME)", Py_TYPE(self)->tp_name);
    return 0;
  }

  return PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", res));

}

PyDoc_STRVAR(s_call_str, "f");
PyDoc_STRVAR(s_call_doc,
"o.f(z, [res]) -> array | scalar\n\
\n\
Computes the activated value, given an input array or scalar\n\
``z``, placing results in ``res`` (and returning it).\n\
\n\
If ``z`` is an array, then you can pass another array in ``res``\n\
to store the results and, in this case, we won't allocate a new\n\
one for that purpose. This can be a speed-up in certain scenarios.\n\
Note this does not work for scalars as it makes little sense to\n\
avoid scalar allocation at this level.\n\
\n\
If you decide to pass an array in ``res``, note this array should\n\
have the exact same dimensions as the input array ``z``. It is an\n\
error otherwise.\n\
\n\
.. note::\n\
\n\
   This method only accepts 64-bit float arrays as input or\n\
   output.\n\
\n\
");

static PyObject* PyBobLearnActivation_call(PyBobLearnActivationObject* self,
  PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:
      return PyBobLearnActivation_call1
        (self, &bob::learn::activation::Activation::f, args, kwds);
      break;

    case 2:
      return PyBobLearnActivation_call2
        (self, &bob::learn::activation::Activation::f, args, kwds);
      break;

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 or 2 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", s_call_str, nargs);

  }

  return 0;

}

PyDoc_STRVAR(s_f_prime_str, "f_prime");
PyDoc_STRVAR(s_f_prime_doc,
"o.f_prime(z, [res]) -> array | scalar\n\
\n\
Computes the derivative of the activated value, given an input\n\
array or scalar ``z``, placing results in ``res`` (and returning\n\
it).\n\
\n\
If ``z`` is an array, then you can pass another array in ``res``\n\
to store the results and, in this case, we won't allocate a new\n\
one for that purpose. This can be a speed-up in certain scenarios.\n\
Note this does not work for scalars as it makes little sense to\n\
avoid scalar allocation at this level.\n\
\n\
If you decide to pass an array in ``res``, note this array should\n\
have the exact same dimensions as the input array ``z``. It is an\n\
error otherwise.\n\
\n\
.. note::\n\
\n\
   This method only accepts 64-bit float arrays as input or\n\
   output.\n\
\n\
");

static PyObject* PyBobLearnActivation_f_prime(PyBobLearnActivationObject* self,
  PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:
      return PyBobLearnActivation_call1
        (self, &bob::learn::activation::Activation::f_prime, args, kwds);
      break;

    case 2:
      return PyBobLearnActivation_call2
        (self, &bob::learn::activation::Activation::f_prime, args, kwds);
      break;

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 or 2 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", s_call_str, nargs);

  }

  return 0;

}

PyDoc_STRVAR(s_f_prime_from_f_str, "f_prime_from_f");
PyDoc_STRVAR(s_f_prime_from_f_doc,
"o.f_prime_from_f(a, [res]) -> array | scalar\n\
\n\
Computes the derivative of the activated value, given the\n\
derivative value ``a``, placing results in ``res`` (and returning\n\
it).\n\
\n\
If ``a`` is an array, then you can pass another array in ``res``\n\
to store the results and, in this case, we won't allocate a new\n\
one for that purpose. This can be a speed-up in certain scenarios.\n\
Note this does not work for scalars as it makes little sense to\n\
avoid scalar allocation at this level.\n\
\n\
If you decide to pass an array in ``res``, note this array should\n\
have the exact same dimensions as the input array ``a``. It is an\n\
error otherwise.\n\
\n\
.. note::\n\
\n\
   This method only accepts 64-bit float arrays as input or\n\
   output.\n\
\n\
");

static PyObject* PyBobLearnActivation_f_prime_from_f
(PyBobLearnActivationObject* self, PyObject* args, PyObject* kwds) {

  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  switch (nargs) {

    case 1:
      return PyBobLearnActivation_call1
        (self, &bob::learn::activation::Activation::f_prime_from_f, args, kwds);
      break;

    case 2:
      return PyBobLearnActivation_call2
        (self, &bob::learn::activation::Activation::f_prime_from_f, args, kwds);
      break;

    default:

      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 1 or 2 arguments, but you provided %" PY_FORMAT_SIZE_T "d (see help)", s_call_str, nargs);

  }

  return 0;

}

PyDoc_STRVAR(s_unique_id_str, "unique_identifier");
PyDoc_STRVAR(s_unique_id_doc,
"o.unique_identifier() -> str\n\
\n\
Returns a unique (string) identifier, used by this class\n\
in connection with the Activation registry.\n\
\n\
");

static PyObject* PyBobLearnActivation_UniqueIdentifier
(PyBobLearnActivationObject* self) {
  return Py_BuildValue("s", self->cxx->unique_identifier().c_str());
}

PyDoc_STRVAR(s_load_str, "load");
PyDoc_STRVAR(s_load_doc,
"o.load(f) -> None\n\
\n\
Loads itself from a :py:class:`bob.io.base.HDF5File`\n\
\n\
");

static PyObject* PyBobLearnActivation_Load(PyBobLearnActivationObject* self,
    PyObject* f) {

  if (!PyBobIoHDF5File_Check(f)) {
    PyErr_Format(PyExc_TypeError, "`%s' cannot load itself from `%s', only from an HDF5 file", Py_TYPE(self)->tp_name, Py_TYPE(f)->tp_name);
    return 0;
  }

  auto h5f = reinterpret_cast<PyBobIoHDF5FileObject*>(f);

  try {
    self->cxx->load(*h5f->f);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot read data from file `%s' (at group `%s'): unknown exception caught", h5f->f->filename().c_str(),
        h5f->f->cwd().c_str());
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_save_str, "save");
PyDoc_STRVAR(s_save_doc,
"o.save(f) -> None\n\
\n\
Saves itself to a :py:class:`bob.io.base.HDF5File`\n\
\n\
");

static PyObject* PyBobLearnActivation_Save
(PyBobLearnActivationObject* self, PyObject* f) {

  if (!PyBobIoHDF5File_Check(f)) {
    PyErr_Format(PyExc_TypeError, "`%s' cannot write itself to `%s', only to an HDF5 file", Py_TYPE(self)->tp_name, Py_TYPE(f)->tp_name);
    return 0;
  }

  auto h5f = reinterpret_cast<PyBobIoHDF5FileObject*>(f);

  try {
    self->cxx->save(*h5f->f);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot write data to file `%s' (at group `%s'): unknown exception caught", h5f->f->filename().c_str(),
        h5f->f->cwd().c_str());
    return 0;
  }

  Py_RETURN_NONE;
}

static PyMethodDef PyBobLearnActivation_methods[] = {
  {
    s_call_str,
    (PyCFunction)PyBobLearnActivation_call,
    METH_VARARGS|METH_KEYWORDS,
    s_call_doc
  },
  {
    s_f_prime_str,
    (PyCFunction)PyBobLearnActivation_f_prime,
    METH_VARARGS|METH_KEYWORDS,
    s_f_prime_doc
  },
  {
    s_f_prime_from_f_str,
    (PyCFunction)PyBobLearnActivation_f_prime_from_f,
    METH_VARARGS|METH_KEYWORDS,
    s_f_prime_from_f_doc
  },
  {
    s_unique_id_str,
    (PyCFunction)PyBobLearnActivation_UniqueIdentifier,
    METH_NOARGS,
    s_unique_id_doc
  },
  {
    s_load_str,
    (PyCFunction)PyBobLearnActivation_Load,
    METH_O,
    s_load_doc
  },
  {
    s_save_str,
    (PyCFunction)PyBobLearnActivation_Save,
    METH_O,
    s_save_doc
  },
  {0} /* Sentinel */
};

int PyBobLearnActivation_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnActivation_Type));
}

static PyObject* PyBobLearnActivation_RichCompare (PyBobLearnActivationObject* self, PyObject* other, int op) {

  if (!PyBobLearnActivation_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'",
        Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }

  auto other_ = reinterpret_cast<PyBobLearnActivationObject*>(other);

  switch (op) {
    case Py_EQ:
      if (self->cxx->str() == other_->cxx->str()) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    case Py_NE:
      if (self->cxx->str() != other_->cxx->str()) Py_RETURN_TRUE;
      Py_RETURN_FALSE;
      break;
    default:
      Py_INCREF(Py_NotImplemented);
      return Py_NotImplemented;
  }

}

static PyObject* PyBobLearnActivation_Str (PyBobLearnActivationObject* self) {
  return Py_BuildValue("s", self->cxx->str().c_str());
}

PyTypeObject PyBobLearnActivation_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_activation_str,                               /* tp_name */
    sizeof(PyBobLearnActivationObject),             /* tp_basicsize */
    0,                                              /* tp_itemsize */
    (destructor)PyBobLearnActivation_delete,        /* tp_dealloc */
    0,                                              /* tp_print */
    0,                                              /* tp_getattr */
    0,                                              /* tp_setattr */
    0,                                              /* tp_compare */
    0,                                              /* tp_repr */
    0,                                              /* tp_as_number */
    0,                                              /* tp_as_sequence */
    0,                                              /* tp_as_mapping */
    0,                                              /* tp_hash */
    (ternaryfunc)PyBobLearnActivation_call,         /* tp_call */
    (reprfunc)PyBobLearnActivation_Str,             /* tp_str */
    0,                                              /* tp_getattro */
    0,                                              /* tp_setattro */
    0,                                              /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,       /* tp_flags */
    s_activation_doc,                               /* tp_doc */
    0,                                              /* tp_traverse */
    0,                                              /* tp_clear */
    (richcmpfunc)PyBobLearnActivation_RichCompare,  /* tp_richcompare */
    0,                                              /* tp_weaklistoffset */
    0,                                              /* tp_iter */
    0,                                              /* tp_iternext */
    PyBobLearnActivation_methods,                   /* tp_methods */
    0,                                              /* tp_members */
    0,                                              /* tp_getset */
    0,                                              /* tp_base */
    0,                                              /* tp_dict */
    0,                                              /* tp_descr_get */
    0,                                              /* tp_descr_set */
    0,                                              /* tp_dictoffset */
    (initproc)PyBobLearnActivation_init,            /* tp_init */
    0,                                              /* tp_alloc */
    PyBobLearnActivation_new,                       /* tp_new */
};
