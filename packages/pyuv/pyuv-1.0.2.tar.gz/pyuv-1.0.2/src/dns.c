
static void
pyuv__getaddrinfo_cb(uv_getaddrinfo_t* req, int status, struct addrinfo* res)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    struct addrinfo *ptr;
    Loop *loop;
    GAIRequest *gai_req;
    PyObject *addr, *item, *errorno, *dns_result, *result;

    ASSERT(req);

    gai_req = PYUV_CONTAINER_OF(req, GAIRequest, req);
    loop = REQUEST(gai_req)->loop;

    if (status != 0) {
        errorno = PyInt_FromLong((long)status);
        dns_result = Py_None;
        Py_INCREF(Py_None);
        goto callback;
    }

    dns_result = PyList_New(0);
    if (!dns_result) {
        errorno = PyInt_FromLong((long)UV_ENOMEM);
        dns_result = Py_None;
        Py_INCREF(Py_None);
        goto callback;
    }

    for (ptr = res; ptr; ptr = ptr->ai_next) {
        if (!ptr->ai_addrlen)
            continue;

        addr = makesockaddr(ptr->ai_addr);
        if (!addr) {
            PyErr_Clear();
            break;
        }

        item = PyStructSequence_New(&AddrinfoResultType);
        if (!item) {
            PyErr_Clear();
            break;
        }
        PyStructSequence_SET_ITEM(item, 0, PyInt_FromLong((long)ptr->ai_family));
        PyStructSequence_SET_ITEM(item, 1, PyInt_FromLong((long)ptr->ai_socktype));
        PyStructSequence_SET_ITEM(item, 2, PyInt_FromLong((long)ptr->ai_protocol));
        PyStructSequence_SET_ITEM(item, 3, Py_BuildValue("s", ptr->ai_canonname ? ptr->ai_canonname : ""));
        PyStructSequence_SET_ITEM(item, 4, addr);

        PyList_Append(dns_result, item);
        Py_DECREF(item);
    }
    errorno = Py_None;
    Py_INCREF(Py_None);

callback:
    result = PyObject_CallFunctionObjArgs(gai_req->callback, dns_result, errorno, NULL);
    if (result == NULL) {
        handle_uncaught_exception(loop);
    }
    Py_XDECREF(result);
    Py_DECREF(dns_result);
    Py_DECREF(errorno);

    uv_freeaddrinfo(res);
    UV_REQUEST(gai_req) = NULL;
    Py_DECREF(gai_req);

    PyGILState_Release(gstate);
}


static void
pyuv__getnameinfo_cb(uv_getnameinfo_t* req, int status, const char *hostname, const char *service)
{
    PyGILState_STATE gstate = PyGILState_Ensure();
    Loop *loop;
    GNIRequest *gni_req;
    PyObject *errorno, *gni_result, *result;

    ASSERT(req);

    gni_req = PYUV_CONTAINER_OF(req, GNIRequest, req);
    loop = REQUEST(gni_req)->loop;

    if (status != 0) {
        errorno = PyInt_FromLong((long)status);
        gni_result = Py_None;
        Py_INCREF(Py_None);
        goto callback;
    }

    gni_result = Py_BuildValue("ss", hostname, service);
    if (!gni_result) {
        errorno = PyInt_FromLong((long)UV_ENOMEM);
        gni_result = Py_None;
        Py_INCREF(Py_None);
        goto callback;
    }

    errorno = Py_None;
    Py_INCREF(Py_None);

callback:
    result = PyObject_CallFunctionObjArgs(gni_req->callback, gni_result, errorno, NULL);
    if (result == NULL) {
        handle_uncaught_exception(loop);
    }
    Py_XDECREF(result);
    Py_DECREF(gni_result);
    Py_DECREF(errorno);

    UV_REQUEST(gni_req) = NULL;
    Py_DECREF(gni_req);

    PyGILState_Release(gstate);
}


static PyObject *
Util_func_getaddrinfo(PyObject *obj, PyObject *args, PyObject *kwargs)
{
    char *host_str, *service_str;
    char port_str[6];
    int family, socktype, protocol, flags, err;
    long port;
    struct addrinfo hints;
    Loop *loop;
    GAIRequest *gai_req;
    PyObject *callback, *host, *service, *idna, *ascii;

    static char *kwlist[] = {"loop", "callback", "host", "port", "family", "socktype", "protocol", "flags", NULL};

    UNUSED_ARG(obj);
    gai_req = NULL;
    idna = ascii = NULL;
    port = socktype = protocol = flags = 0;
    family = AF_UNSPEC;
    service = Py_None;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!OO|Oiiii:getaddrinfo", kwlist, &LoopType, &loop, &callback, &host, &service, &family, &socktype, &protocol, &flags)) {
        return NULL;
    }

    if (host == Py_None) {
        host_str = NULL;
    } else if (PyUnicode_Check(host)) {
        idna = PyObject_CallMethod(host, "encode", "s", "idna");
        if (!idna)
            return NULL;
        host_str = PyBytes_AS_STRING(idna);
    } else if (PyBytes_Check(host)) {
        host_str = PyBytes_AsString(host);
    } else {
        PyErr_SetString(PyExc_TypeError, "getaddrinfo() argument 3 must be string or None");
        goto error;
    }

    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "a callable is required");
        goto error;
    }

    if (service == Py_None) {
        service_str = NULL;
    } else if (PyUnicode_Check(service)) {
        ascii = PyObject_CallMethod(service, "encode", "s", "ascii");
        if (!ascii)
            return NULL;
        service_str = PyBytes_AS_STRING(ascii);
    } else if (PyBytes_Check(service)) {
        service_str = PyBytes_AS_STRING(service);
    } else if (PyInt_Check(service)) {
        port = PyInt_AsLong(service);
        if (port < 0 || port > 0xffff) {
            PyErr_SetString(PyExc_ValueError, "port must be between 0 and 65535");
            goto error;
        }
        PyOS_snprintf(port_str, sizeof(port_str), "%ld", port);
        service_str = port_str;
    } else {
        PyErr_SetString(PyExc_TypeError, "getaddrinfo() argument 4 must be string or int");
        goto error;
    }

    gai_req = (GAIRequest *)PyObject_CallFunctionObjArgs((PyObject *)&GAIRequestType, loop, callback, NULL);
    if (!gai_req) {
        PyErr_NoMemory();
        goto error;
    }

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = family;
    hints.ai_socktype = socktype;
    hints.ai_protocol = protocol;
    hints.ai_flags = flags;

    err = uv_getaddrinfo(loop->uv_loop, &gai_req->req, &pyuv__getaddrinfo_cb, host_str, service_str, &hints);
    if (err < 0) {
        RAISE_UV_EXCEPTION(err, PyExc_UVError);
        goto error;
    }

    Py_XDECREF(idna);
    Py_XDECREF(ascii);

    Py_INCREF(gai_req);
    return (PyObject *)gai_req;

error:
    Py_XDECREF(idna);
    Py_XDECREF(ascii);
    Py_XDECREF(gai_req);
    return NULL;
}


static PyObject *
Util_func_getnameinfo(PyObject *obj, PyObject *args, PyObject *kwargs)
{
    int err, flags;
    struct sockaddr_storage ss;
    Loop *loop;
    GNIRequest *gni_req;
    PyObject *callback, *addr;

    static char *kwlist[] = {"loop", "callback", "address", "flags", NULL};

    gni_req = NULL;
    flags = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!OO|i:getaddrinfo", kwlist, &LoopType, &loop, &callback, &addr, &flags)) {
        return NULL;
    }

    if (!PyCallable_Check(callback)) {
        PyErr_SetString(PyExc_TypeError, "a callable is required");
        return NULL;
    }

    if (pyuv_parse_addr_tuple(addr, &ss) < 0) {
        /* Error is set by the function itself */
        return NULL;
    }

    gni_req = (GNIRequest *)PyObject_CallFunctionObjArgs((PyObject *)&GNIRequestType, loop, callback, NULL);
    if (!gni_req) {
        PyErr_NoMemory();
        return NULL;
    }

    err = uv_getnameinfo(loop->uv_loop, &gni_req->req, &pyuv__getnameinfo_cb, (struct sockaddr*) &ss, flags);
    if (err < 0) {
        RAISE_UV_EXCEPTION(err, PyExc_UVError);
        Py_XDECREF(gni_req);
        return NULL;
    }

    Py_INCREF(gni_req);
    return (PyObject *)gni_req;
}


static PyMethodDef
Dns_methods[] = {
    { "getaddrinfo", (PyCFunction)Util_func_getaddrinfo, METH_VARARGS|METH_KEYWORDS, "Getaddrinfo" },
    { "getnameinfo", (PyCFunction)Util_func_getnameinfo, METH_VARARGS|METH_KEYWORDS, "Getnameinfo" },
    { NULL }
};


#ifdef PYUV_PYTHON3
static PyModuleDef pyuv_dns_module = {
    PyModuleDef_HEAD_INIT,
    "pyuv._cpyuv.dns",      /*m_name*/
    NULL,                   /*m_doc*/
    -1,                     /*m_size*/
    Dns_methods,            /*m_methods*/
};
#endif

PyObject *
init_dns(void)
{
    PyObject *module;
#ifdef PYUV_PYTHON3
    module = PyModule_Create(&pyuv_dns_module);
#else
    module = Py_InitModule("pyuv._cpyuv.dns", Dns_methods);
#endif
    if (module == NULL) {
        return NULL;
    }

    /* initialize PyStructSequence types */
    if (AddrinfoResultType.tp_name == 0)
        PyStructSequence_InitType(&AddrinfoResultType, &addrinfo_result_desc);

    return module;
}

