/* This file is used to make _multipackmodule.c */
/* $Revision$ */
/* module_methods:
  {"_hybrd", minpack_hybrd, METH_VARARGS, doc_hybrd},
  {"_hybrj", minpack_hybrj, METH_VARARGS, doc_hybrj},
  {"_lmdif", minpack_lmdif, METH_VARARGS, doc_lmdif},
  {"_lmder", minpack_lmder, METH_VARARGS, doc_lmder},
  {"_chkder", minpack_chkder, METH_VARARGS, doc_chkder},
 */

/* link libraries:
   minpack
   linpack_lite
   blas
*/

/* python files:
   minpack.py
*/

#if defined(NO_APPEND_FORTRAN)
#if defined(UPPERCASE_FORTRAN)
/* nothing to do in that case */
#else
#define CHKDER chkder
#define HYBRD  hybrd
#define HYBRJ  hybrj
#define LMDIF  lmdif
#define LMDER  lmder
#define LMSTR  lmstr
#endif
#else
#if defined(UPPERCASE_FORTRAN)
#define CHKDER CHKDER_
#define HYBRD  HYBRD_
#define HYBRJ  HYBRJ_
#define LMDIF  LMDIF_
#define LMDER  LMDER_
#define LMSTR  LMSTR_
#else
#define CHKDER chkder_
#define HYBRD  hybrd_
#define HYBRJ  hybrj_
#define LMDIF  lmdif_
#define LMDER  lmder_
#define LMSTR  lmstr_
#endif
#endif

extern void CHKDER(int*,int*,double*,double*,double*,int*,double*,double*,int*,double*);
extern void HYBRD(void*,int*,double*,double*,double*,int*,int*,int*,double*,double*,int*,double*,int*,int*,int*,double*,int*,double*,int*,double*,double*,double*,double*,double*);
extern void HYBRJ(void*,int*,double*,double*,double*,int*,double*,int*,double*,int*,double*,int*,int*,int*,int*,double*,int*,double*,double*,double*,double*,double*);
extern void LMDIF(void*,int*,int*,double*,double*,double*,double*,double*,int*,double*,double*,int*,double*,int*,int*,int*,double*,int*,int*,double*,double*,double*,double*,double*);
extern void LMDER(void*,int*,int*,double*,double*,double*,int*,double*,double*,double*,int*,double*,int*,double*,int*,int*,int*,int*,int*,double*,double*,double*,double*,double*);
extern void LMSTR(void*,int*,int*,double*,double*,double*,int*,double*,double*,double*,int*,double*,int*,double*,int*,int*,int*,int*,int*,double*,double*,double*,double*,double*);

int raw_multipack_calling_function(int *n, double *x, double *fvec, int *iflag)
{
  /* This is the function called from the Fortran code it should
        -- use call_python_function to get a multiarrayobject result
	-- check for errors and return -1 if any
	-- otherwise place result of calculation in *fvec
  */

  PyArrayObject *result_array = NULL;
 
  result_array = (PyArrayObject *)call_python_function(multipack_python_function, *n, x, multipack_extra_arguments, 1, minpack_error);
  if (result_array == NULL) {
    *iflag = -1;
    return -1;
  }
  memcpy(fvec, result_array->data, (*n)*sizeof(double));
  Py_DECREF(result_array);
  return 0;

}


int jac_multipack_calling_function(int *n, double *x, double *fvec, double *fjac, int *ldfjac, int *iflag)
{
  /* This is the function called from the Fortran code it should
        -- use call_python_function to get a multiarrayobject result
	-- check for errors and return -1 if any
	-- otherwise place result of calculation in *fvec or *fjac.

     If iflag = 1 this should compute the function.
     If iflag = 2 this should compute the jacobian (derivative matrix)
  */

  PyArrayObject *result_array;

  if (*iflag == 1) {
    result_array = (PyArrayObject *)call_python_function(multipack_python_function, *n, x, multipack_extra_arguments, 1, minpack_error);
    if (result_array == NULL) {
      *iflag = -1;
      return -1;
    }
    memcpy(fvec, result_array->data, (*n)*sizeof(double));
  }
  else {         /* iflag == 2 */
    result_array = (PyArrayObject *)call_python_function(multipack_python_jacobian, *n, x, multipack_extra_arguments, 2, minpack_error);
    if (result_array == NULL) {
      *iflag = -1;
      return -1;
    }
    if (multipack_jac_transpose == 1)
      MATRIXC2F(fjac, result_array->data, *n, *ldfjac)
    else
      memcpy(fjac, result_array->data, (*n)*(*ldfjac)*sizeof(double));
  }

  Py_DECREF(result_array);
  return 0;
}

int raw_multipack_lm_function(int *m, int *n, double *x, double *fvec, int *iflag)
{
  /* This is the function called from the Fortran code it should
        -- use call_python_function to get a multiarrayobject result
	-- check for errors and return -1 if any
	-- otherwise place result of calculation in *fvec
  */

  PyArrayObject *result_array = NULL;
 
  result_array = (PyArrayObject *)call_python_function(multipack_python_function,*n, x, multipack_extra_arguments, 1, minpack_error);
  if (result_array == NULL) {
    *iflag = -1;
    return -1;
  }
  memcpy(fvec, result_array->data, (*m)*sizeof(double));
  Py_DECREF(result_array);
  return 0;
}


int jac_multipack_lm_function(int *m, int *n, double *x, double *fvec, double *fjac, int *ldfjac, int *iflag)
{
  /* This is the function called from the Fortran code it should
        -- use call_python_function to get a multiarrayobject result
	-- check for errors and return -1 if any
	-- otherwise place result of calculation in *fvec or *fjac.

     If iflag = 1 this should compute the function.
     If iflag = 2 this should compute the jacobian (derivative matrix)
  */

  PyArrayObject *result_array;

  if (*iflag == 1) {
    result_array = (PyArrayObject *)call_python_function(multipack_python_function, *n, x, multipack_extra_arguments, 1, minpack_error);
    if (result_array == NULL) {
      *iflag = -1;
      return -1;
    }
    memcpy(fvec, result_array->data, (*m)*sizeof(double));
  }
  else {         /* iflag == 2 */
    result_array = (PyArrayObject *)call_python_function(multipack_python_jacobian, *n, x, multipack_extra_arguments, 2, minpack_error);
    if (result_array == NULL) {
      *iflag = -1;
      return -1;
    }
    if (multipack_jac_transpose == 1) 
      MATRIXC2F(fjac, result_array->data, *n, *ldfjac)
    else
      memcpy(fjac, result_array->data, (*n)*(*ldfjac)*sizeof(double));
  }

  Py_DECREF(result_array);
  return 0;
}

int smjac_multipack_lm_function(int *m, int *n, double *x, double *fvec, double *fjrow, int *iflag)
{
  /* This is the function called from the Fortran code it should
        -- use call_python_function to get a multiarrayobject result
	-- check for errors and return -1 if any
	-- otherwise place result of calculation in *fvec or *fjac.

     If iflag = 1 this should compute the function.
     If iflag = i this should compute the (i-1)-st row of the jacobian.
  */
  int row;
  PyObject *newargs, *ob_row;
  PyArrayObject *result_array;

  if (*iflag == 1) {
    result_array = (PyArrayObject *)call_python_function(multipack_python_function, *n, x, multipack_extra_arguments, 1, minpack_error);
    if (result_array == NULL) {
      *iflag = -1;
      return -1;
    }
    memcpy(fvec, result_array->data, (*m)*sizeof(double));
  }
  else {         /* iflag == i */
    /* append row number to argument list and call row-based jacobian */
    row = *iflag - 2;

    if ((ob_row = PyInt_FromLong((long)row)) == NULL) {
      *iflag = -1;
      return -1;
    }
    newargs = PySequence_Concat( ob_row, multipack_extra_arguments);
    Py_DECREF(ob_row);
    if (newargs == NULL) {
      PyErr_SetString(minpack_error, "Internal error constructing argument list.");
      *iflag = -1;
      return -1;
    }

    result_array = (PyArrayObject *)call_python_function(multipack_python_jacobian, *n, x, newargs, 2, minpack_error);
    if (result_array == NULL) {
      Py_DECREF(newargs);
      *iflag = -1;
      return -1;
    }
    memcpy(fjrow, result_array->data, (*n)*sizeof(double));
  }

  Py_DECREF(result_array);
  return 0;
}


static char doc_hybrd[] = "[x,infodict,info] = _hybrd(fun, x0, args, full_output, xtol, maxfev, ml, mu, epsfcn, factor, diag)";

static PyObject *minpack_hybrd(PyObject *dummy, PyObject *args) {
  PyObject *fcn, *x0, *extra_args = NULL, *o_diag = NULL;
  int      full_output = 0, maxfev = -10, ml = -10, mu = -10;
  double   xtol = 1.49012e-8, epsfcn = 0.0, factor = 1.0e2;
  int      mode = 2, nprint = 0, info, nfev, ldfjac;
  npy_intp n,lr;
  int      n_int, lr_int;  /* for casted storage to pass int into HYBRD */
  double   *x, *fvec, *diag, *fjac, *r, *qtf;

  PyArrayObject *ap_x = NULL, *ap_fvec = NULL;
  PyArrayObject *ap_fjac = NULL, *ap_r = NULL, *ap_qtf = NULL;
  PyArrayObject *ap_diag = NULL;

  npy_intp dims[2];
  int      allocated = 0;
  double   *wa = NULL;

  STORE_VARS();    /* Define storage variables for global variables. */
  
  if (!PyArg_ParseTuple(args, "OO|OidiiiddO", &fcn, &x0, &extra_args, &full_output, &xtol, &maxfev, &ml, &mu, &epsfcn, &factor, &o_diag)) return NULL;

  INIT_FUNC(fcn,extra_args,minpack_error);

  /* Initial input vector */
  ap_x = (PyArrayObject *)PyArray_ContiguousFromObject(x0, NPY_DOUBLE, 1, 1);
  if (ap_x == NULL) goto fail;
  x = (double *) ap_x->data;
  n = ap_x->dimensions[0];

  lr = n * (n + 1) / 2;
  if (ml < 0) ml = n-1;
  if (mu < 0) mu = n-1;
  if (maxfev < 0) maxfev = 200*(n+1);

  /* Setup array to hold the function evaluations */
  ap_fvec = (PyArrayObject *)call_python_function(fcn, n, x, extra_args, 1, minpack_error);
  if (ap_fvec == NULL) goto fail;
  fvec = (double *) ap_fvec->data;
  if (ap_fvec->nd == 0) 
    n = 1;
  else if (ap_fvec->dimensions[0] < n)
    n = ap_fvec->dimensions[0];

  SET_DIAG(ap_diag,o_diag,mode);

  dims[0] = n; dims[1] = n;
  ap_r = (PyArrayObject *)PyArray_SimpleNew(1,&lr,NPY_DOUBLE);
  ap_qtf = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_DOUBLE);
  ap_fjac = (PyArrayObject *)PyArray_SimpleNew(2,dims,NPY_DOUBLE);

  if (ap_r == NULL || ap_qtf == NULL || ap_fjac ==NULL) goto fail;

  r = (double *) ap_r->data;
  qtf = (double *) ap_qtf->data;
  fjac = (double *) ap_fjac->data;
  ldfjac = dims[1];

  if ((wa = malloc(4*n * sizeof(double)))==NULL) {
    PyErr_NoMemory();
    goto fail;
  }
  allocated = 1;

  /* Call the underlying FORTRAN routines. */
  n_int = n; lr_int = lr; /* cast/store/pass into HYBRD */
  HYBRD(raw_multipack_calling_function, &n_int, x, fvec, &xtol, &maxfev, &ml, &mu, &epsfcn, diag, &mode, &factor, &nprint, &info, &nfev, fjac, &ldfjac, r, &lr_int, qtf, wa, wa+n, wa+2*n, wa+3*n);

  RESTORE_FUNC();

  if (info < 0) goto fail;            /* Python Terminated */


  free(wa);
  Py_DECREF(extra_args);
  Py_DECREF(ap_diag);

  if (full_output) {
    return Py_BuildValue("N{s:N,s:i,s:N,s:N,s:N}i",PyArray_Return(ap_x),"fvec",PyArray_Return(ap_fvec),"nfev",nfev,"fjac",PyArray_Return(ap_fjac),"r",PyArray_Return(ap_r),"qtf",PyArray_Return(ap_qtf),info);
  }
  else {
    Py_DECREF(ap_fvec);
    Py_DECREF(ap_fjac);
    Py_DECREF(ap_r);
    Py_DECREF(ap_qtf);
    return Py_BuildValue("Ni",PyArray_Return(ap_x),info);
  }

 fail:
  RESTORE_FUNC();
  Py_XDECREF(extra_args);
  Py_XDECREF(ap_x);
  Py_XDECREF(ap_fvec);
  Py_XDECREF(ap_diag);
  Py_XDECREF(ap_fjac);
  Py_XDECREF(ap_r);
  Py_XDECREF(ap_qtf);
  if (allocated) free(wa);
  return NULL;
}


static char doc_hybrj[] = "[x,infodict,info] = _hybrj(fun, Dfun, x0, args, full_output, col_deriv, xtol, maxfev, factor, diag)";

static PyObject *minpack_hybrj(PyObject *dummy, PyObject *args) {
  PyObject *fcn, *Dfun, *x0, *extra_args = NULL, *o_diag = NULL;
  int      full_output = 0, maxfev = -10, col_deriv = 1;
  double   xtol = 1.49012e-8, factor = 1.0e2;
  int      mode = 2, nprint = 0, info, nfev, njev, ldfjac;
  npy_intp n, lr;
  int n_int, lr_int;
  double   *x, *fvec, *diag, *fjac, *r, *qtf;

  PyArrayObject *ap_x = NULL, *ap_fvec = NULL;
  PyArrayObject *ap_fjac = NULL, *ap_r = NULL, *ap_qtf = NULL;
  PyArrayObject *ap_diag = NULL;

  npy_intp dims[2];
  int      allocated = 0;
  double   *wa = NULL;

  STORE_VARS();

  if (!PyArg_ParseTuple(args, "OOO|OiididO", &fcn, &Dfun, &x0, &extra_args, &full_output, &col_deriv, &xtol, &maxfev, &factor, &o_diag)) return NULL;

  INIT_JAC_FUNC(fcn,Dfun,extra_args,col_deriv,minpack_error);

  /* Initial input vector */
  ap_x = (PyArrayObject *)PyArray_ContiguousFromObject(x0, NPY_DOUBLE, 1, 1);
  if (ap_x == NULL) goto fail;
  x = (double *) ap_x->data;
  n = ap_x->dimensions[0];
  lr = n * (n + 1) / 2;

  if (maxfev < 0) maxfev = 100*(n+1);

  /* Setup array to hold the function evaluations */
  ap_fvec = (PyArrayObject *)call_python_function(fcn, n, x, extra_args, 1, minpack_error);
  if (ap_fvec == NULL) goto fail;
  fvec = (double *) ap_fvec->data;
  if (ap_fvec->nd == 0)
    n = 1;
  else if (ap_fvec->dimensions[0] < n)
    n = ap_fvec->dimensions[0];

  SET_DIAG(ap_diag,o_diag,mode);

  dims[0] = n; dims[1] = n;
  ap_r = (PyArrayObject *)PyArray_SimpleNew(1,&lr,NPY_DOUBLE);
  ap_qtf = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_DOUBLE);
  ap_fjac = (PyArrayObject *)PyArray_SimpleNew(2,dims,NPY_DOUBLE);

  if (ap_r == NULL || ap_qtf == NULL || ap_fjac ==NULL) goto fail;

  r = (double *) ap_r->data;
  qtf = (double *) ap_qtf->data;
  fjac = (double *) ap_fjac->data;

  ldfjac = dims[1];

  if ((wa = malloc(4*n * sizeof(double)))==NULL) {
    PyErr_NoMemory();
    goto fail;
  }
  allocated = 1;

  /* Call the underlying FORTRAN routines. */
  n_int = n; lr_int = lr; /* cast/store/pass into HYBRJ */
  HYBRJ(jac_multipack_calling_function, &n_int, x, fvec, fjac, &ldfjac, &xtol, &maxfev, diag, &mode, &factor, &nprint, &info, &nfev, &njev, r, &lr_int, qtf, wa, wa+n, wa+2*n, wa+3*n);

  RESTORE_JAC_FUNC();

  if (info < 0) goto fail;            /* Python Terminated */

  free(wa);
  Py_DECREF(extra_args);
  Py_DECREF(ap_diag);

  if (full_output) {
    return Py_BuildValue("N{s:N,s:i,s:i,s:N,s:N,s:N}i",PyArray_Return(ap_x),"fvec",PyArray_Return(ap_fvec),"nfev",nfev,"njev",njev,"fjac",PyArray_Return(ap_fjac),"r",PyArray_Return(ap_r),"qtf",PyArray_Return(ap_qtf),info);
  }
  else {
    Py_DECREF(ap_fvec);
    Py_DECREF(ap_fjac);
    Py_DECREF(ap_r);
    Py_DECREF(ap_qtf);
    return Py_BuildValue("Ni",PyArray_Return(ap_x),info);
  }

 fail:
  RESTORE_JAC_FUNC();
  Py_XDECREF(extra_args);
  Py_XDECREF(ap_x);
  Py_XDECREF(ap_fvec);
  Py_XDECREF(ap_fjac);
  Py_XDECREF(ap_diag);
  Py_XDECREF(ap_r);
  Py_XDECREF(ap_qtf);
  if (allocated) free(wa);
  return NULL;
  
}

/************************ Levenberg-Marquardt *******************/

static char doc_lmdif[] = "[x,infodict,info] = _lmdif(fun, x0, args, full_output, ftol, xtol, gtol, maxfev, epsfcn, factor, diag)";

static PyObject *minpack_lmdif(PyObject *dummy, PyObject *args) {
  PyObject *fcn, *x0, *extra_args = NULL, *o_diag = NULL;
  int      full_output = 0, maxfev = -10;
  double   xtol = 1.49012e-8, ftol = 1.49012e-8;
  double   gtol = 0.0, epsfcn = 0.0, factor = 1.0e2;
  int      m, mode = 2, nprint = 0, info, nfev, ldfjac, *ipvt;
  npy_intp n;
  int      n_int;  /* for casted storage to pass int into LMDIF */
  double   *x, *fvec, *diag, *fjac, *qtf;

  PyArrayObject *ap_x = NULL, *ap_fvec = NULL;
  PyArrayObject *ap_fjac = NULL, *ap_ipvt = NULL, *ap_qtf = NULL;
  PyArrayObject *ap_diag = NULL;

  npy_intp dims[2];
  int      allocated = 0;
  double   *wa = NULL;

  STORE_VARS();

  if (!PyArg_ParseTuple(args, "OO|OidddiddO", &fcn, &x0, &extra_args, &full_output, &ftol, &xtol, &gtol, &maxfev, &epsfcn, &factor, &o_diag)) return NULL;

  INIT_FUNC(fcn,extra_args,minpack_error);

  /* Initial input vector */
  ap_x = (PyArrayObject *)PyArray_ContiguousFromObject(x0, NPY_DOUBLE, 1, 1);
  if (ap_x == NULL) goto fail;
  x = (double *) ap_x->data;
  n = ap_x->dimensions[0];
  dims[0] = n;

  SET_DIAG(ap_diag,o_diag,mode);

  if (maxfev < 0) maxfev = 200*(n+1);

  /* Setup array to hold the function evaluations and find it's size*/
  ap_fvec = (PyArrayObject *)call_python_function(fcn, n, x, extra_args, 1, minpack_error);
  if (ap_fvec == NULL) goto fail;
  fvec = (double *) ap_fvec->data;
  m = (ap_fvec->nd > 0 ? ap_fvec->dimensions[0] : 1);

  dims[0] = n; dims[1] = m;
  ap_ipvt = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_INT);
  ap_qtf = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_DOUBLE);
  ap_fjac = (PyArrayObject *)PyArray_SimpleNew(2,dims,NPY_DOUBLE);

  if (ap_ipvt == NULL || ap_qtf == NULL || ap_fjac ==NULL) goto fail;

  ipvt = (int *) ap_ipvt->data;
  qtf = (double *) ap_qtf->data;
  fjac = (double *) ap_fjac->data;
  ldfjac = dims[1];
  wa = (double *)malloc((3*n + m)* sizeof(double));
  if (wa == NULL) {
    PyErr_NoMemory();
    goto fail;
  }
  allocated = 1;

  /* Call the underlying FORTRAN routines. */
  n_int = n; /* to provide int*-pointed storage for int argument of LMDIF */
  LMDIF(raw_multipack_lm_function, &m, &n_int, x, fvec, &ftol, &xtol, &gtol, &maxfev, &epsfcn, diag, &mode, &factor, &nprint, &info, &nfev, fjac, &ldfjac, ipvt, qtf, wa, wa+n, wa+2*n, wa+3*n);
    
  RESTORE_FUNC();

  if (info < 0) goto fail;           /* Python error */

  free(wa);
  Py_DECREF(extra_args); 
  Py_DECREF(ap_diag);

  if (full_output) {
    return Py_BuildValue("N{s:N,s:i,s:N,s:N,s:N}i",PyArray_Return(ap_x),"fvec",PyArray_Return(ap_fvec),"nfev",nfev,"fjac",PyArray_Return(ap_fjac),"ipvt",PyArray_Return(ap_ipvt),"qtf",PyArray_Return(ap_qtf),info);
  }
  else {
    Py_DECREF(ap_fvec);
    Py_DECREF(ap_fjac);
    Py_DECREF(ap_ipvt);
    Py_DECREF(ap_qtf);
    return Py_BuildValue("Ni",PyArray_Return(ap_x),info);
  }

 fail:
  RESTORE_FUNC();
  Py_XDECREF(extra_args);
  Py_XDECREF(ap_x);
  Py_XDECREF(ap_fvec);
  Py_XDECREF(ap_fjac);
  Py_XDECREF(ap_diag);
  Py_XDECREF(ap_ipvt);
  Py_XDECREF(ap_qtf);
  if (allocated) free(wa);
  return NULL;  
}


static char doc_lmder[] = "[x,infodict,info] = _lmder(fun, Dfun, x0, args, full_output, col_deriv, ftol, xtol, gtol, maxfev, factor, diag)";

static PyObject *minpack_lmder(PyObject *dummy, PyObject *args) {
  PyObject *fcn, *x0, *Dfun, *extra_args = NULL, *o_diag = NULL;
  int      full_output = 0, maxfev = -10, col_deriv = 1;
  double   xtol = 1.49012e-8, ftol = 1.49012e-8;
  double   gtol = 0.0, factor = 1.0e2;
  int      m, mode = 2, nprint = 0, info, nfev, njev, ldfjac, *ipvt;
  npy_intp n;
  int n_int;
  double   *x, *fvec, *diag, *fjac, *qtf;

  PyArrayObject *ap_x = NULL, *ap_fvec = NULL;
  PyArrayObject *ap_fjac = NULL, *ap_ipvt = NULL, *ap_qtf = NULL;
  PyArrayObject *ap_diag = NULL;

  npy_intp dims[2];
  int      allocated = 0;
  double   *wa = NULL;

  STORE_VARS();

  if (!PyArg_ParseTuple(args, "OOO|OiidddidO", &fcn, &Dfun, &x0, &extra_args, &full_output, &col_deriv, &ftol, &xtol, &gtol, &maxfev, &factor, &o_diag)) return NULL;

  INIT_JAC_FUNC(fcn,Dfun,extra_args,col_deriv,minpack_error);

  /* Initial input vector */
  ap_x = (PyArrayObject *)PyArray_ContiguousFromObject(x0, NPY_DOUBLE, 1, 1);
  if (ap_x == NULL) goto fail;
  x = (double *) ap_x->data;
  n = ap_x->dimensions[0];

  if (maxfev < 0) maxfev = 100*(n+1);

  /* Setup array to hold the function evaluations */
  ap_fvec = (PyArrayObject *)call_python_function(fcn, n, x, extra_args, 1, minpack_error);
  if (ap_fvec == NULL) goto fail;
  fvec = (double *) ap_fvec->data;

  SET_DIAG(ap_diag,o_diag,mode);

  m = (ap_fvec->nd > 0 ? ap_fvec->dimensions[0] : 1);

  dims[0] = n; dims[1] = m;
  ap_ipvt = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_INT);
  ap_qtf = (PyArrayObject *)PyArray_SimpleNew(1,&n,NPY_DOUBLE);
  ap_fjac = (PyArrayObject *)PyArray_SimpleNew(2,dims,NPY_DOUBLE);

  if (ap_ipvt == NULL || ap_qtf == NULL || ap_fjac ==NULL) goto fail;

  ipvt = (int *) ap_ipvt->data;
  qtf = (double *) ap_qtf->data;
  fjac = (double *) ap_fjac->data;
  ldfjac = dims[1];
  wa = (double *)malloc((3*n + m)* sizeof(double));
  if (wa == NULL) {
    PyErr_NoMemory();
    goto fail;
  }
  allocated = 1;

  /* Call the underlying FORTRAN routines. */
  n_int = n;
  LMDER(jac_multipack_lm_function, &m, &n_int, x, fvec, fjac, &ldfjac, &ftol, &xtol, &gtol, &maxfev, diag, &mode, &factor, &nprint, &info, &nfev, &njev, ipvt, qtf, wa, wa+n, wa+2*n, wa+3*n);

  RESTORE_JAC_FUNC();

  if (info < 0) goto fail;           /* Python error */

  free(wa);
  Py_DECREF(extra_args);
  Py_DECREF(ap_diag);

  if (full_output) {
    return Py_BuildValue("N{s:N,s:i,s:i,s:N,s:N,s:N}i",PyArray_Return(ap_x),"fvec",PyArray_Return(ap_fvec),"nfev",nfev,"njev",njev,"fjac",PyArray_Return(ap_fjac),"ipvt",PyArray_Return(ap_ipvt),"qtf",PyArray_Return(ap_qtf),info);
  }
  else {
    Py_DECREF(ap_fvec);
    Py_DECREF(ap_fjac);
    Py_DECREF(ap_ipvt);
    Py_DECREF(ap_qtf);
    return Py_BuildValue("Ni",PyArray_Return(ap_x),info);
  }

 fail:
  RESTORE_JAC_FUNC();
  Py_XDECREF(extra_args);
  Py_XDECREF(ap_x);
  Py_XDECREF(ap_fvec);
  Py_XDECREF(ap_fjac);
  Py_XDECREF(ap_diag);
  Py_XDECREF(ap_ipvt);
  Py_XDECREF(ap_qtf);
  if (allocated) free(wa);
  return NULL;  
}


/** Check gradient function **/

static char doc_chkder[] = "_chkder(m,n,x,fvec,fjac,ldfjac,xp,fvecp,mode,err)";

static PyObject *minpack_chkder(PyObject *self, PyObject *args)
{
  PyArrayObject *ap_fvecp = NULL, *ap_fjac = NULL, *ap_err = NULL;
  PyArrayObject *ap_x = NULL, *ap_fvec = NULL, *ap_xp = NULL;
  PyObject *o_x, *o_fvec, *o_fjac, *o_fvecp;
  double *xp, *fvecp, *fjac, *fvec, *x;
  double *err;
  int mode, m, n, ldfjac;

  if (!PyArg_ParseTuple(args,"iiOOOiO!OiO!",&m, &n, &o_x, &o_fvec, &o_fjac, &ldfjac, &PyArray_Type, (PyObject **)&ap_xp, &o_fvecp, &mode, &PyArray_Type, (PyObject **)&ap_err)) return NULL;

  ap_x = (PyArrayObject *)PyArray_ContiguousFromObject(o_x,NPY_DOUBLE,1,1);
  if (ap_x == NULL) goto fail;
  if (n != ap_x->dimensions[0])
     PYERR(minpack_error,"Input data array (x) must have length n");
  x = (double *) ap_x -> data;
  if (!ISCONTIGUOUS(ap_xp) || (ap_xp->descr->type_num != NPY_DOUBLE))
     PYERR(minpack_error,"Seventh argument (xp) must be contiguous array of type Float64.");

  if (mode == 1) {
    fvec = NULL;
    fjac = NULL;
    xp = (double *)ap_xp->data;
    fvecp = NULL;
    err = NULL;
    CHKDER(&m, &n, x, fvec, fjac, &ldfjac, xp, fvecp, &mode, err);
  }
  else if (mode == 2) {
    if (!ISCONTIGUOUS(ap_err) || (ap_err->descr->type_num != NPY_DOUBLE))
       PYERR(minpack_error,"Last argument (err) must be contiguous array of type Float64.");
    ap_fvec = (PyArrayObject *)PyArray_ContiguousFromObject(o_fvec,NPY_DOUBLE,1,1);
    ap_fjac = (PyArrayObject *)PyArray_ContiguousFromObject(o_fjac,NPY_DOUBLE,2,2);
    ap_fvecp = (PyArrayObject *)PyArray_ContiguousFromObject(o_fvecp,NPY_DOUBLE,1,1);
    if (ap_fvec == NULL || ap_fjac == NULL || ap_fvecp == NULL) goto fail;

    fvec = (double *)ap_fvec -> data;
    fjac = (double *)ap_fjac -> data;
    xp = (double *)ap_xp->data;
    fvecp = (double *)ap_fvecp -> data;
    err = (double *)ap_err->data;    

    CHKDER(&m, &n, x, fvec, fjac, &m, xp, fvecp, &mode, err);

    Py_DECREF(ap_fvec);
    Py_DECREF(ap_fjac);
    Py_DECREF(ap_fvecp);
  }
  else 
    PYERR(minpack_error,"Invalid mode, must be 1 or 2.");

  Py_DECREF(ap_x);

  Py_INCREF(Py_None);
  return Py_None;

 fail:
  Py_XDECREF(ap_fvec);
  Py_XDECREF(ap_fjac);
  Py_XDECREF(ap_fvecp);
  Py_XDECREF(ap_x);
  return NULL;
}









