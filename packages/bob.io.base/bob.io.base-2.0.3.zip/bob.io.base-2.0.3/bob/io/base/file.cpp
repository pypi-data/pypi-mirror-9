/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Tue  5 Nov 11:16:09 2013
 *
 * @brief Bindings to bob::io::base::File
 */

#define BOB_IO_BASE_MODULE
#include "bobskin.h"
#include <bob.io.base/api.h>
#include <numpy/arrayobject.h>
#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <stdexcept>

#include <bob.io.base/CodecRegistry.h>
#include <bob.io.base/utils.h>

#define FILETYPE_NAME "File"
PyDoc_STRVAR(s_file_str, BOB_EXT_MODULE_PREFIX "." FILETYPE_NAME);

PyDoc_STRVAR(s_file_doc,
"File(filename, [mode='r', [pretend_extension='']]) -> new bob::io::base::File\n\
\n\
Use this object to read and write data into files.\n\
\n\
Constructor parameters:\n\
\n\
filename\n\
  [str] The file path to the file you want to open\n\
\n\
mode\n\
  [str] A single character (one of ``'r'``, ``'w'``, ``'a'``),\n\
  indicating if you'd like to read, write or append into the file.\n\
  If you choose ``'w'`` and the file already exists, it will be\n\
  truncated.By default, the opening mode is read-only (``'r'``).\n\
\n\
pretend_extension\n\
  [str, optional] Normally we read the file matching the extension\n\
  to one of the available codecs installed with the present release\n\
  of Bob. If you set this parameter though, we will read the file\n\
  as it had a given extension. The value should start with a ``'.'``.\n\
  For example ``'.hdf5'``, to make the file be treated like an HDF5\n\
  file.\n\
\n\
"
);

/* How to create a new PyBobIoFileObject */
static PyObject* PyBobIoFile_New(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIoFileObject* self = (PyBobIoFileObject*)type->tp_alloc(type, 0);

  self->f.reset();

  return reinterpret_cast<PyObject*>(self);
}

static void PyBobIoFile_Delete (PyBobIoFileObject* o) {

  o->f.reset();
  Py_TYPE(o)->tp_free((PyObject*)o);

}

int PyBobIo_FilenameConverter (PyObject* o, PyObject** b) {
#if PY_VERSION_HEX >= 0x03020000
  if (!PyUnicode_FSConverter(o, b)) return 0;
#else
  if (PyUnicode_Check(o)) {
    *b = PyUnicode_AsEncodedString(o, Py_FileSystemDefaultEncoding, "strict");
  }
  else {
#if PY_VERSION_HEX >= 0x03000000
    *b = PyObject_Bytes(o);
#else
    *b = PyObject_Str(o);
#endif
  }
  if (!b) return 0;
#endif
  return 1;
}

/* The __init__(self) method */
static int PyBobIoFile_Init(PyBobIoFileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"filename", "mode", "pretend_extension", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* filename = 0;
  char* pretend_extension = 0;

#if PY_VERSION_HEX >= 0x03000000
#  define MODE_CHAR "C"
  int mode = 'r';
#else
#  define MODE_CHAR "c"
  char mode = 'r';
#endif

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|" MODE_CHAR "s", kwlist,
        &PyBobIo_FilenameConverter, &filename, &mode, &pretend_extension)) return -1;

#undef MODE_CHAR

  auto filename_ = make_safe(filename);

  if (mode != 'r' && mode != 'w' && mode != 'a') {
    PyErr_Format(PyExc_ValueError, "file open mode string should have 1 element and be either 'r' (read), 'w' (write) or 'a' (append)");
    return -1;
  }

#if PY_VERSION_HEX >= 0x03000000
  const char* c_filename = PyBytes_AS_STRING(filename);
#else
  const char* c_filename = PyString_AS_STRING(filename);
#endif

  try {
    if (pretend_extension) {
      self->f = bob::io::base::open(c_filename, mode, pretend_extension);
    }
    else {
      self->f = bob::io::base::open(c_filename, mode);
    }
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

static PyObject* PyBobIoFile_Repr(PyBobIoFileObject* self) {
  return
# if PY_VERSION_HEX >= 0x03000000
  PyUnicode_FromFormat
# else
  PyString_FromFormat
# endif
  ("%s(filename='%s', codec='%s')", Py_TYPE(self)->tp_name,
   self->f->filename(), self->f->name());
}

static PyObject* PyBobIoFile_Filename(PyBobIoFileObject* self) {
  return Py_BuildValue("s", self->f->filename());
}

static PyObject* PyBobIoFile_CodecName(PyBobIoFileObject* self) {
  return Py_BuildValue("s", self->f->name());
}

PyDoc_STRVAR(s_filename_str, "filename");
PyDoc_STRVAR(s_filename_doc,
"The path to the file being read/written"
);

PyDoc_STRVAR(s_codec_name_str, "codec_name");
PyDoc_STRVAR(s_codec_name_doc,
"Name of the File class implementation -- available for\n\
compatibility reasons with the previous versions of this\n\
library."
);

static PyGetSetDef PyBobIoFile_getseters[] = {
    {
      s_filename_str,
      (getter)PyBobIoFile_Filename,
      0,
      s_filename_doc,
      0,
    },
    {
      s_codec_name_str,
      (getter)PyBobIoFile_CodecName,
      0,
      s_codec_name_doc,
      0,
    },
    {0}  /* Sentinel */
};

static Py_ssize_t PyBobIoFile_Len (PyBobIoFileObject* self) {
  Py_ssize_t retval = self->f->size();
  return retval;
}

int PyBobIo_AsTypenum (bob::io::base::array::ElementType type) {

  switch(type) {
    case bob::io::base::array::t_bool:
      return NPY_BOOL;
    case bob::io::base::array::t_int8:
      return NPY_INT8;
    case bob::io::base::array::t_int16:
      return NPY_INT16;
    case bob::io::base::array::t_int32:
      return NPY_INT32;
    case bob::io::base::array::t_int64:
      return NPY_INT64;
    case bob::io::base::array::t_uint8:
      return NPY_UINT8;
    case bob::io::base::array::t_uint16:
      return NPY_UINT16;
    case bob::io::base::array::t_uint32:
      return NPY_UINT32;
    case bob::io::base::array::t_uint64:
      return NPY_UINT64;
    case bob::io::base::array::t_float32:
      return NPY_FLOAT32;
    case bob::io::base::array::t_float64:
      return NPY_FLOAT64;
#ifdef NPY_FLOAT128
    case bob::io::base::array::t_float128:
      return NPY_FLOAT128;
#endif
    case bob::io::base::array::t_complex64:
      return NPY_COMPLEX64;
    case bob::io::base::array::t_complex128:
      return NPY_COMPLEX128;
#ifdef NPY_COMPLEX256
    case bob::io::base::array::t_complex256:
      return NPY_COMPLEX256;
#endif
    default:
      PyErr_Format(PyExc_TypeError, "unsupported Bob/C++ element type (%s)", bob::io::base::array::stringize(type));
  }

  return NPY_NOTYPE;

}

static PyObject* PyBobIoFile_GetIndex (PyBobIoFileObject* self, Py_ssize_t i) {

  if (i < 0) i += self->f->size(); ///< adjust for negative indexing

  if (i < 0 || (size_t)i >= self->f->size()) {
    PyErr_Format(PyExc_IndexError, "file index out of range - `%s' only contains %" PY_FORMAT_SIZE_T "d object(s)", self->f->filename(), self->f->size());
    return 0;
  }

  const bob::io::base::array::typeinfo& info = self->f->type();

  npy_intp shape[NPY_MAXDIMS];
  for (size_t k=0; k<info.nd; ++k) shape[k] = info.shape[k];

  int type_num = PyBobIo_AsTypenum(info.dtype);
  if (type_num == NPY_NOTYPE) return 0; ///< failure

  PyObject* retval = PyArray_SimpleNew(info.nd, shape, type_num);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  try {
    bobskin skin((PyArrayObject*)retval, info.dtype);
    self->f->read(skin, i);
  }
  catch (std::exception& e) {
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading object #%" PY_FORMAT_SIZE_T "d from file `%s'", i, self->f->filename());
    return 0;
  }

  return Py_BuildValue("O", retval);

}

static PyObject* PyBobIoFile_GetSlice (PyBobIoFileObject* self, PySliceObject* slice) {

  Py_ssize_t start, stop, step, slicelength;
#if PY_VERSION_HEX < 0x03000000
  if (PySlice_GetIndicesEx(slice,
#else
  if (PySlice_GetIndicesEx(reinterpret_cast<PyObject*>(slice),
#endif
        self->f->size(), &start, &stop, &step, &slicelength) < 0) return 0;

  //creates the return array
  const bob::io::base::array::typeinfo& info = self->f->type();

  int type_num = PyBobIo_AsTypenum(info.dtype);
  if (type_num == NPY_NOTYPE) return 0; ///< failure

  if (slicelength <= 0) return PyArray_SimpleNew(0, 0, type_num);

  npy_intp shape[NPY_MAXDIMS];
  shape[0] = slicelength;
  for (size_t k=0; k<info.nd; ++k) shape[k+1] = info.shape[k];

  PyObject* retval = PyArray_SimpleNew(info.nd+1, shape, type_num);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  Py_ssize_t counter = 0;
  for (auto i = start; (start<=stop)?i<stop:i>stop; i+=step) {

    //get slice to fill
    PyObject* islice = Py_BuildValue("n", counter++);
    if (!islice) return 0;
    auto islice_ = make_safe(islice);

    PyObject* item = PyObject_GetItem(retval, islice);
    if (!item) return 0;
    auto item_ = make_safe(item);

    try {
      bobskin skin((PyArrayObject*)item, info.dtype);
      self->f->read(skin, i);
    }
    catch (std::exception& e) {
      if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, e.what());
      return 0;
    }
    catch (...) {
      if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught unknown exception while reading object #%" PY_FORMAT_SIZE_T "d from file `%s'", i, self->f->filename());
      return 0;
    }

  }

  return Py_BuildValue("O", retval);

}

static PyObject* PyBobIoFile_GetItem (PyBobIoFileObject* self, PyObject* item) {
   if (PyIndex_Check(item)) {
     Py_ssize_t i = PyNumber_AsSsize_t(item, PyExc_IndexError);
     if (i == -1 && PyErr_Occurred()) return 0;
     return PyBobIoFile_GetIndex(self, i);
   }
   if (PySlice_Check(item)) {
     return PyBobIoFile_GetSlice(self, (PySliceObject*)item);
   }
   else {
     PyErr_Format(PyExc_TypeError, "File indices must be integers, not %s",
         Py_TYPE(item)->tp_name);
     return 0;
   }
}

static PyMappingMethods PyBobIoFile_Mapping = {
    (lenfunc)PyBobIoFile_Len, //mp_lenght
    (binaryfunc)PyBobIoFile_GetItem, //mp_subscript
    0 /* (objobjargproc)PyBobIoFile_SetItem //mp_ass_subscript */
};

static PyObject* PyBobIoFile_Read(PyBobIoFileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"index", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t i = PY_SSIZE_T_MIN;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|n", kwlist, &i)) return 0;

  if (i != PY_SSIZE_T_MIN) {

    // reads a specific object inside the file

    if (i < 0) i += self->f->size();

    if (i < 0 || (size_t)i >= self->f->size()) {
      PyErr_Format(PyExc_IndexError, "file index out of range - `%s' only contains %" PY_FORMAT_SIZE_T "d object(s)", self->f->filename(), self->f->size());
      return 0;
    }

    return PyBobIoFile_GetIndex(self, i);

  }

  // reads the whole file in a single shot

  const bob::io::base::array::typeinfo& info = self->f->type_all();

  npy_intp shape[NPY_MAXDIMS];
  for (size_t k=0; k<info.nd; ++k) shape[k] = info.shape[k];

  int type_num = PyBobIo_AsTypenum(info.dtype);
  if (type_num == NPY_NOTYPE) return 0; ///< failure

  PyObject* retval = PyArray_SimpleNew(info.nd, shape, type_num);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  try {
    bobskin skin((PyArrayObject*)retval, info.dtype);
    self->f->read_all(skin);
  }
  catch (std::runtime_error& e) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught std::runtime_error while reading all contents of file `%s': %s", self->f->filename(), e.what());
    return 0;
  }
  catch (std::exception& e) {
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught unknown while reading all contents of file `%s'", self->f->filename());
    return 0;
  }

  return Py_BuildValue("O", retval);

}

PyDoc_STRVAR(s_read_str, "read");
PyDoc_STRVAR(s_read_doc,
"read([index]) -> numpy.ndarray\n\
\n\
Reads a specific object in the file, or the whole file.\n\
\n\
Parameters:\n\
\n\
index\n\
  [int|long, optional] The index to the object one wishes\n\
  to retrieve from the file. Negative indexing is supported.\n\
  If not given, impliess retrieval of the whole file contents.\n\
\n\
This method reads data from the file. If you specified an\n\
index, it reads just the object indicated by the index, as\n\
you would do using the ``[]`` operator. If an index is\n\
not specified, reads the whole contents of the file into a\n\
:py:class:`numpy.ndarray`.\n\
"
);

static PyObject* PyBobIoFile_Write(PyBobIoFileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* bz = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist, &PyBlitzArray_Converter, &bz)) return 0;

  auto bz_ = make_safe(bz);

  try {
    bobskin skin(bz);
    self->f->write(skin);
  }
  catch (std::runtime_error& e) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught std::runtime_error while writing to file `%s': %s", self->f->filename(), e.what());
    return 0;
  }
  catch (std::exception& e) {
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught unknown while writing to file `%s'", self->f->filename());
    return 0;
  }

  Py_RETURN_NONE;

}

PyDoc_STRVAR(s_write_str, "write");
PyDoc_STRVAR(s_write_doc,
"write(array) -> None\n\
\n\
Writes the contents of an object to the file.\n\
\n\
Parameters:\n\
\n\
array\n\
  [array] The array to be written into the file. It can be a\n\
  :py:class:`numpy.array`, a :py:class:`bob.blitz.array` or any other object which can be\n\
  converted to either of them, as long as the number of\n\
  dimensions and scalar type are supported by\n\
  :py:class:`bob.blitz.array`.\n\
\n\
This method writes data to the file. It acts like the\n\
given array is the only piece of data that will ever be written\n\
to such a file. No more data appending may happen after a call to\n\
this method.\n\
"
);

static PyObject* PyBobIoFile_Append(PyBobIoFileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"array", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* bz = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist, &PyBlitzArray_Converter, &bz)) return 0;
  auto bz_ = make_safe(bz);
  Py_ssize_t pos = -1;

  try {
    bobskin skin(bz);
    pos = self->f->append(skin);
  }
  catch (std::runtime_error& e) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught std::runtime_error while appending to file `%s': %s", self->f->filename(), e.what());
    return 0;
  }
  catch (std::exception& e) {
    if (!PyErr_Occurred()) PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    if (!PyErr_Occurred()) PyErr_Format(PyExc_RuntimeError, "caught unknown while appending to file `%s'", self->f->filename());
    return 0;
  }

  return Py_BuildValue("n", pos);

}

PyDoc_STRVAR(s_append_str, "append");
PyDoc_STRVAR(s_append_doc,
"append(array) -> int\n\
\n\
Adds the contents of an object to the file.\n\
\n\
Parameters:\n\
\n\
array\n\
  [array] The array to be added into the file. It can be a\n\
  :py:class:`numpy.ndarray`, a :py:class`bob.blitz.array` or any other object which can be\n\
  converted to either of them, as long as the number of\n\
  dimensions and scalar type are supported by\n\
  :py:class:`bob.blitz.array`.\n\
\n\
This method appends data to the file. If the file does not\n\
exist, creates a new file, else, makes sure that the inserted\n\
array respects the previously set file structure.\n\
\n\
Returns the current position of the newly written array.\n\
"
);

PyObject* PyBobIo_TypeInfoAsTuple (const bob::io::base::array::typeinfo& ti) {

  int type_num = PyBobIo_AsTypenum(ti.dtype);
  if (type_num == NPY_NOTYPE) return 0;

  PyObject* retval = Py_BuildValue("NNN",
      reinterpret_cast<PyObject*>(PyArray_DescrFromType(type_num)),
      PyTuple_New(ti.nd), //shape
      PyTuple_New(ti.nd)  //strides
      );
  if (!retval) return 0;

  PyObject* shape = PyTuple_GET_ITEM(retval, 1);
  PyObject* stride = PyTuple_GET_ITEM(retval, 2);
  for (Py_ssize_t i=0; (size_t)i<ti.nd; ++i) {
    PyTuple_SET_ITEM(shape, i, Py_BuildValue("n", ti.shape[i]));
    PyTuple_SET_ITEM(stride, i, Py_BuildValue("n", ti.stride[i]));
  }

  return retval;

}

static PyObject* PyBobIoFile_Describe(PyBobIoFileObject* self, PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"all", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* all = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &all)) return 0;

  const bob::io::base::array::typeinfo* info = 0;
  if (all && PyObject_IsTrue(all)) info = &self->f->type_all();
  else info = &self->f->type();

  /* Now return type description and tuples with shape and strides */
  return PyBobIo_TypeInfoAsTuple(*info);
}

PyDoc_STRVAR(s_describe_str, "describe");
PyDoc_STRVAR(s_describe_doc,
"describe([all]) -> tuple\n\
\n\
Returns a description (dtype, shape, stride) of data at the file.\n\
\n\
Parameters:\n\
\n\
all\n\
  [bool] If set, return the shape and strides for reading\n\
  the whole file contents in one go.\n\
\n\
");

static PyMethodDef PyBobIoFile_Methods[] = {
    {
      s_read_str,
      (PyCFunction)PyBobIoFile_Read,
      METH_VARARGS|METH_KEYWORDS,
      s_read_doc,
    },
    {
      s_write_str,
      (PyCFunction)PyBobIoFile_Write,
      METH_VARARGS|METH_KEYWORDS,
      s_write_doc,
    },
    {
      s_append_str,
      (PyCFunction)PyBobIoFile_Append,
      METH_VARARGS|METH_KEYWORDS,
      s_append_doc,
    },
    {
      s_describe_str,
      (PyCFunction)PyBobIoFile_Describe,
      METH_VARARGS|METH_KEYWORDS,
      s_describe_doc,
    },
    {0}  /* Sentinel */
};

/**********************************
 * Definition of Iterator to File *
 **********************************/

#define FILEITERTYPE_NAME "File.iter"
PyDoc_STRVAR(s_fileiterator_str, BOB_EXT_MODULE_PREFIX "." FILEITERTYPE_NAME);

/* How to create a new PyBobIoFileIteratorObject */
static PyObject* PyBobIoFileIterator_New(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIoFileIteratorObject* self = (PyBobIoFileIteratorObject*)type->tp_alloc(type, 0);

  return reinterpret_cast<PyObject*>(self);
}

static PyObject* PyBobIoFileIterator_Iter (PyBobIoFileIteratorObject* self) {
  return reinterpret_cast<PyObject*>(self);
}

static PyObject* PyBobIoFileIterator_Next (PyBobIoFileIteratorObject* self) {
  if ((size_t)self->curpos >= self->pyfile->f->size()) {
    Py_XDECREF((PyObject*)self->pyfile);
    self->pyfile = 0;
    return 0;
  }
  return PyBobIoFile_GetIndex(self->pyfile, self->curpos++);
}

#if PY_VERSION_HEX >= 0x03000000
#  define Py_TPFLAGS_HAVE_ITER 0
#endif

PyTypeObject PyBobIoFileIterator_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_fileiterator_str,                         /* tp_name */
    sizeof(PyBobIoFileIteratorObject),          /* tp_basicsize */
    0,                                          /* tp_itemsize */
    0,                                          /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_compare */
    0,                                          /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    0,                                          /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER,  /* tp_flags */
    0,                                          /* tp_doc */
    0,		                                      /* tp_traverse */
    0,		                                      /* tp_clear */
    0,                                          /* tp_richcompare */
    0,		                                      /* tp_weaklistoffset */
    (getiterfunc)PyBobIoFileIterator_Iter,      /* tp_iter */
    (iternextfunc)PyBobIoFileIterator_Next      /* tp_iternext */
};

static PyObject* PyBobIoFile_Iter (PyBobIoFileObject* self) {
  PyBobIoFileIteratorObject* retval = (PyBobIoFileIteratorObject*)PyBobIoFileIterator_New(&PyBobIoFileIterator_Type, 0, 0);
  if (!retval) return 0;
  retval->pyfile = self;
  retval->curpos = 0;
  return Py_BuildValue("N", retval);
}

PyTypeObject PyBobIoFile_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_file_str,                                 /*tp_name*/
    sizeof(PyBobIoFileObject),                  /*tp_basicsize*/
    0,                                          /*tp_itemsize*/
    (destructor)PyBobIoFile_Delete,             /*tp_dealloc*/
    0,                                          /*tp_print*/
    0,                                          /*tp_getattr*/
    0,                                          /*tp_setattr*/
    0,                                          /*tp_compare*/
    (reprfunc)PyBobIoFile_Repr,                 /*tp_repr*/
    0,                                          /*tp_as_number*/
    0,                                          /*tp_as_sequence*/
    &PyBobIoFile_Mapping,                       /*tp_as_mapping*/
    0,                                          /*tp_hash */
    0,                                          /*tp_call*/
    (reprfunc)PyBobIoFile_Repr,                 /*tp_str*/
    0,                                          /*tp_getattro*/
    0,                                          /*tp_setattro*/
    0,                                          /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,   /*tp_flags*/
    s_file_doc,                                 /* tp_doc */
    0,		                                      /* tp_traverse */
    0,		                                      /* tp_clear */
    0,                                          /* tp_richcompare */
    0,		                                      /* tp_weaklistoffset */
    (getiterfunc)PyBobIoFile_Iter,              /* tp_iter */
    0,		                                      /* tp_iternext */
    PyBobIoFile_Methods,                        /* tp_methods */
    0,                                          /* tp_members */
    PyBobIoFile_getseters,                      /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    0,                                          /* tp_descr_get */
    0,                                          /* tp_descr_set */
    0,                                          /* tp_dictoffset */
    (initproc)PyBobIoFile_Init,                 /* tp_init */
    0,                                          /* tp_alloc */
    PyBobIoFile_New,                            /* tp_new */
};
