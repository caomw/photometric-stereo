#include <mve/scene.h>
#include <Python.h>
#include <structmember.h>
#include "view.h"

/***************************************************************************
 * View List Object
 *
 */

struct ViewListObj {
  PyObject_HEAD
  mve::Scene::ViewList *thisptr;
};

static Py_ssize_t ViewList_len(ViewListObj* self)
{
  return self->thisptr->size();
}

static PyObject* ViewList_item(ViewListObj* self, Py_ssize_t index)
{
  // negative index is handled before
  mve::View::Ptr ptr = self->thisptr->operator[](index);
  if (ptr == NULL)
    return NULL;

  PyObject* obj = ViewObj_Create(ptr);
  return obj;
}

static PyObject* ViewList_slice(ViewListObj* self, Py_ssize_t i1, Py_ssize_t i2)
{
  PyObject* list = PyList_New(i2-i1);

  for (Py_ssize_t i = i1; i < i2; ++i) {
    PyList_SetItem(list, i, ViewList_item(self, i));
  }

  return list;
}

static PySequenceMethods ViewList_seq_methods = {
  (lenfunc)ViewList_len, // sq_length
  0, // sq_concat
  0, // sq_repeat
  (ssizeargfunc)ViewList_item, // sq_item
  (ssizessizeargfunc)ViewList_slice, // sq_slice
  0, // sq_ass_item
  0, // sq_ass_slice
  0, // sq_contains
  0, // sq_inplace_oncat
  0  // sq_inplace_repeat
};

static PyTypeObject ViewListType = {
  PyObject_HEAD_INIT(NULL)
  0, // ob_size
  "mve.core.Scene.ViewList", // tp_name
  sizeof(ViewListObj), // tp_basicsize
  0, // tp_itemsize
  0, // tp_dealloc
  0, // tp_print
  0, // tp_getattr
  0, // tp_setattr
#if PY_MAJOR_VERSION < 3
  0, // tp_compare
#else
  0, // reserved
#endif
  0, // tp_repr
  0, // tp_as_number
  &ViewList_seq_methods, // tp_as_sequence
  0, // tp_as_mapping
  0, // tp_hash
  0, // tp_call
  0, // tp_str
  0, // tp_getattro
  0, // tp_setattro
  0, // tp_as_buffer
  (Py_TPFLAGS_HAVE_WEAKREFS | Py_TPFLAGS_HAVE_CLASS |
   Py_TPFLAGS_HAVE_ITER), // tp_flags
  "MVE Scene::ViewList", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter TODO
  0, // tp_iternext TODO
  0, // tp_methods
  0, // tp_members
  0, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  0, // tp_init
  0, // tp_alloc
  0, // tp_new
  0, // tp_free
  0, // tp_is_gc
};

PyObject* ViewListObj_New(mve::Scene::ViewList* viewlist)
{
  ViewListObj* obj = PyObject_New(ViewListObj, (PyTypeObject*)&ViewListType);
  PyObject_Init((PyObject*)obj, (PyTypeObject*)&ViewListType);
  obj->thisptr = viewlist;
  return (PyObject*) obj;
}

/***************************************************************************
 * Scene Object
 *
 */

struct SceneObj {
  PyObject_HEAD
  mve::Scene::Ptr thisptr;
  PyObject *viewlist;
};

static PyObject* Scene_load(SceneObj *self, PyObject *args)
{
  const char* path = PyString_AsString(args);
  if (path) {
    self->thisptr->load_scene(path);
  }
  return Py_None;
}

static PyObject* Scene_GetViews(SceneObj *self, void* closure)
{
  mve::Scene::ViewList& views = self->thisptr->get_views();

  if (!self->viewlist) {
    self->viewlist = ViewListObj_New(&views);
  }

  Py_INCREF(self->viewlist);
  return (PyObject*) self->viewlist;
}

static PyMethodDef Scene_methods[] = {
  {"load", (PyCFunction)Scene_load, METH_O, "Load Scene"},
  {NULL, NULL, 0, NULL}
};

static PyGetSetDef Scene_getset[] = {
  {"views", (getter)Scene_GetViews, NULL, "Views", NULL },
  {NULL, NULL, NULL, NULL, NULL}
};

static int Scene_Init(SceneObj *self, PyObject *args, PyObject *keywords)
{
  //printf("%p\n", self->thisptr.get());
  self->thisptr = mve::Scene::create();
  return 0;
}

static void Scene_Dealloc(SceneObj *self)
{
  self->thisptr.reset();

  if (self->viewlist) {
    Py_DECREF(self->viewlist);
    self->viewlist = NULL;
  }
}

static PyTypeObject SceneType = {
#if PY_MAJOR_VERSION < 3
  PyObject_HEAD_INIT(NULL)
#endif
  0, // ob_size
  "mve.core.Scene", // tp_name
  sizeof(SceneObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)Scene_Dealloc, // tp_dealloc
  0, // tp_print
  0, // tp_getattr
  0, // tp_setattr
#if PY_MAJOR_VERSION < 3
  0, // tp_compare
#else
  0, // reserved
#endif
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
  Py_TPFLAGS_HAVE_WEAKREFS | Py_TPFLAGS_HAVE_CLASS, // tp_flags
  "MVE Scene", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter
  0, // tp_iternext
  Scene_methods, // tp_methods
  0, // tp_members
  Scene_getset, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  (initproc)Scene_Init, // tp_init
};

void load_Scene(PyObject* mod)
{
  ViewListType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&ViewListType) < 0)
    return;
  Py_INCREF(&ViewListType);

  SceneType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&SceneType) < 0)
    return;
  Py_INCREF(&SceneType);

  PyModule_AddObject(mod, "Scene", (PyObject*)&SceneType);
}
