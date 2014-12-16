#pragma once

#include <util/ref_ptr.h>
#include <Python.h>

template<typename T>
struct PyRefPtr {
  PyObject_HEAD
  util::RefPtr<T> thisptr;
};

