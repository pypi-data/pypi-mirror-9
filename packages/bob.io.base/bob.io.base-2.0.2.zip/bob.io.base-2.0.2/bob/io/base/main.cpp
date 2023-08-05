/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 25 Oct 16:54:55 2013
 *
 * @brief Bindings to bob::io
 */

#define BOB_IO_BASE_MODULE
#include <bob.io.base/api.h>

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>

/**
 * Creates an str object, from a C or C++ string. Returns a **new
 * reference**.
 */
static PyObject* make_object(const char* s) {
  return Py_BuildValue("s", s);
}

static PyObject* PyBobIo_Extensions(PyObject*) {

  typedef std::map<std::string, std::string> map_type;
  const map_type& table = bob::io::base::CodecRegistry::getExtensions();

  PyObject* retval = PyDict_New();
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  for (auto it=table.begin(); it!=table.end(); ++it) {
    PyObject* pyvalue = make_object(it->second.c_str());
    if (!pyvalue) return 0;
    if (PyDict_SetItemString(retval, it->first.c_str(), pyvalue) != 0) {
      return 0;
    }
  }

  Py_INCREF(retval);
  return retval;

}

PyDoc_STRVAR(s_extensions_str, "extensions");
PyDoc_STRVAR(s_extensions_doc,
"extensions() -> dict\n\
\n\
Returns a dictionary containing all extensions and descriptions\n\
currently stored on the global codec registry\n\
");

static PyMethodDef module_methods[] = {
    {
      s_extensions_str,
      (PyCFunction)PyBobIo_Extensions,
      METH_NOARGS,
      s_extensions_doc,
    },
    {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Core bob::io classes and methods");

int PyBobIo_APIVersion = BOB_IO_BASE_API_VERSION;

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

static PyObject* create_module (void) {

  PyBobIoFile_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIoFile_Type) < 0) return 0;

  PyBobIoFileIterator_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIoFileIterator_Type) < 0) return 0;

  PyBobIoHDF5File_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIoHDF5File_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m);

  /* register some constants */
  if (PyModule_AddIntConstant(m, "__api_version__", BOB_IO_BASE_API_VERSION) < 0) return 0;
  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0) return 0;

  /* register the types to python */
  Py_INCREF(&PyBobIoFile_Type);
  if (PyModule_AddObject(m, "File", (PyObject *)&PyBobIoFile_Type) < 0) return 0;

  Py_INCREF(&PyBobIoFileIterator_Type);
  if (PyModule_AddObject(m, "File.iter", (PyObject *)&PyBobIoFileIterator_Type) < 0) return 0;

  Py_INCREF(&PyBobIoHDF5File_Type);
  if (PyModule_AddObject(m, "HDF5File", (PyObject *)&PyBobIoHDF5File_Type) < 0) return 0;

  static void* PyBobIo_API[PyBobIo_API_pointers];

  /* exhaustive list of C APIs */

  /**************
   * Versioning *
   **************/

  PyBobIo_API[PyBobIo_APIVersion_NUM] = (void *)&PyBobIo_APIVersion;

  /**********************************
   * Bindings for bob.io.base.File *
   **********************************/

  PyBobIo_API[PyBobIoFile_Type_NUM] = (void *)&PyBobIoFile_Type;

  PyBobIo_API[PyBobIoFileIterator_Type_NUM] = (void *)&PyBobIoFileIterator_Type;

  /************************
   * I/O generic bindings *
   ************************/

  PyBobIo_API[PyBobIo_AsTypenum_NUM] = (void *)PyBobIo_AsTypenum;

  PyBobIo_API[PyBobIo_TypeInfoAsTuple_NUM] = (void *)PyBobIo_TypeInfoAsTuple;

  PyBobIo_API[PyBobIo_FilenameConverter_NUM] = (void *)PyBobIo_FilenameConverter;

  /*****************
   * HDF5 bindings *
   *****************/

  PyBobIo_API[PyBobIoHDF5File_Type_NUM] = (void *)&PyBobIoHDF5File_Type;

  PyBobIo_API[PyBobIoHDF5File_Check_NUM] = (void *)&PyBobIoHDF5File_Check;

  PyBobIo_API[PyBobIoHDF5File_Converter_NUM] = (void *)&PyBobIoHDF5File_Converter;

/*****************************************
 * Code Registration and De-registration *
 *****************************************/

  PyBobIo_API[PyBobIoCodec_Register_NUM] = (void *)&PyBobIoCodec_Register;

  PyBobIo_API[PyBobIoCodec_Deregister_NUM] = (void *)&PyBobIoCodec_Deregister;

  PyBobIo_API[PyBobIoCodec_IsRegistered_NUM] = (void *)&PyBobIoCodec_IsRegistered;

  PyBobIo_API[PyBobIoCodec_GetDescription_NUM] = (void *)&PyBobIoCodec_GetDescription;

#if PY_VERSION_HEX >= 0x02070000

  /* defines the PyCapsule */

  PyObject* c_api_object = PyCapsule_New((void *)PyBobIo_API,
      BOB_EXT_MODULE_PREFIX "." BOB_EXT_MODULE_NAME "._C_API", 0);

#else

  PyObject* c_api_object = PyCObject_FromVoidPtr((void *)PyBobIo_API, 0);

#endif

  if (!c_api_object) return 0;

  if (PyModule_AddObject(m, "_C_API", c_api_object) < 0) return 0;

  /* imports dependencies */
  if (import_bob_blitz() < 0) {
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
