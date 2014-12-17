#include "image_base.h"
#include <mve/image_base.h>
#include <Python.h>
#include <numpy/arrayobject.h>

static int _ImageTypeToNumpyDataType(mve::ImageType ty)
{
  switch (ty) {
    case mve::IMAGE_TYPE_UINT8: return NPY_UINT8;
    case mve::IMAGE_TYPE_UINT16: return NPY_UINT16;
    case mve::IMAGE_TYPE_UINT32: return NPY_UINT32;
    case mve::IMAGE_TYPE_UINT64: return NPY_UINT64;
    case mve::IMAGE_TYPE_SINT8: return NPY_INT8;
    case mve::IMAGE_TYPE_SINT16: return NPY_INT16;
    case mve::IMAGE_TYPE_SINT32: return NPY_INT32;
    case mve::IMAGE_TYPE_SINT64: return NPY_INT64;
    case mve::IMAGE_TYPE_FLOAT: return NPY_FLOAT32;
    case mve::IMAGE_TYPE_DOUBLE: return NPY_FLOAT64;
  };
  return NPY_NOTYPE;
}

/***************************************************************************
 * ImageBase Object
 *
 */

struct ImageBaseObj {
  PyObject_HEAD
  mve::ImageBase::Ptr thisptr;
};

static PyMethodDef ImageBase_methods[] = {
  {NULL, NULL, 0, NULL}
};

static PyObject* ImageBase_GetWidth(ImageBaseObj *self, void* closure)
{
  return PyLong_FromLong(self->thisptr->width());
}

static PyObject* ImageBase_GetHeight(ImageBaseObj *self, void* closure)
{
  return PyLong_FromLong(self->thisptr->height());
}

static PyObject* ImageBase_GetChannels(ImageBaseObj *self, void* closure)
{
  return PyLong_FromLong(self->thisptr->channels());
}

static PyObject* ImageBase_GetByteSize(ImageBaseObj *self, void* closure)
{
  return PyLong_FromLong(self->thisptr->get_byte_size());
}

static PyObject* ImageBase_GetImageType(ImageBaseObj *self, void* closure)
{
  return PyLong_FromLong(self->thisptr->get_type());
}

static PyObject* ImageBase_GetData(ImageBaseObj *self, void* closure)
{
  mve::ImageBase::Ptr ptr = self->thisptr;
  int ndim = (ptr->channels() == 1 ? 2 : 3);
  npy_intp dims[] = { ptr->height(), ptr->width(), ptr->channels() };
  void *data = ptr->get_byte_pointer();
  PyObject* arr = PyArray_SimpleNewFromData(ndim, dims, _ImageTypeToNumpyDataType(ptr->get_type()), data);

  Py_INCREF((PyObject*) self);
  PyArray_SetBaseObject((PyArrayObject*)arr, (PyObject*)self);

  return arr;
}

static PyGetSetDef ImageBase_getset[] = {
  {"width", (getter)ImageBase_GetWidth, 0, "Width", NULL },
  {"height", (getter)ImageBase_GetHeight, 0, "Height", NULL},
  {"channels", (getter)ImageBase_GetChannels, 0, "Channels", NULL},
  {"byte_size", (getter)ImageBase_GetByteSize, 0, "Size in Bytes", NULL},
  {"image_type", (getter)ImageBase_GetImageType, 0, "Image Type", NULL},
  {"data", (getter)ImageBase_GetData, 0, "Data", NULL},
  {NULL, NULL, NULL, NULL, NULL}
};

static int ImageBase_Init(ImageBaseObj *self, PyObject *args, PyObject *kwds)
{
  self->thisptr = new mve::ImageBase();
  return 0;
}

static PyObject* ImageBase_New(PyTypeObject *subtype, PyObject *args, PyObject *kwds)
{
  //ImageBaseObj* obj = (ImageBaseObj*) subtype->tp_alloc(subtype, 0);
  ImageBaseObj* obj = (ImageBaseObj*) PyType_GenericNew(subtype, args, kwds);

  ::new(&(obj->thisptr)) mve::ImageBase::Ptr();

  return (PyObject*) obj;
}

static void ImageBase_Dealloc(ImageBaseObj *self)
{
  self->thisptr.reset();
}

static PyTypeObject ImageBaseType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "mve.core.ImageBase", // tp_name
  sizeof(ImageBaseObj), // tp_basicsize
  0, // tp_itemsize
  (destructor)ImageBase_Dealloc, // tp_dealloc
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
  "MVE ImageBase", // tp_doc
  0, // tp_traverse
  0, // tp_clear
  0, // tp_richcompare
  0, // tp_weaklistoffset
  0, // tp_iter
  0, // tp_iternext
  ImageBase_methods, // tp_methods
  0, // tp_members
  ImageBase_getset, // tp_getset
  0, // tp_base
  0, // tp_dict
  0, // tp_descr_get
  0, // tp_descr_set
  0, // tp_dictoffset
  (initproc)ImageBase_Init, // tp_init
  0, // tp_alloc
  (newfunc)ImageBase_New, // tp_new
  0, // tp_free
  0, // tp_is_gc
 };

/***************************************************************************
 *
 *
 */

PyObject* ImageBase_Create(mve::ImageBase::Ptr ptr)
{
  PyObject* args = PyTuple_New(0);
  PyObject* kwds = PyDict_New();
  PyObject* obj = ImageBaseType.tp_new(&ImageBaseType, args, kwds);
  Py_DECREF(args);
  Py_DECREF(kwds);

  ((ImageBaseObj*) obj)->thisptr = ptr;

  return obj;
}

void load_ImageBase(PyObject *mod)
{
  // Import Numpy API
  import_array();

  if (PyType_Ready(&ImageBaseType) < 0)
    abort();
  Py_INCREF(&ImageBaseType);

  PyModule_AddObject(mod, "ImageBase", (PyObject*)&ImageBaseType);

  PyModule_AddIntConstant(mod, "IMAGE_TYPE_UNKNOWN", mve::IMAGE_TYPE_UNKNOWN);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_UINT8", mve::IMAGE_TYPE_UINT8);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_UINT16", mve::IMAGE_TYPE_UINT16);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_UINT32", mve::IMAGE_TYPE_UINT32);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_UINT64", mve::IMAGE_TYPE_UINT64);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_SINT8", mve::IMAGE_TYPE_SINT8);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_SINT16", mve::IMAGE_TYPE_SINT16);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_SINT32", mve::IMAGE_TYPE_SINT32);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_SINT64", mve::IMAGE_TYPE_SINT64);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_FLOAT", mve::IMAGE_TYPE_FLOAT);
  PyModule_AddIntConstant(mod, "IMAGE_TYPE_DOUBLE", mve::IMAGE_TYPE_DOUBLE);
}
