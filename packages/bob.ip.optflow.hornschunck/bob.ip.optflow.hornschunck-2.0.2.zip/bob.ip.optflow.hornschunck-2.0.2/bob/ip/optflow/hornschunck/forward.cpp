/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 11 Apr 09:34:12 2014 CEST
 *
 * @brief Bindings for spatio-temporal gradient functors
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>
#include <structmember.h>

#include "SpatioTemporalGradient.h"

/************************************************
 * Implementation of ForwardGradient base class *
 ************************************************/

#define CLASS_NAME "ForwardGradient"

static auto s_forward = bob::extension::ClassDoc(
    BOB_EXT_MODULE_PREFIX "." CLASS_NAME,

    "Computes the spatio-temporal gradient using a 2-term approximation",

    "This class computes the spatio-temporal gradient using a 2-term "
    "approximation composed of 2 separable kernels (one for the diference "
    "term and another one for the averaging term)."
    )
    .add_constructor(
        bob::extension::FunctionDoc(
          CLASS_NAME,
          "Constructor",
          "We initialize with the shape of the images we need to treat and "
          "with the kernels to be applied. The shape is used by the internal "
          "buffers.\n"
          )
        .add_prototype("difference, average, (height, width)", "")
        .add_parameter("difference", "array-like, 1D float64", "The kernel that contains the difference operation. Typically, this is ``[1, -1]``. Note the kernel is mirrored during the convolution operation. To obtain a ``[-1, +1]`` sliding operator, specify ``[+1, -1]``. This kernel must have a shape = (2,).")
        .add_parameter("average", "array-like, 1D float64", "The kernel that contains the spatial averaging operation. This kernel is typically ``[+1, +1]``. This kernel must have a shape = (2,).")
        .add_parameter("(height, width)", "tuple", "the height and width of images to be fed into the the gradient estimator")
        )
    ;

typedef struct {
  PyObject_HEAD
  bob::ip::optflow::ForwardGradient* cxx;
} PyBobIpOptflowForwardGradientObject;


static int PyBobIpOptflowForwardGradient_init
(PyBobIpOptflowForwardGradientObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"difference", "average", "shape", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* diff = 0;
  PyBlitzArrayObject* avg = 0;
  Py_ssize_t height, width;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&(nn)", kwlist,
        &PyBlitzArray_Converter, &diff,
        &PyBlitzArray_Converter, &avg,
        &height, &width)) return -1;

  //protects acquired resources through this scope
  auto diff_ = make_safe(diff);
  auto avg_ = make_safe(avg);

  if (diff->type_num != NPY_FLOAT64 || diff->ndim != 1 || diff->shape[0] != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays with 2 elements for input kernel `difference', but you provided a %" PY_FORMAT_SIZE_T "d array with data type = `%s' and %" PY_FORMAT_SIZE_T "d elements", Py_TYPE(self)->tp_name, diff->ndim, PyBlitzArray_TypenumAsString(diff->type_num), diff->shape[0]);
    return 0;
  }

  if (avg->type_num != NPY_FLOAT64 || avg->ndim != 1 || avg->shape[0] != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays with 2 elements for input kernel `average', but you provided a %" PY_FORMAT_SIZE_T "d array with data type = `%s' and %" PY_FORMAT_SIZE_T "d elements", Py_TYPE(self)->tp_name, avg->ndim, PyBlitzArray_TypenumAsString(avg->type_num), avg->shape[0]);
    return 0;
  }

  try {
    blitz::TinyVector<int,2> shape;
    shape(0) = height; shape(1) = width;
    self->cxx = new bob::ip::optflow::ForwardGradient(
        *PyBlitzArrayCxx_AsBlitz<double,1>(diff),
        *PyBlitzArrayCxx_AsBlitz<double,1>(avg),
        shape);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static void PyBobIpOptflowForwardGradient_delete
(PyBobIpOptflowForwardGradientObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

static auto s_shape = bob::extension::VariableDoc(
    "shape",
    "tuple",
    "The shape pre-configured for this gradient estimator: ``(height, width)``"
    );

static PyObject* PyBobIpOptflowForwardGradient_getShape
(PyBobIpOptflowForwardGradientObject* self, void* /*closure*/) {
  auto shape = self->cxx->getShape();
  return Py_BuildValue("nn", shape(0), shape(1));
}

static int PyBobIpOptflowForwardGradient_setShape (PyBobIpOptflowForwardGradientObject* self, PyObject* o, void* /*closure*/) {

  Py_ssize_t height = 0;
  Py_ssize_t width = 0;

  if (!PyArg_ParseTuple(o, "nn", &height, &width)) return -1;

  try {
    blitz::TinyVector<int,2> shape;
    shape(0) = height; shape(1) = width;
    self->cxx->setShape(shape);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `shape' of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static auto s_difference = bob::extension::VariableDoc(
    "difference",
    "array-like, 1D float64",
    "The kernel that contains the difference operation. Typically, this is ``[1, -1]``. Note the kernel is mirrored during the convolution operation. To obtain a ``[-1, +1]`` sliding operator, specify ``[+1, -1]``. This kernel must have a shape = (2,).");

static PyObject* PyBobIpOptflowForwardGradient_getDifference
(PyBobIpOptflowForwardGradientObject* self, void* /*closure*/) {
  auto retval = PyBlitzArrayCxx_NewFromConstArray(self->cxx->getDiffKernel());
  if (!retval) return 0;
  return PyBlitzArray_NUMPY_WRAP(retval);
}

static int PyBobIpOptflowForwardGradient_setDifference
(PyBobIpOptflowForwardGradientObject* self, PyObject* o, void* /*closure*/) {

  PyBlitzArrayObject* kernel = 0;

  if (!PyBlitzArray_Converter(o, &kernel)) return 0;

  if (kernel->type_num != NPY_FLOAT64 ||
      kernel->ndim != 1 ||
      kernel->shape[0] != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays with 2 elements for `difference' kernel, but you provided a %" PY_FORMAT_SIZE_T "d array with data type = `%s' and %" PY_FORMAT_SIZE_T "d elements", Py_TYPE(self)->tp_name, kernel->ndim, PyBlitzArray_TypenumAsString(kernel->type_num), kernel->shape[0]);
    return -1;
  }

  try {
    self->cxx->setDiffKernel(*PyBlitzArrayCxx_AsBlitz<double,1>(kernel));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `difference' kernel of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static auto s_average = bob::extension::VariableDoc(
    "average",
    "array-like, 1D float64",
    "The kernel that contains the average operation. Typically, this is ``[1, -1]``. Note the kernel is mirrored during the convolution operation. To obtain a ``[-1, +1]`` sliding operator, specify ``[+1, -1]``. This kernel must have a shape = (2,).");

static PyObject* PyBobIpOptflowForwardGradient_getAverage
(PyBobIpOptflowForwardGradientObject* self, void* /*closure*/) {
  auto retval = PyBlitzArrayCxx_NewFromConstArray(self->cxx->getAvgKernel());
  if (!retval) return 0;
  return PyBlitzArray_NUMPY_WRAP(retval);
}

static int PyBobIpOptflowForwardGradient_setAverage
(PyBobIpOptflowForwardGradientObject* self, PyObject* o, void* /*closure*/) {

  PyBlitzArrayObject* kernel = 0;

  if (!PyBlitzArray_Converter(o, &kernel)) return 0;

  if (kernel->type_num != NPY_FLOAT64 ||
      kernel->ndim != 1 ||
      kernel->shape[0] != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 1D 64-bit float arrays with 2 elements for `average' kernel, but you provided a %" PY_FORMAT_SIZE_T "d array with data type = `%s' and %" PY_FORMAT_SIZE_T "d elements", Py_TYPE(self)->tp_name, kernel->ndim, PyBlitzArray_TypenumAsString(kernel->type_num), kernel->shape[0]);
    return -1;
  }

  try {
    self->cxx->setAvgKernel(*PyBlitzArrayCxx_AsBlitz<double,1>(kernel));
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot reset `average' kernel of %s: unknown exception caught", Py_TYPE(self)->tp_name);
    return -1;
  }

  return 0;

}

static PyGetSetDef PyBobIpOptflowForwardGradient_getseters[] = {
    {
      s_difference.name(),
      (getter)PyBobIpOptflowForwardGradient_getDifference,
      (setter)PyBobIpOptflowForwardGradient_setDifference,
      s_difference.doc(),
      0
    },
    {
      s_average.name(),
      (getter)PyBobIpOptflowForwardGradient_getAverage,
      (setter)PyBobIpOptflowForwardGradient_setAverage,
      s_average.doc(),
      0
    },
    {
      s_shape.name(),
      (getter)PyBobIpOptflowForwardGradient_getShape,
      (setter)PyBobIpOptflowForwardGradient_setShape,
      s_shape.doc(),
      0
    },
    {0}  /* Sentinel */
};

#if PY_VERSION_HEX >= 0x03000000
#  define PYOBJECT_STR PyObject_Str
#else
#  define PYOBJECT_STR PyObject_Unicode
#endif

PyObject* PyBobIpOptflowForwardGradient_Repr(PyBobIpOptflowForwardGradientObject* self) {

  /**
   * Expected output:
   *
   * <bob.ip.optflow.hornschunck.ForwardGradient((3, 2))>
   */

  auto shape = make_safe(PyBobIpOptflowForwardGradient_getShape(self, 0));
  if (!shape) return 0;
  auto shape_str = make_safe(PyObject_Str(shape.get()));

  PyObject* retval = PyUnicode_FromFormat("<%s(%U)>", Py_TYPE(self)->tp_name, shape_str.get());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyObject* PyBobIpOptflowForwardGradient_Str(PyBobIpOptflowForwardGradientObject* self) {

  /**
   * Expected output:
   *
   * bob.ip.optflow.hornschunck.ForwardGradient((3, 2))
   *  difference: [ -1. 1. ]
   *  average: [ 1. 1. ]
   */

  auto d = make_safe(PyBobIpOptflowForwardGradient_getDifference(self, 0));
  auto d_str = make_safe(PYOBJECT_STR(d.get()));
  auto diff = make_safe(PyUnicode_FromFormat("\n difference: %U", d_str.get()));

  auto a = make_safe(PyBobIpOptflowForwardGradient_getAverage(self, 0));
  auto a_str = make_safe(PYOBJECT_STR(a.get()));
  auto avg = make_safe(PyUnicode_FromFormat("\n average: %U", a_str.get()));

  auto shape = make_safe(PyBobIpOptflowForwardGradient_getShape(self, 0));
  if (!shape) return 0;
  auto shape_str = make_safe(PyObject_Str(shape.get()));

  PyObject* retval = PyUnicode_FromFormat("%s(%U)%U%U", Py_TYPE(self)->tp_name, shape_str.get(), diff.get(), avg.get());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

static auto s_evaluate = bob::extension::FunctionDoc(
    "evaluate",
    "Evaluates the spatio-temporal gradient from the input image pair"
    )
    .add_prototype("image1, image2, [ex, ey, et]", "ex, ey, et")
    .add_parameter("image1, image2", "array-like (2D, float64)",
      "Sequence of images to evaluate the gradient from. Both images should have the same shape, which should match that of this functor.")
    .add_parameter("ex, ey, et", "array (2D, float64)", "The evaluated gradients in the horizontal, vertical and time directions (respectively) will be output in these variables, which should have dimensions matching those of this functor. If you don't provide arrays for ``ex``, ``ey`` and ``et``, then they will be allocated internally and returned. You must either provide neither ``ex``, ``ey`` and ``et`` or all, otherwise an exception will be raised.")
    .add_return("ex, ey, et", "array (2D, float64)", "The evaluated gradients are returned by this function. Each matrix will have a shape that matches the input images.")
    ;

static PyObject* PyBobIpOptflowForwardGradient_evaluate
(PyBobIpOptflowForwardGradientObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "image1",
    "image2",
    "ex",
    "ey",
    "et",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* ex = 0;
  PyBlitzArrayObject* ey = 0;
  PyBlitzArrayObject* et = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&|O&O&O&", kwlist,
        &PyBlitzArray_Converter, &image1,
        &PyBlitzArray_Converter, &image2,
        &PyBlitzArray_OutputConverter, &ex,
        &PyBlitzArray_OutputConverter, &ey,
        &PyBlitzArray_OutputConverter, &et
        )) return 0;

  //protects acquired resources through this scope
  auto image1_ = make_safe(image1);
  auto image2_ = make_safe(image2);
  auto ex_ = make_xsafe(ex);
  auto ey_ = make_xsafe(ey);
  auto et_ = make_xsafe(et);

  if (image1->type_num != NPY_FLOAT64 || image1->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image1', but you passed a %" PY_FORMAT_SIZE_T "dD array with type `%s'", Py_TYPE(self)->tp_name, image1->ndim, PyBlitzArray_TypenumAsString(image1->type_num));
    return 0;
  }

  if (image2->type_num != NPY_FLOAT64 || image2->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image2', but you passed a %" PY_FORMAT_SIZE_T "dD array with type `%s'", Py_TYPE(self)->tp_name, image2->ndim, PyBlitzArray_TypenumAsString(image2->type_num));
    return 0;
  }

  //check all input image dimensions are consistent
  Py_ssize_t height = self->cxx->getShape()(0);
  Py_ssize_t width = self->cxx->getShape()(1);

  if (image1->shape[0] != height || image1->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `image1', but `image1''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, image1->shape[0], image1->shape[1]);
    return 0;
  }

  if (image2->shape[0] != height || image2->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `image2', but `image2''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, image2->shape[0], image2->shape[1]);
    return 0;
  }

  if ((ex && !ey) || (ex && !et) ||
      (ey && !ex) || (ey && !et) ||
      (et && !ex) || (et && !ey)) {
    PyErr_Format(PyExc_RuntimeError, "`%s' requires `ex', `ey' and `et' or none", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (ex) {

    if (ex->type_num != NPY_FLOAT64 || ex->ndim != 2) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `ex'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (ey->type_num != NPY_FLOAT64 || ey->ndim != 2) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `ey'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (et->type_num != NPY_FLOAT64 || et->ndim != 2) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `et'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (ex->shape[0] != height || ex->shape[1] != width) {
      PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `ex', but `ex''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, ex->shape[0], ex->shape[1]);
      return 0;
    }

    if (ey->shape[0] != height || ey->shape[1] != width) {
      PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `ey', but `ey''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, ey->shape[0], ey->shape[1]);
      return 0;
    }

    if (et->shape[0] != height || et->shape[1] != width) {
      PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `et', but `et''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, et->shape[0], et->shape[1]);
      return 0;
    }

  }
  else { //allocates ex, ey and et

    ex = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
        image1->ndim, image1->shape);
    auto bz_ex = PyBlitzArrayCxx_AsBlitz<double,2>(ex);
    (*bz_ex) = 0.;
    ex_ = make_safe(ex);

    ey = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
        image1->ndim, image1->shape);
    auto bz_ey = PyBlitzArrayCxx_AsBlitz<double,2>(ey);
    (*bz_ey) = 0.;
    ey_ = make_safe(ey);

    et = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
        image1->ndim, image1->shape);
    auto bz_et = PyBlitzArrayCxx_AsBlitz<double,2>(et);
    (*bz_et) = 0.;
    et_ = make_safe(et);

  }

  /** all basic checks are done, can call the functor now **/
  try {
    self->cxx->operator()(
        *PyBlitzArrayCxx_AsBlitz<double,2>(image1),
        *PyBlitzArrayCxx_AsBlitz<double,2>(image2),
        *PyBlitzArrayCxx_AsBlitz<double,2>(ex),
        *PyBlitzArrayCxx_AsBlitz<double,2>(ey),
        *PyBlitzArrayCxx_AsBlitz<double,2>(et)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot evaluate gradient: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  return Py_BuildValue("(NNN)",
    PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", ex)),
    PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", ey)),
    PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", et))
    );

}

static PyMethodDef PyBobIpOptflowForwardGradient_methods[] = {
  {
    s_evaluate.name(),
    (PyCFunction)PyBobIpOptflowForwardGradient_evaluate,
    METH_VARARGS|METH_KEYWORDS,
    s_evaluate.doc()
  },
  {0} /* Sentinel */
};

static PyObject* PyBobIpOptflowForwardGradient_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIpOptflowForwardGradientObject* self =
    (PyBobIpOptflowForwardGradientObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyTypeObject PyBobIpOptflowForwardGradient_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_forward.name(),                                    /* tp_name */
    sizeof(PyBobIpOptflowForwardGradientObject),         /* tp_basicsize */
    0,                                                   /* tp_itemsize */
    (destructor)PyBobIpOptflowForwardGradient_delete,    /* tp_dealloc */
    0,                                                   /* tp_print */
    0,                                                   /* tp_getattr */
    0,                                                   /* tp_setattr */
    0,                                                   /* tp_compare */
    (reprfunc)PyBobIpOptflowForwardGradient_Repr,        /* tp_repr */
    0,                                                   /* tp_as_number */
    0,                                                   /* tp_as_sequence */
    0,                                                   /* tp_as_mapping */
    0,                                                   /* tp_hash */
    (ternaryfunc)PyBobIpOptflowForwardGradient_evaluate, /* tp_call */
    (reprfunc)PyBobIpOptflowForwardGradient_Str,         /* tp_str */
    0,                                                   /* tp_getattro */
    0,                                                   /* tp_setattro */
    0,                                                   /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,            /* tp_flags */
    s_forward.doc(),                                     /* tp_doc */
    0,                                                   /* tp_traverse */
    0,                                                   /* tp_clear */
    0,                                                   /* tp_richcompare */
    0,                                                   /* tp_weaklistoffset */
    0,                                                   /* tp_iter */
    0,                                                   /* tp_iternext */
    PyBobIpOptflowForwardGradient_methods,               /* tp_methods */
    0,                                                   /* tp_members */
    PyBobIpOptflowForwardGradient_getseters,             /* tp_getset */
    0,                                                   /* tp_base */
    0,                                                   /* tp_dict */
    0,                                                   /* tp_descr_get */
    0,                                                   /* tp_descr_set */
    0,                                                   /* tp_dictoffset */
    (initproc)PyBobIpOptflowForwardGradient_init,        /* tp_init */
    0,                                                   /* tp_alloc */
    PyBobIpOptflowForwardGradient_new,                   /* tp_new */
};

#undef CLASS_NAME
#define CLASS_NAME "HornAndSchunckGradient"
static auto s_hs = bob::extension::ClassDoc(
    BOB_EXT_MODULE_PREFIX "." CLASS_NAME,

    "Computes the spatio-temporal gradient using a 2-term approximation",

    "This class computes the spatio-temporal gradient using the same "
    "approximation as the one described by Horn & Schunck in the paper titled "
    "'Determining Optical Flow', published in 1981, Artificial Intelligence, "
    "* Vol. 17, No. 1-3, pp. 185-203.\n"
    "\n"
    "This is equivalent to convolving the image sequence with the following "
    "(separate) kernels:\n"
    "\n"
    ".. math::\n"
    "   \n"
    "   E_x = \\frac{1}{4} ([-1,+1]^T * ([+1,+1]*i_1) + [-1,+1]^T * ([+1,+1]*i_2))\\\\\n"
    "   E_y = \\frac{1}{4} ([+1,+1]^T * ([-1,+1]*i_1) + [+1,+1]^T * ([-1,+1]*i_2))\\\\\n"
    "   E_t = \\frac{1}{4} ([+1,+1]^T * ([+1,+1]*i_1) - [+1,+1]^T * ([+1,+1]*i_2))\\\\\n"
    "\n"
    )
    .add_constructor(
        bob::extension::FunctionDoc(
          CLASS_NAME,
          "Constructor",
          "We initialize with the shape of the images we need to treat. "
          "The shape is used by the internal buffers.\n"
          "\n"
          "The difference kernel for this operator is fixed to "
          ":math:`[+1/4; -1/4]`. The averaging kernel is fixed to "
          ":math:`[+1; +1]`.\n"
          "\n"
          )
        .add_prototype("(height, width)", "")
        .add_parameter("(height, width)", "tuple", "the height and width of images to be fed into the the gradient estimator")
        )
    ;

typedef struct {
  PyBobIpOptflowForwardGradientObject parent;
  bob::ip::optflow::HornAndSchunckGradient* cxx;
} PyBobIpOptflowHornAndSchunckGradientObject;

static int PyBobIpOptflowHornAndSchunckGradient_init
(PyBobIpOptflowHornAndSchunckGradientObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"shape", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t height, width;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "(nn)", kwlist,
        &height, &width)) return -1;

  try {
    blitz::TinyVector<int,2> shape;
    shape(0) = height; shape(1) = width;
    self->cxx = new bob::ip::optflow::HornAndSchunckGradient(shape);
  }
  catch (std::exception& ex) {
    PyErr_SetString(PyExc_RuntimeError, ex.what());
    return -1;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "cannot create new object of type `%s' - unknown exception thrown", Py_TYPE(self)->tp_name);
    return -1;
  }

  self->parent.cxx = self->cxx;

  return 0;

}

static void PyBobIpOptflowHornAndSchunckGradient_delete
(PyBobIpOptflowHornAndSchunckGradientObject* self) {

  self->parent.cxx = 0;
  delete self->cxx;
  Py_TYPE(&self->parent)->tp_free((PyObject*)self);

}

PyTypeObject PyBobIpOptflowHornAndSchunckGradient_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_hs.name(),                                             /*tp_name*/
    sizeof(PyBobIpOptflowHornAndSchunckGradientObject),      /*tp_basicsize*/
    0,                                                       /*tp_itemsize*/
    (destructor)PyBobIpOptflowHornAndSchunckGradient_delete, /*tp_dealloc*/
    0,                                                       /*tp_print*/
    0,                                                       /*tp_getattr*/
    0,                                                       /*tp_setattr*/
    0,                                                       /*tp_compare*/
    0,                                                       /*tp_repr*/
    0,                                                       /*tp_as_number*/
    0,                                                       /*tp_as_sequence*/
    0,                                                       /*tp_as_mapping*/
    0,                                                       /*tp_hash */
    0,                                                       /*tp_call*/
    0,                                                       /*tp_str*/
    0,                                                       /*tp_getattro*/
    0,                                                       /*tp_setattro*/
    0,                                                       /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,                /*tp_flags*/
    s_hs.doc(),                                              /* tp_doc */
    0,		                                                   /* tp_traverse */
    0,		                                                   /* tp_clear */
    0,                                                       /* tp_richcompare */
    0,		                                                   /* tp_weaklistoffset */
    0,		                                                   /* tp_iter */
    0,		                                                   /* tp_iternext */
    0,                                                       /* tp_methods */
    0,                                                       /* tp_members */
    0,                                                       /* tp_getset */
    0,                                                       /* tp_base */
    0,                                                       /* tp_dict */
    0,                                                       /* tp_descr_get */
    0,                                                       /* tp_descr_set */
    0,                                                       /* tp_dictoffset */
    (initproc)PyBobIpOptflowHornAndSchunckGradient_init,     /* tp_init */
    0,                                                       /* tp_alloc */
    0,                                                       /* tp_new */
};
