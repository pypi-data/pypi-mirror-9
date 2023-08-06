/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue 12 Nov 18:19:22 2013
 *
 * @brief Bindings to bob::io::base::HDF5File
 */

#define BOB_IO_BASE_MODULE
#include <bob.io.base/api.h>

#include <boost/make_shared.hpp>
#include <numpy/arrayobject.h>
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>
#include <stdexcept>
#include <cstring>


#define HDF5FILE_NAME "HDF5File"
PyDoc_STRVAR(s_hdf5file_str, BOB_EXT_MODULE_PREFIX "." HDF5FILE_NAME);

PyDoc_STRVAR(s_hdf5file_doc,
"* HDF5File(filename, [mode='r'])\n\
* HDF5File(hdf5)\n\
\n\
Reads and writes data to HDF5 files.\n\
\n\
Constructor parameters:\n\
\n\
filename\n\
  [str] The file path to the file you want to read from/write to\n\
\n\
mode\n\
  [str, optional] The opening mode: Use ``'r'`` for read-only,\n\
  ``'a'`` for read/write/append, ``'w'`` for read/write/truncate\n\
  or ``'x'`` for (read/write/exclusive). This flag defaults to\n\
  ``'r'``.\n\
\n\
hdf5\n\
  [:py:class:`bob.io.base.HDF5File`] An HDF5 file to copy-construct,\n\
  (a shallow copy of the file will be created) \n\
\n\
HDF5 stands for Hierarchical Data Format version 5. It is a\n\
flexible, binary file format that allows one to store and read\n\
data efficiently into files. It is a cross-platform,\n\
cross-architecture format.\n\
\n\
Objects of this class allows users to read and write data from\n\
and to files in HDF5 format. For an introduction to HDF5, visit\n\
the `HDF5 Website <http://www.hdfgroup.org/HDF5>`_.\n\
\n\
");

int PyBobIoHDF5File_Check(PyObject* o) {
  if (!o) return 0;
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobIoHDF5File_Type));
}

int PyBobIoHDF5File_Converter(PyObject* o, PyBobIoHDF5FileObject** a) {
  if (!PyBobIoHDF5File_Check(o)) return 0;
  Py_INCREF(o);
  (*a) = reinterpret_cast<PyBobIoHDF5FileObject*>(o);
  return 1;
}

/* How to create a new PyBobIoHDF5FileObject */
static PyObject* PyBobIoHDF5File_New(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIoHDF5FileObject* self = (PyBobIoHDF5FileObject*)type->tp_alloc(type, 0);

  self->f.reset();

  return reinterpret_cast<PyObject*>(self);
}

static void PyBobIoHDF5File_Delete (PyBobIoHDF5FileObject* o) {

  o->f.reset();
  Py_TYPE(o)->tp_free((PyObject*)o);

}

static bob::io::base::HDF5File::mode_t mode_from_char (char mode) {

  bob::io::base::HDF5File::mode_t new_mode = bob::io::base::HDF5File::inout;

  switch (mode) {
    case 'r': new_mode = bob::io::base::HDF5File::in; break;
    case 'a': new_mode = bob::io::base::HDF5File::inout; break;
    case 'w': new_mode = bob::io::base::HDF5File::trunc; break;
    case 'x': new_mode = bob::io::base::HDF5File::excl; break;
    default:
      PyErr_SetString(PyExc_RuntimeError, "Supported flags are 'r' (read-only), 'a' (read/write/append), 'w' (read/write/truncate) or 'x' (read/write/exclusive)");
  }

  return new_mode;

}

/* The __init__(self) method */
static int PyBobIoHDF5File_Init(PyBobIoHDF5FileObject* self,
    PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"filename", "mode", 0};
  static char** kwlist1 = const_cast<char**>(const_kwlist);
  static char* kwlist2[] = {const_cast<char*>("hdf5"), 0};

  // get the number of command line arguments
  Py_ssize_t nargs = (args?PyTuple_Size(args):0) + (kwds?PyDict_Size(kwds):0);

  if (!nargs){
    // at least one argument is required
    PyErr_Format(PyExc_TypeError, "`%s' constructor requires at least one parameter", Py_TYPE(self)->tp_name);
    return -1;
  } // nargs == 0

  PyObject* k = Py_BuildValue("s", kwlist2[0]);
  auto k_ = make_safe(k);
  if (
    (kwds && PyDict_Contains(kwds, k)) ||
    (args && PyBobIoHDF5File_Check(PyTuple_GET_ITEM(args, 0)))
  ){
    PyBobIoHDF5FileObject* other;
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist2, &PyBobIoHDF5File_Converter, &other))
      return -1;
    auto other_ = make_safe(other);
    self->f = other->f;
    return 0;
  }


#if PY_VERSION_HEX >= 0x03000000
#  define MODE_CHAR "C"
  int mode = 'r';
#else
#  define MODE_CHAR "c"
  char mode = 'r';
#endif

  PyObject* filename = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|" MODE_CHAR, kwlist1,
        &PyBobIo_FilenameConverter, &filename, &mode))
    return -1;

#undef MODE_CHAR

  auto filename_ = make_safe(filename);

  if (mode != 'r' && mode != 'w' && mode != 'a' && mode != 'x') {
    PyErr_Format(PyExc_ValueError, "file open mode string should have 1 element and be either 'r' (read), 'w' (write), 'a' (append), 'x' (exclusive)");
    return -1;
  }
  bob::io::base::HDF5File::mode_t mode_mode = mode_from_char(mode);
  if (PyErr_Occurred()) return -1;

#if PY_VERSION_HEX >= 0x03000000
  const char* c_filename = PyBytes_AS_STRING(filename);
#else
  const char* c_filename = PyString_AS_STRING(filename);
#endif

  try {
    self->f.reset(new bob::io::base::HDF5File(c_filename, mode_mode));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot open file `%s' with mode `%c': unknown exception caught", c_filename, mode);
    return -1;
  }

  return 0; ///< SUCCESS
}

static PyObject* PyBobIoHDF5File_Repr(PyBobIoHDF5FileObject* self) {
  return
# if PY_VERSION_HEX >= 0x03000000
  PyUnicode_FromFormat
# else
  PyString_FromFormat
# endif
  ("%s(filename='%s')", Py_TYPE(self)->tp_name, self->f->filename().c_str());
}

static PyObject* PyBobIoHDF5File_Flush(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {
  /* Parses input arguments in a single shot */
  static char* kwlist[] = {0};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) return 0;

  try {
    self->f->flush();
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while flushing HDF5 file `%s'", filename);
    return 0;
  }
  Py_RETURN_NONE;
}

static auto s_flush = bob::extension::FunctionDoc(
  "flush",
  "Flushes the content of the HDF5 file to disk",
  "When the HDF5File is open for writing, this function synchronizes the contents on the disk with the one from the file."
  "When the file is open for reading, nothing happens.",
  true
)
  .add_prototype("")
;


static PyObject* PyBobIoHDF5File_Close(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {
  /* Parses input arguments in a single shot */
  static char * kwlist[] = {0};

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "", kwlist)) return 0;

  try {
    self->f->close();
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while closing HDF5 file `%s'", filename);
    return 0;
  }

  Py_RETURN_NONE;
}

static auto s_close = bob::extension::FunctionDoc(
  "close",
  "Closes this file",
  "This function closes the HDF5File after flushing all its contents to disk."
  "After the HDF5File is closed, any operation on it will result in an exception.",
  true
)
  .add_prototype("")
;


static PyObject* PyBobIoHDF5File_ChangeDirectory(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* path = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &path)) return 0;

  try {
    self->f->cd(path);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while changing directory to `%s' in HDF5 file `%s'", path, filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_cd_str, "cd");
PyDoc_STRVAR(s_cd_doc,
"x.cd(path) -> None\n\
\n\
Changes the current prefix path.\n\
\n\
Parameters:\n\
\n\
path\n\
  [str] The path to change directories to\n\
\n\
When this object is started, the prefix path is empty, which\n\
means all following paths to data objects should be given using\n\
the full path. If you set this to a different value, it will be\n\
used as a prefix to any subsequent operation until you reset\n\
it. If path starts with ``'/'``, it is treated as an absolute\n\
path. ``'..'`` and ``'.'`` are supported. This object should\n\
be an :py:class:`str` object. If the value is relative, it is\n\
added to the current path. If it is absolute, it causes the\n\
prefix to be reset. Note all operations taking a relative path,\n\
following a :py:func:`cd`, will be considered relative to the value\n\
defined by the ``cwd`` property of this object.\n\
");

static PyObject* PyBobIoHDF5File_HasGroup(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* path = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &path)) return 0;

  try {
    if (self->f->hasGroup(path)) Py_RETURN_TRUE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while checking for group `%s' in HDF5 file `%s'", path, filename);
    return 0;
  }

  Py_RETURN_FALSE;
}

PyDoc_STRVAR(s_has_group_str, "has_group");
PyDoc_STRVAR(s_has_group_doc,
"x.has_group(path) -> bool\n\
\n\
Checks if a path (group) exists inside a file\n\
\n\
Parameters:\n\
\n\
path\n\
  [str] The path to check\n\
\n\
Checks if a path (i.e. a *group* in HDF5 parlance) exists inside\n\
a file. This method does not work for datasets, only for\n\
directories. If the given path is relative, it is take w.r.t.\n\
to the current working directory.\n\
");

static PyObject* PyBobIoHDF5File_CreateGroup(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* path = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &path)) return 0;

  try {
    self->f->createGroup(path);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while creating group `%s' in HDF5 file `%s'", path, filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_create_group_str, "create_group");
PyDoc_STRVAR(s_create_group_doc,
"x.create_group(path) -> None\n\
\n\
Creates a new path (group) inside the file.\n\
\n\
Parameters:\n\
\n\
path\n\
  [str] The path to check\n\
\n\
Creates a new directory (i.e., a *group* in HDF5 parlance) inside\n\
the file. A relative path is taken w.r.t. to the current\n\
directory. If the directory already exists (check it with\n\
:py:meth:`bob.io.base.HDF5File.has_group`, an exception will be raised.\n\
");

static PyObject* PyBobIoHDF5File_HasDataset(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"key", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* key = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &key)) return 0;

  try {
    if (self->f->contains(key)) Py_RETURN_TRUE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while checking for dataset `%s' in HDF5 file `%s'", key, filename);
    return 0;
  }

  Py_RETURN_FALSE;
}

PyDoc_STRVAR(s_has_key_str, "has_key");
PyDoc_STRVAR(s_has_dataset_str, "has_dataset");
PyDoc_STRVAR(s_has_dataset_doc,
"x.has_dataset(key) -> bool\n\
\n\
Checks if a dataset exists inside a file\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The dataset path to check\n\
\n\
Checks if a dataset exists inside a file, on the specified path.\n\
If the given path is relative, it is take w.r.t. to the current\n\
working directory.\n\
");

static bob::io::base::hdf5type PyBobIo_H5FromTypenum (int type_num) {

  switch(type_num) {
    case NPY_STRING:     return bob::io::base::s;
    case NPY_BOOL:       return bob::io::base::b;
    case NPY_INT8:       return bob::io::base::i8;
    case NPY_INT16:      return bob::io::base::i16;
    case NPY_INT32:      return bob::io::base::i32;
    case NPY_INT64:      return bob::io::base::i64;
    case NPY_UINT8:      return bob::io::base::u8;
    case NPY_UINT16:     return bob::io::base::u16;
    case NPY_UINT32:     return bob::io::base::u32;
    case NPY_UINT64:     return bob::io::base::u64;
    case NPY_FLOAT32:    return bob::io::base::f32;
    case NPY_FLOAT64:    return bob::io::base::f64;
#ifdef NPY_FLOAT128
    case NPY_FLOAT128:   return bob::io::base::f128;
#endif
    case NPY_COMPLEX64:  return bob::io::base::c64;
    case NPY_COMPLEX128: return bob::io::base::c128;
#ifdef NPY_COMPLEX256
    case NPY_COMPLEX256: return bob::io::base::c256;
#endif
#if defined(__LP64__) || defined(__APPLE__)
    case NPY_LONGLONG:
                         switch (NPY_BITSOF_LONGLONG) {
                           case 8: return bob::io::base::i8;
                           case 16: return bob::io::base::i16;
                           case 32: return bob::io::base::i32;
                           case 64: return bob::io::base::i64;
                           default: return bob::io::base::unsupported;
                         }
                         break;
    case NPY_ULONGLONG:
                         switch (NPY_BITSOF_LONGLONG) {
                           case 8: return bob::io::base::u8;
                           case 16: return bob::io::base::u16;
                           case 32: return bob::io::base::u32;
                           case 64: return bob::io::base::u64;
                           default: return bob::io::base::unsupported;
                         }
                         break;
#endif
    default:             return bob::io::base::unsupported;
  }

}

static int PyBobIo_H5AsTypenum (bob::io::base::hdf5type type) {

  switch(type) {
    case bob::io::base::s:    return NPY_STRING;
    case bob::io::base::b:    return NPY_BOOL;
    case bob::io::base::i8:   return NPY_INT8;
    case bob::io::base::i16:  return NPY_INT16;
    case bob::io::base::i32:  return NPY_INT32;
    case bob::io::base::i64:  return NPY_INT64;
    case bob::io::base::u8:   return NPY_UINT8;
    case bob::io::base::u16:  return NPY_UINT16;
    case bob::io::base::u32:  return NPY_UINT32;
    case bob::io::base::u64:  return NPY_UINT64;
    case bob::io::base::f32:  return NPY_FLOAT32;
    case bob::io::base::f64:  return NPY_FLOAT64;
#ifdef NPY_FLOAT128
    case bob::io::base::f128: return NPY_FLOAT128;
#endif
    case bob::io::base::c64:  return NPY_COMPLEX64;
    case bob::io::base::c128: return NPY_COMPLEX128;
#ifdef NPY_COMPLEX256
    case bob::io::base::c256: return NPY_COMPLEX256;
#endif
    default:            return NPY_NOTYPE;
  }

}

static PyObject* PyBobIo_HDF5TypeAsTuple (const bob::io::base::HDF5Type& t) {

  const bob::io::base::HDF5Shape& sh = t.shape();
  size_t ndim = sh.n();
  const hsize_t* shptr = sh.get();

  int type_num = PyBobIo_H5AsTypenum(t.type());
  if (type_num == NPY_NOTYPE) {
    PyErr_Format(PyExc_TypeError, "unsupported HDF5 element type (%d) found during conversion to numpy type number", (int)t.type());
    return 0;
  }

  PyObject* dtype = reinterpret_cast<PyObject*>(PyArray_DescrFromType(type_num));
  if (!dtype) return 0;

  PyObject* shape = PyTuple_New(ndim);
  if (!shape) return 0;

  PyObject* retval = Py_BuildValue("NN", dtype, shape); //steals references
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  for (Py_ssize_t i=0; i<(Py_ssize_t)ndim; ++i) {
    PyObject* value = Py_BuildValue("n", shptr[i]);
    if (!value) return 0;
    PyTuple_SET_ITEM(shape, i, value);
  }

  return Py_BuildValue("O", retval);

}

static PyObject* PyBobIo_HDF5DescriptorAsTuple (const bob::io::base::HDF5Descriptor& d) {

  PyObject* type = PyBobIo_HDF5TypeAsTuple(d.type);
  if (!type) return 0;
  PyObject* size = Py_BuildValue("n", d.size);
  if (!size) {
    Py_DECREF(type);
    return 0;
  }
  PyObject* expand = d.expandable? Py_True : Py_False;

  return Py_BuildValue("NNO", type, size, expand); //steals references, except for True/False

}

static PyObject* PyBobIoHDF5File_Describe(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"key", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* key = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &key)) return 0;

  PyObject* retval = 0;
  boost::shared_ptr<PyObject> retval_;

  try {
    const std::vector<bob::io::base::HDF5Descriptor>& dv = self->f->describe(key);
    retval = PyTuple_New(dv.size());
    retval_ = make_safe(retval);

    for (size_t k=0; k<dv.size(); ++k) {
      PyObject* entry = PyBobIo_HDF5DescriptorAsTuple(dv[k]);
      if (!entry) return 0;
      PyTuple_SET_ITEM(retval, k, entry);
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while getting description for dataset `%s' in HDF5 file `%s'", key, filename);
    return 0;
  }

  return Py_BuildValue("O", retval);
}

PyDoc_STRVAR(s_describe_str, "describe");
PyDoc_STRVAR(s_describe_doc,
"x.describe(path) -> tuple\n\
\n\
Describes a dataset type/shape, if it exists inside a file\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The dataset path to describe\n\
\n\
If a given path to an HDF5 dataset exists inside the file,\n\
return a type description of objects recorded in such a dataset,\n\
otherwise, raises an exception. The returned value type is a\n\
tuple of tuples (HDF5Type, number-of-objects, expandable)\n\
describing the capabilities if the file is read using theses\n\
formats.\n\
");

static PyObject* PyBobIoHDF5File_Unlink(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"key", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* key = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &key)) return 0;

  try {
    self->f->unlink(key);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while unlinking dataset `%s' in HDF5 file `%s'", key, filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_unlink_str, "unlink");
PyDoc_STRVAR(s_unlink_doc,
"x.unlink(key) -> None\n\
\n\
Unlinks datasets inside the file making them invisible.\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The dataset path to describe\n\
\n\
If a given path to an HDF5 dataset exists inside the file,\n\
unlinks it. Please note this will note remove the data from\n\
the file, just make it inaccessible. If you wish to cleanup,\n\
save the reacheable objects from this file to another HDF5File\n\
object using copy(), for example.\n\
");

static PyObject* PyBobIoHDF5File_Rename(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"from", "to", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* from = 0;
  const char* to = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "ss", kwlist, &from, &to)) return 0;

  try {
    self->f->rename(from, to);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while renaming dataset `%s' to `%s' in HDF5 file `%s'", from, to, filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_rename_str, "rename");
PyDoc_STRVAR(s_rename_doc,
"x.rename(from, to) -> None\n\
\n\
Renames datasets in a file\n\
\n\
Parameters:\n\
\n\
from\n\
  [str] The path to the data being renamed\n\
\n\
to\n\
  [str] The new name of the dataset\n\
\n\
");

static PyObject* PyBobIoHDF5File_Paths(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"relative", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* pyrel = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &pyrel)) return 0;

  bool relative = false;
  if (pyrel && PyObject_IsTrue(pyrel)) relative = true;

  PyObject* retval = 0;
  boost::shared_ptr<PyObject> retval_;

  try {
    std::vector<std::string> values;
    self->f->paths(values, relative);
    retval = PyTuple_New(values.size());
    if (!retval) return 0;
    retval_ = make_safe(retval);
    for (size_t i=0; i<values.size(); ++i) {
      PyTuple_SET_ITEM(retval, i, Py_BuildValue("s", values[i].c_str()));
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while reading dataset names from HDF5 file `%s'", filename);
    return 0;
  }

  return Py_BuildValue("O", retval);
}

PyDoc_STRVAR(s_keys_str, "keys");
PyDoc_STRVAR(s_paths_str, "paths");
PyDoc_STRVAR(s_paths_doc,
"x.paths([relative=False]) -> tuple\n\
\n\
Lists datasets available inside this file\n\
\n\
Parameters:\n\
\n\
relative\n\
  [bool, optional] if set to ``True``, the returned paths are\n\
  relative to the current working directory, otherwise they are\n\
  absolute.\n\
\n\
Returns all paths to datasets available inside this file, stored\n\
under the current working directory. If relative is set to ``True``,\n\
the returned paths are relative to the current working directory,\n\
otherwise they are absolute.\n\
");

static PyObject* PyBobIoHDF5File_SubGroups(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"relative", "recursive", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* pyrel = 0;
  PyObject* pyrec = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|OO", kwlist, &pyrel, &pyrec)) return 0;

  bool relative = (pyrel && PyObject_IsTrue(pyrel));
  bool recursive = (!pyrec || PyObject_IsTrue(pyrec));

  PyObject* retval = 0;

  try {
    std::vector<std::string> values;
    self->f->sub_groups(values, relative, recursive);
    retval = PyTuple_New(values.size());
    for (size_t i=0; i<values.size(); ++i) {
      PyTuple_SET_ITEM(retval, i, Py_BuildValue("s", values[i].c_str()));
    }
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while reading group names from HDF5 file `%s'", filename);
    return 0;
  }

  return retval;
}

PyDoc_STRVAR(s_sub_groups_str, "sub_groups");
PyDoc_STRVAR(s_sub_groups_doc,
"x.sub_groups([relative=False, [recursive=True]]) -> tuple\n\
\n\
Lists groups (directories) in the current file.\n\
\n\
Parameters:\n\
\n\
relative\n\
  [bool, optional] if set to ``True``, the returned sub-groups are\n\
  relative to the current working directory, otherwise they are\n\
  absolute.\n\
\n\
recursive\n\
  [bool, optional] if set to ``False``, the returned sub-groups\n\
  are only the ones in the current directory. Otherwise, recurse\n\
  down the directory structure.\n\
\n\
");

static PyObject* PyBobIoHDF5File_Xread(PyBobIoHDF5FileObject* self,
    const char* p, int descriptor, int pos) {

  const std::vector<bob::io::base::HDF5Descriptor>* D = 0;
  try {
    D = &self->f->describe(p);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while trying to describe dataset `%s' from HDF5 file `%s'", p, filename);
    return 0;
  }

  //last descriptor always contains the full readout.
  const bob::io::base::HDF5Type& type = (*D)[descriptor].type;
  const bob::io::base::HDF5Shape& shape = type.shape();

  if (shape.n() == 1 && shape[0] == 1) { //read as scalar
    try {
      switch(type.type()) {
        case bob::io::base::s:
          return Py_BuildValue("s", self->f->read<std::string>(p, pos).c_str());
        case bob::io::base::b:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<bool>(p, pos));
        case bob::io::base::i8:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<int8_t>(p, pos));
        case bob::io::base::i16:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<int16_t>(p, pos));
        case bob::io::base::i32:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<int32_t>(p, pos));
        case bob::io::base::i64:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<int64_t>(p, pos));
        case bob::io::base::u8:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<uint8_t>(p, pos));
        case bob::io::base::u16:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<uint16_t>(p, pos));
        case bob::io::base::u32:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<uint32_t>(p, pos));
        case bob::io::base::u64:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<uint64_t>(p, pos));
        case bob::io::base::f32:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<float>(p, pos));
        case bob::io::base::f64:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<double>(p, pos));
        case bob::io::base::f128:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<long double>(p, pos));
        case bob::io::base::c64:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<std::complex<float> >(p, pos));
        case bob::io::base::c128:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<std::complex<double> >(p, pos));
        case bob::io::base::c256:
          return PyBlitzArrayCxx_FromCScalar(self->f->read<std::complex<long double> >(p, pos));
        default:
          PyErr_Format(PyExc_TypeError, "unsupported HDF5 type: %s", type.str().c_str());
          return 0;
      }
    }
    catch (std::exception& e) {
      PyErr_SetString(PyExc_RuntimeError, e.what());
      return 0;
    }
    catch (...) {
      const char* filename = "<unknown>";
      try{ filename = self->f->filename().c_str(); } catch(...){}
      PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading %s scalar from dataset `%s' at position %d from HDF5 file `%s'", bob::io::base::stringize(type.type()), p, pos, filename);
      return 0;
    }
  }

  //read as an numpy array
  int type_num = PyBobIo_H5AsTypenum(type.type());
  if (type_num == NPY_NOTYPE) return 0; ///< failure

  npy_intp pyshape[NPY_MAXDIMS];
  for (size_t k=0; k<shape.n(); ++k) pyshape[k] = shape.get()[k];

  PyObject* retval = PyArray_SimpleNew(shape.n(), pyshape, type_num);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  try {
    self->f->read_buffer(p, pos, type, PyArray_DATA((PyArrayObject*)retval));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading dataset `%s' at position %d with descriptor `%s' from HDF5 file `%s'", p, pos, type.str().c_str(), filename);
    return 0;
  }

  return Py_BuildValue("O", retval);
}

static PyObject* PyBobIoHDF5File_Read(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"key", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* key = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s", kwlist, &key)) return 0;

  return PyBobIoHDF5File_Xread(self, key, 1, 0);

}

PyDoc_STRVAR(s_read_str, "read");
PyDoc_STRVAR(s_read_doc,
"x.read(key, [pos=-1]) -> numpy.ndarray\n\
\n\
Reads whole datasets from the file.\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The path to the dataset to read data from. Can be\n\
  an absolute value (starting with a leading ``'/'``) or\n\
  relative to the current working directory (``cwd``).\n\
\n\
");

static PyObject* PyBobIoHDF5File_ListRead(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"key", "pos", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* key = 0;
  Py_ssize_t pos = -1;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|n", kwlist, &key, &pos)) return 0;

  if (pos >= 0) return PyBobIoHDF5File_Xread(self, key, 0, pos);

  //otherwise returns as a list
  const std::vector<bob::io::base::HDF5Descriptor>* D = 0;
  try {
    D = &self->f->describe(key);
  }
  catch (std::exception& e) {
    PyErr_Format(PyExc_RuntimeError, "%s", e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while trying to describe dataset `%s' from HDF5 file `%s'", key, filename);
    return 0;
  }

  PyObject* retval = PyTuple_New((*D)[0].size);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  for (uint64_t k=0; k<(*D)[0].size; ++k) {
    PyObject* item = PyBobIoHDF5File_Xread(self, key, 0, k);
    if (!item) return 0;
    PyTuple_SET_ITEM(retval, k, item);
  }

  return Py_BuildValue("O", retval);

}

PyDoc_STRVAR(s_lread_str, "lread");
PyDoc_STRVAR(s_lread_doc,
"x.lread(key, [pos=-1]) -> list|numpy.ndarray\n\
\n\
Reads some contents of the dataset.\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The path to the dataset to read data from. Can be\n\
  an absolute value (starting with a leading ``'/'``) or\n\
  relative to the current working directory (``cwd``).\n\
\n\
pos\n\
  [int, optional] Returns a single object if ``pos`` >= 0,\n\
  otherwise a list by reading all objects in sequence.\n\
\n\
This method reads contents from a dataset, treating the\n\
N-dimensional dataset like a container for multiple objects\n\
with N-1 dimensions. It returns a single\n\
:py:class:`numpy.ndarray` in case ``pos`` is set to a\n\
value >= 0, or a list of arrays otherwise.\n\
");

/**
 * Sets at 't', the type of the object 'o' according to our support types.
 * Raise in case of problems. Furthermore, returns 'true' if the object is as
 * simple scalar.
 */

static void null_char_array_deleter(char*) {}

#if PY_VERSION_HEX >= 0x03000000
static void char_array_deleter(char* o) { delete[] o; }
#endif

static boost::shared_ptr<char> PyBobIo_GetString(PyObject* o) {

#if PY_VERSION_HEX < 0x03000000

  return boost::shared_ptr<char>(PyString_AsString(o), null_char_array_deleter);

#else

  if (PyBytes_Check(o)) {
    //fast way out
    return boost::shared_ptr<char>(PyBytes_AsString(o), null_char_array_deleter);
  }

  PyObject* bytes = 0;

  if (PyUnicode_Check(o)) {
    //re-encode using utf-8
    bytes = PyUnicode_AsEncodedString(o, "utf-8", "strict");
  }
  else {
    //tries coercion
    bytes = PyObject_Bytes(o);
  }
  auto bytes_ = make_safe(bytes); ///< protects acquired resource

  Py_ssize_t length = PyBytes_GET_SIZE(bytes)+1;
  char* copy = new char[length];
  std::strncpy(copy, PyBytes_AsString(bytes), length);

  return boost::shared_ptr<char>(copy, char_array_deleter);

#endif

}

static int PyBobIoHDF5File_SetStringType(bob::io::base::HDF5Type& t, PyObject* o) {
  auto value = PyBobIo_GetString(o);
  if (!value) return -1;
  t = bob::io::base::HDF5Type(value.get());
  return 0;
}

template <typename T> int PyBobIoHDF5File_SetType(bob::io::base::HDF5Type& t) {
  T v;
  t = bob::io::base::HDF5Type(v);
  return 0;
}

/**
 * A function to check for python scalars that works with numpy-1.6.x
 */
static bool PyBobIoHDF5File_IsPythonScalar(PyObject* obj) {
  return (
    PyBool_Check(obj) ||
#if PY_VERSION_HEX < 0x03000000
    PyString_Check(obj) ||
#else
    PyBytes_Check(obj) ||
#endif
    PyUnicode_Check(obj) ||
#if PY_VERSION_HEX < 0x03000000
    PyInt_Check(obj) ||
#endif
    PyLong_Check(obj) ||
    PyFloat_Check(obj) ||
    PyComplex_Check(obj)
    );
}

/**
 * Returns the type of object `op' is - a scalar (return value = 0), a
 * bob.blitzarray (return value = 1), a numpy.ndarray (return value = 2), an
 * object which is convertible to a numpy.ndarray (return value = 3) or returns
 * -1 if the object cannot be converted. No error is set on the python stack.
 *
 * If the object is convertible into a numpy.ndarray, then it is converted into
 * a numpy ndarray and the resulting object is placed in `converted'. If
 * `*converted' is set to 0 (NULL), then we don't try a conversion, returning
 * -1.
 */
static int PyBobIoHDF5File_GetObjectType(PyObject* o, bob::io::base::HDF5Type& t,
    PyObject** converted=0) {

  if (PyArray_IsScalar(o, Generic) || PyBobIoHDF5File_IsPythonScalar(o)) {

    if (PyArray_IsScalar(o, String))
      return PyBobIoHDF5File_SetStringType(t, o);

    else if (PyBool_Check(o))
      return PyBobIoHDF5File_SetType<bool>(t);

#if PY_VERSION_HEX < 0x03000000
    else if (PyString_Check(o))
      return PyBobIoHDF5File_SetStringType(t, o);

#else
    else if (PyBytes_Check(o))
      return PyBobIoHDF5File_SetStringType(t, o);

#endif
    else if (PyUnicode_Check(o))
      return PyBobIoHDF5File_SetStringType(t, o);

#if PY_VERSION_HEX < 0x03000000
    else if (PyInt_Check(o))
      return PyBobIoHDF5File_SetType<int32_t>(t);

#endif
    else if (PyLong_Check(o))
      return PyBobIoHDF5File_SetType<int64_t>(t);

    else if (PyFloat_Check(o))
      return PyBobIoHDF5File_SetType<double>(t);

    else if (PyComplex_Check(o))
      return PyBobIoHDF5File_SetType<std::complex<double> >(t);

    else if (PyArray_IsScalar(o, Bool))
      return PyBobIoHDF5File_SetType<bool>(t);

    else if (PyArray_IsScalar(o, Int8))
      return PyBobIoHDF5File_SetType<int8_t>(t);

    else if (PyArray_IsScalar(o, UInt8))
      return PyBobIoHDF5File_SetType<uint8_t>(t);

    else if (PyArray_IsScalar(o, Int16))
      return PyBobIoHDF5File_SetType<int16_t>(t);

    else if (PyArray_IsScalar(o, UInt16))
      return PyBobIoHDF5File_SetType<uint16_t>(t);

    else if (PyArray_IsScalar(o, Int32))
      return PyBobIoHDF5File_SetType<int32_t>(t);

    else if (PyArray_IsScalar(o, UInt32))
      return PyBobIoHDF5File_SetType<uint32_t>(t);

    else if (PyArray_IsScalar(o, Int64))
      return PyBobIoHDF5File_SetType<int64_t>(t);

    else if (PyArray_IsScalar(o, UInt64))
      return PyBobIoHDF5File_SetType<uint64_t>(t);

    else if (PyArray_IsScalar(o, Float))
      return PyBobIoHDF5File_SetType<float>(t);

    else if (PyArray_IsScalar(o, Double))
      return PyBobIoHDF5File_SetType<double>(t);

    else if (PyArray_IsScalar(o, LongDouble))
      return PyBobIoHDF5File_SetType<long double>(t);

    else if (PyArray_IsScalar(o, CFloat))
      return PyBobIoHDF5File_SetType<std::complex<float> >(t);

    else if (PyArray_IsScalar(o, CDouble))
      return PyBobIoHDF5File_SetType<std::complex<double> >(t);

    else if (PyArray_IsScalar(o, CLongDouble))
      return PyBobIoHDF5File_SetType<std::complex<long double> >(t);

    //if you get to this, point, it is an unsupported scalar
    return -1;

  }

  else if (PyBlitzArray_Check(o)) {

    PyBlitzArrayObject* bz = reinterpret_cast<PyBlitzArrayObject*>(o);
    bob::io::base::hdf5type h5type = PyBobIo_H5FromTypenum(bz->type_num);
    if (h5type == bob::io::base::unsupported) return -1;
    bob::io::base::HDF5Shape h5shape(bz->ndim, bz->shape);
    t = bob::io::base::HDF5Type(h5type, h5shape);
    return 1;

  }

  else if (PyArray_CheckExact(o) && PyArray_ISCARRAY_RO((PyArrayObject*)o)) {

    PyArrayObject* np = reinterpret_cast<PyArrayObject*>(o);
    bob::io::base::hdf5type h5type = PyBobIo_H5FromTypenum(PyArray_DESCR(np)->type_num);
    if (h5type == bob::io::base::unsupported) return -1;
    bob::io::base::HDF5Shape h5shape(PyArray_NDIM(np), PyArray_DIMS(np));
    t = bob::io::base::HDF5Type(h5type, h5shape);
    return 2;

  }

  else if (converted) {

    *converted = PyArray_FromAny(o, 0, 1, 0,
#if     NPY_FEATURE_VERSION >= NUMPY17_API /* NumPy C-API version >= 1.7 */
        NPY_ARRAY_CARRAY_RO,
#       else
        NPY_CARRAY_RO,
#       endif
        0);
    if (!*converted) return -1; ///< error condition

    PyArrayObject* np = reinterpret_cast<PyArrayObject*>(*converted);
    bob::io::base::hdf5type h5type = PyBobIo_H5FromTypenum(PyArray_DESCR(np)->type_num);
    if (h5type == bob::io::base::unsupported) {
      Py_CLEAR(*converted);
      return -1;
    }
    bob::io::base::HDF5Shape h5shape(PyArray_NDIM(np), PyArray_DIMS(np));
    t = bob::io::base::HDF5Type(h5type, h5shape);
    return 3;

  }

  //if you get to this, point, it is an unsupported type
  return -1;

}

template <typename T>
static PyObject* PyBobIoHDF5File_ReplaceScalar(PyBobIoHDF5FileObject* self,
    const char* path, Py_ssize_t pos, PyObject* o) {

  T value = PyBlitzArrayCxx_AsCScalar<T>(o);
  if (PyErr_Occurred()) return 0;
  self->f->replace(path, pos, value);

  Py_RETURN_NONE;

}

static PyObject* PyBobIoHDF5File_Replace(PyBobIoHDF5FileObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", "pos", "data", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* path = 0;
  Py_ssize_t pos = -1;
  PyObject* data = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "snO", kwlist, &path, &pos, &data)) return 0;

  bob::io::base::HDF5Type type;
  PyObject* converted = 0;
  int is_array = PyBobIoHDF5File_GetObjectType(data, type, &converted);
  auto converted_ = make_xsafe(converted);

  if (is_array < 0) { ///< error condition, signal
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_TypeError, "error replacing position %" PY_FORMAT_SIZE_T "d of dataset `%s' at HDF5 file `%s': no support for storing objects of type `%s' on HDF5 files", pos, path, filename, Py_TYPE(data)->tp_name);
    return 0;
  }

  try {

    if (!is_array) { //write as a scalar

      switch(type.type()) {
        case bob::io::base::s:
          {
            auto value = PyBobIo_GetString(data);
            if (!value) return 0;
            self->f->replace<std::string>(path, pos, value.get());
            Py_RETURN_NONE;
          }
        case bob::io::base::b:
          return PyBobIoHDF5File_ReplaceScalar<bool>(self, path, pos, data);
        case bob::io::base::i8:
          return PyBobIoHDF5File_ReplaceScalar<int8_t>(self, path, pos, data);
        case bob::io::base::i16:
          return PyBobIoHDF5File_ReplaceScalar<int16_t>(self, path, pos, data);
        case bob::io::base::i32:
          return PyBobIoHDF5File_ReplaceScalar<int32_t>(self, path, pos, data);
        case bob::io::base::i64:
          return PyBobIoHDF5File_ReplaceScalar<int64_t>(self, path, pos, data);
        case bob::io::base::u8:
          return PyBobIoHDF5File_ReplaceScalar<uint8_t>(self, path, pos, data);
        case bob::io::base::u16:
          return PyBobIoHDF5File_ReplaceScalar<uint16_t>(self, path, pos, data);
        case bob::io::base::u32:
          return PyBobIoHDF5File_ReplaceScalar<uint32_t>(self, path, pos, data);
        case bob::io::base::u64:
          return PyBobIoHDF5File_ReplaceScalar<uint64_t>(self, path, pos, data);
        case bob::io::base::f32:
          return PyBobIoHDF5File_ReplaceScalar<float>(self, path, pos, data);
        case bob::io::base::f64:
          return PyBobIoHDF5File_ReplaceScalar<double>(self, path, pos, data);
        case bob::io::base::f128:
          return PyBobIoHDF5File_ReplaceScalar<long double>(self, path, pos, data);
        case bob::io::base::c64:
          return PyBobIoHDF5File_ReplaceScalar<std::complex<float> >(self, path, pos, data);
        case bob::io::base::c128:
          return PyBobIoHDF5File_ReplaceScalar<std::complex<double> >(self, path, pos, data);
        case bob::io::base::c256:
          return PyBobIoHDF5File_ReplaceScalar<std::complex<long double> >(self, path, pos, data);
        default:
          break;
      }

    }

    else { //write as array

      switch (is_array) {
        case 1: //bob.blitz.array
          self->f->write_buffer(path, pos, type, ((PyBlitzArrayObject*)data)->data);
          break;

        case 2: //numpy.ndarray
          self->f->write_buffer(path, pos, type, PyArray_DATA((PyArrayObject*)data));
          break;

        case 3: //converted numpy.ndarray
          self->f->write_buffer(path, pos, type, PyArray_DATA((PyArrayObject*)converted));
          break;

        default:
          const char* filename = "<unknown>";
          try{ filename = self->f->filename().c_str(); } catch(...){}
          PyErr_Format(PyExc_NotImplementedError, "error replacing position %" PY_FORMAT_SIZE_T "d of dataset `%s' at HDF5 file `%s': HDF5 replace function is uncovered for array type %d (DEBUG ME)", pos, path, filename, is_array);
          return 0;
      }

    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot replace object in position %" PY_FORMAT_SIZE_T "d at HDF5 file `%s': unknown exception caught", pos, filename);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_replace_str, "replace");
PyDoc_STRVAR(s_replace_doc,
"x.replace(path, pos, data) -> None\n\
\n\
Modifies the value of a scalar/array in a dataset.\n\
\n\
Parameters:\n\
\n\
key\n\
  [str] The path to the dataset to read data from. Can be\n\
  an absolute value (starting with a leading ``'/'``) or\n\
  relative to the current working directory (``cwd``).\n\
\n\
pos\n\
  [int] Position, within the dataset, of the object to be\n\
  replaced. The object position on the dataset must exist,\n\
  or an exception is raised.\n\
\n\
data\n\
  [scalar|numpy.ndarray] Object to replace the value with.\n\
  This value must be compatible with the typing information\n\
  on the dataset, or an exception will be raised.\n\
\n\
");

template <typename T>
static int PyBobIoHDF5File_AppendScalar(PyBobIoHDF5FileObject* self,
    const char* path, PyObject* o) {

  T value = PyBlitzArrayCxx_AsCScalar<T>(o);
  if (PyErr_Occurred()) return 0;
  self->f->append(path, value);

  return 1;

}

static int PyBobIoHDF5File_InnerAppend(PyBobIoHDF5FileObject* self, const char* path, PyObject* data, Py_ssize_t compression) {

  bob::io::base::HDF5Type type;
  PyObject* converted = 0;
  int is_array = PyBobIoHDF5File_GetObjectType(data, type, &converted);
  auto converted_ = make_xsafe(converted);

  if (is_array < 0) { ///< error condition, signal
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_TypeError, "error appending to object `%s' of HDF5 file `%s': no support for storing objects of type `%s' on HDF5 files", path, filename, Py_TYPE(data)->tp_name);
    return 0;
  }

  try {

    if (!is_array) { //write as a scalar

      switch(type.type()) {
        case bob::io::base::s:
          {
            auto value = PyBobIo_GetString(data);
            if (!value) return 0;
            self->f->append<std::string>(path, value.get());
            return 1;
          }
        case bob::io::base::b:
          return PyBobIoHDF5File_AppendScalar<bool>(self, path, data);
        case bob::io::base::i8:
          return PyBobIoHDF5File_AppendScalar<int8_t>(self, path, data);
        case bob::io::base::i16:
          return PyBobIoHDF5File_AppendScalar<int16_t>(self, path, data);
        case bob::io::base::i32:
          return PyBobIoHDF5File_AppendScalar<int32_t>(self, path, data);
        case bob::io::base::i64:
          return PyBobIoHDF5File_AppendScalar<int64_t>(self, path, data);
        case bob::io::base::u8:
          return PyBobIoHDF5File_AppendScalar<uint8_t>(self, path, data);
        case bob::io::base::u16:
          return PyBobIoHDF5File_AppendScalar<uint16_t>(self, path, data);
        case bob::io::base::u32:
          return PyBobIoHDF5File_AppendScalar<uint32_t>(self, path, data);
        case bob::io::base::u64:
          return PyBobIoHDF5File_AppendScalar<uint64_t>(self, path, data);
        case bob::io::base::f32:
          return PyBobIoHDF5File_AppendScalar<float>(self, path, data);
        case bob::io::base::f64:
          return PyBobIoHDF5File_AppendScalar<double>(self, path, data);
        case bob::io::base::f128:
          return PyBobIoHDF5File_AppendScalar<long double>(self, path, data);
        case bob::io::base::c64:
          return PyBobIoHDF5File_AppendScalar<std::complex<float> >(self, path, data);
        case bob::io::base::c128:
          return PyBobIoHDF5File_AppendScalar<std::complex<double> >(self, path, data);
        case bob::io::base::c256:
          return PyBobIoHDF5File_AppendScalar<std::complex<long double> >(self, path, data);
        default:
          break;
      }

    }

    else { //write as array

      switch (is_array) {
        case 1: //bob.blitz.array
          if (!self->f->contains(path)) self->f->create(path, type, true, compression);
          self->f->extend_buffer(path, type, ((PyBlitzArrayObject*)data)->data);
          break;

        case 2: //numpy.ndarray
          if (!self->f->contains(path)) self->f->create(path, type, true, compression);
          self->f->extend_buffer(path, type, PyArray_DATA((PyArrayObject*)data));
          break;

        case 3: //converted numpy.ndarray
          if (!self->f->contains(path)) self->f->create(path, type, true, compression);
          self->f->extend_buffer(path, type, PyArray_DATA((PyArrayObject*)converted));
          break;

        default:{
          const char* filename = "<unknown>";
          try{ filename = self->f->filename().c_str(); } catch(...){}
          PyErr_Format(PyExc_NotImplementedError, "error appending to object `%s' at HDF5 file `%s': HDF5 replace function is uncovered for array type %d (DEBUG ME)", path, filename, is_array);
          return 0;
        }
      }

    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot append to object `%s' at HDF5 file `%s': unknown exception caught", path, filename);
    return 0;
  }

  return 1;

}

static PyObject* PyBobIoHDF5File_Append(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", "data", "compression", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  char* path = 0;
  PyObject* data = 0;
  Py_ssize_t compression = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "sO|n", kwlist, &path, &data, &compression)) return 0;

  if (compression < 0 || compression > 9) {
    PyErr_SetString(PyExc_ValueError, "compression should be set to an integer value between and including 0 and 9");
    return 0;
  }

  // special case: user passes a tuple or list of arrays or scalars to append
  if (PyTuple_Check(data) || PyList_Check(data)) {
    PyObject* iter = PyObject_GetIter(data);
    if (!iter) return 0;
    auto iter_ = make_safe(iter);
    while (PyObject* item = PyIter_Next(iter)) {
      auto item_ = make_safe(item);
      int ok = PyBobIoHDF5File_InnerAppend(self, path, item, compression);
      if (!ok) return 0;
    }
    Py_RETURN_NONE;
  }

  int ok = PyBobIoHDF5File_InnerAppend(self, path, data, compression);
  if (!ok) return 0;
  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_append_str, "append");
PyDoc_STRVAR(s_append_doc,
"x.append(path, data, [compression=0]) -> None\n\
\n\
Appends a scalar or an array to a dataset\n\
\n\
Parameters:\n\
\n\
path\n\
  [str] The path to the dataset to read data from. Can be\n\
  an absolute value (starting with a leading ``'/'``) or\n\
  relative to the current working directory (``cwd``).\n\
\n\
data\n\
  [scalar|numpy.ndarray] Object to append to the dataset.\n\
  This value must be compatible with the typing information\n\
  on the dataset, or an exception will be raised.\n\
  You can also, optionally, set this to an iterable of\n\
  scalars or arrays. This will cause this method to iterate\n\
  over the elements and add each individually.\n\
\n\
compression\n\
  This parameter is effective when appending arrays. Set this\n\
  to a number betwen 0 (default) and 9 (maximum) to compress\n\
  the contents of this dataset. This setting is only effective\n\
  if the dataset does not yet exist, otherwise, the previous\n\
  setting is respected.\n\
\n\
");

template <typename T>
static PyObject* PyBobIoHDF5File_SetScalar(PyBobIoHDF5FileObject* self,
    const char* path, PyObject* o) {

  T value = PyBlitzArrayCxx_AsCScalar<T>(o);
  if (PyErr_Occurred()) return 0;
  self->f->set(path, value);

  Py_RETURN_NONE;

}

static PyObject* PyBobIoHDF5File_Set(PyBobIoHDF5FileObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", "data", "compression", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  char* path = 0;
  PyObject* data = 0;
  Py_ssize_t compression = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "sO|n", kwlist, &path, &data, &compression)) return 0;

  if (compression < 0 || compression > 9) {
    PyErr_SetString(PyExc_ValueError, "compression should be set to an integer value between and including 0 and 9");
    return 0;
  }

  bob::io::base::HDF5Type type;
  PyObject* converted = 0;
  int is_array = PyBobIoHDF5File_GetObjectType(data, type, &converted);
  auto converted_ = make_xsafe(converted);

  if (is_array < 0) { ///< error condition, signal
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_TypeError, "error setting object `%s' of HDF5 file `%s': no support for storing objects of type `%s' on HDF5 files", path, filename, Py_TYPE(data)->tp_name);
    return 0;
  }

  try {

    if (!is_array) { //write as a scalar

      switch(type.type()) {
        case bob::io::base::s:
          {
            auto value = PyBobIo_GetString(data);
            if (!value) return 0;
            self->f->set<std::string>(path, value.get());
            Py_RETURN_NONE;
          }
          break;
        case bob::io::base::b:
          return PyBobIoHDF5File_SetScalar<bool>(self, path, data);
        case bob::io::base::i8:
          return PyBobIoHDF5File_SetScalar<int8_t>(self, path, data);
        case bob::io::base::i16:
          return PyBobIoHDF5File_SetScalar<int16_t>(self, path, data);
        case bob::io::base::i32:
          return PyBobIoHDF5File_SetScalar<int32_t>(self, path, data);
        case bob::io::base::i64:
          return PyBobIoHDF5File_SetScalar<int64_t>(self, path, data);
        case bob::io::base::u8:
          return PyBobIoHDF5File_SetScalar<uint8_t>(self, path, data);
        case bob::io::base::u16:
          return PyBobIoHDF5File_SetScalar<uint16_t>(self, path, data);
        case bob::io::base::u32:
          return PyBobIoHDF5File_SetScalar<uint32_t>(self, path, data);
        case bob::io::base::u64:
          return PyBobIoHDF5File_SetScalar<uint64_t>(self, path, data);
        case bob::io::base::f32:
          return PyBobIoHDF5File_SetScalar<float>(self, path, data);
        case bob::io::base::f64:
          return PyBobIoHDF5File_SetScalar<double>(self, path, data);
        case bob::io::base::f128:
          return PyBobIoHDF5File_SetScalar<long double>(self, path, data);
        case bob::io::base::c64:
          return PyBobIoHDF5File_SetScalar<std::complex<float> >(self, path, data);
        case bob::io::base::c128:
          return PyBobIoHDF5File_SetScalar<std::complex<double> >(self, path, data);
        case bob::io::base::c256:
          return PyBobIoHDF5File_SetScalar<std::complex<long double> >(self, path, data);
        default:
          break;
      }

    }

    else { //write as array

      switch (is_array) {
        case 1: //bob.blitz.array
          if (!self->f->contains(path)) self->f->create(path, type, false, compression);
          self->f->write_buffer(path, 0, type, ((PyBlitzArrayObject*)data)->data);
          break;

        case 2: //numpy.ndarray
          if (!self->f->contains(path)) self->f->create(path, type, false, compression);
          self->f->write_buffer(path, 0, type, PyArray_DATA((PyArrayObject*)data));
          break;

        case 3: //converted numpy.ndarray
          if (!self->f->contains(path)) self->f->create(path, type, false, compression);
          self->f->write_buffer(path, 0, type, PyArray_DATA((PyArrayObject*)converted));
          break;

        default:
          const char* filename = "<unknown>";
          try{ filename = self->f->filename().c_str(); } catch(...){}
          PyErr_Format(PyExc_NotImplementedError, "error setting object `%s' at HDF5 file `%s': HDF5 replace function is uncovered for array type %d (DEBUG ME)", path, filename, is_array);
          return 0;
      }

    }

  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot set object `%s' at HDF5 file `%s': unknown exception caught", path, filename);
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_str, "set");
PyDoc_STRVAR(s_set_doc,
"x.set(path, data, [compression=0]) -> None\n\
\n\
Sets the scalar or array at position 0 to the given value.\n\
\n\
Parameters:\n\
\n\
path\n\
  [str] The path to the dataset to read data from. Can be\n\
  an absolute value (starting with a leading ``'/'``) or\n\
  relative to the current working directory (``cwd``).\n\
\n\
data\n\
  [scalar|numpy.ndarray] Object to append to the dataset.\n\
  This value must be compatible with the typing information\n\
  on the dataset, or an exception will be raised.\n\
  You can also, optionally, set this to an iterable of\n\
  scalars or arrays. This will cause this method to iterate\n\
  over the elements and add each individually.\n\
\n\
compression\n\
  This parameter is effective when appending arrays. Set this\n\
  to a number betwen 0 (default) and 9 (maximum) to compress\n\
  the contents of this dataset. This setting is only effective\n\
  if the dataset does not yet exist, otherwise, the previous\n\
  setting is respected.\n\
\n\
This method is equivalent to checking if the scalar or array at\n\
position 0 exists and then replacing it. If the path does not\n\
exist, we append the new scalar or array.\n\
");

static PyObject* PyBobIoHDF5File_Copy(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"file", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBobIoHDF5FileObject* other = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist, &PyBobIoHDF5File_Converter, &other)) return 0;

  try {
    self->f->copy(*other->f);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "unknown exception caught while copying contents of file `%s' to file `%s'", self->f->filename().c_str(), filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_copy_str, "copy");
PyDoc_STRVAR(s_copy_doc,
"x.copy(file) -> None\n\
\n\
Copies all accessible content to another HDF5 file\n\
\n\
Parameters:\n\
\n\
file\n\
  [HDF5File] The file (already opened), to copy the contents to.\n\
  Unlinked contents of this file will not be copied. This can be\n\
  used as a method to trim unwanted content in a file.\n\
\n\
");

template <typename T> static PyObject* PyBobIoHDF5File_ReadScalarAttribute
(PyBobIoHDF5FileObject* self, const char* path, const char* name,
 const bob::io::base::HDF5Type& type) {
  T value;
  try {
    self->f->read_attribute(path, name, type, static_cast<void*>(&value));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading attribute `%s' at resource `%s' with descriptor `%s' from HDF5 file `%s'", name, path, type.str().c_str(), filename);
    return 0;
  }
  return PyBlitzArrayCxx_FromCScalar(value);
}

template <> PyObject* PyBobIoHDF5File_ReadScalarAttribute<const char*>
(PyBobIoHDF5FileObject* self, const char* path, const char* name,
 const bob::io::base::HDF5Type& type) {
  std::string retval;
  try {
    self->f->getAttribute(path, name, retval);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading string attribute `%s' at resource `%s' with descriptor `%s' from HDF5 file `%s'", name, path, type.str().c_str(), filename);
    return 0;
  }
  return Py_BuildValue("s", retval.c_str());
}

static PyObject* PyBobIoHDF5File_ReadAttribute(PyBobIoHDF5FileObject* self,
    const char* path, const char* name, const bob::io::base::HDF5Type& type) {

  //no error detection: this should be done before reaching this method

  const bob::io::base::HDF5Shape& shape = type.shape();

  if (type.type() == bob::io::base::s || (shape.n() == 1 && shape[0] == 1)) {
    //read as scalar
    switch(type.type()) {
      case bob::io::base::s:
        return PyBobIoHDF5File_ReadScalarAttribute<const char*>(self, path, name, type);
      case bob::io::base::b:
        return PyBobIoHDF5File_ReadScalarAttribute<bool>(self, path, name, type);
      case bob::io::base::i8:
        return PyBobIoHDF5File_ReadScalarAttribute<int8_t>(self, path, name, type);
      case bob::io::base::i16:
        return PyBobIoHDF5File_ReadScalarAttribute<int16_t>(self, path, name, type);
      case bob::io::base::i32:
        return PyBobIoHDF5File_ReadScalarAttribute<int32_t>(self, path, name, type);
      case bob::io::base::i64:
        return PyBobIoHDF5File_ReadScalarAttribute<int64_t>(self, path, name, type);
      case bob::io::base::u8:
        return PyBobIoHDF5File_ReadScalarAttribute<uint8_t>(self, path, name, type);
      case bob::io::base::u16:
        return PyBobIoHDF5File_ReadScalarAttribute<uint16_t>(self, path, name, type);
      case bob::io::base::u32:
        return PyBobIoHDF5File_ReadScalarAttribute<uint32_t>(self, path, name, type);
      case bob::io::base::u64:
        return PyBobIoHDF5File_ReadScalarAttribute<uint64_t>(self, path, name, type);
      case bob::io::base::f32:
        return PyBobIoHDF5File_ReadScalarAttribute<float>(self, path, name, type);
      case bob::io::base::f64:
        return PyBobIoHDF5File_ReadScalarAttribute<double>(self, path, name, type);
      case bob::io::base::f128:
        return PyBobIoHDF5File_ReadScalarAttribute<long double>(self, path, name, type);
      case bob::io::base::c64:
        return PyBobIoHDF5File_ReadScalarAttribute<std::complex<float> >(self, path, name, type);
      case bob::io::base::c128:
        return PyBobIoHDF5File_ReadScalarAttribute<std::complex<double> >(self, path, name, type);
      case bob::io::base::c256:
        return PyBobIoHDF5File_ReadScalarAttribute<std::complex<long double> >(self, path, name, type);
      default:
        break;
    }
  }

  //read as an numpy array
  int type_num = PyBobIo_H5AsTypenum(type.type());
  if (type_num == NPY_NOTYPE) return 0; ///< failure

  npy_intp pyshape[NPY_MAXDIMS];
  for (size_t k=0; k<shape.n(); ++k) pyshape[k] = shape.get()[k];

  PyObject* retval = PyArray_SimpleNew(shape.n(), pyshape, type_num);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  try {
    self->f->read_attribute(path, name, type, PyArray_DATA((PyArrayObject*)retval));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading array attribute `%s' at resource `%s' with descriptor `%s' from HDF5 file `%s'", name, path, type.str().c_str(), filename);
    return 0;
  }

  return Py_BuildValue("O", retval);
}

static PyObject* PyBobIoHDF5File_GetAttribute(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"name", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* name = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|s", kwlist, &name, &path)) return 0;

  bob::io::base::HDF5Type type;

  try {
    self->f->getAttributeType(path, name, type);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while getting type for attribute `%s' at resource `%s' from HDF5 file `%s'", name, path, filename);
    return 0;
  }

  if (type.type() == bob::io::base::unsupported) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    boost::format m("unsupported HDF5 data type detected for attribute `%s' at path `%s' of file `%s' - returning None");
    m % name % path % filename;
    PyErr_Warn(PyExc_UserWarning, m.str().c_str());
    Py_RETURN_NONE;
  }

  return PyBobIoHDF5File_ReadAttribute(self, path, name, type);
}

PyDoc_STRVAR(s_get_attribute_str, "get_attribute");
PyDoc_STRVAR(s_get_attribute_doc,
"x.get_attribute(name, [path='.']) -> scalar|numpy.ndarray\n\
\n\
Retrieve a given attribute from the named resource.\n\
\n\
Parameters:\n\
\n\
name\n\
  [str] The name of the attribute to retrieve. If the attribute\n\
  is not available, a ``RuntimeError`` is raised.\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to get an attribute from.\n\
  If the path does not exist, a ``RuntimeError`` is\n\
  raised.\n\
\n\
This method returns a single value corresponding to what is\n\
stored inside the attribute container for the given resource.\n\
If you would like to retrieve all attributes at once, use\n\
:py:meth:`bob.io.base.HDF5File.get_attributes` instead.\n\
");

static PyObject* PyBobIoHDF5File_GetAttributes(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &path)) return 0;

  std::map<std::string, bob::io::base::HDF5Type> attributes;
  self->f->listAttributes(path, attributes);
  PyObject* retval = PyDict_New();
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  for (auto k=attributes.begin(); k!=attributes.end(); ++k) {
    PyObject* item = 0;
    if (k->second.type() == bob::io::base::unsupported) {
      const char* filename = "<unknown>";
      try{ filename = self->f->filename().c_str(); } catch(...){}
      boost::format m("unsupported HDF5 data type detected for attribute `%s' at path `%s' of file `%s' - returning None");
      m % k->first % k->second.str() % filename;
      PyErr_Warn(PyExc_UserWarning, m.str().c_str());
      item = Py_BuildValue("");
    }
    else item = PyBobIoHDF5File_ReadAttribute(self, path, k->first.c_str(), k->second);

    if (!item) return 0;
    auto item_ = make_safe(item);

    if (PyDict_SetItemString(retval, k->first.c_str(), item) != 0) return 0;
  }

  return Py_BuildValue("O", retval);

}

PyDoc_STRVAR(s_get_attributes_str, "get_attributes");
PyDoc_STRVAR(s_get_attributes_doc,
"x.get_attributes([path='.']) -> dict\n\
\n\
All attributes of the given path organized in dictionary\n\
\n\
Parameters:\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to get all attributes from.\n\
  If the path does not exist, a ``RuntimeError`` is\n\
  raised.\n\
\n\
Attributes are returned in a dictionary in which each key\n\
corresponds to the attribute name and each value corresponds\n\
to the value stored inside the HDF5 file. To retrieve only\n\
a specific attribute, use :py:meth:`bob.io.base.HDF5File.get_attribute`.\n\
");

template <typename T> PyObject* PyBobIoHDF5File_WriteScalarAttribute
(PyBobIoHDF5FileObject* self, const char* path, const char* name,
 const bob::io::base::HDF5Type& type, PyObject* o) {

  T value = PyBlitzArrayCxx_AsCScalar<T>(o);
  if (PyErr_Occurred()) return 0;

  try {
    self->f->write_attribute(path, name, type, static_cast<void*>(&value));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while writing attribute `%s' at resource `%s' with descriptor `%s' at HDF5 file `%s'", name, path, type.str().c_str(), filename);
    return 0;
  }

  Py_RETURN_NONE;

}

template <> PyObject* PyBobIoHDF5File_WriteScalarAttribute<const char*>
(PyBobIoHDF5FileObject* self, const char* path, const char* name,
 const bob::io::base::HDF5Type& type, PyObject* o) {

  auto value = PyBobIo_GetString(o);
  if (!value) return 0;

  try {
    self->f->write_attribute(path, name, type, static_cast<const void*>(value.get()));
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "caught unknown exception while writing string attribute `%s' at resource `%s' with descriptor `%s' at HDF5 file `%s'", name, path, type.str().c_str(), filename);
    return 0;
  }

  Py_RETURN_NONE;

}

static PyObject* PyBobIoHDF5File_WriteAttribute(PyBobIoHDF5FileObject* self,
    const char* path, const char* name, const bob::io::base::HDF5Type& type,
    PyObject* o, int is_array, PyObject* converted) {

  //no error detection: this should be done before reaching this method

  if (!is_array) { //write as a scalar
    switch(type.type()) {
      case bob::io::base::s:
        return PyBobIoHDF5File_WriteScalarAttribute<const char*>(self, path, name, type, o);
      case bob::io::base::b:
        return PyBobIoHDF5File_WriteScalarAttribute<bool>(self, path, name, type, o);
      case bob::io::base::i8:
        return PyBobIoHDF5File_WriteScalarAttribute<int8_t>(self, path, name, type, o);
      case bob::io::base::i16:
        return PyBobIoHDF5File_WriteScalarAttribute<int16_t>(self, path, name, type, o);
      case bob::io::base::i32:
        return PyBobIoHDF5File_WriteScalarAttribute<int32_t>(self, path, name, type, o);
      case bob::io::base::i64:
        return PyBobIoHDF5File_WriteScalarAttribute<int64_t>(self, path, name, type, o);
      case bob::io::base::u8:
        return PyBobIoHDF5File_WriteScalarAttribute<uint8_t>(self, path, name, type, o);
      case bob::io::base::u16:
        return PyBobIoHDF5File_WriteScalarAttribute<uint16_t>(self, path, name, type, o);
      case bob::io::base::u32:
        return PyBobIoHDF5File_WriteScalarAttribute<uint32_t>(self, path, name, type, o);
      case bob::io::base::u64:
        return PyBobIoHDF5File_WriteScalarAttribute<uint64_t>(self, path, name, type, o);
      case bob::io::base::f32:
        return PyBobIoHDF5File_WriteScalarAttribute<float>(self, path, name, type, o);
      case bob::io::base::f64:
        return PyBobIoHDF5File_WriteScalarAttribute<double>(self, path, name, type, o);
      case bob::io::base::f128:
        return PyBobIoHDF5File_WriteScalarAttribute<long double>(self, path, name, type, o);
      case bob::io::base::c64:
        return PyBobIoHDF5File_WriteScalarAttribute<std::complex<float> >(self, path, name, type, o);
      case bob::io::base::c128:
        return PyBobIoHDF5File_WriteScalarAttribute<std::complex<double> >(self, path, name, type, o);
      case bob::io::base::c256:
        return PyBobIoHDF5File_WriteScalarAttribute<std::complex<long double> >(self, path, name, type, o);
      default:
        break;
    }
  }

  else { //write as an numpy array

    try {
      switch (is_array) {

        case 1: //bob.blitz.array
          self->f->write_attribute(path, name, type, ((PyBlitzArrayObject*)o)->data);
          break;

        case 2: //numpy.ndarray
          self->f->write_attribute(path, name, type, PyArray_DATA((PyArrayObject*)o));
          break;

        case 3: //converted numpy.ndarray
          self->f->write_attribute(path, name, type, PyArray_DATA((PyArrayObject*)converted));
          break;

        default:{
          const char* filename = "<unknown>";
          try{ filename = self->f->filename().c_str(); } catch(...){}
          PyErr_Format(PyExc_NotImplementedError, "error setting attribute `%s' at resource `%s' of HDF5 file `%s': HDF5 attribute setting function is uncovered for array type %d (DEBUG ME)", name, path, filename, is_array);
          return 0;
        }
      }
    }
    catch (std::exception& e) {
      PyErr_SetString(PyExc_RuntimeError, e.what());
      return 0;
    }
    catch (...) {
      const char* filename = "<unknown>";
      try{ filename = self->f->filename().c_str(); } catch(...){}
      PyErr_Format(PyExc_RuntimeError, "caught unknown exception while writing array attribute `%s' at resource `%s' with descriptor `%s' at HDF5 file `%s'", name, path, type.str().c_str(), filename);
      return 0;
    }

  }

  Py_RETURN_NONE;

}

static PyObject* PyBobIoHDF5File_SetAttribute(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"name", "value", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* name = 0;
  PyObject* value = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "sO|s", kwlist, &name, &value, &path)) return 0;

  bob::io::base::HDF5Type type;
  PyObject* converted = 0;
  int is_array = PyBobIoHDF5File_GetObjectType(value, type, &converted);
  auto converted_ = make_xsafe(converted);

  if (is_array < 0) { ///< error condition, signal
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_TypeError, "error setting attribute `%s' of resource `%s' at HDF5 file `%s': no support for storing objects of type `%s' on HDF5 files", name, path, filename, Py_TYPE(value)->tp_name);
    return 0;
  }

  return PyBobIoHDF5File_WriteAttribute(self, path, name, type, value, is_array, converted);

}

PyDoc_STRVAR(s_set_attribute_str, "set_attribute");
PyDoc_STRVAR(s_set_attribute_doc,
"x.set_attribute(name, value, [path='.']) -> None\n\
\n\
Sets a given attribute at the named resource.\n\
\n\
Parameters:\n\
\n\
name\n\
  [str] The name of the attribute to set.\n\
\n\
value\n\
  [scalar|numpy.ndarray] A simple scalar to set for the given\n\
  attribute on the named resources (``path``). Only simple\n\
  scalars (booleans, integers, floats and complex numbers) and\n\
  arrays of those are supported at the time being. You can use\n\
  :py:mod:`numpy` scalars to set values with arbitrary\n\
  precision (e.g. :py:class:`numpy.uint8`).\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to set an attribute at.\n\
\n\
.. warning::\n\
\n\
   Attributes in HDF5 files are supposed to be small containers or\n\
   simple scalars that provide extra information about the data\n\
   stored on the main resource (dataset or group|directory).\n\
   Attributes cannot be retrieved in chunks, contrary to data in\n\
   datasets.\n\
   \n\
   Currently, *no limitations* for the size of values stored on\n\
   attributes is imposed.\n\
\n\
");

static PyObject* PyBobIoHDF5File_SetAttributes(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"attrs", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* attrs = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O|s", kwlist, &attrs, &path)) return 0;

  if (!PyDict_Check(attrs)) {
    PyErr_SetString(PyExc_TypeError, "parameter `attrs' should be a dictionary where keys are strings and values are the attribute values");
    return 0;
  }

  PyObject *key, *value;
  Py_ssize_t pos = 0;
  while (PyDict_Next(attrs, &pos, &key, &value)) {
    bob::io::base::HDF5Type type;
    PyObject* converted = 0;

    auto name = PyBobIo_GetString(key);
    if (!name) return 0;

    int is_array = PyBobIoHDF5File_GetObjectType(value, type, &converted);
    auto converted_ = make_xsafe(converted);

    if (is_array < 0) { ///< error condition, signal
      const char* filename = "<unknown>";
      try{ filename = self->f->filename().c_str(); } catch(...){}
      PyErr_Format(PyExc_TypeError, "error setting attribute `%s' of resource `%s' at HDF5 file `%s': no support for storing objects of type `%s' on HDF5 files", name.get(), path, filename, Py_TYPE(value)->tp_name);
      return 0;
    }

    PyObject* retval = PyBobIoHDF5File_WriteAttribute(self, path, name.get(), type, value, is_array, converted);
    if (!retval) return 0;
    Py_DECREF(retval);

  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_set_attributes_str, "set_attributes");
PyDoc_STRVAR(s_set_attributes_doc,
"x.set_attributes(attrs, [path='.']) -> None\n\
\n\
Sets attributes in a given (existing) path using a dictionary\n\
\n\
Parameters:\n\
\n\
attrs\n\
  [dict] A python dictionary containing pairs of strings and\n\
  values. Each value in the dictionary should be simple scalars\n\
  (booleans, integers, floats and complex numbers) or arrays of\n\
  those are supported at the time being. You can use\n\
  :py:mod:`numpy` scalars to set values with arbitrary precision\n\
  (e.g. :py:class:`numpy.uint8`).\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to set attributes at.\n\
\n\
.. warning::\n\
\n\
   Attributes in HDF5 files are supposed to be small containers or\n\
   simple scalars that provide extra information about the data\n\
   stored on the main resource (dataset or group|directory).\n\
   Attributes cannot be retrieved in chunks, contrary to data in\n\
   datasets.\n\
   \n\
   Currently, *no limitations* for the size of values stored on\n\
   attributes is imposed.\n\
\n\
");

static PyObject* PyBobIoHDF5File_DelAttribute(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"name", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* name = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|s", kwlist, &name, &path)) return 0;

  try {
    self->f->deleteAttribute(path, name);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot delete attribute `%s' at resource `%s' of HDF5 file `%s': unknown exception caught", name, path, filename);
    return 0;
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_del_attribute_str, "del_attribute");
PyDoc_STRVAR(s_del_attribute_doc,
"x.del_attribute(name, [path='.']) -> None\n\
\n\
Removes a given attribute at the named resource.\n\
\n\
Parameters:\n\
\n\
name\n\
  [str] The name of the attribute to delete. A\n\
  ``RuntimeError`` is raised if the attribute does\n\
  not exist.\n\
\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to set an attribute at.\n\
  If the path does not exist, a ``RuntimeError`` is\n\
  raised.\n\
\n\
");

static PyObject* PyBobIoHDF5File_DelAttributes(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"attrs", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* attrs = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|Os", kwlist, &attrs, &path)) return 0;

  if (attrs && !PyIter_Check(attrs)) {
    PyErr_SetString(PyExc_TypeError, "parameter `attrs', if set, must be an iterable of strings");
    return 0;
  }

  if (attrs) {
    PyObject* iter = PyObject_GetIter(attrs);
    if (!iter) return 0;
    auto iter_ = make_safe(iter);
    while (PyObject* item = PyIter_Next(iter)) {
      auto item_ = make_safe(item);
      auto name = PyBobIo_GetString(item);
      if (!name) return 0;
      try {
        self->f->deleteAttribute(path, name.get());
      }
      catch (std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return 0;
      }
      catch (...) {
        const char* filename = "<unknown>";
        try{ filename = self->f->filename().c_str(); } catch(...){}
        PyErr_Format(PyExc_RuntimeError, "cannot delete attribute `%s' at resource `%s' of HDF5 file `%s': unknown exception caught", name.get(), path, filename);
        return 0;
      }
    }
    Py_RETURN_NONE;
  }

  //else, find the attributes and remove all of them
  std::map<std::string, bob::io::base::HDF5Type> attributes;
  try {
    self->f->listAttributes(path, attributes);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot list attributes at resource `%s' of HDF5 file `%s': unknown exception caught", path, filename);
    return 0;
  }
  for (auto k=attributes.begin(); k!=attributes.end(); ++k) {
    try {
      self->f->deleteAttribute(path, k->first);
    }
    catch (std::exception& e) {
      PyErr_SetString(PyExc_RuntimeError, e.what());
      return 0;
    }
    catch (...) {
      const char* filename = "<unknown>";
      try{ filename = self->f->filename().c_str(); } catch(...){}
      PyErr_Format(PyExc_RuntimeError, "cannot delete attribute `%s' at resource `%s' of HDF5 file `%s': unknown exception caught", k->first.c_str(), path, filename);
      return 0;
    }
  }

  Py_RETURN_NONE;
}

PyDoc_STRVAR(s_del_attributes_str, "del_attributes");
PyDoc_STRVAR(s_del_attributes_doc,
"x.del_attributes([attrs=None, [path='.']]) -> None\n\
\n\
Removes attributes in a given (existing) path\n\
\n\
Parameters:\n\
\n\
attrs\n\
  [list] An iterable containing the names of the attributes to\n\
  be removed. If not given or set to ``None``, then\n\
  remove all attributes at the named resource.\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to set attributes at.\n\
  If the path does not exist, a ``RuntimeError`` is\n\
  raised.\n\
\n\
");

static PyObject* PyBobIoHDF5File_HasAttribute(PyBobIoHDF5FileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"name", "path", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  const char* name = 0;
  const char* path = ".";
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "s|s", kwlist, &name, &path)) return 0;

  try {
    if (self->f->hasAttribute(path, name)) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot verify existence of attribute `%s' at resource `%s' of HDF5 file `%s': unknown exception caught", name, path, filename);
    return 0;
  }
}

PyDoc_STRVAR(s_has_attribute_str, "has_attribute");
PyDoc_STRVAR(s_has_attribute_doc,
"x.has_attribute(name, [path='.']) -> bool\n\
\n\
Checks existence of a given attribute at the named resource.\n\
\n\
Parameters:\n\
\n\
name\n\
  [str] The name of the attribute to check.\n\
\n\
\n\
path\n\
  [str, optional] The path leading to the resource (dataset or\n\
  group|directory) you would like to set an attribute at.\n\
  If the path does not exist, a ``RuntimeError`` is\n\
  raised.\n\
\n\
");

static PyMethodDef PyBobIoHDF5File_Methods[] = {
  {
    s_close.name(),
    (PyCFunction)PyBobIoHDF5File_Close,
    METH_VARARGS|METH_KEYWORDS,
    s_close.doc()
  },
  {
    s_flush.name(),
    (PyCFunction)PyBobIoHDF5File_Flush,
    METH_VARARGS|METH_KEYWORDS,
    s_flush.doc()
  },
  {
    s_cd_str,
    (PyCFunction)PyBobIoHDF5File_ChangeDirectory,
    METH_VARARGS|METH_KEYWORDS,
    s_cd_doc,
  },
  {
    s_has_group_str,
    (PyCFunction)PyBobIoHDF5File_HasGroup,
    METH_VARARGS|METH_KEYWORDS,
    s_has_group_doc,
  },
  {
    s_create_group_str,
    (PyCFunction)PyBobIoHDF5File_CreateGroup,
    METH_VARARGS|METH_KEYWORDS,
    s_create_group_doc,
  },
  {
    s_has_dataset_str,
    (PyCFunction)PyBobIoHDF5File_HasDataset,
    METH_VARARGS|METH_KEYWORDS,
    s_has_dataset_doc,
  },
  {
    s_has_key_str,
    (PyCFunction)PyBobIoHDF5File_HasDataset,
    METH_VARARGS|METH_KEYWORDS,
    s_has_dataset_doc,
  },
  {
    s_describe_str,
    (PyCFunction)PyBobIoHDF5File_Describe,
    METH_VARARGS|METH_KEYWORDS,
    s_describe_doc,
  },
  {
    s_unlink_str,
    (PyCFunction)PyBobIoHDF5File_Unlink,
    METH_VARARGS|METH_KEYWORDS,
    s_unlink_doc,
  },
  {
    s_rename_str,
    (PyCFunction)PyBobIoHDF5File_Rename,
    METH_VARARGS|METH_KEYWORDS,
    s_rename_doc,
  },
  {
    s_paths_str,
    (PyCFunction)PyBobIoHDF5File_Paths,
    METH_VARARGS|METH_KEYWORDS,
    s_paths_doc,
  },
  {
    s_keys_str,
    (PyCFunction)PyBobIoHDF5File_Paths,
    METH_VARARGS|METH_KEYWORDS,
    s_paths_doc,
  },
  {
    s_sub_groups_str,
    (PyCFunction)PyBobIoHDF5File_SubGroups,
    METH_VARARGS|METH_KEYWORDS,
    s_sub_groups_doc,
  },
  {
    s_read_str,
    (PyCFunction)PyBobIoHDF5File_Read,
    METH_VARARGS|METH_KEYWORDS,
    s_read_doc,
  },
  {
    "get",
    (PyCFunction)PyBobIoHDF5File_Read,
    METH_VARARGS|METH_KEYWORDS,
    s_read_doc,
  },
  {
    s_lread_str,
    (PyCFunction)PyBobIoHDF5File_ListRead,
    METH_VARARGS|METH_KEYWORDS,
    s_lread_doc,
  },
  {
    s_replace_str,
    (PyCFunction)PyBobIoHDF5File_Replace,
    METH_VARARGS|METH_KEYWORDS,
    s_replace_doc,
  },
  {
    s_append_str,
    (PyCFunction)PyBobIoHDF5File_Append,
    METH_VARARGS|METH_KEYWORDS,
    s_append_doc,
  },
  {
    s_set_str,
    (PyCFunction)PyBobIoHDF5File_Set,
    METH_VARARGS|METH_KEYWORDS,
    s_set_doc,
  },
  {
    "write",
    (PyCFunction)PyBobIoHDF5File_Set,
    METH_VARARGS|METH_KEYWORDS,
    s_set_doc,
  },
  {
    s_copy_str,
    (PyCFunction)PyBobIoHDF5File_Copy,
    METH_VARARGS|METH_KEYWORDS,
    s_copy_doc,
  },
  {
    s_get_attribute_str,
    (PyCFunction)PyBobIoHDF5File_GetAttribute,
    METH_VARARGS|METH_KEYWORDS,
    s_get_attribute_doc,
  },
  {
    s_get_attributes_str,
    (PyCFunction)PyBobIoHDF5File_GetAttributes,
    METH_VARARGS|METH_KEYWORDS,
    s_get_attributes_doc,
  },
  {
    s_set_attribute_str,
    (PyCFunction)PyBobIoHDF5File_SetAttribute,
    METH_VARARGS|METH_KEYWORDS,
    s_set_attribute_doc,
  },
  {
    s_set_attributes_str,
    (PyCFunction)PyBobIoHDF5File_SetAttributes,
    METH_VARARGS|METH_KEYWORDS,
    s_set_attributes_doc,
  },
  {
    s_del_attribute_str,
    (PyCFunction)PyBobIoHDF5File_DelAttribute,
    METH_VARARGS|METH_KEYWORDS,
    s_del_attribute_doc,
  },
  {
    s_del_attributes_str,
    (PyCFunction)PyBobIoHDF5File_DelAttributes,
    METH_VARARGS|METH_KEYWORDS,
    s_del_attributes_doc,
  },
  {
    s_has_attribute_str,
    (PyCFunction)PyBobIoHDF5File_HasAttribute,
    METH_VARARGS|METH_KEYWORDS,
    s_has_attribute_doc,
  },
  {0}  /* Sentinel */
};

static PyObject* PyBobIoHDF5File_Cwd(PyBobIoHDF5FileObject* self) {
  try{
    return Py_BuildValue("s", self->f->cwd().c_str());
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot access 'cwd' in HDF5 file `%s': unknown exception caught", filename);
    return 0;
  }
}

PyDoc_STRVAR(s_cwd_str, "cwd");
PyDoc_STRVAR(s_cwd_doc,
"The current working directory set on the file"
);

static PyObject* PyBobIoHDF5File_Filename(PyBobIoHDF5FileObject* self) {
  try{
    return Py_BuildValue("s", self->f->filename().c_str());
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot access 'filename' in HDF5 file `%s': unknown exception caught", filename);
    return 0;
  }
}

static auto s_filename = bob::extension::VariableDoc(
  "filename",
  "str",
  "The name (and path) of the underlying file on hard disk"
);

static PyObject* PyBobIoHDF5File_Writable(PyBobIoHDF5FileObject* self) {
  try{
    return Py_BuildValue("b", self->f->writable());
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    const char* filename = "<unknown>";
    try{ filename = self->f->filename().c_str(); } catch(...){}
    PyErr_Format(PyExc_RuntimeError, "cannot access 'writable' in HDF5 file `%s': unknown exception caught", filename);
    return 0;
  }
}

static auto s_writable = bob::extension::VariableDoc(
  "writable",
  "bool",
  "Has this file been opened in writable mode?"
);

static PyGetSetDef PyBobIoHDF5File_getseters[] = {
    {
      s_cwd_str,
      (getter)PyBobIoHDF5File_Cwd,
      0,
      s_cwd_doc,
      0,
    },
    {
      s_filename.name(),
      (getter)PyBobIoHDF5File_Filename,
      0,
      s_filename.doc(),
      0,
    },
    {
      s_writable.name(),
      (getter)PyBobIoHDF5File_Writable,
      0,
      s_writable.doc(),
      0,
    },
    {0}  /* Sentinel */
};

PyTypeObject PyBobIoHDF5File_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_hdf5file_str,                             /*tp_name*/
    sizeof(PyBobIoHDF5FileObject),              /*tp_basicsize*/
    0,                                          /*tp_itemsize*/
    (destructor)PyBobIoHDF5File_Delete,         /*tp_dealloc*/
    0,                                          /*tp_print*/
    0,                                          /*tp_getattr*/
    0,                                          /*tp_setattr*/
    0,                                          /*tp_compare*/
    (reprfunc)PyBobIoHDF5File_Repr,             /*tp_repr*/
    0,                                          /*tp_as_number*/
    0,                                          /*tp_as_sequence*/
    0, //&PyBobIoHDF5File_Mapping,                   /*tp_as_mapping*/
    0,                                          /*tp_hash */
    0,                                          /*tp_call*/
    (reprfunc)PyBobIoHDF5File_Repr,             /*tp_str*/
    0,                                          /*tp_getattro*/
    0,                                          /*tp_setattro*/
    0,                                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags*/
    s_hdf5file_doc,                             /* tp_doc */
    0,		                                      /* tp_traverse */
    0,		                                      /* tp_clear */
    0,                                          /* tp_richcompare */
    0,		                                      /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,		                                      /* tp_iternext */
    PyBobIoHDF5File_Methods,                    /* tp_methods */
    0,                                          /* tp_members */
    PyBobIoHDF5File_getseters,                  /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    (initproc)PyBobIoHDF5File_Init,             /* tp_init */
    0,                                          /* tp_alloc */
    PyBobIoHDF5File_New,                        /* tp_new */
};
