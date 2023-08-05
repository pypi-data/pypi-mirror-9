/**
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 * @date Tue Oct 11 12:32:10 2011 +0200
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */
#include "ndarray.h"

#include <bob.learn.linear/pca.h>
#include <bob.learn.misc/EMPCATrainer.h>

using namespace boost::python;

typedef bob::learn::misc::EMTrainer<bob::learn::linear::Machine, blitz::Array<double,2> > EMTrainerLinearBase;

static void py_train(EMTrainerLinearBase& trainer,
  bob::learn::linear::Machine& machine, bob::python::const_ndarray data)
{
  trainer.train(machine, data.bz<double,2>());
}

static void py_initialize(EMTrainerLinearBase& trainer,
  bob::learn::linear::Machine& machine, bob::python::const_ndarray data)
{
  trainer.initialize(machine, data.bz<double,2>());
}

static void py_finalize(EMTrainerLinearBase& trainer,
  bob::learn::linear::Machine& machine, bob::python::const_ndarray data)
{
  trainer.finalize(machine, data.bz<double,2>());
}

static void py_eStep(EMTrainerLinearBase& trainer,
  bob::learn::linear::Machine& machine, bob::python::const_ndarray data)
{
  trainer.eStep(machine, data.bz<double,2>());
}

static void py_mStep(EMTrainerLinearBase& trainer,
  bob::learn::linear::Machine& machine, bob::python::const_ndarray data)
{
  trainer.mStep(machine, data.bz<double,2>());
}

void bind_trainer_empca()
{

  class_<EMTrainerLinearBase, boost::noncopyable>("EMTrainerLinear", "The base python class for all EM-based trainers.", no_init)
    .add_property("convergence_threshold", &EMTrainerLinearBase::getConvergenceThreshold, &EMTrainerLinearBase::setConvergenceThreshold, "Convergence threshold")
    .add_property("max_iterations", &EMTrainerLinearBase::getMaxIterations, &EMTrainerLinearBase::setMaxIterations, "Max iterations")
    .add_property("compute_likelihood_variable", &EMTrainerLinearBase::getComputeLikelihood, &EMTrainerLinearBase::setComputeLikelihood, "Indicates whether the log likelihood should be computed during EM or not")
    .add_property("rng", &EMTrainerLinearBase::getRng, &EMTrainerLinearBase::setRng, "The Mersenne Twister mt19937 random generator used for the initialization of subspaces/arrays before the EM loop.")
    .def("train", &py_train, (arg("self"), arg("machine"), arg("data")), "Trains a machine using data")
    .def("initialize", &py_initialize, (arg("self"), arg("machine"), arg("data")), "This method is called before the EM algorithm")
    .def("finalize", &py_finalize, (arg("self"), arg("machine"), arg("data")), "This method is called at the end of the EM algorithm")
    .def("e_step", &py_eStep, (arg("self"), arg("machine"), arg("data")),
       "Updates the hidden variable distribution (or the sufficient statistics) given the Machine parameters. ")
    .def("m_step", &py_mStep, (arg("self"), arg("machine"), arg("data")), "Updates the Machine parameters given the hidden variable distribution (or the sufficient statistics)")
    .def("compute_likelihood", &EMTrainerLinearBase::computeLikelihood, (arg("self"), arg("machine")), "Computes the current log likelihood given the hidden variable distribution (or the sufficient statistics)")
  ;

  class_<bob::learn::misc::EMPCATrainer, boost::noncopyable, bases<EMTrainerLinearBase> >("EMPCATrainer",
      "This class implements the EM algorithm for a Linear Machine (Probabilistic PCA).\n"
      "See Section 12.2 of Bishop, \"Pattern recognition and machine learning\", 2006", init<optional<double,size_t,bool> >((arg("self"), arg("convergence_threshold"), arg("max_iterations"), arg("compute_likelihood"))))
    .def(init<const bob::learn::misc::EMPCATrainer&>((arg("self"), arg("trainer")), "Copy constructs an EMPCATrainer"))
    .def(self == self)
    .def(self != self)
    .def("is_similar_to", &bob::learn::misc::EMPCATrainer::is_similar_to, (arg("self"), arg("other"), arg("r_epsilon")=1e-5, arg("a_epsilon")=1e-8), "Compares this EMPCATrainer with the 'other' one to be approximately the same.")
    .add_property("sigma2", &bob::learn::misc::EMPCATrainer::getSigma2, &bob::learn::misc::EMPCATrainer::setSigma2, "The noise sigma2 of the probabilistic model")
  ;
}
