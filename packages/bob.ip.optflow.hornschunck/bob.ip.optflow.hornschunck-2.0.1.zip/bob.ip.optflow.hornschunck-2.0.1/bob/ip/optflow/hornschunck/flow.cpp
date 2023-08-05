/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Wed 09 Apr 2014 13:09:22 CEST
 *
 * @brief Bindings for Horn & Schunck's Optical Flow framework
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>
#include <structmember.h>

#include "HornAndSchunckFlow.h"

/*************************************
 * Implementation of Flow base class *
 *************************************/

#define CLASS_NAME "Flow"

static auto s_flow = bob::extension::ClassDoc(
    BOB_EXT_MODULE_PREFIX "." CLASS_NAME,

    "Estimates the Optical Flow between images.",

    "This is a clone of the Vanilla Horn & Schunck method that uses a Sobel "
    "gradient estimator instead of the forward estimator used by the "
    "classical method. The Laplacian operator is also replaced with a more "
    "common implementation. The Sobel filter requires 3 images for the "
    "gradient estimation. Therefore, this implementation inputs 3 image sets "
    "instead of just 2. The flow is calculated w.r.t. **central** image.\n"
    "\n"
    "For more details on the general technique from Horn & Schunck, see the "
    "module's documentation."
    )
    .add_constructor(
        bob::extension::FunctionDoc(
          CLASS_NAME,
          "Initializes the functor with the sizes of images to be treated."
          )
        .add_prototype("(height, width)", "")
        .add_parameter("(height, width)", "tuple", "the height and width of images to be fed into the the flow estimator")
        )
    ;


typedef struct {
  PyObject_HEAD
  bob::ip::optflow::HornAndSchunckFlow* cxx;
} PyBobIpOptflowHornAndSchunckObject;


static int PyBobIpOptflowHornAndSchunck_init
(PyBobIpOptflowHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"shape", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t height, width;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "(nn)", kwlist,
        &height, &width)) return -1;

  try {
    blitz::TinyVector<int,2> shape;
    shape(0) = height; shape(1) = width;
    self->cxx = new bob::ip::optflow::HornAndSchunckFlow(shape);
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

static void PyBobIpOptflowHornAndSchunck_delete
(PyBobIpOptflowHornAndSchunckObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

static auto s_shape = bob::extension::VariableDoc(
    "shape",
    "tuple",
    "The shape pre-configured for this flow estimator: ``(height, width)``"
    );

static PyObject* PyBobIpOptflowHornAndSchunck_getShape
(PyBobIpOptflowHornAndSchunckObject* self, void* /*closure*/) {
  auto shape = self->cxx->getShape();
  return Py_BuildValue("nn", shape(0), shape(1));
}

static int PyBobIpOptflowHornAndSchunck_setShape (PyBobIpOptflowHornAndSchunckObject* self, PyObject* o, void* /*closure*/) {

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

static PyGetSetDef PyBobIpOptflowHornAndSchunck_getseters[] = {
    {
      s_shape.name(),
      (getter)PyBobIpOptflowHornAndSchunck_getShape,
      (setter)PyBobIpOptflowHornAndSchunck_setShape,
      s_shape.doc(),
      0
    },
    {0}  /* Sentinel */
};

PyObject* PyBobIpOptflowHornAndSchunck_Repr(PyBobIpOptflowHornAndSchunckObject* self) {

  /**
   * Expected output:
   *
   * <bob.ip.optflow.hornschunck.Flow((3, 2))>
   */

  auto shape = make_safe(PyBobIpOptflowHornAndSchunck_getShape(self, 0));
  if (!shape) return 0;
  auto shape_str = make_safe(PyObject_Str(shape.get()));

  PyObject* retval = PyUnicode_FromFormat("<%s(%U)>",
      Py_TYPE(self)->tp_name, shape_str.get());

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

static auto s_estimate = bob::extension::FunctionDoc(
    "estimate",
    "Estimates the optical flow leading to ``image2``. This method will use "
    "leading image ``image1`` and the after image ``image3``, to estimate "
    "the optical flow leading to ``image2``. All input images should be 2D "
    "64-bit float arrays with the shape ``(height, width)`` as specified in "
    "the construction of the object."
    )
    .add_prototype("alpha, iterations, image1, image2, image3, [u, v]", "u, v")
    .add_parameter("alpha", "float", "The weighting factor between brightness constness and the field smoothness. According to original paper, :math:`\\alpha^2` should be more or less set to noise in estimating :math:`E_x^2 + E_y^2`. In practice, many algorithms consider values around 200 a good default. The higher this number is, the more importance on smoothing you will be putting.")
    .add_parameter("iterations", "int", "Number of iterations for which to minimize the flow error")
    .add_parameter("image1, image2, image3", "array-like (2D, float64)",
      "Sequence of images to estimate the flow from")
    .add_parameter("u, v", "array (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively) will be output in these variables, which should have dimensions matching those of this functor. If you don't provide arrays for ``u`` and ``v``, then they will be allocated internally and returned. You must either provide neither ``u`` and ``v`` or both, otherwise an exception will be raised. Notice that, if you provide ``u`` and ``v`` which are non-zero, they will be taken as initial values for the error minimization. These arrays will be updated with the final value of the flow leading to ``image2``.")
    .add_return("u, v", "array (2D, float)", "The estimated flows in the horizontal and vertical directions (respectively)."
    )
    ;

static PyObject* PyBobIpOptflowHornAndSchunck_estimate
(PyBobIpOptflowHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "alpha",
    "iterations",
    "image1",
    "image2",
    "image3",
    "u",
    "v",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  double alpha;
  Py_ssize_t iterations;
  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* image3 = 0;
  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "dnO&O&O&|O&O&", kwlist,
        &alpha, &iterations,
        &PyBlitzArray_Converter, &image1,
        &PyBlitzArray_Converter, &image2,
        &PyBlitzArray_Converter, &image3,
        &PyBlitzArray_OutputConverter, &u,
        &PyBlitzArray_OutputConverter, &v
        )) return 0;

  //protects acquired resources through this scope
  auto image1_ = make_safe(image1);
  auto image2_ = make_safe(image2);
  auto image3_ = make_safe(image3);
  auto u_ = make_xsafe(u);
  auto v_ = make_xsafe(v);

  if (image1->type_num != NPY_FLOAT64 || image1->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image1'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (image2->type_num != NPY_FLOAT64 || image2->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image2'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (image3->type_num != NPY_FLOAT64 || image3->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image3'", Py_TYPE(self)->tp_name);
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

  if (image3->shape[0] != height || image3->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `image3', but `image3''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, image3->shape[0], image3->shape[1]);
    return 0;
  }

  if (u && !v) {
    PyErr_Format(PyExc_RuntimeError, "`%s' requires either both `u' and `v' or none, but you provided `u' and not `v'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (v && !u) {
    PyErr_Format(PyExc_RuntimeError, "`%s' requires either both `u' and `v' or none, but you provided `v' and not `u'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (u) { //&& v

    if (u->type_num != NPY_FLOAT64 || u->ndim != 2) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `u'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (v->type_num != NPY_FLOAT64 || v->ndim != 2) {
      PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `v'", Py_TYPE(self)->tp_name);
      return 0;
    }

    if (u->shape[0] != height || u->shape[1] != width) {
      PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `u', but `u''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, u->shape[0], u->shape[1]);
      return 0;
    }

    if (v->shape[0] != height || v->shape[1] != width) {
      PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `v', but `v''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, v->shape[0], v->shape[1]);
      return 0;
    }

  }
  else { //allocates u and v

    u = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
        image1->ndim, image1->shape);
    auto bz_u = PyBlitzArrayCxx_AsBlitz<double,2>(u);
    (*bz_u) = 0.;
    u_ = make_safe(u);

    v = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
        image1->ndim, image1->shape);
    auto bz_v = PyBlitzArrayCxx_AsBlitz<double,2>(v);
    (*bz_v) = 0.;
    v_ = make_safe(v);

  }

  /** all basic checks are done, can call the functor now **/
  try {
    self->cxx->operator()(alpha, iterations,
        *PyBlitzArrayCxx_AsBlitz<double,2>(image1),
        *PyBlitzArrayCxx_AsBlitz<double,2>(image2),
        *PyBlitzArrayCxx_AsBlitz<double,2>(image3),
        *PyBlitzArrayCxx_AsBlitz<double,2>(u),
        *PyBlitzArrayCxx_AsBlitz<double,2>(v)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot estimate flow: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(u);
  Py_INCREF(v);

  return Py_BuildValue("(OO)",
    PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(u)),
    PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(v))
    );

}

static auto s_eval_ec2 = bob::extension::FunctionDoc(
    "eval_ec2",
    "Calculates the square of the smoothness error (:math:`E_c^2`) by using the formula described in the paper: :math:`E_c^2 = (\\bar{u} - u)^2 + (\\bar{v} - v)^2`. Sets the input matrix with the discrete values."
    )
    .add_prototype("u, v", "error")
    .add_parameter("u, v", "array-like (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively), which should have dimensions matching those of this functor.")
    .add_return("error", "array (2D, float)", "The square of the smoothness error."
    )
    ;

static PyObject* PyBobIpOptflowHornAndSchunck_eval_ec2
(PyBobIpOptflowHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "u",
    "v",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&", kwlist,
        &PyBlitzArray_Converter, &u,
        &PyBlitzArray_Converter, &v
        )) return 0;

  //protects acquired resources through this scope
  auto u_ = make_safe(u);
  auto v_ = make_safe(v);

  if (u->type_num != NPY_FLOAT64 || u->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `u'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (v->type_num != NPY_FLOAT64 || v->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `v'", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_ssize_t height = self->cxx->getShape()(0);
  Py_ssize_t width = self->cxx->getShape()(1);

  if (u->shape[0] != height || u->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `u', but `u''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, u->shape[0], u->shape[1]);
    return 0;
  }

  if (v->shape[0] != height || v->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `v', but `v''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, v->shape[0], v->shape[1]);
    return 0;
  }

  //allocates the error return
  auto error = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
      u->ndim, u->shape);
  auto error_ = make_safe(error);

  /** all basic checks are done, can call the functor now **/
  try {
    self->cxx->evalEc2(
        *PyBlitzArrayCxx_AsBlitz<double,2>(u),
        *PyBlitzArrayCxx_AsBlitz<double,2>(v),
        *PyBlitzArrayCxx_AsBlitz<double,2>(error)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot calculate smoothness error: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(error);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(error));

}

static auto s_eval_eb = bob::extension::FunctionDoc(
    "eval_eb",
    "Calculates the brightness error (:math:`E_b`) as defined in the paper: :math:`E_b = (E_x u + E_y v + E_t)`"
    )
    .add_prototype("image1, image2, image3, u, v", "error")
    .add_parameter("image1, image2, image3", "array-like (2D, float64)",
      "Sequence of images the flow was estimated with")
    .add_parameter("u, v", "array-like (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively), which should have dimensions matching those of this functor.")
    .add_return("error", "array (2D, float)", "The evaluated brightness error."
    )
    ;

static PyObject* PyBobIpOptflowHornAndSchunck_eval_eb
(PyBobIpOptflowHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "image1",
    "image2",
    "image3",
    "u",
    "v",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* image3 = 0;
  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&O&O&O&", kwlist,
        &PyBlitzArray_Converter, &image1,
        &PyBlitzArray_Converter, &image2,
        &PyBlitzArray_Converter, &image3,
        &PyBlitzArray_Converter, &u,
        &PyBlitzArray_Converter, &v
        )) return 0;

  //protects acquired resources through this scope
  auto image1_ = make_safe(image1);
  auto image2_ = make_safe(image2);
  auto image3_ = make_safe(image3);
  auto u_ = make_safe(u);
  auto v_ = make_safe(v);

  if (image1->type_num != NPY_FLOAT64 || image1->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image1'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (image2->type_num != NPY_FLOAT64 || image2->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image2'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (image3->type_num != NPY_FLOAT64 || image3->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `image3'", Py_TYPE(self)->tp_name);
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

  if (image3->shape[0] != height || image3->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `image3', but `image3''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, image3->shape[0], image3->shape[1]);
    return 0;
  }

  if (u->type_num != NPY_FLOAT64 || u->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for (optional) input array `u'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (v->type_num != NPY_FLOAT64 || v->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' only supports 2D 64-bit float arrays for input array `v'", Py_TYPE(self)->tp_name);
    return 0;
  }

  if (u->shape[0] != height || u->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `u', but `u''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, u->shape[0], u->shape[1]);
    return 0;
  }

  if (v->shape[0] != height || v->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "`%s' only supports arrays with shape (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) for input array `v', but `v''s shape is (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", Py_TYPE(self)->tp_name, height, width, v->shape[0], v->shape[1]);
    return 0;
  }

  //allocates the error return
  auto error = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
      u->ndim, u->shape);
  auto error_ = make_safe(error);

  /** all basic checks are done, can call the functor now **/
  try {
    self->cxx->evalEb(
        *PyBlitzArrayCxx_AsBlitz<double,2>(image1),
        *PyBlitzArrayCxx_AsBlitz<double,2>(image2),
        *PyBlitzArrayCxx_AsBlitz<double,2>(image3),
        *PyBlitzArrayCxx_AsBlitz<double,2>(u),
        *PyBlitzArrayCxx_AsBlitz<double,2>(v),
        *PyBlitzArrayCxx_AsBlitz<double,2>(error)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_Format(PyExc_RuntimeError, "%s cannot estimate brightness error: unknown exception caught", Py_TYPE(self)->tp_name);
    return 0;
  }

  Py_INCREF(error);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(error));

}

static PyMethodDef PyBobIpOptflowHornAndSchunck_methods[] = {
  {
    s_estimate.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_estimate,
    METH_VARARGS|METH_KEYWORDS,
    s_estimate.doc()
  },
  {
    s_eval_ec2.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_eval_ec2,
    METH_VARARGS|METH_KEYWORDS,
    s_eval_ec2.doc()
  },
  {
    s_eval_eb.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_eval_eb,
    METH_VARARGS|METH_KEYWORDS,
    s_eval_eb.doc()
  },
  {0} /* Sentinel */
};

static PyObject* PyBobIpOptflowHornAndSchunck_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIpOptflowHornAndSchunckObject* self =
    (PyBobIpOptflowHornAndSchunckObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyTypeObject PyBobIpOptflowHornAndSchunck_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_flow.name(),                                      /* tp_name */
    sizeof(PyBobIpOptflowHornAndSchunckObject),         /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor)PyBobIpOptflowHornAndSchunck_delete,    /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    (reprfunc)PyBobIpOptflowHornAndSchunck_Repr,        /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    (ternaryfunc)PyBobIpOptflowHornAndSchunck_estimate, /* tp_call */
    (reprfunc)PyBobIpOptflowHornAndSchunck_Repr,        /* tp_str */
    0,                                                  /* tp_getattro */
    0,                                                  /* tp_setattro */
    0,                                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,           /* tp_flags */
    s_flow.doc(),                                       /* tp_doc */
    0,                                                  /* tp_traverse */
    0,                                                  /* tp_clear */
    0,                                                  /* tp_richcompare */
    0,                                                  /* tp_weaklistoffset */
    0,                                                  /* tp_iter */
    0,                                                  /* tp_iternext */
    PyBobIpOptflowHornAndSchunck_methods,               /* tp_methods */
    0,                                                  /* tp_members */
    PyBobIpOptflowHornAndSchunck_getseters,             /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)PyBobIpOptflowHornAndSchunck_init,        /* tp_init */
    0,                                                  /* tp_alloc */
    PyBobIpOptflowHornAndSchunck_new,                   /* tp_new */
};
