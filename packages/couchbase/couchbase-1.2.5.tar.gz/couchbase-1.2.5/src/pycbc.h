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

#ifndef PYCBC_H_
#define PYCBC_H_
/**
 * This file contains the base header for the Python Couchbase Client
 * @author Mark Nunberg
 */

#include <Python.h>
#include <libcouchbase/couchbase.h>

#if LCB_VERSION < 0x020100
#error "Couchbase Python SDK requires libcouchbase 2.1.0 or greater"
#endif

#include <pythread.h>
#include "viewrow/viewrow.h"

#ifdef PYPY_VERSION
#include "pypy-compat.h"
#define PYCBC_REFCNT_ASSERT(x)
#else
#define PYCBC_REFCNT_ASSERT pycbc_assert
#define pycbc_multiresult_wrap(mres) (PyObject *)(mres)
#endif

#include "mresdict.h"

/**
 * See http://docs.python.org/2/c-api/arg.html for an explanation of this
 * definition.
 */
#ifdef PY_SSIZE_T_CLEAN
typedef Py_ssize_t pycbc_strlen_t;
#else
typedef int pycbc_strlen_t;
#endif

#define PYCBC_PACKAGE_NAME "couchbase"
#define PYCBC_MODULE_NAME "_libcouchbase"
#define PYCBC_FQNAME PYCBC_PACKAGE_NAME "." PYCBC_MODULE_NAME

#define PYCBC_TCNAME_ENCODE_KEY "encode_key"
#define PYCBC_TCNAME_ENCODE_VALUE "encode_value"
#define PYCBC_TCNAME_DECODE_KEY "decode_key"
#define PYCBC_TCNAME_DECODE_VALUE "decode_value"

/**
 * Python 2.x and Python 3.x have different ideas of what a basic string
 * and int types are. These blocks help us sort things out if we just want a
 * "plain" integer or string
 */
#if PY_MAJOR_VERSION == 3
#define PYCBC_POBJ_HEAD_INIT(t) { PyObject_HEAD_INIT(t) },

/**
 * The IntFrom* macros get us a 'default' integer type from a long, etc.
 * Implemented (if not a simple macro) in numutil.c
 */
#define pycbc_IntFromL PyLong_FromLong
#define pycbc_IntFromUL PyLong_FromUnsignedLong
#define pycbc_IntFromULL PyLong_FromUnsignedLongLong

/**
 * The IntAs* convert the integer type (long, int) into something we want
 */
#define pycbc_IntAsULL PyLong_AsUnsignedLongLong
#define pycbc_IntAsLL PyLong_AsLongLong
#define pycbc_IntAsUL PyLong_AsUnsignedLong
#define pycbc_IntAsL PyLong_AsLong

/**
 * The SimpleString macros generate strings for us. The 'Z' variant takes a
 * NUL-terminated string, while the 'N' variant accepts a length specifier
 */
#define pycbc_SimpleStringZ(c) PyUnicode_FromString(c)
#define pycbc_SimpleStringN(c, n) PyUnicode_FromStringAndSize(c, n)


#else

/**
 * This defines the PyObject head for our types
 */
#define PYCBC_POBJ_HEAD_INIT(t) PyObject_HEAD_INIT(t)

/**
 * See above block for explanation of these macros
 */
#define pycbc_IntFromL PyInt_FromLong
#define pycbc_IntFromUL PyLong_FromUnsignedLong
#define pycbc_IntFromULL PyLong_FromUnsignedLongLong
#define pycbc_SimpleStringZ(c) PyString_FromString(c)
#define pycbc_SimpleStringN(c, n) PyString_FromStringAndSize(c, n)

unsigned PY_LONG_LONG pycbc_IntAsULL(PyObject *o);
PY_LONG_LONG pycbc_IntAsLL(PyObject *o);
long pycbc_IntAsL(PyObject *o);
unsigned long pycbc_IntAsUL(PyObject *o);


#endif

/**
 * Fetches a valid TTL from the object
 * @param obj an object to be parsed as the TTL
 * @param ttl a pointer to the TTL itself
 * @param nonzero whether to allow a value of 0 for the TTL
 * @return 0 on success, nonzero on error.
 */
int pycbc_get_ttl(PyObject *obj, unsigned long *ttl, int nonzero);

/**
 * Fetches a valid 32 bit integer from the object. The object must be a long
 * or int.
 * @param obj the object containing the number
 * @param out a pointer to a 32 bit integer to be populated
 * @return 0 on success, -1 on failure. On failure, the error indicator is also
 * set
 */
int pycbc_get_u32(PyObject *obj, lcb_uint32_t *out);

/**
 * Converts the object into an PyInt (2.x only) or PyLong (2.x or 3.x)
 */
PyObject *pycbc_maybe_convert_to_int(PyObject *o);

/**
 * Gives us a C buffer from a Python string.
 * @param orig the original object containg a string thing. This is something
 * we can convert into a byte buffer
 *
 * @param buf out, the C buffer, out, set to the new buffer
 * @param nbuf, out, the length of the new buffer
 * @param newkey, out, the new PyObject, which will back the buffer.
 * This should not be DECREF'd until the @c buf is no longer needed
 */
int pycbc_BufFromString(PyObject *orig,
                        char **buf,
                        Py_ssize_t *nbuf,
                        PyObject **newkey);


/**
 * These constants are used internally to figure out the high level
 * operation being performed.
 *
 * Note that not all operations are defined here; it is only those operations
 * where a single C function can handle multiple entry points.
 */
enum {
    PYCBC_CMD_GET = 500,
    PYCBC_CMD_LOCK,
    PYCBC_CMD_TOUCH,
    PYCBC_CMD_GAT,
    PYCBC_CMD_INCR,
    PYCBC_CMD_DECR,
    PYCBC_CMD_ARITH,
    PYCBC_CMD_DELETE,
    PYCBC_CMD_UNLOCK,
    PYCBC_CMD_GETREPLICA,
    /** "Extended" get replica, provides for more options */
    PYCBC_CMD_GETREPLICA_INDEX,
    PYCBC_CMD_GETREPLICA_ALL,
    PYCBC_CMD_ENDURE
};

/**
 * Various exception types to be thrown
 */
enum {
    /** Argument Error. User passed the wrong arguments */
    PYCBC_EXC_ARGUMENTS,

    /** Couldn't encode/decode something */
    PYCBC_EXC_ENCODING,

    /** Operational error returned from LCB */
    PYCBC_EXC_LCBERR,

    /** Internal error. There's something wrong with our code */
    PYCBC_EXC_INTERNAL,

    /** HTTP Error */
    PYCBC_EXC_HTTP,

    /** ObjectThreadError */
    PYCBC_EXC_THREADING,

    /** Object destroyed before it could connect */
    PYCBC_EXC_DESTROYED,

    /** Illegal operation in pipeline context */
    PYCBC_EXC_PIPELINE
};

/* Argument options */
enum {
    /** Entry point is a single key variant */
    PYCBC_ARGOPT_SINGLE = 0x1,

    /** Entry point is a multi key variant */
    PYCBC_ARGOPT_MULTI = 0x2
};

/**
 * Format flags
 */
enum {
    PYCBC_FMT_JSON = 0x0,
    PYCBC_FMT_PICKLE = 0x1,
    PYCBC_FMT_BYTES = 0x2,

    PYCBC_FMT_UTF8 = 0x4,

    PYCBC_FMT_MASK = 0x7
};

typedef enum {
    PYCBC_LOCKMODE_NONE = 0,
    PYCBC_LOCKMODE_EXC = 1,
    PYCBC_LOCKMODE_WAIT = 2,
    PYCBC_LOCKMODE_MAX
} pycbc_lockmode_t;

enum {
    PYCBC_CONN_F_WARNEXPLICIT = 1 << 0,
    PYCBC_CONN_F_USEITEMRESULT = 1 << 1,
    PYCBC_CONN_F_CLOSED = 1 << 2,

    /**
     * For use with (but not limited to) Twisted.
     *
     * Deliver results asynchronously. This means:
     * 1) Don't call lcb_wait()
     * 2) Return an AsyncContainer (i.e. a MultiResult)
     * 3) Invoke the MultiResult (AsyncContainer)'s callback as needed
     */
    PYCBC_CONN_F_ASYNC = 1 << 3,

    /** Whether this instance has been connected */
    PYCBC_CONN_F_CONNECTED = 1 << 4,

    /** Schedule destruction of iops and lcb instance for later */
    PYCBC_CONN_F_ASYNC_DTOR = 1 << 5
};

typedef struct {
    char persist_to;
    char replicate_to;
} pycbc_dur_params;

typedef struct {
    PyObject_HEAD

    /** LCB instance */
    lcb_t instance;

    /** Transcoder object */
    PyObject *tc;

    /** Default format, PyInt */
    PyObject *dfl_fmt;

    /** Connection Errors */
    PyObject *errors;

    /** Callback to be invoked when connected */
    PyObject *conncb;

    /**
     * Callback to be invoked upon destruction. Because we can fall out
     * of scope in middle of an LCB function, this is required.
     *
     * The dtorcb is first called when the refcount of the connection
     */
    PyObject *dtorcb;

    /**
     * Test hook for reacting to durability/persistence settings from within
     * mutator functions
     */
    PyObject *dur_testhook;


    /** String bucket */
    PyObject *bucket;

    /** Pipeline MultiResult container */
    PyObject *pipeline_queue;

    /** If using a custom IOPS, this contains it */
    lcb_io_opt_t iops;

    /** Thread state. Used to lock/unlock the GIL */
    PyThreadState *thrstate;

    PyThread_type_lock lock;
    unsigned int lockmode;

    /** Whether to not raise any exceptions */
    unsigned int quiet;

    /** Whether GIL handling is in effect */
    unsigned int unlock_gil;

    /** Don't decode anything */
    unsigned int data_passthrough;

    /** whether __init__ has already been called */
    unsigned char init_called;

    /** How many operations are waiting for a reply */
    Py_ssize_t nremaining;

    unsigned int flags;

    pycbc_dur_params dur_global;
    unsigned long dur_timeout;

} pycbc_Connection;


/*****************
 * Result Objects.
 *****************
 *
 * These objects are returned to indicate the status/value of operations.
 * The following defines a 'base' class and several 'subclasses'.
 *
 * See result.c and opresult.c
 */

#define pycbc_Result_HEAD \
    PyObject_HEAD \
    lcb_error_t rc; \
    PyObject *key;

#define pycbc_OpResult_HEAD \
    pycbc_Result_HEAD \
    lcb_uint64_t cas;

typedef struct {
    pycbc_Result_HEAD
} pycbc_Result;

typedef struct {
    pycbc_OpResult_HEAD
} pycbc_OperationResult;


#define pycbc_ValResult_HEAD \
    pycbc_OpResult_HEAD \
    PyObject *value; \
    lcb_uint32_t flags;

typedef struct {
    pycbc_ValResult_HEAD
} pycbc_ValueResult;

/**
 * Item or 'Document' object
 */
typedef struct {
    pycbc_ValResult_HEAD
    PyObject* vdict;
} pycbc_Item;

typedef struct {
    pycbc_Result_HEAD
    PyObject *http_data;
    PyObject *headers;

    /**
     * Metadata about the result
     */
    PyObject *rowsbuf;

    /**
     * Callback to invoke upon receipt of data
     */
    PyObject *callback;

    /**
     * Row parser context.
     */
    lcbex_vrow_ctx_t *rctx;

    /**
     * HTTP Request handle
     */
    lcb_http_request_t htreq;


    pycbc_Connection *parent;
    long rows_per_call;
    unsigned short htcode;
    unsigned short format;
    unsigned short htflags;
} pycbc_HttpResult;

enum {
    PYCBC_HTRES_F_CHUNKED   = 1 << 0,
    PYCBC_HTRES_F_QUIET     = 1 << 1,
    PYCBC_HTRES_F_COMPLETE  = 1 << 2
};

PyObject* pycbc_HttpResult__fetch(pycbc_HttpResult *self);
PyObject* pycbc_HttpResult__maybe_raise(pycbc_HttpResult *self);


enum {
    /** 'quiet' boolean set */
    PYCBC_MRES_F_QUIET      = 1 << 0,

    /** We're using a user-created Item; Don't create our own results */
    PYCBC_MRES_F_ITEMS      = 1 << 1,

    /** Items are already allocated and present within the dictionary. */
    PYCBC_MRES_F_UALLOCED   = 1 << 2,

    /** For GET (and possibly others), force FMT_BYTES */
    PYCBC_MRES_F_FORCEBYTES = 1 << 3,

    /** The commands have durability requirements */
    PYCBC_MRES_F_DURABILITY = 1 << 4,

    /** The command is an async subclass. Do we need this? */
    PYCBC_MRES_F_ASYNC = 1 << 5,

    /** This result is from a call to one of the single-item APIs */
    PYCBC_MRES_F_SINGLE = 1 << 6
};
/**
 * Object containing the result of a 'Multi' operation. It's the same as a
 * normal dict, except we add an 'all_ok' field, so a user doesn't need to
 * skim through all the pairs to determine if something failed.
 *
 * See multiresult.c
 */
typedef struct pycbc_MultiResult_st {
    PYCBC_MULTIRESULT_BASE;

    /** parent Connection object */
    pycbc_Connection *parent;

    /**
     * A list of fatal exceptions, i.e. ones not resulting from a bad
     * LCB error code
     */
    PyObject *exceptions;

    /** A failed LCB operation, if any */
    PyObject *errop;

    pycbc_dur_params dur;

    /** Quick-check value to see if everything went well */
    int all_ok;

    /** Options for 'MultiResult' */
    int mropts;
} pycbc_MultiResult;

typedef struct {
    pycbc_MultiResult base;

    /* How many operations do we have remaining */
    unsigned int nops;

    /* Object for the callback */
    PyObject *callback;

    /* Object to be invoked with errors */
    PyObject *errback;
} pycbc_AsyncResult;


/**
 * This structure is passed to our exception throwing function, it's
 * usually wrapped by one of the macros below
 */
struct pycbc_exception_params {
    /** C Source file at which the error was thrown (populated by macro */
    const char *file;

    /** C Source line, as above */
    int line;

    /** LCB Error code, if any */
    lcb_error_t err;

    /** Error message, if any */
    const char *msg;

    /** Key at which the error occurred. Not always present */
    PyObject *key;

    /** Single result which triggered the error, if present */
    PyObject *result;

    /**
     * A MultiResult object. This contains other operations which may
     * or may not have failed. This allows a user to check the status
     * of multi operations in which one of the keys resulted in an
     * exception
     */
    PyObject *all_results;

    /**
     * Extra info which caused the error. This is usually some kind of
     * bad parameter.
     */
    PyObject *objextra;
};

/**
 * Initializes a pycbc_exception_params to contain the proper
 * source context info
 */
#define PYCBC_EXC_STATIC_INIT { __FILE__, __LINE__ }

/**
 * Argument object, used for passing more information to the
 * multi functions. This isn't documented API yest.
 */
typedef struct {
    PyDictObject dict;
    int dummy; /* avoid sizing issues */
} pycbc_ArgumentObject;


/**
 * Object used as the 'value' for observe responses
 */
typedef struct {
    PyObject_HEAD
    unsigned int flags;
    int from_master;
    unsigned PY_LONG_LONG cas;
} pycbc_ObserveInfo;

/**
 * Flags to use for each type to indicate which subfields are relevant to
 * print out.
 */
enum {
    PYCBC_RESFLD_RC     = 1 << 0,
    PYCBC_RESFLD_CAS    = 1 << 1,
    PYCBC_RESFLD_KEY    = 1 << 2,
    PYCBC_RESFLD_FLAGS  = 1 << 3,
    PYCBC_RESFLD_HTCODE = 1 << 4,
    PYCBC_RESFLD_VALUE  = 1 << 5,
    PYCBC_RESFLD_URL    = 1 << 6
};

#define PYCBC_RESULT_BASEFLDS (PYCBC_RESFLD_RC)
#define PYCBC_OPRESULT_BASEFLDS \
    (PYCBC_RESULT_BASEFLDS| \
            PYCBC_RESFLD_CAS| \
            PYCBC_RESFLD_KEY)

#define PYCBC_VALRESULT_BASEFLDS (PYCBC_OPRESULT_BASEFLDS| \
        PYCBC_RESFLD_VALUE| \
        PYCBC_RESFLD_FLAGS)

#define PYCBC_HTRESULT_BASEFLDS \
    (       PYCBC_RESULT_BASEFLDS   | \
            PYCBC_RESFLD_HTCODE     | \
            PYCBC_RESFLD_URL        | \
            PYCBC_RESFLD_VALUE)

#define PYCBC_RESPROPS_NAME "_fldprops"
/**
 * Wrapper around PyType_Ready which also injects the common flags properties
 */
int pycbc_ResultType_ready(PyTypeObject *p, int flags);


/**
 * Extern PyTypeObject declaraions.
 */

/* multiresult.c */
extern PyTypeObject pycbc_MultiResultType;
extern PyTypeObject pycbc_AsyncResultType;

/* result.c */
extern PyTypeObject pycbc_ResultType;

/* opresult.c */
extern PyTypeObject pycbc_OperationResultType;
extern PyTypeObject pycbc_ValueResultType;
extern PyTypeObject pycbc_HttpResultType;

/**
 * Result type check macros
 */
#define PYCBC_VALRES_CHECK(o) \
        PyObject_IsInstance(o, &pycbc_ValueResultType)

#define PYCBC_OPRES_CHECK(o) \
    PyObject_IsInstance(o, (PyObject*)&pycbc_OperationResultType)

extern PyTypeObject pycbc_ArgumentType;

/**
 * XXX: This isn't used.
 */
extern PyObject *pycbc_ExceptionType;

/**
 * X-macro to define the helpers we pass from _bootstrap.py along to
 * the module's '_init_helpers' function. We use an xmacro here because
 * the parameters may change and the argument handling is rather complex.
 * See below (in the pycbc_helpers structure) and in ext.c for more usages.
 */
#define PYCBC_XHELPERS(X) \
    X(result_reprfunc) \
    X(fmt_utf8_flags) \
    X(fmt_bytes_flags) \
    X(fmt_json_flags) \
    X(fmt_pickle_flags) \
    X(pickle_encode) \
    X(pickle_decode) \
    X(json_encode) \
    X(json_decode) \
    X(lcb_errno_map) \
    X(misc_errno_map) \
    X(default_exception) \
    X(obsinfo_reprfunc) \
    X(itmcoll_base_type) \
    X(itmopts_dict_type) \
    X(itmopts_seq_type) \
    X(fmt_auto) \
    X(pypy_mres_factory)

#define PYCBC_XHELPERS_STRS(X) \
    X(tcname_encode_key, PYCBC_TCNAME_ENCODE_KEY) \
    X(tcname_encode_value, PYCBC_TCNAME_ENCODE_VALUE) \
    X(tcname_decode_key, PYCBC_TCNAME_DECODE_KEY) \
    X(tcname_decode_value, PYCBC_TCNAME_DECODE_VALUE) \
    X(ioname_modevent, "update_event") \
    X(ioname_modtimer, "update_timer") \
    X(ioname_startwatch, "start_watching") \
    X(ioname_stopwatch, "stop_watching") \
    X(ioname_mkevent, "io_event_factory") \
    X(ioname_mktimer, "timer_event_factory")

/**
 * Definition of global helpers. This is only instantiated once as
 * pycbc_helpers.
 */
struct pycbc_helpers_ST {
    #define X(n) PyObject *n;
    PYCBC_XHELPERS(X)
    #undef X

    #define X(n, s) PyObject *n;
    PYCBC_XHELPERS_STRS(X)
    #undef X
};

/**
 * We use this one a lot. This is defined in ext.c
 */
extern struct pycbc_helpers_ST pycbc_helpers;

/**
 * Threading macros
 */
#define PYCBC_USE_THREADS

#ifdef PYCBC_USE_THREADS
#define PYCBC_CONN_THR_BEGIN(conn) \
    if ((conn)->unlock_gil) { \
        pycbc_assert((conn)->thrstate == NULL); \
        (conn)->thrstate = PyEval_SaveThread(); \
    }

#define PYCBC_CONN_THR_END(conn) \
    if ((conn)->unlock_gil) { \
        pycbc_assert((conn)->thrstate); \
        PyEval_RestoreThread((conn)->thrstate); \
        (conn)->thrstate = NULL; \
    }

#else
#define PYCBC_CONN_THR_BEGIN(X)
#define PYCBC_CONN_THR_END(X)
#endif

/*******************************
 * Type Initialization Functions
 *******************************
 *
 * These functions are called once from the extension's import method.
 * See ext.c
 *
 * They basically initialize the corresponding Python type so that
 * we can use them further on.
 */

/** Initializes the constants, constants. */
void pycbc_init_pyconstants(PyObject *module);
PyObject *pycbc_lcb_errstr(lcb_t instance, lcb_error_t err);

int pycbc_ResultType_init(PyObject **ptr);
int pycbc_ConnectionType_init(PyObject **ptr);
int pycbc_MultiResultType_init(PyObject **ptr);
int pycbc_ValueResultType_init(PyObject **ptr);
int pycbc_OperationResultType_init(PyObject **ptr);
int pycbc_HttpResultType_init(PyObject **ptr);
int pycbc_TranscoderType_init(PyObject **ptr);
int pycbc_ObserveInfoType_init(PyObject **ptr);
int pycbc_ItemType_init(PyObject **ptr);
int pycbc_EventType_init(PyObject **ptr);
int pycbc_TimerEventType_init(PyObject **ptr);
int pycbc_IOEventType_init(PyObject **ptr);
int pycbc_AsyncResultType_init(PyObject **ptr);

/**
 * Calls the type's constructor with no arguments:
 */
#define PYCBC_TYPE_CTOR(t) PyObject_CallFunction((PyObject*)t, NULL, NULL)


/**
 * Allocators for result functions. See callbacks.c:get_common
 */
PyObject *pycbc_result_new(pycbc_Connection *parent);
PyObject *pycbc_multiresult_new(pycbc_Connection *parent);
pycbc_ValueResult *pycbc_valresult_new(pycbc_Connection *parent);
pycbc_OperationResult *pycbc_opresult_new(pycbc_Connection *parent);
pycbc_HttpResult *pycbc_httpresult_new(pycbc_Connection *parent);
pycbc_Item *pycbc_item_new(pycbc_Connection *parent);

/* For observe info */
pycbc_ObserveInfo * pycbc_observeinfo_new(pycbc_Connection *parent);

/**
 * If an HTTP result was successful or not
 */
int pycbc_httpresult_ok(pycbc_HttpResult *self);

/**
 * Simple function, here because it's defined in result.c but needed in
 * opresult.c
 */
void pycbc_Result_dealloc(pycbc_Result *self);

/**
 * Raise an exception from a multi result. This will raise an exception if:
 * 1) There is a 'fatal' error in the 'exceptions' list
 * 2) There is an 'operr'. 'operr' can be a failed LCB code (if no_raise_enoent
 * is on, this is not present if the failed code was LCB_KEY_ENOENT)
 */
int pycbc_multiresult_maybe_raise(pycbc_MultiResult *self);

/**
 * Return the effective user-facing value from this MultiResult object.
 * This should only be called if 'maybe_raise' returns false.
 * @param self the object
 * @return a new reference to the final result, or NULL on error.
 */
PyObject* pycbc_multiresult_get_result(pycbc_MultiResult *self);

/**
 * Invokes a callback when an operation has been completed. This will either
 * invoke the operation's "error callback" or the operation's "result callback"
 * depending on the state.
 */
void pycbc_asyncresult_invoke(pycbc_AsyncResult *mres);

/**
 * Initialize the callbacks for the lcb_t
 */
void pycbc_callbacks_init(lcb_t instance);
void pycbc_http_callbacks_init(lcb_t instance);


/**
 * "Real" exception handler.
 * @param mode one of the PYCBC_EXC_* constants
 * @param p a struct of exception parameters
 */
void pycbc_exc_wrap_REAL(int mode, struct pycbc_exception_params *p);

/**
 * Get the appropriate Couchbase exception object.
 * @param mode one of the PYCBC_EXC_* constants
 * @param err the libcouchbase error, if any
 * @return a borrowed reference to the appropriate exception class
 */
PyObject* pycbc_exc_map(int mode, lcb_error_t err);

/**
 * Creates a simple exception with a given message. The exception
 * is not thrown.
 */
PyObject* pycbc_exc_message(int mode, lcb_error_t err, const char *msg);

/**
 * Gets the error classifier categories (as a set of bit flags) for a given
 * error code.
 */
PyObject* pycbc_exc_get_categories(PyObject *self, PyObject *arg);
/**
 * Throws an exception. If an exception is pending, it is caught and wrapped,
 * delivered into the CouchbaseError's 'inner_cause' field
 *
 * @param e_mode one of the PYCBC_EXC_* constants
 * @param e_err the LCB error code (use 0 if none)
 * @param e_msg a string message, if any
 * @param e_key the key during the handling of which the error occurred
 * @param e_objextra the problematic object which actually caused the errror
 */
#define PYCBC_EXC_WRAP_EX(e_mode, e_err, e_msg, e_key, e_objextra) { \
    struct pycbc_exception_params __pycbc_ep = {0}; \
    __pycbc_ep.file = __FILE__; \
    __pycbc_ep.line = __LINE__; \
    __pycbc_ep.err = e_err; \
    __pycbc_ep.msg = e_msg; \
    __pycbc_ep.key = e_key; \
    __pycbc_ep.objextra = e_objextra; \
    pycbc_exc_wrap_REAL(e_mode, &__pycbc_ep); \
}

#define PYCBC_EXC_WRAP(mode, err, msg) \
        PYCBC_EXC_WRAP_EX(mode, err, msg, NULL, NULL)

#define PYCBC_EXC_WRAP_OBJ(mode, err, msg, obj) \
    PYCBC_EXC_WRAP_EX(mode, err, msg, NULL, obj)

#define PYCBC_EXC_WRAP_KEY(mode, err, msg, key) \
    PYCBC_EXC_WRAP_EX(mode, err, msg, key, NULL)

#define PYCBC_EXC_WRAP_VALUE PYCBC_EXC_WRAP_KEY

int pycbc_handle_assert(const char *msg, const char* file, int line);

/**
 * This macro can be used as an 'if' structure. It returns false if the
 * condition fails and try otherwise
 */
#define pycbc_assert(e) ((e) ? 1 : pycbc_handle_assert(#e, __FILE__, __LINE__))

/**
 * EXCTHROW macros. These provide error messages for common stages.
 */
#define PYCBC_EXCTHROW_WAIT(err) PYCBC_EXC_WRAP(PYCBC_EXC_LCBERR, err, \
       "There was a problem while trying to send/receive " \
       "your request over the network. This may be a result of a " \
       "bad network or a misconfigured client or server")

#define PYCBC_EXCTHROW_SCHED(err) PYCBC_EXC_WRAP(PYCBC_EXC_LCBERR, err, \
        "There was a problem scheduling your request, or determining " \
        "the appropriate server or vBucket for the key(s) requested. "\
        "This may also be a bug in the SDK if there are no network issues")

#define PYCBC_EXCTHROW_ARGS() PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS, 0, \
                                           "Bad/insufficient arguments provided")

#define PYCBC_EXCTHROW_EMPTYKEY() PYCBC_EXC_WRAP(PYCBC_EXC_ARGUMENTS, 0, \
        "Empty key (i.e. '', empty string) passed")

/**
 * Encodes a key into a buffer.
 * @param conn the connection object
 * @param key. in-out. Input should be the Python key. Output should be the
 * new python object which contains the underlying buffer for the key.
 * @param buf a pointer to a buffer pointer
 * @param nbuf pointer to the length of the buffer
 *
 * The buf parameter will likely be tied to the key parameter, so be sure not
 * to decrement its refcount until buf is no longer needed
 *
 * @return
 * 0 on success, nonzero on error
 */
int pycbc_tc_encode_key(pycbc_Connection *conn,
                        PyObject **key,
                        void **buf,
                        size_t *nbuf);

/**
 * Decodes a key buffer into a python object.
 * @param conn the connection object
 * @param key the key buffer
 * @param nkey the size of the key
 * @param pobj a pointer to a PyObject*, will be set with a newly-created python
 * object which represents the converted key
 *
 * @return
 * 0 on success, nonzero on error
 */
int pycbc_tc_decode_key(pycbc_Connection *conn,
                        const void *key,
                        size_t nkey,
                        PyObject **pobj);

/**
 * Encode a value with flags
 * @param value. in-out. Input should be the Python value, Output should be the
 * new python object which contains the converted value.
 * @param flag_v. Python object representing 'flags'. This is used for efficiency
 * in order to pass a pythonized version of the flags
 * @param buf a pointer to a buffer, likely tied to 'buf'
 * @param nbuf pointer to buffer length
 * @param flags pointer to a flags variable, will be set with the appropriate
 * flags
 */
int pycbc_tc_encode_value(pycbc_Connection *conn,
                          PyObject **value,
                          PyObject *flag_v,
                          void **buf,
                          size_t *nbuf,
                          lcb_uint32_t *flags);

/**
 * Decode a value with flags
 * @param conn the connection object
 * @param value as received from the server
 * @param nvalue length of value
 * @param flags flags as received from the server
 * @param pobj the pythonized value
 */
int pycbc_tc_decode_value(pycbc_Connection *conn,
                          const void *value,
                          size_t nvalue,
                          lcb_uint32_t flags,
                          PyObject **pobj);



/**
 * Like encode_value, but only uses built-in encoders
 */
int pycbc_tc_simple_encode(PyObject **p,
                           void *buf,
                           size_t *nbuf,
                           lcb_uint32_t flags);

/**
 * Like decode_value, but only uses built-in decoders
 */
int pycbc_tc_simple_decode(PyObject **vp,
                           const char *buf,
                           size_t nbuf,
                           lcb_uint32_t flags);

/**
 * Automatically determine the format for the object.
 */
PyObject *
pycbc_tc_determine_format(PyObject *value);

/** IOPS Initializer */
lcb_io_opt_t pycbc_iops_new(pycbc_Connection *conn, PyObject *pyio);
void pycbc_iops_free(lcb_io_opt_t io);
PyObject * pycbc_event_new(void);

/**
 * Event callback handling
 */
void pycbc_invoke_connected_event(pycbc_Connection *conn, lcb_error_t err);

/**
 * Schedule the dtor event
 */
void pycbc_schedule_dtor_event(pycbc_Connection *self);

/**
 * Invoke the error callback to log messages
 */
void pycbc_invoke_error_callback(pycbc_Connection *self,
                                 lcb_error_t err, const char *msg);

/**
 * Pipeline handlers
 */
PyObject* pycbc_Connection__start_pipeline(pycbc_Connection *);
PyObject* pycbc_Connection__end_pipeline(pycbc_Connection *);

/**
 * Control methods
 */
PyObject* pycbc_Connection__cntl(pycbc_Connection *, PyObject *, PyObject *);
PyObject* pycbc_Connection__vbmap(pycbc_Connection *, PyObject *);
#endif /* PYCBC_H_ */
