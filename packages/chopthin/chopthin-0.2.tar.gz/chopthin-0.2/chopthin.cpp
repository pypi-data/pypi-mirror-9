// Implementation of chopthin in Python
// Copyright (C)2015 Axel Gandy

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <Python.h>
#include <numpy/arrayobject.h>

#include <vector>
#include <math.h> //ceil

static PyObject * ChopthinError;
inline int intrand(int n) { return floor(((double)rand())/((double)RAND_MAX)*(double)(n)); }
#define myrunif() ((double)rand()/((double)RAND_MAX))
#define chopthin_error(x) { {PyErr_SetString(ChopthinError, x);  throw 1;} }
#include "chopthin_internal.h"

static PyObject *
chopthin(PyObject *self, PyObject *args)
{
  try{
    PyArrayObject* wpython;
    double eta;
    int N;
    
    if (!PyArg_ParseTuple(args, "Oid",  &wpython, &N,&eta))
      return NULL; 
    
    if (N <=0) chopthin_error("N must be positive");
    
    if (wpython ->nd !=1) chopthin_error("Array has wrong number of dimensions");

    unsigned n = wpython -> dimensions[0];
    printf("%u\n",n);
    double* w= (double*) wpython->data;
    std::vector<double> wvec(w,w+n);
    std::vector<int> indvec(N);
    std::vector<double> wresvec(N);

    chopthin_internal(wvec,N,wresvec,indvec,eta);


    npy_intp dims[1];
    dims[0]=wresvec.size();
    PyArrayObject* wres = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_DOUBLE);
    if (!wres) chopthin_error("Could not allocate vector of result weights");
    PyArrayObject* ires = (PyArrayObject*) PyArray_SimpleNew(1, dims, NPY_INT);
    if (!ires) chopthin_error("Could not allocate vector of result indices");

    double* wresptr = (double*) wres->data;
    int* iresptr= (int*) ires->data;
    for (int i=0; i<N; i++){
      iresptr[i]=indvec[i];
      wresptr[i]=wresvec[i];
    }
    return Py_BuildValue("OO", wres, ires);
  }catch(...){
    return NULL;
  }
}

static PyMethodDef ChopthinMethods[] = {
    {"chopthin",  chopthin, METH_VARARGS,
     "Run the Chopthin Algorithm."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initchopthin(void){
  PyObject *m;
  m= Py_InitModule("chopthin", ChopthinMethods);
  if (m == NULL)
    return;
  
  ChopthinError = PyErr_NewException("chopthin.error", NULL, NULL);
  Py_INCREF(ChopthinError);
  PyModule_AddObject(m, "error", ChopthinError);

  import_array(); // necessary for numpy to work
}

int main(int argc, char *argv[]){
  Py_SetProgramName(argv[0]);
  Py_Initialize();
  initchopthin();
}
