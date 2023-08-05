/*
    Multipack project.
    This file is generated by setmodules.py. Do not modify it.
 */
#include "minpack.h"
static PyObject *minpack_error;
#include "__minpack.h"
static struct PyMethodDef minpack_module_methods[] = {
{"_hybrd", minpack_hybrd, METH_VARARGS, doc_hybrd},
{"_hybrj", minpack_hybrj, METH_VARARGS, doc_hybrj},
{"_lmdif", minpack_lmdif, METH_VARARGS, doc_lmdif},
{"_lmder", minpack_lmder, METH_VARARGS, doc_lmder},
{"_chkder", minpack_chkder, METH_VARARGS, doc_chkder},
{NULL,		NULL, 0, NULL}
};

#if PY_VERSION_HEX >= 0x03000000
static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_minpack",
    NULL,
    -1,
    minpack_module_methods,
    NULL,
    NULL,
    NULL,
    NULL
};
PyObject *PyInit__minpack(void)
{
    PyObject *m, *d, *s;

    m = PyModule_Create(&moduledef);
    import_array();

    d = PyModule_GetDict(m);

    s = PyUnicode_FromString(" 1.10 ");
    PyDict_SetItemString(d, "__version__", s);
    Py_DECREF(s);
    minpack_error = PyErr_NewException ("minpack.error", NULL, NULL);
    PyDict_SetItemString(d, "error", minpack_error);
    if (PyErr_Occurred())
        Py_FatalError("can't initialize module minpack");

    return m;
}
#else
PyMODINIT_FUNC init_minpack(void) {
  PyObject *m, *d, *s;
  m = Py_InitModule("_minpack", minpack_module_methods);
  import_array();
  d = PyModule_GetDict(m);

  s = PyString_FromString(" 1.10 ");
  PyDict_SetItemString(d, "__version__", s);
  Py_DECREF(s);
  minpack_error = PyErr_NewException ("minpack.error", NULL, NULL);
  PyDict_SetItemString(d, "error", minpack_error);
  if (PyErr_Occurred())
    Py_FatalError("can't initialize module minpack");
}
#endif        
