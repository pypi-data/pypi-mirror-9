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

/**
 * This file contains connection events
 */
#include "pycbc.h"
#include "iops.h"

void
pycbc_invoke_connected_event(pycbc_Connection *conn, lcb_error_t err)
{
    PyObject *argtuple;
    PyObject *arg;
    PyObject *ret;

    if (conn->flags & PYCBC_CONN_F_CONNECTED) {
        return;
    }

    conn->flags |= PYCBC_CONN_F_CONNECTED;

    if (conn->conncb == NULL || PyObject_IsTrue(conn->conncb) == 0) {
        return;
    }

    if (err == LCB_SUCCESS) {
        arg = Py_None;
        Py_INCREF(Py_None);
    } else {
        arg = pycbc_exc_message(PYCBC_EXC_LCBERR, err,
                                "Error getting initial connection "
                                "to cluster");
    }

    argtuple = PyTuple_New(1);
    PyTuple_SET_ITEM(argtuple, 0, arg);

    ret = PyObject_CallObject(conn->conncb, argtuple);
    Py_XDECREF(ret);
    Py_XDECREF(conn->conncb);
    conn->conncb = NULL;
    Py_DECREF(argtuple);
}


struct dtor_info_st {
    lcb_t instance;
    lcb_io_opt_t io;
    PyObject *dtorcb;
    PyObject *conncb;
    void *event;
};

static void
dtor_callback(lcb_socket_t sock, short which, void *arg)
{
    struct dtor_info_st *dti = arg;
    if (dti->instance) {
        lcb_destroy(dti->instance);
    }

    if (dti->io) {
        dti->io->v.v0.delete_timer(dti->io, dti->event);
        dti->io->v.v0.destroy_timer(dti->io, dti->event);
        pycbc_iops_free(dti->io);
    }

    if (dti->conncb) {
        PyObject *ret;
        PyObject *exc;
        PyObject *args = PyTuple_New(1);

        exc = pycbc_exc_message(PYCBC_EXC_DESTROYED,
                                0,
                                "Connection object was garbage collected");
        assert(exc);

        PyTuple_SET_ITEM(args, 0, exc);
        ret = PyObject_CallObject(dti->conncb, args);

        Py_XDECREF(ret);
        Py_DECREF(args);
        Py_DECREF(dti->conncb);
        dti->conncb = NULL;
    }

    if (dti->dtorcb) {
        PyObject *ret = PyObject_CallObject(dti->dtorcb, NULL);
        Py_XDECREF(ret);
        Py_DECREF(dti->dtorcb);
        dti->dtorcb = NULL;
    }

    free(dti);
    (void)sock;
    (void)which;
}

void
pycbc_schedule_dtor_event(pycbc_Connection *self)
{
    struct dtor_info_st *dti;

    if ((self->flags & PYCBC_CONN_F_ASYNC_DTOR) == 0) {
        return;
    }

    pycbc_assert(self->iops);

    dti = malloc(sizeof(*dti));
    if (!dti) {
        fprintf(stderr,
                "[PYCBC] Couldn't allocate memory for libcouchbase async "
                "destruction. Instance will leak\n");

    } else {
        dti->instance = self->instance;
        dti->io = self->iops;
        dti->dtorcb = self->dtorcb;
        dti->conncb = self->conncb;
        dti->event = self->iops->v.v0.create_timer(self->iops);

        self->iops->v.v0.update_timer(self->iops, dti->event,
                                      0, dti, dtor_callback);
    }

    self->instance = NULL;
    self->iops = NULL;
    self->dtorcb = NULL;
    self->conncb = NULL;
}

void
pycbc_invoke_error_callback(pycbc_Connection *self,
                            lcb_error_t err, const char *msg)
{
    PyObject *errtuple;
    PyObject *result;

    pycbc_assert(self->errors);

    errtuple = Py_BuildValue("(i,s)", err, msg);
    pycbc_assert(errtuple);

    result = PyObject_CallMethod(self->errors, "append", "(O)", errtuple);

    Py_DECREF(errtuple);
    Py_DECREF(result);
}
