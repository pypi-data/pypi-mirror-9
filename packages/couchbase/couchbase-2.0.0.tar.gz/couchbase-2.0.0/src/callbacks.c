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

#define CB_THREADS

#ifdef CB_THREADS

static void
cb_thr_end(pycbc_Bucket *self)
{
    PYCBC_CONN_THR_END(self);
    Py_INCREF((PyObject *)self);
}

static void
cb_thr_begin(pycbc_Bucket *self)
{
    if (Py_REFCNT(self) > 1) {
        Py_DECREF(self);
        PYCBC_CONN_THR_BEGIN(self);
        return;
    }

    pycbc_assert(self->unlock_gil == 0);
    Py_DECREF(self);
}

#define CB_THR_END cb_thr_end
#define CB_THR_BEGIN cb_thr_begin
#else
#define CB_THR_END(x)
#define CB_THR_BEGIN(x)
#endif


enum {
    RESTYPE_BASE = 1 << 0,
    RESTYPE_VALUE = 1 << 1,
    RESTYPE_OPERATION = 1 << 2,

    /* Extra flag indicating it's ok if it already exists */
    RESTYPE_EXISTS_OK = 1 << 3,

    /* Don't modify "remaining" count */
    RESTYPE_VARCOUNT = 1 << 4
};

static void
maybe_push_operr(pycbc_MultiResult *mres,
                 pycbc_Result *res,
                 lcb_error_t err,
                 int check_enoent)
{
    if (err == LCB_SUCCESS || mres->errop) {
        return;
    }

    if (check_enoent &&
            (mres->mropts & PYCBC_MRES_F_QUIET) &&
            err == LCB_KEY_ENOENT) {
        return;
    }

    mres->errop = (PyObject*)res;
    Py_INCREF(mres->errop);
}


static void
operation_completed(pycbc_Bucket *self, pycbc_MultiResult *mres)
{
    pycbc_assert(self->nremaining);
    --self->nremaining;

    if ((self->flags & PYCBC_CONN_F_ASYNC) == 0) {
        if (!self->nremaining) {
            lcb_breakout(self->instance);
        }
        return;
    }

    if (mres) {
        pycbc_AsyncResult *ares;
        ares = (pycbc_AsyncResult *)mres;
        if (--ares->nops) {
            return;
        }
        pycbc_asyncresult_invoke(ares);
    }
}

static int
get_common_objects(PyObject *cookie,
                   const void *key,
                   size_t nkey,
                   lcb_error_t err,
                   pycbc_Bucket **conn,
                   pycbc_Result **res,
                   int restype,
                   pycbc_MultiResult **mres)

{
    PyObject *hkey;
    PyObject *mrdict;
    int rv;

    pycbc_assert(pycbc_multiresult_check(cookie));
    *mres = (pycbc_MultiResult*)cookie;
    *conn = (*mres)->parent;

    CB_THR_END(*conn);

    rv = pycbc_tc_decode_key(*conn, key, nkey, &hkey);

    if (rv < 0) {
        pycbc_multiresult_adderr(*mres);
        return -1;
    }

    mrdict = pycbc_multiresult_dict(*mres);

    *res = (pycbc_Result*)PyDict_GetItem(mrdict, hkey);

    if (*res) {
        int exists_ok = (restype & RESTYPE_EXISTS_OK) ||
                ( (*mres)->mropts & PYCBC_MRES_F_UALLOCED);

        if (!exists_ok) {
            if ((*conn)->flags & PYCBC_CONN_F_WARNEXPLICIT) {
                PyErr_WarnExplicit(PyExc_RuntimeWarning,
                                   "Found duplicate key",
                                   __FILE__, __LINE__,
                                   "couchbase._libcouchbase",
                                   NULL);

            } else {
                PyErr_WarnEx(PyExc_RuntimeWarning,
                             "Found duplicate key",
                             1);
            }
            /**
             * We need to destroy the existing object and re-create it.
             */
            PyDict_DelItem(mrdict, hkey);
            *res = NULL;

        } else {
            Py_XDECREF(hkey);
        }

    }

    if (*res == NULL) {
        /**
         * Now, get/set the result object
         */
        if ( (*mres)->mropts & PYCBC_MRES_F_ITEMS) {
            *res = (pycbc_Result*)pycbc_item_new(*conn);

        } else if (restype & RESTYPE_BASE) {
            *res = (pycbc_Result*)pycbc_result_new(*conn);

        } else if (restype & RESTYPE_OPERATION) {
            *res = (pycbc_Result*)pycbc_opresult_new(*conn);

        } else if (restype & RESTYPE_VALUE) {
            *res = (pycbc_Result*)pycbc_valresult_new(*conn);

        } else {
            abort();
        }

        PyDict_SetItem(mrdict, hkey, (PyObject*)*res);

        (*res)->key = hkey;
        Py_DECREF(*res);
    }

    if (err) {
        (*res)->rc = err;
    }

    if (err != LCB_SUCCESS) {
        (*mres)->all_ok = 0;
    }

    return 0;
}

static void
durability_callback(lcb_t instance,
                    const void *cookie,
                    lcb_error_t err,
                    const lcb_durability_resp_t *resp)
{
    pycbc_Bucket *conn;
    pycbc_OperationResult *res;
    pycbc_MultiResult *mres;
    int rv;
    lcb_error_t effective_err;

    if (err != LCB_SUCCESS) {
        effective_err = err;
    } else {
        effective_err = resp->v.v0.err;
    }

    rv = get_common_objects((PyObject *)cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            effective_err,
                            &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_OPERATION|RESTYPE_EXISTS_OK,
                            &mres);

    if (rv == -1) {
        CB_THR_BEGIN(conn);

    } else {
        res->rc = effective_err;
        maybe_push_operr(mres, (pycbc_Result*)res, effective_err, 0);
    }

    operation_completed(conn, mres);

    CB_THR_BEGIN(conn);

    (void)instance;
}

static void
invoke_endure_test_notification(pycbc_Bucket *self, pycbc_Result *resp)
{
    PyObject *ret;
    PyObject *argtuple = Py_BuildValue("(O)", resp);
    ret = PyObject_CallObject(self->dur_testhook, argtuple);
    pycbc_assert(ret);

    Py_XDECREF(ret);
    Py_XDECREF(argtuple);
}

/**
 * Common handler for durability
 */
static void
dur_opres_common(const void *cookie, lcb_error_t err,
                 const void *key, lcb_size_t nkey, lcb_cas_t cas, int is_delete)
{
    pycbc_Bucket *conn;
    pycbc_OperationResult *res = NULL;
    pycbc_MultiResult *mres;
    lcb_durability_opts_t dopts = { 0 };
    lcb_durability_cmd_t dcmd = { 0 };
    const lcb_durability_cmd_t * const dcmd_p = &dcmd;
    int rv;

    rv = get_common_objects((PyObject*)cookie,
                            key, nkey, err, &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_OPERATION|RESTYPE_VARCOUNT,
                            &mres);

    if (rv == -1) {
        operation_completed(conn, mres);
        CB_THR_BEGIN(conn);
        return;
    }

    res->rc = err;
    if (err == LCB_SUCCESS) {
        res->cas = cas;
    }

    /** For remove, we check quiet */
    maybe_push_operr(mres, (pycbc_Result*)res, err, is_delete ? 1 : 0);

    if ((mres->mropts & PYCBC_MRES_F_DURABILITY) == 0 || err != LCB_SUCCESS) {
        operation_completed(conn, mres);
        CB_THR_BEGIN(conn);
        return;
    }

    if (conn->dur_testhook && conn->dur_testhook != Py_None) {
        invoke_endure_test_notification(conn, (pycbc_Result *)res);
    }

    /** Setup global options */
    dopts.v.v0.persist_to = mres->dur.persist_to;
    dopts.v.v0.replicate_to = mres->dur.replicate_to;
    dopts.v.v0.timeout = conn->dur_timeout;
    dopts.v.v0.check_delete = is_delete;

    /** Setup key specifics */
    dcmd.v.v0.cas = cas;
    dcmd.v.v0.key = key;
    dcmd.v.v0.nkey = nkey;

    if (mres->dur.persist_to < 0 || mres->dur.replicate_to < 0) {
        dopts.v.v0.cap_max = 1;
    }

    err = lcb_durability_poll(conn->instance, mres, &dopts, 1, &dcmd_p);

    if (err != LCB_SUCCESS) {
        res->rc = err;
        maybe_push_operr(mres, (pycbc_Result*)res, err, 0);
        operation_completed(conn, mres);
    }

    CB_THR_BEGIN(conn);
}

static void
store_callback(lcb_t instance, const void *cookie, lcb_storage_t op,
               lcb_error_t err, const lcb_store_resp_t *resp)
{
    dur_opres_common(cookie, err,
                     resp->v.v0.key, resp->v.v0.nkey, resp->v.v0.cas, 0);

    (void)instance;
    (void)op;
}

static void
get_callback(lcb_t instance,
             const void *cookie,
             lcb_error_t err,
             const lcb_get_resp_t *resp)
{

    int rv;
    pycbc_Bucket *conn = NULL;
    pycbc_ValueResult *res = NULL;
    pycbc_MultiResult *mres = NULL;
    lcb_uint32_t eflags;

    rv = get_common_objects((PyObject*)cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            err,
                            &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_VALUE,
                            &mres);

    if (rv < 0) {
        operation_completed(conn, mres);
        CB_THR_BEGIN(conn);
        return;
    }

    maybe_push_operr(mres, (pycbc_Result*)res, err, 1);



    if (err == LCB_SUCCESS) {
        res->flags = resp->v.v0.flags;
        res->cas = resp->v.v0.cas;

    } else {
        operation_completed(conn, mres);
        CB_THR_BEGIN(conn);
        return;
    }

    if (mres->mropts & PYCBC_MRES_F_FORCEBYTES) {
        eflags = PYCBC_FMT_BYTES;
    } else {
        eflags = resp->v.v0.flags;
    }

    rv = pycbc_tc_decode_value(mres->parent,
                               resp->v.v0.bytes,
                               resp->v.v0.nbytes,
                               eflags,
                               &res->value);
    if (rv < 0) {
        pycbc_multiresult_adderr(mres);
    }

    operation_completed(conn, mres);
    CB_THR_BEGIN(conn);
    (void)instance;
}

static void
delete_callback(lcb_t instance, const void *cookie, lcb_error_t err,
                const lcb_remove_resp_t *resp)
{
    dur_opres_common(cookie, err,
                     resp->v.v0.key, resp->v.v0.nkey, resp->v.v0.cas, 1);
    (void)instance;
}


static void
arithmetic_callback(lcb_t instance,
                    const void *cookie,
                    lcb_error_t err,
                    const lcb_arithmetic_resp_t *resp)
{
    int rv;
    pycbc_Bucket *conn = NULL;
    pycbc_ValueResult *res = NULL;
    pycbc_MultiResult *mres = NULL;

    rv = get_common_objects((PyObject*)cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            err,
                            &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_VALUE,
                            &mres);
    if (rv == 0) {
        res->rc = err;
        if (err == LCB_SUCCESS) {
            res->cas = resp->v.v0.cas;
            res->value = pycbc_IntFromULL(resp->v.v0.value);
        }

        maybe_push_operr(mres, (pycbc_Result*)res, err, 0);
    }

    operation_completed(conn, mres);
    CB_THR_BEGIN(conn);
    (void)instance;
}

static void
unlock_callback(lcb_t instance,
                const void *cookie,
                lcb_error_t err,
                const lcb_unlock_resp_t *resp)
{
    int rv;
    pycbc_Bucket *conn = NULL;
    pycbc_OperationResult *res = NULL;
    pycbc_MultiResult *mres = NULL;

    rv = get_common_objects((PyObject*)cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            err,
                            &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_OPERATION,
                            &mres);
    if (rv == 0) {
        res->rc = err;
        maybe_push_operr(mres, (pycbc_Result*)res, err, 0);
    }

    operation_completed(conn, mres);
    CB_THR_BEGIN(conn);
    (void)instance;
}

static void
touch_callback(lcb_t instance,
               const void *cookie,
               lcb_error_t err,
               const lcb_touch_resp_t *resp)
{
    int rv;
    pycbc_Bucket *conn = NULL;
    pycbc_OperationResult *res = NULL;
    pycbc_MultiResult *mres = NULL;

    rv = get_common_objects((PyObject*) cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            err,
                            &conn,
                            (pycbc_Result**)&res,
                            RESTYPE_OPERATION,
                            &mres);
    if (rv == 0) {
        if (err == LCB_SUCCESS) {
            res->cas = resp->v.v0.cas;
        }
        res->rc = err;
        maybe_push_operr(mres, (pycbc_Result*)res, err, 1);
    }

    operation_completed(conn, mres);
    CB_THR_BEGIN(conn);
    (void)instance;
}

static void
stat_callback(lcb_t instance,
              const void *cookie,
              lcb_error_t err,
              const lcb_server_stat_resp_t *resp)
{
    pycbc_MultiResult *mres;
    PyObject *value;
    PyObject *skey, *knodes;
    PyObject *mrdict;


    mres = (pycbc_MultiResult*)cookie;
    CB_THR_END(mres->parent);

    if (!resp->v.v0.server_endpoint) {
        pycbc_Bucket *parent = mres->parent;
        operation_completed(mres->parent, mres);
        CB_THR_BEGIN(parent);
        return;
    }

    if (err != LCB_SUCCESS) {
        if (mres->errop == NULL) {
            pycbc_Result *res =
                    (pycbc_Result*)pycbc_result_new(mres->parent);
            res->rc = err;
            res->key = Py_None; Py_INCREF(res->key);
            maybe_push_operr(mres, res, err, 0);
        }
        CB_THR_BEGIN(mres->parent);
        return;
    }

    if (!resp->v.v0.server_endpoint) {
        CB_THR_BEGIN(mres->parent);
        return;
    }

    skey = pycbc_SimpleStringN(resp->v.v0.key, resp->v.v0.nkey);
    value = pycbc_SimpleStringN(resp->v.v0.bytes, resp->v.v0.nbytes);
    {
        PyObject *intval = pycbc_maybe_convert_to_int(value);
        if (intval) {
            Py_DECREF(value);
            value = intval;

        } else {
            PyErr_Clear();
        }
    }

    mrdict = pycbc_multiresult_dict(mres);
    knodes = PyDict_GetItem(mrdict, skey);
    if (!knodes) {
        knodes = PyDict_New();
        PyDict_SetItem(mrdict, skey, knodes);
    }

    PyDict_SetItemString(knodes, resp->v.v0.server_endpoint, value);

    Py_DECREF(skey);
    Py_DECREF(value);

    CB_THR_BEGIN(mres->parent);
    (void)instance;
}



static void
observe_callback(lcb_t instance,
                 const void *cookie,
                 lcb_error_t err,
                 const lcb_observe_resp_t *resp)
{
    int rv;
    pycbc_ObserveInfo *oi;
    pycbc_Bucket *conn;
    pycbc_ValueResult *vres;
    pycbc_MultiResult *mres;

    if (!resp->v.v0.key) {
        mres = (pycbc_MultiResult*)cookie;;
        operation_completed(mres->parent, mres);
        return;
    }

    rv = get_common_objects((PyObject*)cookie,
                            resp->v.v0.key,
                            resp->v.v0.nkey,
                            err,
                            &conn,
                            (pycbc_Result**)&vres,
                            RESTYPE_VALUE|RESTYPE_EXISTS_OK|RESTYPE_VARCOUNT,
                            &mres);
    if (rv < 0) {
        goto GT_DONE;
    }

    if (err != LCB_SUCCESS) {
        maybe_push_operr(mres, (pycbc_Result*)vres, err, 0);
        goto GT_DONE;
    }

    if (!vres->value) {
        vres->value = PyList_New(0);
    }

    oi = pycbc_observeinfo_new(conn);
    if (oi == NULL) {
        pycbc_multiresult_adderr(mres);
        goto GT_DONE;
    }

    oi->from_master = resp->v.v0.from_master;
    oi->flags = resp->v.v0.status;
    oi->cas = resp->v.v0.cas;
    PyList_Append(vres->value, (PyObject*)oi);
    Py_DECREF(oi);

    GT_DONE:
    CB_THR_BEGIN(conn);
    (void)instance;
}

static int
start_global_callback(lcb_t instance, pycbc_Bucket **selfptr)
{
    *selfptr = (pycbc_Bucket *)lcb_get_cookie(instance);
    if (!*selfptr) {
        return 0;
    }
    CB_THR_END(*selfptr);
    Py_INCREF((PyObject *)*selfptr);
    return 1;
}

static void
end_global_callback(lcb_t instance, pycbc_Bucket *self)
{
    Py_DECREF((PyObject *)(self));

    self = (pycbc_Bucket *)lcb_get_cookie(instance);
    if (self) {
        CB_THR_BEGIN(self);
    }
}

static void
bootstrap_callback(lcb_t instance, lcb_error_t err)
{
    pycbc_Bucket *self;

    if (!start_global_callback(instance, &self)) {
        return;
    }
    pycbc_invoke_connected_event(self, err);
    end_global_callback(instance, self);
}


void
pycbc_callbacks_init(lcb_t instance)
{
    lcb_set_store_callback(instance, store_callback);
    lcb_set_unlock_callback(instance, unlock_callback);
    lcb_set_get_callback(instance, get_callback);
    lcb_set_touch_callback(instance, touch_callback);
    lcb_set_arithmetic_callback(instance, arithmetic_callback);
    lcb_set_remove_callback(instance, delete_callback);
    lcb_set_stat_callback(instance, stat_callback);
    lcb_set_observe_callback(instance, observe_callback);
    lcb_set_durability_callback(instance, durability_callback);
    lcb_set_bootstrap_callback(instance, bootstrap_callback);

    pycbc_http_callbacks_init(instance);
}
