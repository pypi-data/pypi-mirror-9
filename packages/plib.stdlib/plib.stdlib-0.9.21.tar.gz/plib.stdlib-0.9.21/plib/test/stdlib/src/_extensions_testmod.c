/*
 * _EXTENSIONS_TESTMOD.C
 * Python/C API extension test module for the PLIB3 package
 * Copyright (C) 2008-2014 by Peter A. Donis
 *
 * Released under the GNU General Public License, Version 2
 * See the LICENSE and README files for more information
 *
 */

#include <Python.h>
#include <stdio.h>

static int i1 = 0;
static int i2 = 1;

static void *ptr1 = &i1;
static void *ptr2 = &i2;

static PyObject *
_extensions_cobject_orig(PyObject *self, PyObject *args)
{
    return PyCObject_FromVoidPtr(ptr1, NULL);
}

static PyObject *
_extensions_cobject_same(PyObject *self, PyObject *args)
{
    return PyCObject_FromVoidPtr(ptr1, NULL);
}

static PyObject *
_extensions_cobject_different(PyObject *self, PyObject *args)
{
    return PyCObject_FromVoidPtr(ptr2, NULL);
}

static const char name_orig[] = "capsule_orig";
static const char name_same[] = "capsule_same";
static const char name_diff[] = "capsule_different";

static const char *np_orig = &(name_orig[0]);
static const char *np_same = &(name_same[0]);
static const char *np_diff = &(name_diff[0]);

static PyObject *
_extensions_capsule_orig(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr1, np_orig, NULL);
}

static PyObject *
_extensions_capsule_same(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr1, np_same, NULL);
}

static PyObject *
_extensions_capsule_different(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr2, np_diff, NULL);
}

static PyObject *
_extensions_capsule_null_orig(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr1, NULL, NULL);
}

static PyObject *
_extensions_capsule_null_same(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr1, NULL, NULL);
}

static PyObject *
_extensions_capsule_null_different(PyObject *self, PyObject *args)
{
    return PyCapsule_New(ptr2, NULL, NULL);
}

static PyMethodDef _extensions_testmod_Methods[] = {
    {"cobject_orig", _extensions_cobject_orig, METH_VARARGS, NULL},
    {"cobject_same", _extensions_cobject_same, METH_VARARGS, NULL},
    {"cobject_different", _extensions_cobject_different, METH_VARARGS, NULL},
    {"capsule_orig", _extensions_capsule_orig, METH_VARARGS, NULL},
    {"capsule_same", _extensions_capsule_same, METH_VARARGS, NULL},
    {"capsule_different", _extensions_capsule_different, METH_VARARGS, NULL},
    {"capsule_null_orig", _extensions_capsule_null_orig, METH_VARARGS, NULL},
    {"capsule_null_same", _extensions_capsule_null_same, METH_VARARGS, NULL},
    {"capsule_null_different", _extensions_capsule_null_different, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyDoc_STRVAR(_extensions_testmod__doc__,
"Python/C API extension testing module for the PLIB3.TEST package.");

PyMODINIT_FUNC
init_extensions_testmod(void)
{
    Py_InitModule3("_extensions_testmod", _extensions_testmod_Methods,
                   _extensions_testmod__doc__);
}
