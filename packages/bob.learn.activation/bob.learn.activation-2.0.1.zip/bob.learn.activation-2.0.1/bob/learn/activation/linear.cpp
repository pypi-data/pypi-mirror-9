/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Mon 13 Jan 2014 17:25:32 CET
 *
 * @brief Implementation of the Linear Activation function
 */

#define BOB_LEARN_ACTIVATION_MODULE
#include <bob.learn.activation/api.h>

PyDoc_STRVAR(s_linearactivation_str, BOB_EXT_MODULE_PREFIX ".Linear");

PyDoc_STRVAR(s_linearactivation_doc,
"Linear([C=1.0]) -> new linear activation functor\n\
\n\
Computes :math:`f(z) = C \\cdot z` as activation function.\n\
\n\
The constructor builds a new linear activation function\n\
with a given constant. Don't use this if you just want to\n\
set constant to the default value (1.0). In such a case,\n\
prefer to use the more efficient :py:class:`Identity` activation.\n\
");

static int PyBobLearnLinearActivation_init
(PyBobLearnLinearActivationObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"C", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  double C = 1.0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|d", kwlist, &C)) return -1;

  try {
    self->cxx.reset(new bob::learn::activation::LinearActivation(C));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", s_linearactivation_str);
  }

  self->parent.cxx = self->cxx;

  if (PyErr_Occurred()) return -1;

  return 0;

}

static void PyBobLearnLinearActivation_delete
(PyBobLearnLinearActivationObject* self) {

  self->parent.cxx.reset();
  self->cxx.reset();
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyDoc_STRVAR(s_C_str, "C");
PyDoc_STRVAR(s_C_doc,
"The multiplication factor for the linear function (read-only)"
);

static PyObject* PyBobLearnLinearActivation_C
(PyBobLearnLinearActivationObject* self) {

  return Py_BuildValue("d", self->cxx->C());

}

static PyGetSetDef PyBobLearnLinearActivation_getseters[] = {
    {
      s_C_str,
      (getter)PyBobLearnLinearActivation_C,
      0,
      s_C_doc,
      0
    },
    {0}  /* Sentinel */
};

PyTypeObject PyBobLearnLinearActivation_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_linearactivation_str,                             /*tp_name*/
    sizeof(PyBobLearnLinearActivationObject),           /*tp_basicsize*/
    0,                                                  /*tp_itemsize*/
    (destructor)PyBobLearnLinearActivation_delete,      /*tp_dealloc*/
    0,                                                  /*tp_print*/
    0,                                                  /*tp_getattr*/
    0,                                                  /*tp_setattr*/
    0,                                                  /*tp_compare*/
    0,                                                  /*tp_repr*/
    0,                                                  /*tp_as_number*/
    0,                                                  /*tp_as_sequence*/
    0,                                                  /*tp_as_mapping*/
    0,                                                  /*tp_hash */
    0,                                                  /*tp_call*/
    0,                                                  /*tp_str*/
    0,                                                  /*tp_getattro*/
    0,                                                  /*tp_setattro*/
    0,                                                  /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /*tp_flags*/
    s_linearactivation_doc,                             /* tp_doc */
    0,		                                              /* tp_traverse */
    0,		                                              /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,		                                              /* tp_weaklistoffset */
    0,		                                              /* tp_iter */
    0,		                                              /* tp_iternext */
    0,                                                  /* tp_methods */
    0,                                                  /* tp_members */
    PyBobLearnLinearActivation_getseters,               /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)PyBobLearnLinearActivation_init,          /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};
