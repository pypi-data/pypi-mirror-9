
#include "Python.h"
#include "gpioc.h"

static PyObject* foo(PyObject *self, PyObject *args) {
  char *s = "test";
  return Py_BuildValue("i", PyGPIO_digitalRead(s));
}

static PyMethodDef ctestMethods[]=
{
	{ "foo", foo, METH_VARARGS, "" },
  { NULL, NULL },
};

PyMODINIT_FUNC initctest(void) {
    PyObject *m;

    m = Py_InitModule("ctest", ctestMethods);
    if (m == NULL)
        return;
    if (import_gpio() < 0)
        return;
    /* additional initialization can happen here */
}