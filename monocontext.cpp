#include "Python.h"
#include "v8monoctx.h"


PyObject* PyExc_V8Error;


typedef struct {
	PyObject_HEAD
	monocfg* pCfg;
} PyAgent;


static int PyAgent_init(PyAgent *self, PyObject *args, PyObject *kwargs) {

	unsigned int run_low_memory_notification = 0;   // call LowMemoryNotification after number of requests
	unsigned int run_idle_notification_loop = 0;    // call IdleNotification loop after number of requests
	char* cmd_args;                                 // arguments for V8
	bool watch_templates = false;                   // if template changed since last compilation - recompile it

	static char *kwlist[] = {
		(char*)"run_low_memory_notification",
		(char*)"run_idle_notification_loop",
		(char*)"cmd_args",
		(char*)"watch_templates",
		NULL
	};

	self->pCfg = (monocfg*)calloc(1, sizeof(monocfg));

	if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|IIsI", kwlist,
				&run_low_memory_notification, &run_idle_notification_loop, &cmd_args, &watch_templates)) {
		return -1;
	}

	self->pCfg->run_low_memory_notification = run_low_memory_notification;
	self->pCfg->run_idle_notification_loop = run_idle_notification_loop;

	if (cmd_args != NULL && strlen(cmd_args) > CMD_ARGS_LEN) {
		PyErr_Format(PyExc_ValueError, "cmd_args is limited to %d", CMD_ARGS_LEN);
		return -1;
	}
	strcpy(self->pCfg->cmd_args, cmd_args);

	self->pCfg->watch_templates = watch_templates;

	return 0;
}

static void PyAgent_dealloc(PyAgent* self) {
	self->ob_type->tp_free((PyObject*)self);
	free(self->pCfg);
	self->pCfg = NULL;
}

static PyObject * PyAgent_execute_file(PyAgent *self, PyObject *args) {
	const char *fname;
	const char *append;
	const char *json;

	if (!PyArg_ParseTuple(args, "sss", &fname, &append, &json)) {
		return NULL;
	}

	std::string json_str = (std::string)json;
	std::string out;

	bool res = ExecuteFile(self->pCfg, fname, append, &json_str, &out);
	std::vector<std::string> err = GetErrors();
	PyObject *ErrList = PyList_New(0);

	if (err.size()) {
		for (unsigned i=0; i < err.size(); i++) {
			PyObject *ErrString = Py_BuildValue("s", err.at(i).c_str());
			PyList_Append(ErrList, ErrString);
			Py_DECREF(ErrString);
		}
	}

	if (!res) {
		PyErr_SetObject(PyExc_V8Error, ErrList);
		Py_DECREF(ErrList);
		return NULL;
	}

	PyObject *Output = PyUnicode_FromStringAndSize(out.c_str(), out.length());
	PyObject *ret = Py_BuildValue("OO", Output, ErrList);
	Py_DECREF(Output);
	Py_DECREF(ErrList);
	return ret;
}


static PyObject * PyAgent_load_file(PyAgent *self, PyObject *args) {
	const char *fname;

	if (!PyArg_ParseTuple(args, "s", &fname)) {
		return NULL;
	}

	bool res = LoadFile(self->pCfg, fname);
	std::vector<std::string> err = GetErrors();
	PyObject *ErrList = PyList_New(0);

	if (err.size()) {
		for (unsigned i=0; i < err.size(); i++) {
			PyObject *ErrString = Py_BuildValue("s", err.at(i).c_str());
			PyList_Append(ErrList, ErrString);
			Py_DECREF(ErrString);
		}
	}

	if (!res) {
		PyErr_SetObject(PyExc_V8Error, ErrList);
		Py_DECREF(ErrList);
		return NULL;
	}

	return ErrList;
}

static PyObject* PyAgent_counters(PyAgent* self) {
	PyObject* DumpDict = PyDict_New();

	PyDict_SetItemString(DumpDict, "request_num", PyInt_FromLong(self->pCfg->request_num));
	PyDict_SetItemString(DumpDict, "run_low_memory_notification_time", PyFloat_FromDouble(self->pCfg->run_low_memory_notification_time));
	PyDict_SetItemString(DumpDict, "run_idle_notification_loop_time", PyFloat_FromDouble(self->pCfg->run_idle_notification_loop_time));
	PyDict_SetItemString(DumpDict, "compile_time", PyFloat_FromDouble(self->pCfg->compile_time));
	PyDict_SetItemString(DumpDict, "exec_time", PyFloat_FromDouble(self->pCfg->exec_time));

	return DumpDict;
}

static PyObject* PyAgent_heap_stat(PyAgent* self) {
	PyObject* DumpDict = PyDict_New();

	HeapSt st;
	GetHeapStat(&st);

	PyDict_SetItemString(DumpDict,"total", PyInt_FromLong(st.total_heap_size));
	PyDict_SetItemString(DumpDict,"limit", PyInt_FromLong(st.heap_size_limit));
	PyDict_SetItemString(DumpDict,"used", PyInt_FromLong(st.used_heap_size));
	PyDict_SetItemString(DumpDict,"total_executable", PyInt_FromLong(st.total_heap_size_executable));
	PyDict_SetItemString(DumpDict,"total_physical", PyInt_FromLong(st.total_physical_size));

	return DumpDict;
}

static PyMethodDef PyAgent_methods[] =
{
	{ "execute_file", (PyCFunction)PyAgent_execute_file, METH_VARARGS, "Execute file" },
	{ "load_file", (PyCFunction)PyAgent_load_file, METH_VARARGS, "Load file" },
	{ "counters", (PyCFunction)PyAgent_counters, METH_VARARGS, "Get counters" },
	{ "heap_stat", (PyCFunction)PyAgent_heap_stat, METH_VARARGS, "Get heap statistic" },
	{ NULL, NULL, 0, NULL }  /* Sentinel */
};


static PyTypeObject PyAgentType = {
	PyObject_HEAD_INIT(NULL)
	0,                         /* ob_size */
	"MonoContext",             /* tp_name */
	sizeof(PyAgent),           /* tp_basicsize */
	0,                         /* tp_itemsize */
	(destructor)PyAgent_dealloc, /* tp_dealloc */
	0,                         /* tp_print */
	0,                         /* tp_getattr */
	0,                         /* tp_setattr */
	0,                         /* tp_compare */
	0,                         /* tp_repr */
	0,                         /* tp_as_number */
	0,                         /* tp_as_sequence */
	0,                         /* tp_as_mapping */
	0,                         /* tp_hash */
	0,                         /* tp_call */
	0,                         /* tp_str */
	0,                         /* tp_getattro */
	0,                         /* tp_setattro */
	0,                         /* tp_as_buffer */
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags*/
	"MonoContext class",       /* tp_doc */
	0,                         /* tp_traverse */
	0,                         /* tp_clear */
	0,                         /* tp_richcompare */
	0,                         /* tp_weaklistoffset */
	0,                         /* tp_iter */
	0,                         /* tp_iternext */
	PyAgent_methods,           /* tp_methods */
	0,                         /* tp_members */
	0,                         /* tp_getset */
	0,                         /* tp_base */
	0,                         /* tp_dict */
	0,                         /* tp_descr_get */
	0,                         /* tp_descr_set */
	0,                         /* tp_dictoffset */
	(initproc)PyAgent_init,    /* tp_init */
	0,                         /* tp_alloc */
	0,                         /* tp_new */
};


// This function is called to initialize the module.

PyMODINIT_FUNC
initmonocontext(void)
{
	PyObject* module;

	module = Py_InitModule3("monocontext", NULL, "monocontext module");
	if (module == NULL) {
		return;
	}

	// Fill in some slots in the type, and make it ready
	PyAgentType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&PyAgentType) < 0) {
		return;
	}

	// Add the type to the module.
	Py_INCREF(&PyAgentType);
	PyModule_AddObject(module, "MonoContext", (PyObject*)&PyAgentType);

	PyExc_V8Error = PyErr_NewException((char*)"monocontext.V8Error", NULL, NULL);
	Py_INCREF(PyExc_V8Error);
	PyModule_AddObject(module, "V8Error", PyExc_V8Error);
}
