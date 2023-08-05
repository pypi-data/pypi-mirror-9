/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Thu 20 Sep 2012 14:46:35 CEST
 *
 * @brief Bob/Python extension to flandmark
 */

#include <bob.blitz/cppapi.h>
#include <bob.blitz/cleanup.h>
#include <bob.io.base/api.h>
#include <structmember.h>

#include <bob.extension/documentation.h>

#include <boost/shared_ptr.hpp>
#include <boost/shared_array.hpp>

#include <cstring>

#include "flandmark_detector.h"

/******************************************
 * Implementation of Localizer base class *
 ******************************************/

#define CLASS_NAME "Flandmark"

static auto s_class = bob::extension::ClassDoc(
    BOB_EXT_MODULE_PREFIX "." CLASS_NAME,

    "A key-point localization for faces using Flandmark",

    "This class can be used to locate facial landmarks on pre-detected faces. "
    "You input an image and a bounding-box specification and it returns you the "
    "positions for multiple key-points for the given face image.\n"
    "\n"
    "Consult http://cmp.felk.cvut.cz/~uricamic/flandmark/index.php for more "
    "information.\n"
    "\n"
    )
    .add_constructor(
        bob::extension::FunctionDoc(
          CLASS_NAME,
          "Constructor",
          "Initializes the key-point locator with a model."
          )
        .add_prototype("[model]", "")
        .add_parameter("model", "str (path), optional", "Path to the localization model. If not set (or set to ``None``), then use the default localization model, stored on the class variable ``__default_model__``)")
        )
    ;

typedef struct {
  PyObject_HEAD
  FLANDMARK_Model* flandmark;
  char* filename;
} PyBobIpFlandmarkObject;

static int PyBobIpFlandmark_init
(PyBobIpFlandmarkObject* self, PyObject* args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"model", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyObject* model = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O&", kwlist,
        &PyBobIo_FilenameConverter, &model)) return -1;

  if (!model) { //use what is stored in __default_model__
    PyObject* default_model = PyObject_GetAttrString((PyObject*)self,
        "__default_model__");
    if (!default_model) {
      PyErr_Format(PyExc_RuntimeError, "`%s' needs a model to properly initialize, but the user has not passed one and `__default_model__' is not properly set", Py_TYPE(self)->tp_name);
      return -1;
    }

    auto ok = PyBobIo_FilenameConverter(default_model, &model);
    Py_DECREF(default_model);

    if (!ok || !model) return -1;
  }

  const char* c_filename = 0;

# if PY_VERSION_HEX >= 0x03000000
  c_filename = PyBytes_AS_STRING(model);
# else
  c_filename = PyString_AS_STRING(model);
# endif
  Py_DECREF(model);

  //now we have a filename we can use
  if (!c_filename) return -1;

  self->flandmark = flandmark_init(c_filename);
  if (!self->flandmark) {
    PyErr_Format(PyExc_RuntimeError, "`%s' could not initialize from model file `%s'", Py_TYPE(self)->tp_name, c_filename);
    return -1;
  }

  //flandmark is now initialized, set filename
  self->filename = strndup(c_filename, 256);

  //all good, flandmark is ready
  return 0;

}

static void PyBobIpFlandmark_delete (PyBobIpFlandmarkObject* self) {
  flandmark_free(self->flandmark);
  self->flandmark = 0;
  free(self->filename);
  self->filename = 0;
  Py_TYPE(self)->tp_free((PyObject*)self);
}

static void delete_image(IplImage* i) {
  cvReleaseImage(&i);
}

/**
 * Returns a list of key-point annotations given an image and an iterable over
 * bounding boxes.
 */
static PyObject* call(PyBobIpFlandmarkObject* self,
    boost::shared_ptr<IplImage> image, int nbbx, boost::shared_array<int> bbx) {

  PyObject* retval = PyTuple_New(nbbx);
  if (!retval) return 0;
  auto retval_ = make_safe(retval);

  for (int i=0; i<nbbx; ++i) {

    //allocate output array _and_ Flandmark buffer within a single structure
    Py_ssize_t shape[2];
    shape[0] = self->flandmark->data.options.M;
    shape[1] = 2;
    PyObject* landmarks = PyArray_SimpleNew(2, shape, NPY_FLOAT64);
    if (!landmarks) return 0;
    auto landmarks_ = make_safe(landmarks);
    double* buffer = reinterpret_cast<double*>(PyArray_DATA((PyArrayObject*)landmarks));

    int result = 0;
    Py_BEGIN_ALLOW_THREADS
    result = flandmark_detect(image.get(), &bbx[4*i], self->flandmark, buffer);
    Py_END_ALLOW_THREADS

    if (result != NO_ERR) {
      Py_INCREF(Py_None);
      landmarks = Py_None;
    }
    else {
      //swap keypoint coordinates (x, y) -> (y, x)
      double tmp;
      for (int k = 0; k < (2*self->flandmark->data.options.M); k += 2) {
        tmp         = buffer[k];
        buffer[k]   = buffer[k+1];
        buffer[k+1] = tmp;
      }
      Py_INCREF(landmarks);
    }

    PyTuple_SET_ITEM(retval, i, landmarks);

  }

  Py_INCREF(retval);
  return retval;

}

static auto s_call = bob::extension::FunctionDoc(
    "locate",
    "Locates keypoints on a **single** facial bounding-box on the provided image."
    "This method will locate 8 keypoints inside the bounding-box defined "
    "for the current input image, organized in this way:\n"
    "\n"
    "0. Face center\n"
    "1. Canthus-rl (inner corner of the right eye).\n"
    "\n"
    "   .. note::\n"
    "      \n"
    "      The \"right eye\" means the right eye at the face w.r.t. the person "
    "on the image. That is the left eye in the image, from the viewer's "
    "perspective.\n"
    "\n"
    "2. Canthus-lr (inner corner of the left eye)\n"
    "3. Mouth-corner-r (right corner of the mouth)\n"
    "4. Mouth-corner-l (left corner of the mouth)\n"
    "5. Canthus-rr (outer corner of the right eye)\n"
    "6. Canthus-ll (outer corner of the left eye)\n"
    "7. Nose\n"
    "\n"
    "Each point is returned as tuple defining the pixel positions in the form "
    "(y, x).\n"
    "\n"
    )
    .add_prototype("image, y, x, height, width", "landmarks")
    .add_parameter("image", "array-like (2D, uint8)",
      "The image Flandmark will operate on")
    .add_parameter("y, x", "int", "The top left-most corner of the bounding box containing the face image you want to locate keypoints on.")
    .add_parameter("height, width", "int", "The dimensions accross ``y`` (height) and ``x`` (width) for the bounding box, in number of pixels.")
    .add_return("landmarks", "array (2D, float64)", "Each row in the output array contains the locations of keypoints in the format ``(y, x)``")
    ;

static PyObject* PyBobIpFlandmark_call_single(PyBobIpFlandmarkObject* self,
    PyObject *args, PyObject* kwds) {

  /* Parses input arguments in a single shot */
  static const char* const_kwlist[] = {"image", "y", "x", "height", "width", 0};
  static char** kwlist = const_cast<char**>(const_kwlist);

  PyBlitzArrayObject* image = 0;
  int y = 0;
  int x = 0;
  int height = 0;
  int width = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwds, "O&iiii", kwlist,
        &PyBlitzArray_Converter, &image, &y, &x, &height, &width)) return 0;

  auto image_ = make_safe(image);

  //check
  if (image->type_num != NPY_UINT8 || image->ndim != 2) {
    PyErr_Format(PyExc_TypeError, "`%s' input `image' data must be a 2D array with dtype `uint8' (i.e. a gray-scaled image), but you passed a %" PY_FORMAT_SIZE_T "d array with data type `%s'", Py_TYPE(self)->tp_name, image->ndim, PyBlitzArray_TypenumAsString(image->type_num));
    return 0;
  }

  // converts to OpenCV's IplImage
  boost::shared_ptr<IplImage> cv_image(cvCreateImage(cvSize(image->shape[1], image->shape[0]), IPL_DEPTH_8U, 1), std::ptr_fun(delete_image));

  // copy image data aligned (see http://chi3x10.wordpress.com/2008/05/07/be-aware-of-memory-alignment-of-iplimage-in-opencv)
  for (int yy = 0; yy < image->shape[0]; ++yy)
    std::copy(reinterpret_cast<char*>(image->data) + yy * image->shape[1], reinterpret_cast<char*>(image->data) + (yy+1) * image->shape[1], cv_image->imageData + yy * cv_image->widthStep);

  //prepares the bbx vector
  boost::shared_array<int> bbx(new int[4]);
  bbx[0] = x;
  bbx[1] = y;
  bbx[2] = x + width;
  bbx[3] = y + height;

  PyObject* retval = call(self, cv_image, 1, bbx);
  if (!retval) return 0;

  //gets the first entry, return it
  PyObject* retval0 = PyTuple_GET_ITEM(retval, 0);
  if (!retval0) return 0;

  Py_INCREF(retval0);
  Py_DECREF(retval);

  return retval0;

};

static PyMethodDef PyBobIpFlandmark_methods[] = {
  {
    s_call.name(),
    (PyCFunction)PyBobIpFlandmark_call_single,
    METH_VARARGS|METH_KEYWORDS,
    s_call.doc()
  },
  {0} /* Sentinel */
};

PyObject* PyBobIpFlandmark_Repr(PyBobIpFlandmarkObject* self) {

  /**
   * Expected output:
   *
   * <bob.ip.flandmark(model='...')>
   */

  PyObject* retval = PyUnicode_FromFormat("<%s(model='%s')>",
      Py_TYPE(self)->tp_name, self->filename);

#if PYTHON_VERSION_HEX < 0x03000000
  if (!retval) return 0;
  PyObject* tmp = PyObject_Str(retval);
  Py_DECREF(retval);
  retval = tmp;
#endif

  return retval;

}

PyTypeObject PyBobIpFlandmark_Type = {
    PyVarObject_HEAD_INIT(0, 0)
    s_class.name(),                            /* tp_name */
    sizeof(PyBobIpFlandmarkObject),            /* tp_basicsize */
    0,                                         /* tp_itemsize */
    (destructor)PyBobIpFlandmark_delete,       /* tp_dealloc */
    0,                                         /* tp_print */
    0,                                         /* tp_getattr */
    0,                                         /* tp_setattr */
    0,                                         /* tp_compare */
    (reprfunc)PyBobIpFlandmark_Repr,           /* tp_repr */
    0,                                         /* tp_as_number */
    0,                                         /* tp_as_sequence */
    0,                                         /* tp_as_mapping */
    0,                                         /* tp_hash */
    (ternaryfunc)PyBobIpFlandmark_call_single, /* tp_call */
    (reprfunc)PyBobIpFlandmark_Repr,           /* tp_str */
    0,                                         /* tp_getattro */
    0,                                         /* tp_setattro */
    0,                                         /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,  /* tp_flags */
    s_class.doc(),                             /* tp_doc */
    0,                                         /* tp_traverse */
    0,                                         /* tp_clear */
    0,                                         /* tp_richcompare */
    0,                                         /* tp_weaklistoffset */
    0,                                         /* tp_iter */
    0,                                         /* tp_iternext */
    PyBobIpFlandmark_methods,                  /* tp_methods */
    0,                                         /* tp_members */
    0,                                         /* tp_getset */
    0,                                         /* tp_base */
    0,                                         /* tp_dict */
    0,                                         /* tp_descr_get */
    0,                                         /* tp_descr_set */
    0,                                         /* tp_dictoffset */
    (initproc)PyBobIpFlandmark_init,           /* tp_init */
};
