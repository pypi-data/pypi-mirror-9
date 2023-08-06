/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Mon 13 Jan 2014 17:25:32 CET
 *
 * @brief Implementation of the HyperbolicTangent Activation function
 */

#define BOB_LEARN_ACTIVATION_MODULE
#include <bob.learn.activation/api.h>

PyDoc_STRVAR(s_hyperbolictangentactivation_str,
    BOB_EXT_MODULE_PREFIX ".HyperbolicTangent");

PyDoc_STRVAR(s_hyperbolictangentactivation_doc,
"HyperbolicTangent() -> new HyperbolicTangent\n\
\n\
Computes :math:`f(z) = \\tanh(z)` as activation function.\n\
\n\
");

static int PyBobLearnHyperbolicTangentActivation_init
(PyBobLearnHyperbolicTangentActivationObject* self,
 PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) return -1;

  try {
    self->cxx.reset(new bob::learn::activation::HyperbolicTangentActivation());
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", s_hyperbolictangentactivation_str);
  }

  self->parent.cxx = self->cxx;

  if (PyErr_Occurred()) return -1;

  return 0;

}

static void PyBobLearnHyperbolicTangentActivation_delete
(PyBobLearnHyperbolicTangentActivationObject* self) {

  self->parent.cxx.reset();
  self->cxx.reset();
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyTypeObject PyBobLearnHyperbolicTangentActivation_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_hyperbolictangentactivation_str,                   /*tp_name*/
    sizeof(PyBobLearnHyperbolicTangentActivationObject), /*tp_basicsize*/
    0,                                                   /*tp_itemsize*/
    (destructor)PyBobLearnHyperbolicTangentActivation_delete, /*tp_dealloc*/
    0,                                                   /*tp_print*/
    0,                                                   /*tp_getattr*/
    0,                                                   /*tp_setattr*/
    0,                                                   /*tp_compare*/
    0,                                                   /*tp_repr*/
    0,                                                   /*tp_as_number*/
    0,                                                   /*tp_as_sequence*/
    0,                                                   /*tp_as_mapping*/
    0,                                                   /*tp_hash */
    0,                                                   /*tp_call*/
    0,                                                   /*tp_str*/
    0,                                                   /*tp_getattro*/
    0,                                                   /*tp_setattro*/
    0,                                                   /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,            /*tp_flags*/
    s_hyperbolictangentactivation_doc,                   /* tp_doc */
    0,		                                               /* tp_traverse */
    0,		                                               /* tp_clear */
    0,                                                   /* tp_richcompare */
    0,		                                               /* tp_weaklistoffset */
    0,		                                               /* tp_iter */
    0,		                                               /* tp_iternext */
    0,                                                   /* tp_methods */
    0,                                                   /* tp_members */
    0,                                                   /* tp_getset */
    0,                                                   /* tp_base */
    0,                                                   /* tp_dict */
    0,                                                   /* tp_descr_get */
    0,                                                   /* tp_descr_set */
    0,                                                   /* tp_dictoffset */
    (initproc)PyBobLearnHyperbolicTangentActivation_init,/* tp_init */
    0,                                                   /* tp_alloc */
    0,                                                   /* tp_new */
};
