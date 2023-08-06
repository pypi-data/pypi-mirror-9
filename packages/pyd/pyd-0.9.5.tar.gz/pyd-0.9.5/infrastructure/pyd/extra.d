/*
Copyright (c) 2012 Ellery Newcomer

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/**
  Various utilities operating on non-standard python objects.
*/
module pyd.extra;

import std.traits;
import std.complex;

import pyd.pydobject;
import pyd.exception;
import pyd.make_object;
import deimos.python.Python;

@property PyTypeObject* numpy_ndarray_Type() {
    static PyTypeObject* m_type;
    static bool inited = false;
    if(!inited) {
        inited = true;
        PyObject* numpy = PyImport_ImportModule("numpy");
        if(numpy) {
            scope(exit) Py_XDECREF(numpy);
            m_type = cast(PyTypeObject*) PyObject_GetAttrString(numpy, "ndarray");
        }else{
            PyErr_Clear();
        }
    }
    return m_type;
}

template NumpyFormatType(T) {
    static if(is(Unqual!T == Complex!F, F)) {
        alias Float = F;
        enum supportedComplex = F.sizeof == 4 || F.sizeof == 8;
    }else{
        enum supportedComplex = false;
    }
    enum supported = SimpleFormatType!T.supported || isBoolean!T || supportedComplex;

    static if(SimpleFormatType!T.supported) {
        alias pyType = SimpleFormatType!T.pyType;
    }else{
        PyObject* pyType() {
            assert(supported);

            PyObject* numpy = PyImport_ImportModule("numpy");
            static if(is(Unqual!T == Complex!Float, Float)) {
                static if(Float.sizeof == 4) {
                    return PyObject_GetAttrString(numpy, "complex64");
                }else static if(Float.sizeof == 8) {
                    return PyObject_GetAttrString(numpy, "complex128");
                }else assert(0);
            }else static if(isBoolean!T) {
                return PyObject_GetAttrString(numpy, "bool_");
            }
        }
    }
}
static assert(NumpyFormatType!(Complex!float).supported);

/**
  Convert a D array to numpy.ndarray.
  */
PyObject* d_to_python_numpy_ndarray(T)(T t) 
if((isArray!T || IsStaticArrayPointer!T) &&
        NumpyFormatType!(MatrixInfo!T.MatrixElementType).supported) {
    enforce(numpy_ndarray_Type, "numpy is not available"); 
    alias MatrixInfo!T.MatrixElementType ME;
    Py_ssize_t[] shape = MatrixInfo!T.build_shape(t);
    PyObject* pyshape = d_to_python(shape);
    PyObject* pyformat = NumpyFormatType!ME.pyType();
    PyObject* args = PyTuple_New(2);
    scope(exit) Py_DECREF(args);
    PyTuple_SetItem(args, 0, pyshape);
    PyTuple_SetItem(args, 1, pyformat);
    PyObject* ndarray = numpy_ndarray_Type.tp_new(numpy_ndarray_Type, args, null);
    if(!ndarray) handle_exception();
    enforce(ndarray, "numpy.ndarray.__new__ returned null (and didn't set an exception)");
    PydObject array = new PydObject(ndarray);
    auto buf = array.buffer_view(PyBUF_STRIDES|PyBUF_C_CONTIGUOUS);
    // this really should be optimized, but I am so lazy right now
    enum xx = (MatrixInfo!T.matrixIter(
                "t", "shape", "_indeces",
                MatrixInfo!T.ndim, q{
                static if(is(typeof($array_ixn) == ME)) {
                    buf.set_item!ME($array_ixn, cast(Py_ssize_t[]) _indeces);
                }
                },""));
    mixin(xx);
    // that PydObject stole ownership
    Py_INCREF(ndarray);
    return ndarray;
}
