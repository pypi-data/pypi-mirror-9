
#include <Python.h>
#include "hotpatch/tramp.h"
#include "hotpatch/bin_api.h"
#include <frameobject.h>
#include "vmprof.h"

static PyObject* (*Original_PyEval_EvalFrameEx)(PyFrameObject *f, int throwflag);
int initialized = 0;
PyObject* vmprof_mod = NULL;

#define UNUSED_FLAG 0x1000 // this is a flag unused since Python2.5, let's hope
// noone uses it

static void* PyEval_GetVirtualIp(PyFrameObject* f) {
	char buf[4096];
	char *co_name, *co_filename;
	int co_firstlineno;
    unsigned long res = (unsigned long)f->f_code | 0x7000000000000000;
    // set the first bit to 1; on my system, such address space is unused, so
    // we don't risk spurious conflicts with loaded libraries. The proper
    // solution would be to tell the linker to reserve us some address space
    // and use that.
	if (f->f_code->co_flags & UNUSED_FLAG)
		return (void*)res;
	f->f_code->co_flags |= UNUSED_FLAG;
    co_name = PyString_AsString(f->f_code->co_name);
	co_filename = PyString_AsString(f->f_code->co_filename);
	co_firstlineno = f->f_code->co_firstlineno;
    snprintf(buf, 4096, "py:%s:%d:%s", co_name, co_firstlineno, co_filename);
    vmprof_register_virtual_function(buf, (void*)res, NULL);
    return (void*)res;
}

__attribute__((optimize("O2")))
PyObject* cpyprof_PyEval_EvalFrameEx(PyFrameObject *f, int throwflag) {
    register void* _rsp asm("rsp");
    ptrdiff_t offset;
    volatile PyFrameObject *f2 = f;
    offset = (char*)&f2 - (char*)_rsp;
    if (!vmprof_mainloop_func)
        vmprof_set_mainloop(&cpyprof_PyEval_EvalFrameEx, offset, (void*)PyEval_GetVirtualIp);
	return Original_PyEval_EvalFrameEx(f, throwflag);
}

void init_cpyprof(void) {
	Original_PyEval_EvalFrameEx = PyEval_EvalFrameEx;	
	// monkey-patch PyEval_EvalFrameEx
	init_memprof_config_base();
	bin_init();
	create_tramp_table();
	size_t tramp_size;
	void* tramp_addr = insert_tramp("PyEval_EvalFrameEx", &cpyprof_PyEval_EvalFrameEx, &tramp_size);
	vmprof_set_tramp_range(tramp_addr, tramp_addr+tramp_size);
} 

PyObject *enable_vmprof(PyObject* self, PyObject *args)
{
	int fd, period_usec = -1;
	char *x = NULL;
	int x_len = 0;

	if (!initialized) {
		init_cpyprof();
		initialized = 1;
	}
	if (!PyArg_ParseTuple(args, "i|is#", &fd, &period_usec, &x, &x_len))
		return NULL;
	if (vmprof_enable(fd, period_usec, 1, x, x_len) == -1) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *disable_vmprof(PyObject* self, PyObject *args)
{
	if (vmprof_disable() == -1) {
		PyErr_SetFromErrno(PyExc_OSError);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyMethodDef VmprofMethods[] = {
    {"enable",  enable_vmprof, METH_VARARGS,
     "Enable profiling."},
    {"disable", disable_vmprof, METH_VARARGS,
     "Disable profiling."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC init_vmprof(void)
{
    vmprof_mod = Py_InitModule("_vmprof", VmprofMethods);
    if (vmprof_mod == NULL)
        return;	
}
