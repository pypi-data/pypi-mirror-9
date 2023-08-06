/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 15 Jan 2014 10:15:21 CET
 *
 * @brief C/C++ Python API for activation functors in bob::learn::activation
 */

#ifndef BOB_LEARN_ACTIVATION_H
#define BOB_LEARN_ACTIVATION_H

#include <Python.h>
#include <bob.learn.activation/config.h>
#include <bob.learn.activation/Activation.h>

#define BOB_LEARN_ACTIVATION_MODULE_PREFIX bob.learn.activation
#define BOB_LEARN_ACTIVATION_MODULE_NAME _library

/*******************
 * C API functions *
 *******************/

/* Enum defining entries in the function table */
enum _PyBobLearnActivation_ENUM{
  PyBobLearnActivation_APIVersion_NUM = 0,
  // Bindings for bob.learn.activation.Activation
  PyBobLearnActivation_Type_NUM,
  PyBobLearnActivation_Check_NUM,
  PyBobLearnActivation_NewFromActivation_NUM,
  // Bindings for bob.learn.activation.Identity
  PyBobLearnIdentityActivation_Type_NUM,
  // Bindings for bob.learn.activation.Linear
  PyBobLearnLinearActivation_Type_NUM,
  // Bindings for bob.learn.activation.Logistic
  PyBobLearnLogisticActivation_Type_NUM,
  // Bindings for bob.learn.activation.HyperbolicTangent
  PyBobLearnHyperbolicTangentActivation_Type_NUM,
  // Bindings for bob.learn.activation.MultipliedHyperbolicTangent
  PyBobLearnMultipliedHyperbolicTangentActivation_Type_NUM,
  // Total number of C API pointers
  PyBobLearnActivation_API_pointers
};

/**************
 * Versioning *
 **************/

#define PyBobLearnActivation_APIVersion_TYPE int

/*************************************************
 * Bindings for bob.learn.activation.Activation *
 *************************************************/

typedef struct {
  PyObject_HEAD
  boost::shared_ptr<bob::learn::activation::Activation> cxx;
} PyBobLearnActivationObject;

#define PyBobLearnActivation_Type_TYPE PyTypeObject

#define PyBobLearnActivation_Check_RET int
#define PyBobLearnActivation_Check_PROTO (PyObject* o)

#define PyBobLearnActivation_NewFromActivation_RET PyObject*
#define PyBobLearnActivation_NewFromActivation_PROTO (boost::shared_ptr<bob::learn::activation::Activation> a)

/***********************************************
 * Bindings for bob.learn.activation.Identity *
 ***********************************************/

typedef struct {
  PyBobLearnActivationObject parent;
  boost::shared_ptr<bob::learn::activation::IdentityActivation> cxx;
} PyBobLearnIdentityActivationObject;

#define PyBobLearnIdentityActivation_Type_TYPE PyTypeObject

/*********************************************
 * Bindings for bob.learn.activation.Linear *
 *********************************************/

typedef struct {
  PyBobLearnActivationObject parent;
  boost::shared_ptr<bob::learn::activation::LinearActivation> cxx;
} PyBobLearnLinearActivationObject;

#define PyBobLearnLinearActivation_Type_TYPE PyTypeObject

/***********************************************
 * Bindings for bob.learn.activation.Logistic *
 ***********************************************/

typedef struct {
  PyBobLearnActivationObject parent;
  boost::shared_ptr<bob::learn::activation::LogisticActivation> cxx;
} PyBobLearnLogisticActivationObject;

#define PyBobLearnLogisticActivation_Type_TYPE PyTypeObject

/********************************************************
 * Bindings for bob.learn.activation.HyperbolicTangent *
 ********************************************************/

typedef struct {
  PyBobLearnActivationObject parent;
  boost::shared_ptr<bob::learn::activation::HyperbolicTangentActivation> cxx;
} PyBobLearnHyperbolicTangentActivationObject;

#define PyBobLearnHyperbolicTangentActivation_Type_TYPE PyTypeObject

/******************************************************************
 * Bindings for bob.learn.activation.MultipliedHyperbolicTangent *
 ******************************************************************/

typedef struct {
  PyBobLearnActivationObject parent;
  boost::shared_ptr<bob::learn::activation::MultipliedHyperbolicTangentActivation> cxx;
} PyBobLearnMultipliedHyperbolicTangentActivationObject;

#define PyBobLearnMultipliedHyperbolicTangentActivation_Type_TYPE PyTypeObject


#ifdef BOB_LEARN_ACTIVATION_MODULE

  /* This section is used when compiling `bob.learn.activation' itself */

  /**************
   * Versioning *
   **************/

  extern int PyBobLearnActivation_APIVersion;

  /*************************************************
   * Bindings for bob.learn.activation.Activation *
   *************************************************/

  extern PyBobLearnActivation_Type_TYPE PyBobLearnActivation_Type;

  PyBobLearnActivation_Check_RET PyBobLearnActivation_Check PyBobLearnActivation_Check_PROTO;

  PyBobLearnActivation_NewFromActivation_RET PyBobLearnActivation_NewFromActivation PyBobLearnActivation_NewFromActivation_PROTO;

  /***********************************************
   * Bindings for bob.learn.activation.Identity *
   ***********************************************/

  extern PyBobLearnIdentityActivation_Type_TYPE PyBobLearnIdentityActivation_Type;

  /*********************************************
   * Bindings for bob.learn.activation.Linear *
   *********************************************/

  extern PyBobLearnLinearActivation_Type_TYPE PyBobLearnLinearActivation_Type;

  /***********************************************
   * Bindings for bob.learn.activation.Logistic *
   ***********************************************/

  extern PyBobLearnLogisticActivation_Type_TYPE PyBobLearnLogisticActivation_Type;

  /********************************************************
   * Bindings for bob.learn.activation.HyperbolicTangent *
   ********************************************************/

  extern PyBobLearnHyperbolicTangentActivation_Type_TYPE PyBobLearnHyperbolicTangentActivation_Type;

  /******************************************************************
   * Bindings for bob.learn.activation.MultipliedHyperbolicTangent *
   ******************************************************************/

  extern PyBobLearnMultipliedHyperbolicTangentActivation_Type_TYPE PyBobLearnMultipliedHyperbolicTangentActivation_Type;

#else

  /* This section is used in modules that use `bob.learn.activation's' C-API */

/************************************************************************
 * Macros to avoid symbol collision and allow for separate compilation. *
 * We pig-back on symbols already defined for NumPy and apply the same  *
 * set of rules here, creating our own API symbol names.                *
 ************************************************************************/

#  if defined(PY_ARRAY_UNIQUE_SYMBOL)
#    define BOB_LEARN_ACTIVATION_MAKE_API_NAME_INNER(a) BOB_LEARN_ACTIVATION_ ## a
#    define BOB_LEARN_ACTIVATION_MAKE_API_NAME(a) BOB_LEARN_ACTIVATION_MAKE_API_NAME_INNER(a)
#    define PyBobLearnActivation_API BOB_LEARN_ACTIVATION_MAKE_API_NAME(PY_ARRAY_UNIQUE_SYMBOL)
#  endif

#  if defined(NO_IMPORT_ARRAY)
  extern void **PyBobLearnActivation_API;
#  else
#    if defined(PY_ARRAY_UNIQUE_SYMBOL)
  void **PyBobLearnActivation_API;
#    else
  static void **PyBobLearnActivation_API=NULL;
#    endif
#  endif

  /**************
   * Versioning *
   **************/

# define PyBobLearnActivation_APIVersion (*(PyBobLearnActivation_APIVersion_TYPE *)PyBobLearnActivation_API[PyBobLearnActivation_APIVersion_NUM])

  /*************************************************
   * Bindings for bob.learn.activation.Activation *
   *************************************************/

# define PyBobLearnActivation_Type (*(PyBobLearnActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnActivation_Type_NUM])

# define PyBobLearnActivation_Check (*(PyBobLearnActivation_Check_RET (*)PyBobLearnActivation_Check_PROTO) PyBobLearnActivation_API[PyBobLearnActivation_Check_NUM])

# define PyBobLearnActivation_NewFromActivation (*(PyBobLearnActivation_NewFromActivation_RET (*)PyBobLearnActivation_NewFromActivation_PROTO) PyBobLearnActivation_API[PyBobLearnActivation_NewFromActivation_NUM])

  /***********************************************
   * Bindings for bob.learn.activation.Identity *
   ***********************************************/

# define PyBobLearnIdentityActivation_Type (*(PyBobLearnIdentityActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnIdentityActivation_Type_NUM])

  /*********************************************
   * Bindings for bob.learn.activation.Linear *
   *********************************************/

# define PyBobLearnLinearActivation_Type (*(PyBobLearnLinearActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnLinearActivation_Type_NUM])

  /***********************************************
   * Bindings for bob.learn.activation.Logistic *
   ***********************************************/

# define PyBobLearnLogisticActivation_Type (*(PyBobLearnLogisticActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnLogisticActivation_Type_NUM])

  /********************************************************
   * Bindings for bob.learn.activation.HyperbolicTangent *
   ********************************************************/

# define PyBobLearnHyperbolicTangentActivation_Type (*(PyBobLearnHyperbolicTangentActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnHyperbolicTangentActivation_Type_NUM])

  /******************************************************************
   * Bindings for bob.learn.activation.MultipliedHyperbolicTangent *
   ******************************************************************/

# define PyBobLearnMultipliedHyperbolicTangentActivation_Type (*(PyBobLearnMultipliedHyperbolicTangentActivation_Type_TYPE *)PyBobLearnActivation_API[PyBobLearnMultipliedHyperbolicTangentActivation_Type_NUM])

# if !defined(NO_IMPORT_ARRAY)

  /**
   * Returns -1 on error, 0 on success. PyCapsule_Import will set an exception
   * if there's an error.
   */
  static int import_bob_learn_activation(void) {

    PyObject *c_api_object;
    PyObject *module;

    module = PyImport_ImportModule(BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_PREFIX) "." BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_NAME));

    if (module == NULL) return -1;

    c_api_object = PyObject_GetAttrString(module, "_C_API");

    if (c_api_object == NULL) {
      Py_DECREF(module);
      return -1;
    }

#   if PY_VERSION_HEX >= 0x02070000
    if (PyCapsule_CheckExact(c_api_object)) {
      PyBobLearnActivation_API = (void **)PyCapsule_GetPointer(c_api_object,
          PyCapsule_GetName(c_api_object));
    }
#   else
    if (PyCObject_Check(c_api_object)) {
      PyBobLearnActivation_API = (void **)PyCObject_AsVoidPtr(c_api_object);
    }
#   endif

    Py_DECREF(c_api_object);
    Py_DECREF(module);

    if (!PyBobLearnActivation_API) {
      PyErr_Format(PyExc_ImportError,
#   if PY_VERSION_HEX >= 0x02070000
          "cannot find C/C++ API capsule at `%s.%s._C_API'",
#   else
          "cannot find C/C++ API cobject at `%s.%s._C_API'",
#   endif
          BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_PREFIX),
          BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_NAME));
      return -1;
    }

    /* Checks that the imported version matches the compiled version */
    int imported_version = *(int*)PyBobLearnActivation_API[PyBobLearnActivation_APIVersion_NUM];

    if (BOB_LEARN_ACTIVATION_API_VERSION != imported_version) {
      PyErr_Format(PyExc_ImportError, "%s.%s import error: you compiled against API version 0x%04x, but are now importing an API with version 0x%04x which is not compatible - check your Python runtime environment for errors", BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_PREFIX), BOOST_PP_STRINGIZE(BOB_LEARN_ACTIVATION_MODULE_NAME), BOB_LEARN_ACTIVATION_API_VERSION, imported_version);
      return -1;
    }

    /* If you get to this point, all is good */
    return 0;

  }

# endif //!defined(NO_IMPORT_ARRAY)

#endif /* BOB_LEARN_ACTIVATION_MODULE */

#endif /* BOB_LEARN_ACTIVATION_H */
