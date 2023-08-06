/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 25 Oct 16:54:55 2013
 *
 * @brief Bindings to bob::sp
 */

#ifdef NO_IMPORT_ARRAY
#undef NO_IMPORT_ARRAY
#endif
#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.extension/documentation.h>

#include "HornAndSchunckFlow.h"

extern PyTypeObject PyBobIpOptflowHornAndSchunck_Type;
extern PyTypeObject PyBobIpOptflowVanillaHornAndSchunck_Type;
extern PyTypeObject PyBobIpOptflowForwardGradient_Type;
extern PyTypeObject PyBobIpOptflowHornAndSchunckGradient_Type;
extern PyTypeObject PyBobIpOptflowCentralGradient_Type;
extern PyTypeObject PyBobIpOptflowSobelGradient_Type;
extern PyTypeObject PyBobIpOptflowPrewittGradient_Type;
extern PyTypeObject PyBobIpOptflowIsotropicGradient_Type;

static auto s_laplacian_avg_hs = bob::extension::FunctionDoc(
    "laplacian_avg_hs",

    "Filters the input image using the Laplacian (averaging) operator.",

    "An approximation to the Laplacian operator. Using the following "
    "(non-separable) kernel:\n"
    "\n"
    ".. math::\n"
    "   \n"
    "   k = \\begin{bmatrix}\n"
    "          -1 & -2 & -1\\\\[1em]\n"
    "          -2 & 12 & -2\\\\[1em]\n"
    "          -1 & -2 & -1\\\\\n"
    "       \\end{bmatrix}\n"
    "\n"
    "This is the one used on the Horn & Schunck paper. To calculate the "
    ":math:`\\bar{u}` value we must remove the central mean and multiply by "
    ":math:`\\frac{-1}{12}`, yielding:\n"
    "\n"
    ".. math::\n"
    "   k = \\begin{bmatrix}\n"
    "          \\frac{1}{12} & \\frac{1}{6} & \\frac{1}{12}\\\\[0.3em]\n"
    "          \\frac{1}{6}  &       0      & \\frac{1}{6}\\\\[0.3em]\n"
    "          \\frac{1}{12} & \\frac{1}{6} & \\frac{1}{12}\\\\\n"
    "       \\end{bmatrix}\n"
    "\n"
    ".. note::\n"
    "   \n"
    "   You will get the **wrong** results if you use the Laplacian kernel "
    "directly."
    )
    .add_prototype("input", "output")
    .add_parameter("input", "array-like (2D, float64)",
      "The 2D array to which you'd like to apply the laplacian operator.")
    .add_return("output", "array (2D, float)", "The result of applying the laplacian operator on ``input``.")
    ;

PyObject* PyBobIpOptflowHornAndSchunck_LaplacianAverage(
    PyObject*, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"input", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* input = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist,
        &PyBlitzArray_Converter, &input)) return 0;

  //protects acquired resources through this scope
  auto input_ = make_safe(input);

  if (input->type_num != NPY_FLOAT64 || input->ndim != 2) {
    PyErr_SetString(PyExc_TypeError, "function only supports 2D 64-bit float arrays for `input' array");
    return 0;
  }

  //allocates the output
  auto output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
      input->ndim, input->shape);
  if (!output) return 0;
  auto output_ = make_safe(output);

  try {
    bob::ip::optflow::laplacian_avg_hs(
        *PyBlitzArrayCxx_AsBlitz<double,2>(input),
        *PyBlitzArrayCxx_AsBlitz<double,2>(output)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot apply filter: unknown exception caught");
    return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

static auto s_laplacian_avg_hs_opencv = bob::extension::FunctionDoc(
    "laplacian_avg_hs_opencv",

    "Filters the input image using the Laplacian (averaging) operator.",

    "An approximation to the Laplacian operator. Using the following "
    "(non-separable) kernel:\n"
    "\n"
    ".. math::\n"
    "   \n"
    "   k = \\begin{bmatrix}\n"
    "           0 & -1 &  0\\\\[1em]\n"
    "          -1 &  4 & -1\\\\[1em]\n"
    "           0 & -1 & -0\\\\\n"
    "       \\end{bmatrix}\n"
    "\n"
    "This is used as Laplacian operator in OpenCV. To calculate the "
    ":math:`\\bar{u}` value we must remove the central mean and multiply by "
    ":math:`\\frac{-1}{4}`, yielding:\n"
    "\n"
    ".. math::\n"
    "   k = \\begin{bmatrix}\n"
    "                0       & \\frac{1}{4} &       0     \\\\[0.3em]\n"
    "          \\frac{1}{4}  &       0      & \\frac{1}{4}\\\\[0.3em]\n"
    "                0       & \\frac{1}{4} &       0     \\\\\n"
    "       \\end{bmatrix}\n"
    "\n"
    ".. note::\n"
    "   \n"
    "   You will get the **wrong** results if you use the Laplacian kernel "
    "directly."
    )
    .add_prototype("input", "output")
    .add_parameter("input", "array-like (2D, float64)",
      "The 2D array to which you'd like to apply the laplacian operator.")
    .add_return("output", "array (2D, float)", "The result of applying the laplacian operator on ``input``.")
    ;

PyObject* PyBobIpOptflowHornAndSchunck_LaplacianAverageOpenCV(
    PyObject*, PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {"input", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* input = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&", kwlist,
        &PyBlitzArray_Converter, &input)) return 0;

  //protects acquired resources through this scope
  auto input_ = make_safe(input);

  if (input->type_num != NPY_FLOAT64 || input->ndim != 2) {
    PyErr_SetString(PyExc_TypeError, "function only supports 2D 64-bit float arrays for `input' array");
    return 0;
  }

  //allocates the output
  auto output = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
      input->ndim, input->shape);
  if (!output) return 0;
  auto output_ = make_safe(output);

  try {
    bob::ip::optflow::laplacian_avg_hs_opencv(
        *PyBlitzArrayCxx_AsBlitz<double,2>(input),
        *PyBlitzArrayCxx_AsBlitz<double,2>(output)
        );
  }
  catch (std::exception& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    return 0;
  }
  catch (...) {
    PyErr_SetString(PyExc_RuntimeError, "cannot apply filter: unknown exception caught");
    return 0;
  }

  Py_INCREF(output);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(output));

}

static auto s_flow_error = bob::extension::FunctionDoc(
    "flow_error",

    "Computes the generalized flow error between two images.",

    "This function calculates the flow error between a pair of images:\n"
    "\n"
    ".. math::\n"
    "   \n"
    "   E = i2(x-u,y-v) - i1(x,y))\n"
    "\n"
    )
    .add_prototype("image1, image2, u, v", "E")
    .add_parameter("image1, image2", "array-like (2D, float64)",
      "Sequence of images the flow was estimated with")
    .add_parameter("u, v", "array-like (2D, float64)", "The estimated flows in the horizontal and vertical directions (respectively), which should have dimensions matching those of ``image1`` and ``image2``.")
    .add_return("E", "array (2D, float)", "The estimated flow error E.")
    ;

PyObject* PyBobIpOptflowHornAndSchunck_FlowError(PyObject*,
    PyObject* args, PyObject* kwds) {

  static const char* const_kwlist[] = {
    "image1",
    "image2",
    "u",
    "v",
    };
  static char** kwlist = const_cast<char**>(const_kwlist);

  double alpha;
  Py_ssize_t iterations;
  PyBlitzArrayObject* image1 = 0;
  PyBlitzArrayObject* image2 = 0;
  PyBlitzArrayObject* u = 0;
  PyBlitzArrayObject* v = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&O&O&O&", kwlist,
        &alpha, &iterations,
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
    PyErr_Format(PyExc_TypeError, "function only supports 2D 64-bit float arrays for input array `image1' - you passed a %" PY_FORMAT_SIZE_T "d array of type `%s'", image1->ndim, PyBlitzArray_TypenumAsString(image1->type_num));
    return 0;
  }

  if (image2->type_num != NPY_FLOAT64 || image2->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "function only supports 2D 64-bit float arrays for input array `image2' - you passed a %" PY_FORMAT_SIZE_T "d array of type `%s'", image2->ndim, PyBlitzArray_TypenumAsString(image2->type_num));
    return 0;
  }

  if (u->type_num != NPY_FLOAT64 || u->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "function only supports 2D 64-bit float arrays for input array `u' - you passed a %" PY_FORMAT_SIZE_T "d array of type `%s'", u->ndim, PyBlitzArray_TypenumAsString(u->type_num));
    return 0;
  }

  if (v->type_num != NPY_FLOAT64 || v->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "function only supports 2D 64-bit float arrays for input array `v' - you passed a %" PY_FORMAT_SIZE_T "d array of type `%s'", v->ndim, PyBlitzArray_TypenumAsString(v->type_num));
    return 0;
  }

  //check all input image dimensions are consistent
  Py_ssize_t height = image1->shape[0];
  Py_ssize_t width  = image1->shape[1];

  if (image2->shape[0] != height || image2->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "input array `image1' has shape = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) which differs from that of `image2' = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", height, width, image2->shape[0], image2->shape[1]);
    return 0;
  }

  if (u->shape[0] != height || u->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "input arrays `image1' and `image2' have shape = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) which differs from that of `u' = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", height, width, u->shape[0], u->shape[1]);
    return 0;
  }

  if (v->shape[0] != height || v->shape[1] != width) {
    PyErr_Format(PyExc_RuntimeError, "input arrays `image1', `image2' and `u' have shape = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d) which differs from that of `v' = (%" PY_FORMAT_SIZE_T "d, %" PY_FORMAT_SIZE_T "d)", height, width, v->shape[0], v->shape[1]);
    return 0;
  }

  //allocates the error return
  auto error = (PyBlitzArrayObject*)PyBlitzArray_SimpleNew(NPY_FLOAT64,
      image1->ndim, image1->shape);
  auto error_ = make_safe(error);

  /** all basic checks are done, can call the functor now **/
  try {
    bob::ip::optflow::flowError(
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
    PyErr_SetString(PyExc_RuntimeError, "cannot estimate flow error: unknown exception caught");
    return 0;
  }

  Py_INCREF(error);
  return PyBlitzArray_NUMPY_WRAP(reinterpret_cast<PyObject*>(error));

}

static PyMethodDef module_methods[] = {
  {
    s_laplacian_avg_hs.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_LaplacianAverage,
    METH_VARARGS|METH_KEYWORDS,
    s_laplacian_avg_hs.doc()
  },
  {
    s_laplacian_avg_hs_opencv.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_LaplacianAverageOpenCV,
    METH_VARARGS|METH_KEYWORDS,
    s_laplacian_avg_hs_opencv.doc()
  },
  {
    s_flow_error.name(),
    (PyCFunction)PyBobIpOptflowHornAndSchunck_FlowError,
    METH_VARARGS|METH_KEYWORDS,
    s_flow_error.doc()
  },
  {0}  /* Sentinel */
};

PyDoc_STRVAR(module_docstr, "Optical flow framework of Horn & Schunck");

#if PY_VERSION_HEX >= 0x03000000
static PyModuleDef module_definition = {
  PyModuleDef_HEAD_INIT,
  BOB_EXT_MODULE_NAME,
  module_docstr,
  -1,
  module_methods,
  0, 0, 0, 0
};
#endif

static PyObject* create_module (void) {

  PyBobIpOptflowHornAndSchunck_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIpOptflowHornAndSchunck_Type) < 0) return 0;

  PyBobIpOptflowVanillaHornAndSchunck_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIpOptflowVanillaHornAndSchunck_Type) < 0) return 0;

  PyBobIpOptflowForwardGradient_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIpOptflowForwardGradient_Type) < 0) return 0;

  PyBobIpOptflowHornAndSchunckGradient_Type.tp_base =
    &PyBobIpOptflowForwardGradient_Type;
  if (PyType_Ready(&PyBobIpOptflowHornAndSchunckGradient_Type) < 0) return 0;

  PyBobIpOptflowCentralGradient_Type.tp_new = PyType_GenericNew;
  if (PyType_Ready(&PyBobIpOptflowCentralGradient_Type) < 0) return 0;

  PyBobIpOptflowSobelGradient_Type.tp_base = &PyBobIpOptflowCentralGradient_Type;
  if (PyType_Ready(&PyBobIpOptflowSobelGradient_Type) < 0) return 0;

  PyBobIpOptflowPrewittGradient_Type.tp_base = &PyBobIpOptflowCentralGradient_Type;
  if (PyType_Ready(&PyBobIpOptflowPrewittGradient_Type) < 0) return 0;

  PyBobIpOptflowIsotropicGradient_Type.tp_base =
    &PyBobIpOptflowCentralGradient_Type;
  if (PyType_Ready(&PyBobIpOptflowIsotropicGradient_Type) < 0) return 0;

# if PY_VERSION_HEX >= 0x03000000
  PyObject* m = PyModule_Create(&module_definition);
# else
  PyObject* m = Py_InitModule3(BOB_EXT_MODULE_NAME, module_methods, module_docstr);
# endif
  if (!m) return 0;
  auto m_ = make_safe(m); ///< protects against early returns

  if (PyModule_AddStringConstant(m, "__version__", BOB_EXT_MODULE_VERSION) < 0)
    return 0;

  /* register the types to python */
  Py_INCREF(&PyBobIpOptflowHornAndSchunck_Type);
  if (PyModule_AddObject(m, "Flow",
        (PyObject *)&PyBobIpOptflowHornAndSchunck_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowVanillaHornAndSchunck_Type);
  if (PyModule_AddObject(m, "VanillaFlow",
        (PyObject *)&PyBobIpOptflowVanillaHornAndSchunck_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowForwardGradient_Type);
  if (PyModule_AddObject(m, "ForwardGradient",
        (PyObject *)&PyBobIpOptflowForwardGradient_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowHornAndSchunckGradient_Type);
  if (PyModule_AddObject(m, "HornAndSchunckGradient",
        (PyObject *)&PyBobIpOptflowHornAndSchunckGradient_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowCentralGradient_Type);
  if (PyModule_AddObject(m, "CentralGradient",
        (PyObject *)&PyBobIpOptflowCentralGradient_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowSobelGradient_Type);
  if (PyModule_AddObject(m, "SobelGradient",
        (PyObject *)&PyBobIpOptflowSobelGradient_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowPrewittGradient_Type);
  if (PyModule_AddObject(m, "PrewittGradient",
        (PyObject *)&PyBobIpOptflowPrewittGradient_Type) < 0) return 0;

  Py_INCREF(&PyBobIpOptflowIsotropicGradient_Type);
  if (PyModule_AddObject(m, "IsotropicGradient",
        (PyObject *)&PyBobIpOptflowIsotropicGradient_Type) < 0) return 0;

  /* imports dependencies */
  if (import_bob_blitz() < 0) {
    PyErr_Print();
    PyErr_Format(PyExc_ImportError, "cannot import `%s'", BOB_EXT_MODULE_NAME);
    return 0;
  }

  Py_INCREF(m);
  return m;

}

PyMODINIT_FUNC BOB_EXT_ENTRY_NAME (void) {
# if PY_VERSION_HEX >= 0x03000000
  return
# endif
    create_module();
}
