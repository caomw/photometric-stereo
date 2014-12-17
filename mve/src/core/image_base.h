#pragma once

#include <mve/image_base.h>
#include <Python.h>

PyObject* ImageBase_Create(mve::ImageBase::Ptr ptr);

void load_ImageBase(PyObject *mod);

