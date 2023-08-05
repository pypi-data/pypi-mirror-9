/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Mon 13 Jan 2014 17:25:32 CET
 *
 * @brief Implementation of the MultipliedHyperbolicTangent Activation function
 */

#define BOB_LEARN_ACTIVATION_MODULE
#include <bob.learn.activation/api.h>

PyDoc_STRVAR(s_multtanhactivation_str,
    BOB_EXT_MODULE_PREFIX ".MultipliedHyperbolicTangent");

PyDoc_STRVAR(s_multtanhactivation_doc,
"MultipliedHyperbolicTangent([C=1.0, [M=1.0]]) -> new multiplied hyperbolic tangent functor\n\
\n\
Computes :math:`f(z) = C \\cdot \\tanh(Mz)` as activation\n\
function.\n\
\n\
Builds a new hyperbolic tangent activation function with a given\n\
constant for the inner and outter products. Don't use this if you\n\
just want to set the constants to the default values (1.0). In\n\
such a case, prefer to use the more efficient\n\
:py:class:`HyperbolicTangent` activation.\n\
");

static int PyBobLearnMultipliedHyperbolicTangentActivation_init
(PyBobLearnMultipliedHyperbolicTangentActivationObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"C", "M", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  double C = 1.0;
  double M = 1.0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|dd", kwlist, &C, &M))
    return -1;

  try {
    self->cxx.reset(new bob::learn::activation::MultipliedHyperbolicTangentActivation(C, M));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", s_multtanhactivation_str);
  }

  self->parent.cxx = self->cxx;

  if (PyErr_Occurred()) return -1;

  return 0;

}

static void PyBobLearnMultipliedHyperbolicTangentActivation_delete
(PyBobLearnMultipliedHyperbolicTangentActivationObject* self) {

  self->parent.cxx.reset();
  self->cxx.reset();
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyDoc_STRVAR(s_C_str, "C");
PyDoc_STRVAR(s_C_doc,
"The outter multiplication factor for the multiplied hyperbolic\n\
tangent function (read-only).\n\
");

static PyObject* PyBobLearnMultipliedHyperbolicTangentActivation_C
(PyBobLearnMultipliedHyperbolicTangentActivationObject* self) {

  return Py_BuildValue("d", self->cxx->C());

}

PyDoc_STRVAR(s_M_str, "M");
PyDoc_STRVAR(s_M_doc,
"The inner multiplication factor for the multiplied hyperbolic\n\
tangent function (read-only).\n\
"
);

static PyObject* PyBobLearnMultipliedHyperbolicTangentActivation_M
(PyBobLearnMultipliedHyperbolicTangentActivationObject* self) {

  return Py_BuildValue("d", self->cxx->M());

}

static PyGetSetDef PyBobLearnMultipliedHyperbolicTangentActivation_getseters[] = {
    {
      s_C_str,
      (getter)PyBobLearnMultipliedHyperbolicTangentActivation_C,
      0,
      s_C_doc,
      0
    },
    {
      s_M_str,
      (getter)PyBobLearnMultipliedHyperbolicTangentActivation_M,
      0,
      s_M_doc,
      0
    },
    {0}  /* Sentinel */
};

PyTypeObject PyBobLearnMultipliedHyperbolicTangentActivation_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_multtanhactivation_str,                           /*tp_name*/
    sizeof(PyBobLearnMultipliedHyperbolicTangentActivationObject),       /*tp_basicsize*/
    0,                                                  /*tp_itemsize*/
    (destructor)PyBobLearnMultipliedHyperbolicTangentActivation_delete,  /*tp_dealloc*/
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
    s_multtanhactivation_doc,                           /* tp_doc */
    0,		                                              /* tp_traverse */
    0,		                                              /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,		                                              /* tp_weaklistoffset */
    0,		                                              /* tp_iter */
    0,		                                              /* tp_iternext */
    0,                                                  /* tp_methods */
    0,                                                  /* tp_members */
    PyBobLearnMultipliedHyperbolicTangentActivation_getseters,           /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)PyBobLearnMultipliedHyperbolicTangentActivation_init,      /* tp_init */
    0,                                                  /* tp_alloc */
    0,                                                  /* tp_new */
};
