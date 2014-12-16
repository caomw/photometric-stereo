#include <mve/view.h>
#include <Python.h>
#include <structmember.h>

struct ViewObj {
  PyObject_HEAD
  mve::View::Ptr thisptr;
};

static PyMemberDef View_members[] = {
  { NULL }
};

static PyMethodDef View_methods[] = {
  {NULL, NULL, 0, NULL}
};

static int View_init(ViewObj *self, PyObject *args, PyObject *keywords)
{
  self->thisptr = mve::View::create();
  return 0;
}

static void View_dealloc(ViewObj *self)
{
  self->thisptr.reset();
}

static PyTypeObject ViewType = {
  PyObject_HEAD_INIT(NULL)
  0, // ob_size
  "mve.core.View", // tp_name
  sizeof(ViewObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)View_dealloc, // tp_dealloc
  0, // tp_print
  0, // tp_getattr
  0, // tp_setattr
  0, // tp_compare
  0, // tp_repr
  0, // tp_as_number
  0, // tp_as_sequence
  0, // tp_as_mapping
  0, // tp_hash
  0, // tp_call
  0, // tp_str
  0, // tp_getattro
  0, // tp_setattro
  0, // tp_as_buffer
  Py_TPFLAGS_DEFAULT, // tp_flags
  "MVE View", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter
  0, // tp_iternext
  View_methods, // tp_methods
  View_members, // tp_members
  0, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  (initproc)View_init, // tp_init
};

void load_View(PyObject* mod)
{
  ViewType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&ViewType) < 0)
    return;

  Py_INCREF(&ViewType);
  PyModule_AddObject(mod, "View", (PyObject*)&ViewType);
}
