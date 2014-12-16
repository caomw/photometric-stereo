#include <mve/view.h>
#include <mve/camera.h>
#include <Python.h>
#include <structmember.h>
#include <numpy/arrayobject.h>
#include <new>

/***************************************************************************
 * Camera Info Object
 *
 */

struct CameraInfoObj {
  PyObject_HEAD
  mve::CameraInfo instance;
};

static PyObject* CameraInfo_GetPosition(CameraInfoObj* self);
static PyObject* CameraInfo_GetTranslation(CameraInfoObj* self);
static PyObject* CameraInfo_GetViewDirection(CameraInfoObj* self);
static PyObject* CameraInfo_GetWorldToCamMatrix(CameraInfoObj* self);
static PyObject* CameraInfo_GetCamToWorldMatrix(CameraInfoObj* self);
static PyObject* CameraInfo_GetWorldToCamRotation(CameraInfoObj* self);
static PyObject* CameraInfo_GetCamToWorldRotation(CameraInfoObj* self);
static PyObject* CameraInfo_GetCalibration(CameraInfoObj* self, PyObject* args);
static PyObject* CameraInfo_GetInverseCalibration(CameraInfoObj* self, PyObject* args);
//static PyObject* CameraInfo_GetReprojection
static PyObject* CameraInfo_GetExtrinsicString(CameraInfoObj* self);
static PyObject* CameraInfo_GetIntrinsicString(CameraInfoObj* self);
static PyObject* CameraInfo_GetFocalLength(CameraInfoObj* self);
static PyObject* CameraInfo_GetPrincipalPoint(CameraInfoObj* self);
static PyObject* CameraInfo_GetPixelAspect(CameraInfoObj* self);
static PyObject* CameraInfo_GetDistortion(CameraInfoObj* self);

static PyMethodDef CameraInfo_methods[] = {
  //{"get_calibration"},
  //{"get_reprojection", },
  //{"get_inverse_calibration"},
  {NULL, NULL, 0, NULL}
};

static PyGetSetDef CameraInfo_getset[] = {
  //{"position", (getter)CameraInfo_GetPosition, NULL, "Position", NULL},
  //{"translation", (getter)CameraInfo_GetTranslation, NULL, "Translation Vector", NULL},
  //{"view_dir", (getter)CameraInfo_GetViewDirection, NULL, "View Direction", NULL},
  //{"world_to_cam_matrix", (getter)CameraInfo_GetWorldToCamMatrix, NULL, "World to Camera Matrix", NULL},
  //{"cam_to_world_matrix", (getter)CameraInfo_GetCamToWorldMatrix, NULL, "Camera to World Matrix", NULL},
  //{"extrinsic_str"}
  //{"intrinsic_str"}
  //{"focal_length"}
  //{"principal_point"}
  //{"pixel_aspect"}
  //{"distortion"}
  {NULL, NULL, NULL, NULL, NULL}
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

static PyObject* View_CacheCleanup(ViewObj *self)
{
  self->thisptr->cache_cleanup();
  return Py_None;
}

static PyMethodDef View_methods[] = {
  {"cache_cleanup", (PyCFunction)View_CacheCleanup, METH_NOARGS, "Clean Cache"},
  {NULL, NULL, 0, NULL}
};

static int View_Init(ViewObj *self, PyObject *args, PyObject *kwds)
{
  self->thisptr = mve::View::create();
  return 0;
}

static PyObject* View_New(PyTypeObject *subtype, PyObject *args, PyObject *kwds)
{
  //ViewObj* obj = (ViewObj*) subtype->tp_alloc(subtype, 0);
  ViewObj* obj = (ViewObj*) PyType_GenericNew(subtype, args, kwds);

  ::new(&(obj->thisptr)) mve::View::Ptr();

  return (PyObject*) obj;
}

static void View_Dealloc(ViewObj *self)
{
  self->thisptr.reset();
}

static PyObject* View_GetId(ViewObj *self, void* closure)
{
  return PyLong_FromSize_t(self->thisptr->get_id());
}

static int View_SetId(ViewObj *self, PyObject *value, void* closure)
{
  self->thisptr->set_id(PyLong_AsSsize_t(value));
  return 0;
}

static PyObject* View_GetName(ViewObj *self, void* closure)
{
  return PyString_FromString(self->thisptr->get_name().c_str());
}

static int View_SetName(ViewObj *self, PyObject *value, void* closure)
{
  self->thisptr->set_name(PyString_AsString(value));
  return 0;
}

static PyObject* View_GetCamera(ViewObj *self, void* closure)
{
  return PyString_FromString("yoooo");
}

static PyGetSetDef View_getset[] = {
  {"id", (getter)View_GetId, (setter)View_SetId, "ID", NULL },
  {"name", (getter)View_GetName, (setter)View_SetName, "Name", NULL},
  {"camera", (getter)View_GetCamera, NULL, "Camera", NULL},
  {NULL, NULL, NULL, NULL, NULL}
};

static PyTypeObject ViewType = {
#if PY_MAJOR_VERSION < 3
  PyObject_HEAD_INIT(NULL)
#endif
  0, // ob_size
  "mve.core.View", // tp_name
  sizeof(ViewObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)View_Dealloc, // tp_dealloc
  0, // tp_print
  0, // tp_getattr (deprecated)
  0, // tp_setattr (deprecated)
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
  "MVE View", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter
  0, // tp_iternext
  View_methods, // tp_methods
  View_members, // tp_members
  View_getset, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  (initproc)View_Init, // tp_init
  0, // tp_alloc
  (newfunc)View_New, // tp_new
  0, // tp_free
  0, // tp_is_gc
};

/***************************************************************************
 *
 *
 */

PyObject* ViewObj_Create(mve::View::Ptr ptr)
{
  PyObject* args = PyTuple_New(0);
  PyObject* kwds = PyDict_New();
  PyObject* obj = ViewType.tp_new(&ViewType, args, kwds);
  Py_DECREF(args);
  Py_DECREF(kwds);

  ((ViewObj*) obj)->thisptr = ptr;

  return obj;
}

void load_View(PyObject* mod)
{
  if (PyType_Ready(&ViewType) < 0)
    abort();
  Py_INCREF(&ViewType);

  PyModule_AddObject(mod, "View", (PyObject*)&ViewType);
}
