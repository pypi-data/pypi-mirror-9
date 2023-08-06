/**
 * @author Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
 * @date Tue 03 Fev 11:22:00 2015
 *
 * @brief Python API for bob::learn::em
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include "main.h"

/******************************************************************/
/************ Constructor Section *********************************/
/******************************************************************/

static auto EMPCATrainer_doc = bob::extension::ClassDoc(
  BOB_EXT_MODULE_PREFIX "._EMPCATrainer",
  ""

).add_constructor(
  bob::extension::FunctionDoc(
    "__init__",
    "Creates a EMPCATrainer",
    "",
    true
  )
  .add_prototype("convergence_threshold","")
  .add_prototype("other","")
  .add_prototype("","")

  .add_parameter("other", ":py:class:`bob.learn.em.EMPCATrainer`", "A EMPCATrainer object to be copied.")
  .add_parameter("convergence_threshold", "double", "")

);


static int PyBobLearnEMEMPCATrainer_init_copy(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {

  char** kwlist = EMPCATrainer_doc.kwlist(1);
  PyBobLearnEMEMPCATrainerObject* tt;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!", kwlist, &PyBobLearnEMEMPCATrainer_Type, &tt)){
    EMPCATrainer_doc.print_usage();
    return -1;
  }

  self->cxx.reset(new bob::learn::em::EMPCATrainer(*tt->cxx));
  return 0;
}

static int PyBobLearnEMEMPCATrainer_init_number(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {

  char** kwlist = EMPCATrainer_doc.kwlist(0);
  double convergence_threshold    = 0.0001;
  //Parsing the input argments
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "d", kwlist, &convergence_threshold))
    return -1;

  if(convergence_threshold < 0){
    PyErr_Format(PyExc_TypeError, "convergence_threshold argument must be greater than to zero");
    return -1;
  }

  self->cxx.reset(new bob::learn::em::EMPCATrainer(convergence_threshold));
  return 0;
}

static int PyBobLearnEMEMPCATrainer_init(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {
  BOB_TRY

  int nargs = (args?PyTuple_Size(args):0) + (kwargs?PyDict_Size(kwargs):0);

  switch (nargs) {

    case 0:{ //default initializer ()
      self->cxx.reset(new bob::learn::em::EMPCATrainer());
      return 0;
    }
    case 1:{
      //Reading the input argument
      PyObject* arg = 0;
      if (PyTuple_Size(args))
        arg = PyTuple_GET_ITEM(args, 0);
      else {
        PyObject* tmp = PyDict_Values(kwargs);
        auto tmp_ = make_safe(tmp);
        arg = PyList_GET_ITEM(tmp, 0);
      }

      // If the constructor input is EMPCATrainer object
      if (PyBobLearnEMEMPCATrainer_Check(arg))
        return PyBobLearnEMEMPCATrainer_init_copy(self, args, kwargs);
      else if(PyString_Check(arg))
        return PyBobLearnEMEMPCATrainer_init_number(self, args, kwargs);
    }
    default:{
      PyErr_Format(PyExc_RuntimeError, "number of arguments mismatch - %s requires 0 or 1 arguments, but you provided %d (see help)", Py_TYPE(self)->tp_name, nargs);
      EMPCATrainer_doc.print_usage();
      return -1;
    }
  }
  BOB_CATCH_MEMBER("cannot create EMPCATrainer", 0)
  return 0;
}


static void PyBobLearnEMEMPCATrainer_delete(PyBobLearnEMEMPCATrainerObject* self) {
  self->cxx.reset();
  Py_TYPE(self)->tp_free((PyObject*)self);
}


int PyBobLearnEMEMPCATrainer_Check(PyObject* o) {
  return PyObject_IsInstance(o, reinterpret_cast<PyObject*>(&PyBobLearnEMEMPCATrainer_Type));
}


static PyObject* PyBobLearnEMEMPCATrainer_RichCompare(PyBobLearnEMEMPCATrainerObject* self, PyObject* other, int op) {
  BOB_TRY

  if (!PyBobLearnEMEMPCATrainer_Check(other)) {
    PyErr_Format(PyExc_TypeError, "cannot compare `%s' with `%s'", Py_TYPE(self)->tp_name, Py_TYPE(other)->tp_name);
    return 0;
  }
  auto other_ = reinterpret_cast<PyBobLearnEMEMPCATrainerObject*>(other);
  switch (op) {
    case Py_EQ:
      if (*self->cxx==*other_->cxx) Py_RETURN_TRUE; else Py_RETURN_FALSE;
    case Py_NE:
      if (*self->cxx==*other_->cxx) Py_RETURN_FALSE; else Py_RETURN_TRUE;
    default:
      Py_INCREF(Py_NotImplemented);
      return Py_NotImplemented;
  }
  BOB_CATCH_MEMBER("cannot compare EMPCATrainer objects", 0)
}


/******************************************************************/
/************ Variables Section ***********************************/
/******************************************************************/

static PyGetSetDef PyBobLearnEMEMPCATrainer_getseters[] = { 
  {0}  // Sentinel
};


/******************************************************************/
/************ Functions Section ***********************************/
/******************************************************************/

/*** initialize ***/
static auto initialize = bob::extension::FunctionDoc(
  "initialize",
  "",
  "",
  true
)
.add_prototype("linear_machine,data")
.add_parameter("linear_machine", ":py:class:`bob.learn.linear.Machine`", "LinearMachine Object")
.add_parameter("data", "array_like <float, 2D>", "Input data")
.add_parameter("rng", ":py:class:`bob.core.random.mt19937`", "The Mersenne Twister mt19937 random generator used for the initialization of subspaces/arrays before the EM loop.");
static PyObject* PyBobLearnEMEMPCATrainer_initialize(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {
  BOB_TRY

  /* Parses input arguments in a single shot */
  char** kwlist = initialize.kwlist(0);

  PyBobLearnLinearMachineObject* linear_machine = 0;
  PyBlitzArrayObject* data                      = 0;
  PyBoostMt19937Object* rng = 0;

  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!O&|O!", kwlist, &PyBobLearnLinearMachine_Type, &linear_machine,
                                                                 &PyBlitzArray_Converter, &data,
                                                                 &PyBoostMt19937_Type, &rng)) return 0;
  auto data_ = make_safe(data);
  
  if(rng){
    boost::shared_ptr<boost::mt19937> rng_cpy = (boost::shared_ptr<boost::mt19937>)new boost::mt19937(*rng->rng);
    self->cxx->setRng(rng_cpy);
  }
  

  self->cxx->initialize(*linear_machine->cxx, *PyBlitzArrayCxx_AsBlitz<double,2>(data));

  BOB_CATCH_MEMBER("cannot perform the initialize method", 0)

  Py_RETURN_NONE;
}


/*** eStep ***/
static auto eStep = bob::extension::FunctionDoc(
  "eStep",
  "",
  "",
  true
)
.add_prototype("linear_machine,data")
.add_parameter("linear_machine", ":py:class:`bob.learn.linear.Machine`", "LinearMachine Object")
.add_parameter("data", "array_like <float, 2D>", "Input data");
static PyObject* PyBobLearnEMEMPCATrainer_eStep(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {
  BOB_TRY

  /* Parses input arguments in a single shot */
  char** kwlist = eStep.kwlist(0);

  PyBobLearnLinearMachineObject* linear_machine;
  PyBlitzArrayObject* data = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!O&", kwlist, &PyBobLearnLinearMachine_Type, &linear_machine,
                                                                 &PyBlitzArray_Converter, &data)) return 0;
  auto data_ = make_safe(data);

  self->cxx->eStep(*linear_machine->cxx, *PyBlitzArrayCxx_AsBlitz<double,2>(data));


  BOB_CATCH_MEMBER("cannot perform the eStep method", 0)

  Py_RETURN_NONE;
}


/*** mStep ***/
static auto mStep = bob::extension::FunctionDoc(
  "mStep",
  "",
  0,
  true
)
.add_prototype("linear_machine,data")
.add_parameter("linear_machine", ":py:class:`bob.learn.em.LinearMachine`", "LinearMachine Object")
.add_parameter("data", "array_like <float, 2D>", "Input data");
static PyObject* PyBobLearnEMEMPCATrainer_mStep(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {
  BOB_TRY

  /* Parses input arguments in a single shot */
  char** kwlist = mStep.kwlist(0);

  PyBobLearnLinearMachineObject* linear_machine;
  PyBlitzArrayObject* data = 0;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!O&", kwlist, &PyBobLearnLinearMachine_Type, &linear_machine,
                                                                 &PyBlitzArray_Converter, &data)) return 0;
  auto data_ = make_safe(data);

  self->cxx->mStep(*linear_machine->cxx, *PyBlitzArrayCxx_AsBlitz<double,2>(data));


  BOB_CATCH_MEMBER("cannot perform the mStep method", 0)

  Py_RETURN_NONE;
}


/*** computeLikelihood ***/
static auto compute_likelihood = bob::extension::FunctionDoc(
  "compute_likelihood",
  "",
  0,
  true
)
.add_prototype("linear_machine,data")
.add_parameter("linear_machine", ":py:class:`bob.learn.em.LinearMachine`", "LinearMachine Object");
static PyObject* PyBobLearnEMEMPCATrainer_compute_likelihood(PyBobLearnEMEMPCATrainerObject* self, PyObject* args, PyObject* kwargs) {
  BOB_TRY

  /* Parses input arguments in a single shot */
  char** kwlist = compute_likelihood.kwlist(0);

  PyBobLearnLinearMachineObject* linear_machine;
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!", kwlist, &PyBobLearnLinearMachine_Type, &linear_machine)) return 0;

  double value = self->cxx->computeLikelihood(*linear_machine->cxx);
  return Py_BuildValue("d", value);

  BOB_CATCH_MEMBER("cannot perform the computeLikelihood method", 0)
}



static PyMethodDef PyBobLearnEMEMPCATrainer_methods[] = {
  {
    initialize.name(),
    (PyCFunction)PyBobLearnEMEMPCATrainer_initialize,
    METH_VARARGS|METH_KEYWORDS,
    initialize.doc()
  },
  {
    eStep.name(),
    (PyCFunction)PyBobLearnEMEMPCATrainer_eStep,
    METH_VARARGS|METH_KEYWORDS,
    eStep.doc()
  },
  {
    mStep.name(),
    (PyCFunction)PyBobLearnEMEMPCATrainer_mStep,
    METH_VARARGS|METH_KEYWORDS,
    mStep.doc()
  },
  {
    compute_likelihood.name(),
    (PyCFunction)PyBobLearnEMEMPCATrainer_compute_likelihood,
    METH_VARARGS|METH_KEYWORDS,
    compute_likelihood.doc()
  },
  {0} /* Sentinel */
};


/******************************************************************/
/************ Module Section **************************************/
/******************************************************************/

// Define the Gaussian type struct; will be initialized later
PyTypeObject PyBobLearnEMEMPCATrainer_Type = {
  PyVarObject_HEAD_INIT(0,0)
  0
};

bool init_BobLearnEMEMPCATrainer(PyObject* module)
{
  // initialize the type struct
  PyBobLearnEMEMPCATrainer_Type.tp_name = EMPCATrainer_doc.name();
  PyBobLearnEMEMPCATrainer_Type.tp_basicsize = sizeof(PyBobLearnEMEMPCATrainerObject);
  PyBobLearnEMEMPCATrainer_Type.tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE;//Enable the class inheritance
  PyBobLearnEMEMPCATrainer_Type.tp_doc = EMPCATrainer_doc.doc();

  // set the functions
  PyBobLearnEMEMPCATrainer_Type.tp_new = PyType_GenericNew;
  PyBobLearnEMEMPCATrainer_Type.tp_init = reinterpret_cast<initproc>(PyBobLearnEMEMPCATrainer_init);
  PyBobLearnEMEMPCATrainer_Type.tp_dealloc = reinterpret_cast<destructor>(PyBobLearnEMEMPCATrainer_delete);
  PyBobLearnEMEMPCATrainer_Type.tp_richcompare = reinterpret_cast<richcmpfunc>(PyBobLearnEMEMPCATrainer_RichCompare);
  PyBobLearnEMEMPCATrainer_Type.tp_methods = PyBobLearnEMEMPCATrainer_methods;
  PyBobLearnEMEMPCATrainer_Type.tp_getset = PyBobLearnEMEMPCATrainer_getseters;
  PyBobLearnEMEMPCATrainer_Type.tp_call = reinterpret_cast<ternaryfunc>(PyBobLearnEMEMPCATrainer_compute_likelihood);


  // check that everything is fine
  if (PyType_Ready(&PyBobLearnEMEMPCATrainer_Type) < 0) return false;

  // add the type to the module
  Py_INCREF(&PyBobLearnEMEMPCATrainer_Type);
  return PyModule_AddObject(module, "_EMPCATrainer", (PyObject*)&PyBobLearnEMEMPCATrainer_Type) >= 0;
}

