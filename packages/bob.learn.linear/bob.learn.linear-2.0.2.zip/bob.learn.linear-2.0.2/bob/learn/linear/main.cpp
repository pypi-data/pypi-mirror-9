/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 13 Dec 2013 12:35:59 CET
 *
 * @brief Bindings to bob::learn::linear
 */

#define BOB_LEARN_LINEAR_MODULE
#include <bob.learn.linear/api.h>

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>
#include <bob.learn.activation/api.h>

static PyMethodDef module_methods[] = {
    {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Bob's Linear machine and trainers");

int PyBobLearnLinear_APIVersion = BOB_LEARN_LINEAR_API_VERSION;

#if PY_VERSION_HEX >= 0x03000000
static PyModuleDef module_definition = {
  PyModuleDef_HEAD_INIT,
  BOB_EXT_MODULE_NAME,
  module_docstr,
  -1,
  module_methods,
  0, 0, 0, 0
};
#endif

extern bool init_BobLearnLinearBIC(PyObject* module);

static PyObject* create_module (void) {

  PyBobLearnLinearMachine_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearMachine_Type) < 0) return 0;

  PyBobLearnLinearPCATrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearPCATrainer_Type) < 0) return 0;

  PyBobLearnLinearFisherLDATrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearFisherLDATrainer_Type) < 0) return 0;

  PyBobLearnLinearCGLogRegTrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearCGLogRegTrainer_Type) < 0) return 0;

  PyBobLearnLinearWhiteningTrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearWhiteningTrainer_Type) < 0) return 0;

  PyBobLearnLinearWCCNTrainer_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobLearnLinearWCCNTrainer_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m);

  /* register some constants */
  if (PyModule_AddIntConstant(m, "__api_version__", BOB_LEARN_LINEAR_API_VERSION) < 0) return 0;
  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0) return 0;

  /* register the types to python */
  Py_INCREF(&PyBobLearnLinearMachine_Type);
  if (PyModule_AddObject(m, "Machine", (PyObject *)&PyBobLearnLinearMachine_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnLinearPCATrainer_Type);
  if (PyModule_AddObject(m, "PCATrainer", (PyObject *)&PyBobLearnLinearPCATrainer_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnLinearFisherLDATrainer_Type);
  if (PyModule_AddObject(m, "FisherLDATrainer", (PyObject *)&PyBobLearnLinearFisherLDATrainer_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnLinearCGLogRegTrainer_Type);
  if (PyModule_AddObject(m, "CGLogRegTrainer", (PyObject *)&PyBobLearnLinearCGLogRegTrainer_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnLinearWhiteningTrainer_Type);
  if (PyModule_AddObject(m, "WhiteningTrainer", (PyObject *)&PyBobLearnLinearWhiteningTrainer_Type) < 0) return 0;

  Py_INCREF(&PyBobLearnLinearWCCNTrainer_Type);
  if (PyModule_AddObject(m, "WCCNTrainer", (PyObject *)&PyBobLearnLinearWCCNTrainer_Type) < 0) return 0;

  if (!init_BobLearnLinearBIC(m)) return 0;

  static void* PyBobLearnLinear_API[PyBobLearnLinear_API_pointers];

  /* exhaustive list of C APIs */

  /**************
   * Versioning *
   **************/

  PyBobLearnLinear_API[PyBobLearnLinear_APIVersion_NUM] = (void *)&PyBobLearnLinear_APIVersion;

  /******************************************
   * Bindings for bob.learn.linear.Machine *
   ******************************************/

  PyBobLearnLinear_API[PyBobLearnLinearMachine_Type_NUM] = (void *)&PyBobLearnLinearMachine_Type;

  PyBobLearnLinear_API[PyBobLearnLinearMachine_Check_NUM] = (void *)&PyBobLearnLinearMachine_Check;

  PyBobLearnLinear_API[PyBobLearnLinearMachine_NewFromSize_NUM] = (void *)&PyBobLearnLinearMachine_NewFromSize;

  /*********************************************
   * Bindings for bob.learn.linear.PCATrainer *
   *********************************************/

  PyBobLearnLinear_API[PyBobLearnLinearPCATrainer_Type_NUM] = (void *)&PyBobLearnLinearPCATrainer_Type;

  PyBobLearnLinear_API[PyBobLearnLinearPCATrainer_Check_NUM] = (void *)&PyBobLearnLinearPCATrainer_Check;

  /***************************************************
   * Bindings for bob.learn.linear.FisherLDATrainer *
   ***************************************************/

  PyBobLearnLinear_API[PyBobLearnLinearFisherLDATrainer_Type_NUM] = (void *)&PyBobLearnLinearFisherLDATrainer_Type;

  PyBobLearnLinear_API[PyBobLearnLinearFisherLDATrainer_Check_NUM] = (void *)&PyBobLearnLinearFisherLDATrainer_Check;

  /**************************************************
   * Bindings for bob.learn.linear.CGLogRegTrainer *
   **************************************************/

  PyBobLearnLinear_API[PyBobLearnLinearCGLogRegTrainer_Type_NUM] = (void *)&PyBobLearnLinearCGLogRegTrainer_Type;

  PyBobLearnLinear_API[PyBobLearnLinearCGLogRegTrainer_Check_NUM] = (void *)&PyBobLearnLinearCGLogRegTrainer_Check;

  /***************************************************
   * Bindings for bob.learn.linear.WhiteningTrainer *
   ***************************************************/

  PyBobLearnLinear_API[PyBobLearnLinearWhiteningTrainer_Type_NUM] = (void *)&PyBobLearnLinearWhiteningTrainer_Type;

  PyBobLearnLinear_API[PyBobLearnLinearWhiteningTrainer_Check_NUM] = (void *)&PyBobLearnLinearWhiteningTrainer_Check;

  /***************************************************
   * Bindings for bob.learn.linear.WCCNTrainer *
   ***************************************************/

  PyBobLearnLinear_API[PyBobLearnLinearWCCNTrainer_Type_NUM] = (void *)&PyBobLearnLinearWCCNTrainer_Type;

  PyBobLearnLinear_API[PyBobLearnLinearWCCNTrainer_Check_NUM] = (void *)&PyBobLearnLinearWCCNTrainer_Check;

#if PY_VERSION_HEX >= 0x02070000

  /* defines the PyCapsule */

  PyObject* c_api_object = PyCapsule_New((void *)PyBobLearnLinear_API,
      BOB_EXT_MODULE_PREFIX "." BOB_EXT_MODULE_NAME "._C_API", 0);

#else

  PyObject* c_api_object = PyCObject_FromVoidPtr((void *)PyBobLearnLinear_API, 0);

#endif

  if (c_api_object) PyModule_AddObject(m, "_C_API", c_api_object);

  /* imports dependencies */
  if (import_bob_blitz() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  if (import_bob_io_base() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  if (import_bob_learn_activation() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  Py_INCREF(m);
  return m;

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
