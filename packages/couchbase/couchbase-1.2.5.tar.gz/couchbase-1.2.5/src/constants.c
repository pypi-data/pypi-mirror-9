/**
 *     Copyright 2013 Couchbase, Inc.
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 **/

#include "pycbc.h"
#include "iops.h"

/**
 * Very simple file that simply adds LCB constants to the module
 */

#define XERR(X) \
    X(SUCCESS) \
    X(AUTH_CONTINUE) \
    X(AUTH_ERROR) \
    X(DELTA_BADVAL) \
    X(E2BIG) \
    X(EBUSY) \
    X(ENOMEM) \
    X(ERANGE) \
    X(ERROR) \
    X(ETMPFAIL) \
    X(CLIENT_ETMPFAIL) \
    X(KEY_EEXISTS) \
    X(KEY_ENOENT) \
    X(DLOPEN_FAILED) \
    X(DLSYM_FAILED) \
    X(NETWORK_ERROR) \
    X(NOT_MY_VBUCKET) \
    X(NOT_STORED) \
    X(NOT_SUPPORTED) \
    X(UNKNOWN_HOST) \
    X(PROTOCOL_ERROR) \
    X(ETIMEDOUT) \
    X(BUCKET_ENOENT) \
    X(CONNECT_ERROR) \
    X(EBADHANDLE) \
    X(SERVER_BUG) \
    X(PLUGIN_VERSION_MISMATCH) \
    X(INVALID_HOST_FORMAT) \
    X(INVALID_CHAR) \
    X(DURABILITY_ETOOMANY) \
    X(DUPLICATE_COMMANDS)

#define XHTTP(X) \
    X(HTTP_METHOD_GET) \
    X(HTTP_METHOD_POST) \
    X(HTTP_METHOD_PUT) \
    X(HTTP_METHOD_DELETE)



#define XSTORAGE(X) \
    X(ADD) \
    X(REPLACE) \
    X(SET) \
    X(APPEND) \
    X(PREPEND)

void
pycbc_init_pyconstants(PyObject *module)
{
#define X(b) \
    PyModule_AddIntMacro(module, LCB_##b);
    XERR(X);
    XSTORAGE(X);
    XHTTP(X);
#undef X

    PyModule_AddIntMacro(module, PYCBC_CMD_GET);
    PyModule_AddIntMacro(module, PYCBC_CMD_LOCK);
    PyModule_AddIntMacro(module, PYCBC_CMD_TOUCH);
    PyModule_AddIntMacro(module, PYCBC_CMD_GAT);
    PyModule_AddIntMacro(module, PYCBC_CMD_INCR);
    PyModule_AddIntMacro(module, PYCBC_CMD_DECR);

    PyModule_AddIntMacro(module, PYCBC_EXC_ARGUMENTS);
    PyModule_AddIntMacro(module, PYCBC_EXC_ENCODING);
    PyModule_AddIntMacro(module, PYCBC_EXC_LCBERR);
    PyModule_AddIntMacro(module, PYCBC_EXC_INTERNAL);
    PyModule_AddIntMacro(module, PYCBC_EXC_HTTP);
    PyModule_AddIntMacro(module, PYCBC_EXC_THREADING);
    PyModule_AddIntMacro(module, PYCBC_EXC_DESTROYED);
    PyModule_AddIntMacro(module, PYCBC_EXC_PIPELINE);

    PyModule_AddIntMacro(module, LCB_TYPE_BUCKET);
    PyModule_AddIntMacro(module, LCB_TYPE_CLUSTER);
    PyModule_AddIntMacro(module, LCB_HTTP_TYPE_VIEW);
    PyModule_AddIntMacro(module, LCB_HTTP_TYPE_MANAGEMENT);

    PyModule_AddIntMacro(module, PYCBC_RESFLD_CAS);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_FLAGS);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_KEY);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_VALUE);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_RC);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_HTCODE);
    PyModule_AddIntMacro(module, PYCBC_RESFLD_URL);

    PyModule_AddIntConstant(module, "FMT_JSON", PYCBC_FMT_JSON);
    PyModule_AddIntConstant(module, "FMT_BYTES", PYCBC_FMT_BYTES);
    PyModule_AddIntConstant(module, "FMT_UTF8", PYCBC_FMT_UTF8);
    PyModule_AddIntConstant(module, "FMT_PICKLE", PYCBC_FMT_PICKLE);
    PyModule_AddIntConstant(module, "FMT_MASK", PYCBC_FMT_MASK);

    PyModule_AddIntConstant(module, "OBS_PERSISTED", LCB_OBSERVE_PERSISTED);
    PyModule_AddIntConstant(module, "OBS_FOUND", LCB_OBSERVE_FOUND);
    PyModule_AddIntConstant(module, "OBS_NOTFOUND", LCB_OBSERVE_NOT_FOUND);
    PyModule_AddIntConstant(module, "OBS_LOGICALLY_DELETED",
                            LCB_OBSERVE_PERSISTED|
                            LCB_OBSERVE_NOT_FOUND);

    PyModule_AddIntConstant(module, "OBS_MASK",
                            LCB_OBSERVE_PERSISTED|
                            LCB_OBSERVE_FOUND|
                            LCB_OBSERVE_NOT_FOUND);

    PyModule_AddIntConstant(module, "LOCKMODE_WAIT", PYCBC_LOCKMODE_WAIT);
    PyModule_AddIntConstant(module, "LOCKMODE_EXC", PYCBC_LOCKMODE_EXC);
    PyModule_AddIntConstant(module, "LOCKMODE_NONE", PYCBC_LOCKMODE_NONE);

    PyModule_AddIntMacro(module, PYCBC_CONN_F_WARNEXPLICIT);
    PyModule_AddIntMacro(module, PYCBC_CONN_F_CLOSED);
    PyModule_AddIntMacro(module, PYCBC_CONN_F_ASYNC);
    PyModule_AddIntMacro(module, PYCBC_CONN_F_ASYNC_DTOR);

    PyModule_AddIntMacro(module, PYCBC_EVACTION_WATCH);
    PyModule_AddIntMacro(module, PYCBC_EVACTION_UNWATCH);
    PyModule_AddIntMacro(module, PYCBC_EVACTION_SUSPEND);
    PyModule_AddIntMacro(module, PYCBC_EVACTION_RESUME);
    PyModule_AddIntMacro(module, PYCBC_EVACTION_CLEANUP);
    PyModule_AddIntMacro(module, PYCBC_EVSTATE_INITIALIZED);
    PyModule_AddIntMacro(module, PYCBC_EVSTATE_ACTIVE);
    PyModule_AddIntMacro(module, PYCBC_EVSTATE_SUSPENDED);
    PyModule_AddIntMacro(module, PYCBC_EVTYPE_IO);
    PyModule_AddIntMacro(module, PYCBC_EVTYPE_TIMER);
    PyModule_AddIntMacro(module, LCB_READ_EVENT);
    PyModule_AddIntMacro(module, LCB_WRITE_EVENT);
    PyModule_AddIntMacro(module, LCB_RW_EVENT);

#if LCB_VERSION < 0x020300
#define LCB_ERRTYPE_DATAOP 0
#define LCB_ERRTYPE_FATAL 0
#define LCB_ERRTYPE_INTERNAL 0
#define LCB_ERRTYPE_NETWORK 0
#define LCB_ERRTYPE_TRANSIENT 0
#define LCB_ERRTYPE_INPUT 0
#endif
    PyModule_AddIntMacro(module, LCB_ERRTYPE_DATAOP);
    PyModule_AddIntMacro(module, LCB_ERRTYPE_FATAL);
    PyModule_AddIntMacro(module, LCB_ERRTYPE_INTERNAL);
    PyModule_AddIntMacro(module, LCB_ERRTYPE_NETWORK);
    PyModule_AddIntMacro(module, LCB_ERRTYPE_TRANSIENT);
    PyModule_AddIntMacro(module, LCB_ERRTYPE_INPUT);
}


PyObject *
pycbc_lcb_errstr(lcb_t instance, lcb_error_t err)
{
#if PY_MAJOR_VERSION == 3

    return PyUnicode_InternFromString(lcb_strerror(instance, err));
#else
    return PyString_InternFromString(lcb_strerror(instance, err));
#endif

}
