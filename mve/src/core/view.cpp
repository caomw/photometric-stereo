#include <mve/view.h>
#include <mve/camera.h>
#include <Python.h>
#include <structmember.h>

/***************************************************************************
 * Camera Info Object
 *
 */

struct CameraInfoObj {
  PyObject_HEAD
  mve::CameraInfo instance;
};

static PyMethodDef CameraInfo_methods[] = {
  //{"get_calibration_matrix"},
  //{"get_projection_matrix", },
  {NULL, NULL, 0, NULL}
};

/***************************************************************************
 * View Object
 *
 */

struct ViewObj {
  PyObject_HEAD
  mve::View::Ptr thisptr;
};

static PyMemberDef View_members[] = {
  { NULL }
};

static PyObject* View_cache_cleanup(ViewObj *self)
{
  self->thisptr->cache_cleanup();
  return Py_None;
}

static PyMethodDef View_methods[] = {
  {"cache_cleanup", (PyCFunction)View_cache_cleanup, METH_NOARGS, "Clean Cache"},
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

static PyObject* View_getId(ViewObj *self)
{
  return PyLong_FromSize_t(self->thisptr->get_id());
}

static int View_setId(ViewObj *self, PyObject *value)
{
  self->thisptr->set_id(PyLong_AsSsize_t(value));
  return 0;
}

static PyObject* View_getName(ViewObj *self)
{
  return PyString_FromString(self->thisptr->get_name().c_str());
}

static int View_setName(ViewObj *self, PyObject *value)
{
  self->thisptr->set_name(PyString_AsString(value));
  return 0;
}

static PyObject* View_getCamera(ViewObj *self)
{
  return PyString_FromString("yoooo");
}

static PyObject* View_getAttr(ViewObj *self, PyObject *name)
{
  if (PyString_Check(name)){
    const char* cname = PyString_AsString(name);
    if (strcmp(cname, "id") == 0) {
      return View_getId(self);
    } else if (strcmp(cname, "name") == 0) {
      return View_getName(self);
    } else if (strcmp(cname, "camera") == 0) {
      return View_getCamera(self);
    }
  }
  return PyObject_GenericGetAttr((PyObject*)self, name);
}

static int View_setAttr(ViewObj *self, PyObject *name, PyObject *value)
{
  if (PyString_Check(name)){
    const char* cname = PyString_AsString(name);
    if (strcmp(cname, "id") == 0) {
      return View_setId(self, value);
    } else if (strcmp(cname, "name") == 0) {
      return View_setName(self, value);
    }
  }
  return PyObject_GenericSetAttr((PyObject*)self, name, value);
}

static PyTypeObject ViewType = {
#if PY_MAJOR_VERSION < 3
  PyObject_HEAD_INIT(NULL)
#endif
  0, // ob_size
  "mve.core.View", // tp_name
  sizeof(ViewObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)View_dealloc, // tp_dealloc
  0, // tp_print
  0, // tp_getattr (deprecated)
  0, // tp_setattr (deprecated)
  0, // tp_compare
  0, // tp_repr
  0, // tp_as_number
  0, // tp_as_sequence
  0, // tp_as_mapping
  0, // tp_hash
  0, // tp_call
  0, // tp_str
  (getattrofunc)View_getAttr, // tp_getattro
  (setattrofunc)View_setAttr, // tp_setattro
  0, // tp_as_buffer
  Py_TPFLAGS_HAVE_WEAKREFS | Py_TPFLAGS_HAVE_CLASS, // tp_flags
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
  0, // tp_alloc
  0, // tp_new
  0, // tp_free
  0, // tp_is_gc
};

/***************************************************************************
 *
 *
 */

PyObject* ViewObj_New(mve::View::Ptr ptr)
{
  ViewObj* obj = PyObject_New(ViewObj, (PyTypeObject*)&ViewType);
  obj->thisptr = ptr;
  return (PyObject*)obj;
}

void load_View(PyObject* mod)
{
  ViewType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&ViewType) < 0)
    return;

  Py_INCREF(&ViewType);
  PyModule_AddObject(mod, "View", (PyObject*)&ViewType);
}
