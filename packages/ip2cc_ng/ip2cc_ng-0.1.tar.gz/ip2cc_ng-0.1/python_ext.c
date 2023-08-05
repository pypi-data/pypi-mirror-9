#include <Python.h>
#include <structmember.h>

#include "ip2cc.h"


typedef struct {
  PyObject_HEAD
  ip2cc_tree_t tree;
  size_t value_len;
} ip2cc;

static void ip2cc_free_(ip2cc *self)
{
  ip2cc_free(self->tree);
  self->ob_type->tp_free(self);
}

static PyObject *ip2cc_new_(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
  ip2cc *self = (ip2cc *) type->tp_alloc(type, 0);
  self->value_len = 0;
  self->tree = ip2cc_make_tree();
  return (PyObject *) self;
}

static int ip2cc_init_(ip2cc *self, PyObject *args, PyObject *kwargs)
{
  self->value_len = 0;
  if (! PyArg_ParseTuple(args, "|l", &self->value_len)) {
    return -1;
  }
  if (self->value_len < 2) {
    self->value_len = 2;
  }
  return 0;
}

static PyObject *ip2cc_store_(ip2cc *self, PyObject *args)
{
  char *raw_ip, *value;
  if (! PyArg_ParseTuple(args, "ss", &raw_ip, &value)) {
    Py_RETURN_NONE;
  }
  if(ip2cc_store(self->tree, raw_ip, value)) {
    Py_RETURN_FALSE;
  }
  Py_RETURN_TRUE;
}

static PyObject *ip2cc_lookup_(ip2cc *self, PyObject *args)
{
  char *raw_ip, *value;
  if (! PyArg_ParseTuple(args, "s", &raw_ip)) {
    Py_RETURN_NONE;
  }
  value = ip2cc_lookup(self->tree, raw_ip);
  if (value) {
    return PyString_FromString(value);
  }
  Py_RETURN_NONE;
}

static PyObject *ip2cc_read_(ip2cc *self, PyObject *args)
{
  char *filename;
  if (! PyArg_ParseTuple(args, "s", &filename)) {
    PyErr_SetString(PyExc_RuntimeError, "filename argument required");
    return NULL;
  }
  FILE *fp = fopen(filename, "r");
  if (! fp) {
    PyErr_SetString(PyExc_IOError, "can not read database file");
    return NULL;
  }
  int res;
  Py_BEGIN_ALLOW_THREADS;
  res = ip2cc_read_tree(self->tree, self->value_len, fp);
  fclose(fp);
  Py_END_ALLOW_THREADS;
  if (res) {
    PyErr_SetString(PyExc_IOError, "broken database");
    return NULL;
  }
  Py_RETURN_NONE;
}

static PyObject *ip2cc_write_(ip2cc *self, PyObject *args)
{
  char *filename;
  if (! PyArg_ParseTuple(args, "s", &filename)) {
    PyErr_SetString(PyExc_RuntimeError, "filename argument required");
    return NULL;
  }
  FILE *fp = fopen(filename, "w");
  if (! fp) {
    PyErr_SetString(PyExc_IOError, "can not write database file");
    return NULL;
  }
  size_t byte_size;
  Py_BEGIN_ALLOW_THREADS;
  byte_size = ip2cc_write_tree(self->tree, self->value_len, fp);
  fclose(fp);
  Py_END_ALLOW_THREADS;
  return PyLong_FromUnsignedLong(byte_size);
}

static PyMemberDef ip2cc_members[] = {
  {"value_len", T_INT, offsetof(ip2cc, value_len), 0, "stored value length"},
  {NULL}
};

static PyMethodDef ip2cc_methods[] = {
  {"store", (PyCFunction)ip2cc_store_, METH_VARARGS, "add a value to given ip"},
  {"lookup", (PyCFunction)ip2cc_lookup_, METH_VARARGS, "lookup given ip"},
  {"read", (PyCFunction)ip2cc_read_, METH_VARARGS, "read database from file"},
  {"write", (PyCFunction)ip2cc_write_, METH_VARARGS, "write database to file"},
  {NULL}
};

static PyTypeObject ip2ccType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "ip2cc.Ip2cc",             /*tp_name*/
  sizeof(ip2cc),             /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor)ip2cc_free_,   /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
  "ip2cc objects",           /* tp_doc */
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,		                     /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  ip2cc_methods,             /* tp_methods */
  ip2cc_members,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)ip2cc_init_,     /* tp_init */
  0,                         /* tp_alloc */
  ip2cc_new_,                /* tp_new */
};

static PyMethodDef ip2ccMethods[] = {
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC initip2cc(void) {
  PyObject *mod;
  if (PyType_Ready(&ip2ccType) < 0) {
    return;
  }
  mod = Py_InitModule("ip2cc", ip2ccMethods);
  if (mod == NULL) {
    return;
  }
  Py_INCREF(&ip2ccType);
  PyModule_AddObject(mod, "Ip2cc", (PyObject *)&ip2ccType);
}
