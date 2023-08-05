/*
 * _EXTENSIONS.C
 * Python/C API extension module for the PLIB package
 * Copyright (C) 2008-2014 by Peter A. Donis
 *
 * Released under the GNU General Public License, Version 2
 * See the LICENSE and README files for more information
 *
 */

#include <Python.h>
#include <stdio.h>

/* Old (deprecated) CObject API */

static char old_msg[] =
"Argument x to cobject_compare() is not a CObject.";

void
make_old_message(int i)
{
    switch (i) {
        case 1:
            old_msg[9] = '1';
            break;
        case 2:
            old_msg[9] = '2';
            break;
        default:
            old_msg[9] = 'x';
    }
    PyErr_SetString(PyExc_TypeError, old_msg);
}

static PyObject *
_extensions_PyCObjectCompare(PyObject *self, PyObject *args)
{
    int int1, int2;
    void *void1, *void2;
    PyObject *cobj1, *cobj2;

    /* Unpack arguments */
    if (!PyArg_ParseTuple(args, "OO:cobject_compare", &cobj1, &cobj2))
        return NULL;

    /* Check for valid CObject pointer input */
    int1 = PyCObject_Check(cobj1);
    if (!int1) {
        make_old_message(1);
        return NULL;
    }
    int2 = PyCObject_Check(cobj2);
    if (!int2) {
        make_old_message(2);
        return NULL;
    }

    /* Check whether CObjects wrap same pointer */
    void1 = PyCObject_AsVoidPtr(cobj1);
    void2 = PyCObject_AsVoidPtr(cobj2);
    if (void1 == void2) {
        Py_INCREF(Py_True);
        return Py_True;
      }
    Py_INCREF(Py_False);
    return Py_False;
}

PyDoc_STRVAR(cobject_compare__doc__,
"cobject_compare(PyCObject, PyCObject) -> bool\n\n"
"See if two CObjects wrap the same C-level pointer.");

/* New Capsule API */

static char msg[] =
"Argument x to capsule_compare() is not a Capsule.";

void
make_message(int i)
{
    switch (i) {
        case 1:
            msg[9] = '1';
            break;
        case 2:
            msg[9] = '2';
            break;
        default:
            msg[9] = 'x';
    }
    PyErr_SetString(PyExc_TypeError, msg);
}

static PyObject *
_extensions_PyCapsuleCompare(PyObject *self, PyObject *args)
{
    int int1, int2;
    void *void1, *void2;
    PyObject *cap1, *cap2, *err;
    char *name1, *name2;

    /* Unpack arguments */
    if (!PyArg_ParseTuple(args, "OO:capsule_compare", &cap1, &cap2))
        return NULL;

    /* Check for valid Capsule pointer input */
    int1 = PyCapsule_CheckExact(cap1);
    if (!int1) {
        make_message(1);
        return NULL;
    }
    int2 = PyCapsule_CheckExact(cap2);
    if (!int2) {
        make_message(2);
        return NULL;
    }

    /* Get Capsule names */
    name1 = PyCapsule_GetName(cap1);
    err = PyErr_Occurred();
    if (err != NULL) {
        return NULL;
    }
    name2 = PyCapsule_GetName(cap2);
    err = PyErr_Occurred();
    if (err != NULL) {
        return NULL;
    }

    /* Check whether Capsules wrap same pointer */
    void1 = PyCapsule_GetPointer(cap1, name1);
    err = PyErr_Occurred();
    if (err != NULL) {
        return NULL;
    }
    void2 = PyCapsule_GetPointer(cap2, name2);
    err = PyErr_Occurred();
    if (err != NULL) {
        return NULL;
    }
    if (void1 == void2) {
        Py_INCREF(Py_True);
        return Py_True;
      }
    Py_INCREF(Py_False);
    return Py_False;
}

PyDoc_STRVAR(capsule_compare__doc__,
"capsule_compare(PyCapsule, PyCapsule) -> bool\n\n"
"See if two Capsules wrap the same C-level pointer.");

/* Module setup */

static PyMethodDef _extensions_Methods[] = {
    {"cobject_compare", _extensions_PyCObjectCompare, METH_VARARGS,
        cobject_compare__doc__},
    {"capsule_compare", _extensions_PyCapsuleCompare, METH_VARARGS,
        capsule_compare__doc__},
    {NULL, NULL, 0, NULL} /* Sentinel */
};

PyDoc_STRVAR(_extensions__doc__,
"Python/C API extension module for the PLIB package.");

PyMODINIT_FUNC
init_extensions(void)
{
    Py_InitModule3("_extensions", _extensions_Methods, _extensions__doc__);
}
