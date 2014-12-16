#include <mve/scene.h>
#include <Python.h>
#include <structmember.h>

struct SceneObj {
  PyObject_HEAD
  mve::Scene::Ptr thisptr;
};

static PyMemberDef Scene_members[] = {
  {NULL}
};

static PyObject* Scene_load(SceneObj *self, PyObject *args)
{
  const char* path = PyString_AsString(args);
  if (path) {
    self->thisptr->load_scene(path);
  }
  return Py_None;
}

static PyMethodDef Scene_methods[] = {
  {"load", (PyCFunction)Scene_load, METH_O, "Load Scene"},
  {NULL, NULL, 0, NULL}
};

static int Scene_init(SceneObj *self, PyObject *args, PyObject *keywords)
{
  //printf("%p\n", self->thisptr.get());
  self->thisptr = mve::Scene::create();
  return 0;
}

static void Scene_dealloc(SceneObj *self)
{
  self->thisptr.reset();
}

static PyTypeObject SceneType = {
  PyObject_HEAD_INIT(NULL)
  0, // ob_size
  "mve.core.Scene", // tp_name
  sizeof(SceneObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)Scene_dealloc, // tp_dealloc
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
  "MVE Scene", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter
  0, // tp_iternext
  Scene_methods, // tp_methods
  Scene_members, // tp_members
  0, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  (initproc)Scene_init, // tp_init
};

void load_Scene(PyObject* mod)
{
  SceneType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&SceneType) < 0)
    return;

  Py_INCREF(&SceneType);
  PyModule_AddObject(mod, "Scene", (PyObject*)&SceneType);
}
