/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 16 Oct 17:40:24 2013
 *
 * @brief Pythonic bindings to C++ constructs on bob.io::base
 */

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif

#include <bob.blitz/capi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>

#include "utils.h"
#include "file.h"
#include "bobskin.h"

PyDoc_STRVAR(s_read_varnames_str, "read_varnames");
PyDoc_STRVAR(s_read_varnames_doc,
"read_varnames(path) -> list\n\
\n\
Returns the list of variable names stored in the given Matlab(R) file.\n\
"
);

PyObject* PyBobIoMatlab_ReadVarNames(PyObject*, PyObject* o) {

  PyObject* filename = 0;

  if (!PyBobIo_FilenameConverter(o, &filename)) return 0;

  auto filename_ = make_safe(filename);

#if PY_VERSION_HEX >= 0x03000000
  const char* c_filename = PyBytes_AS_STRING(filename);
#else
  const char* c_filename = PyString_AS_STRING(filename);
#endif

  auto list = list_variables(c_filename);
  PyObject* retval = PyTuple_New(list->size());
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  int k = 0;
  for (auto it = list->begin(); it != list->end(); ++it, ++k) {
    PyObject* item = Py_BuildValue("s", it->second.first.c_str());
    if (!item) return 0;
    PyTuple_SET_ITEM(retval, k, item);
  }

  return Py_BuildValue("O", retval);

}

PyDoc_STRVAR(s_read_matrix_str, "read_matrix");
PyDoc_STRVAR(s_read_matrix_doc,
"read_matrix(path, [varname]) -> array\n\
\n\
Reads the matlab matrix with the given varname from the given file.\n\
\n\
Keyword arguments:\n\
\n\
path, string\n\
  A string containing the path (relative or absolute) to the Matlab(R)\n\
  file from which you wisht to read the matrix from.\n\
\n\
varname, string (optional)\n\
  If this parameter is not specified, the first matrix will be returned.\n\
  Otherwise, specify here one of the values returned by\n\
  :py:func:`read_varnames`\n\
\n\
");

PyObject* PyBobIoMatlab_ReadMatrix(PyObject*, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"path", "varname", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* filename = 0;
  const char* varname = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&|s", kwlist,
        &PyBobIo_FilenameConverter, &filename, &varname)) return 0;

  auto filename_ = make_safe(filename);

#if PY_VERSION_HEX >= 0x03000000
  const char* c_filename = PyBytes_AS_STRING(filename);
#else
  const char* c_filename = PyString_AS_STRING(filename);
#endif

  // open matlab file
  auto matfile = make_matfile(c_filename, MAT_ACC_RDONLY);

  if (!matfile) {
    PyErr_Format(PyExc_RuntimeError,
        "Could open the matlab file `%s'", c_filename);
    return 0;
  }

  try {
    // get type of data
    bob::io::base::array::typeinfo info;
    mat_peek(c_filename, info, varname);

    npy_intp shape[NPY_MAXDIMS];
    for (size_t k=0; k<info.nd; ++k) shape[k] = info.shape[k];

    int type_num = PyBobIo_AsTypenum(info.dtype);
    if (type_num == NPY_NOTYPE) return 0; ///< failure

    PyObject* retval = PyArray_SimpleNew(info.nd, shape, type_num);
    if (!retval) return 0;
    auto retval_ = make_safe(retval);

    bobskin skin((PyArrayObject*)retval, info.dtype);
    read_array(matfile, skin, varname);

    return Py_BuildValue("O", retval);
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot read contents of variable `%s' at matlab file `%s'", varname, c_filename);
    return 0;
  }

}

static PyMethodDef module_methods[] = {
  {
    s_read_varnames_str,
    (PyCFunction)PyBobIoMatlab_ReadVarNames,
    METH_O,
    s_read_varnames_doc,
  },
  {
    s_read_matrix_str,
    (PyCFunction)PyBobIoMatlab_ReadMatrix,
    METH_VARARGS|METH_KEYWORDS,
    s_read_matrix_doc,
  },
  {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Matlab(R) I/O support for Bob");

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

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m);

  /* register some constants */
  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0) return 0;

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

  /* activates matlab plugin */
  if (!PyBobIoCodec_Register(".mat", "Matlab binary files (v4 and superior)", &make_file)) {
    PyErr_Print();
    //do not return 0, or we may crash badly
  }

  return Py_BuildValue("O", m);

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
