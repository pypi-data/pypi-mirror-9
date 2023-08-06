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

#define CLASS_NAME "VanillaFlow"

static auto s_flow = bob::extension::ClassDoc(
    BOB_EXT_MODULE_PREFIX "." CLASS_NAME,

    "Estimates the Optical Flow between images.",

    "Estimates the Optical Flow between two sequences of images (``image1``, "
    "the starting image and ``image2``, the final image). It does this using "
    "the iterative method described by Horn & Schunck in the paper titled "
    "\"Determining Optical Flow\", published in 1981, Artificial "
    "Intelligence, Vol. 17, No. 1-3, pp. 185-203.\n"
    "\n"
    "The method constrains the calculation with two assertions that can be "
    "made on a natural sequence of images:\n"
    "\n"
    "1. For the same lighting conditions, the brightness (:math:`E`) of the "
    "shapes in an image do not change and, therefore, the derivative of E "
    "w.r.t. time (:math:`\\frac{dE}{dt}`) equals zero.\n"
    "\n"
    "2. The relative velocities of adjancent points in an image varies "
    "smoothly. The smothness constraint is applied on the image data using "
    "the Laplacian operator.\n"
    "\n"
    "It then approximates the calculation of conditions 1 and 2 above using "
    "a Taylor series expansion and ignoring terms with order greater or "
    "equal 2. This technique is also know as \"Finite Differences\" and is "
    "applied in other engineering fields such as Fluid Mechanics.\n"
    "\n"
    "The problem is finally posed as an iterative process that simultaneously"
    "minimizes conditions 1 and 2 above. A weighting factor (:math:`\\alpha` "
    "- also sometimes referred as :math:`\\lambda` in some implementations) "
    "controls the relative importance of the two above conditions. The higher "
    "it gets, the smoother the field will be.\n"
    "\n"
    ".. note::\n"
    "   \n"
    "   OpenCV also has an implementation for H&S optical flow. "
    "It sets :math:`\\lambda = \\alpha^2`\n"
    "\n"
    "This is the set of equations that are implemented:\n"
    "\n"
    ".. math::\n"
    "   \n"
    "   u(n+1) = U(n) - E_x[E_x * U(n) + E_y * V(n) + E_t] /\n"
    "                                          (\\alpha^2 + E_x^2 + E_y^2)\\\\\n"
    "   v(n+1) = V(n) - E_y[E_y * U(n) + E_y * V(n) + E_t] /\n"
    "                                          (\\alpha^2 + E_x^2 + E_y^2)\\\\\n"
    "\n"
    "Where:\n"
    "\n"
    ":math:`u(\\cdot)`\n"
    "  is the relative velocity in the :math:`x` direction\n"
    "\n"
    ":math:`v(\\cdot)`\n"
    "  is the relative velocity in the :math:`y` direction\n"
    "\n"
    ":math:`E_x`, :math:`E_y` and :math:`E_t`\n"
    "  are partial derivatives of brightness in the :math:`x`, :math:`y` "
    "and :math:`t` directions, estimated using finite differences based "
    "on the input images, ``i1`` and ``i2``\n"
    "\n"
    ":math:`U(\\cdot)`\n"
    "  laplacian estimates for x given equations in Section 8 of the paper\n"
    "\n"
    ":math:`V(\\cdot)`\n"
    "  laplacian estimates for y given equations in Section 8 of the paper\n"
    "\n"
    "According to paper, :math:`\\alpha^2` should be more or less set to "
    "noise in estimating :math:`E_x^2 + E_y^2`. In practice, many algorithms "
    "consider values around 200 a good default. The higher this number is, "
    "the more importance on smoothing you will be putting.\n"
    "\n"
    "The initial conditions are set such that :math:`u(0) = v(0) = 0`, "
    "except in the case where you provide them. For example, if you are "
    "analyzing a video stream, it is a good idea to use the previous "
    "estimate as the initial conditions.\n"
    "\n"
    ".. note::\n"
    "   \n"
    "   This is a dense flow estimator. The optical flow is computed for all "
    "pixels in the image.\n"
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
  bob::ip::optflow::VanillaHornAndSchunckFlow* cxx;
} PyBobIpOptflowVanillaHornAndSchunckObject;


static int PyBobIpOptflowVanillaHornAndSchunck_init
(PyBobIpOptflowVanillaHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"shape", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  Py_ssize_t height, width;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "(nn)", kwlist,
        &height, &width)) return -1;

  try {
    blitz::TinyVector<int,2> shape;
    shape(0) = height; shape(1) = width;
    self->cxx = new bob::ip::optflow::VanillaHornAndSchunckFlow(shape);
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

static void PyBobIpOptflowVanillaHornAndSchunck_delete
(PyBobIpOptflowVanillaHornAndSchunckObject* self) {

  delete self->cxx;
  Py_TYPE(self)->tp_free((PyObject*)self);

}

static auto s_shape = bob::extension::VariableDoc(
    "shape",
    "tuple",
    "The shape pre-configured for this flow estimator: ``(height, width)``"
    );

static PyObject* PyBobIpOptflowVanillaHornAndSchunck_getShape
(PyBobIpOptflowVanillaHornAndSchunckObject* self, void* /*closure*/) {
  auto shape = self->cxx->getShape();
  return Py_BuildValue("nn", shape(0), shape(1));
}

static int PyBobIpOptflowVanillaHornAndSchunck_setShape (PyBobIpOptflowVanillaHornAndSchunckObject* self, PyObject* o, void* /*closure*/) {

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

static PyGetSetDef PyBobIpOptflowVanillaHornAndSchunck_getseters[] = {
    {
      s_shape.name(),
      (getter)PyBobIpOptflowVanillaHornAndSchunck_getShape,
      (setter)PyBobIpOptflowVanillaHornAndSchunck_setShape,
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

PyObject* PyBobIpOptflowVanillaHornAndSchunck_Repr(PyBobIpOptflowVanillaHornAndSchunckObject* self) {

  /**
   * Expected output:
   *
   * <bob.ip.optflow.hornschunck.VanillaFlow((3, 2))>
   */

  auto shape = make_safe(PyBobIpOptflowVanillaHornAndSchunck_getShape(self, 0));
  if (!shape) return 0;
  auto shape_str = make_safe(PyObject_Str(shape.get()));

  return PyUnicode_FromFormat("<%s(%U)>",
      Py_TYPE(self)->tp_name, shape_str.get());

}

static auto s_estimate = bob::extension::FunctionDoc(
    "estimate",
    "Estimates the optical flow leading to ``image2``. This method will use "
    "the leading image ``image1``, to estimate the optical flow leading to "
    "``image2``. All input images should be 2D 64-bit float arrays with the "
    "shape ``(height, width)`` as specified in the construction of the object."
    )
    .add_prototype("alpha, iterations, image1, image2, [u, v]", "u, v")
    .add_parameter("alpha", "float", "The weighting factor between brightness constness and the field smoothness. According to original paper, :math:`\\alpha^2` should be more or less set to noise in estimating :math:`E_x^2 + E_y^2`. In practice, many algorithms consider values around 200 a good default. The higher this number is, the more importance on smoothing you will be putting.")
    .add_parameter("iterations", "int", "Number of iterations for which to minimize the flow error")
    .add_parameter("image1, image2", "array-like (2D, float64)",
      "Sequence of images to estimate the flow from")
    .add_parameter("u, v", "array (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively) will be output in these variables, which should have dimensions matching those of this functor. If you don't provide arrays for ``u`` and ``v``, then they will be allocated internally and returned. You must either provide neither ``u`` and ``v`` or both, otherwise an exception will be raised. Notice that, if you provide ``u`` and ``v`` which are non-zero, they will be taken as initial values for the error minimization. These arrays will be updated with the final value of the flow leading to ``image2``.")
    .add_return("u, v", "array (2D, float)", "The estimated flows in the horizontal and vertical directions (respectively)."
    )
    ;

static PyObject* PyBobIpOptflowVanillaHornAndSchunck_estimate
(PyBobIpOptflowVanillaHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "alpha",
    "iterations",
    "image1",
    "image2",
    "u",
    "v",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  double alpha;
  Py_ssize_t iterations;
  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "dnO&O&|O&O&", kwlist,
        &alpha, &iterations,
        &PyBlitzArray_Converter, &image1,
        &PyBlitzArray_Converter, &image2,
        &PyBlitzArray_OutputConverter, &u,
        &PyBlitzArray_OutputConverter, &v
        )) return 0;

  //protects acquired resources through this scope
  auto image1_ = make_safe(image1);
  auto image2_ = make_safe(image2);
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

  return Py_BuildValue("(NN)",
    PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", u)),
    PyBlitzArray_NUMPY_WRAP(Py_BuildValue("O", v))
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

static PyObject* PyBobIpOptflowVanillaHornAndSchunck_eval_ec2
(PyBobIpOptflowVanillaHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

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
    .add_prototype("image1, image2, u, v", "error")
    .add_parameter("image1, image2", "array-like (2D, float64)",
      "Sequence of images the flow was estimated with")
    .add_parameter("u, v", "array-like (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively), which should have dimensions matching those of this functor.")
    .add_return("error", "array (2D, float)", "The evaluated brightness error."
    )
    ;

static PyObject* PyBobIpOptflowVanillaHornAndSchunck_eval_eb
(PyBobIpOptflowVanillaHornAndSchunckObject* self, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "image1",
    "image2",
    "u",
    "v",
    0
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&O&O&", kwlist,
        &PyBlitzArray_Converter, &image1,
        &PyBlitzArray_Converter, &image2,
        &PyBlitzArray_Converter, &u,
        &PyBlitzArray_Converter, &v
        )) return 0;

  //protects acquired resources through this scope
  auto image1_ = make_safe(image1);
  auto image2_ = make_safe(image2);
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

static PyMethodDef PyBobIpOptflowVanillaHornAndSchunck_methods[] = {
  {
    s_estimate.name(),
    (PyCFunction)PyBobIpOptflowVanillaHornAndSchunck_estimate,
    METH_VARARGS|METH_KEYWORDS,
    s_estimate.doc()
  },
  {
    s_eval_ec2.name(),
    (PyCFunction)PyBobIpOptflowVanillaHornAndSchunck_eval_ec2,
    METH_VARARGS|METH_KEYWORDS,
    s_eval_ec2.doc()
  },
  {
    s_eval_eb.name(),
    (PyCFunction)PyBobIpOptflowVanillaHornAndSchunck_eval_eb,
    METH_VARARGS|METH_KEYWORDS,
    s_eval_eb.doc()
  },
  {0} /* Sentinel */
};

static PyObject* PyBobIpOptflowVanillaHornAndSchunck_new
(PyTypeObject* type, PyObject*, PyObject*) {

  /* Allocates the python object itself */
  PyBobIpOptflowVanillaHornAndSchunckObject* self =
    (PyBobIpOptflowVanillaHornAndSchunckObject*)type->tp_alloc(type, 0);

  self->cxx = 0;

  return reinterpret_cast<PyObject*>(self);

}

PyTypeObject PyBobIpOptflowVanillaHornAndSchunck_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_flow.name(),                                      /* tp_name */
    sizeof(PyBobIpOptflowVanillaHornAndSchunckObject),  /* tp_basicsize */
    0,                                                  /* tp_itemsize */
    (destructor)PyBobIpOptflowVanillaHornAndSchunck_delete, /* tp_dealloc */
    0,                                                  /* tp_print */
    0,                                                  /* tp_getattr */
    0,                                                  /* tp_setattr */
    0,                                                  /* tp_compare */
    (reprfunc)PyBobIpOptflowVanillaHornAndSchunck_Repr, /* tp_repr */
    0,                                                  /* tp_as_number */
    0,                                                  /* tp_as_sequence */
    0,                                                  /* tp_as_mapping */
    0,                                                  /* tp_hash */
    (ternaryfunc)PyBobIpOptflowVanillaHornAndSchunck_estimate, /* tp_call */
    (reprfunc)PyBobIpOptflowVanillaHornAndSchunck_Repr, /* tp_str */
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
    PyBobIpOptflowVanillaHornAndSchunck_methods,        /* tp_methods */
    0,                                                  /* tp_members */
    PyBobIpOptflowVanillaHornAndSchunck_getseters,      /* tp_getset */
    0,                                                  /* tp_base */
    0,                                                  /* tp_dict */
    0,                                                  /* tp_descr_get */
    0,                                                  /* tp_descr_set */
    0,                                                  /* tp_dictoffset */
    (initproc)PyBobIpOptflowVanillaHornAndSchunck_init, /* tp_init */
    0,                                                  /* tp_alloc */
    PyBobIpOptflowVanillaHornAndSchunck_new,            /* tp_new */
};
