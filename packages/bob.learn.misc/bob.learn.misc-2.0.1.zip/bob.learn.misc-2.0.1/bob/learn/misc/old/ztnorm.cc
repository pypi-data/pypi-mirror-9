/**
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 * @date Tue Jul 19 15:33:20 2011 +0200
 *
 * @brief Binds ZT-normalization to python
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include "ndarray.h"

#include <bob.learn.misc/ZTNorm.h>

using namespace boost::python;

static object ztnorm1(
  bob::python::const_ndarray rawscores_probes_vs_models,
  bob::python::const_ndarray rawscores_zprobes_vs_models,
  bob::python::const_ndarray rawscores_probes_vs_tmodels,
  bob::python::const_ndarray rawscores_zprobes_vs_tmodels,
  bob::python::const_ndarray mask_zprobes_vs_tmodels_istruetrial)
{
  const blitz::Array<double,2> rawscores_probes_vs_models_ =
    rawscores_probes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_zprobes_vs_models_ =
    rawscores_zprobes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_probes_vs_tmodels_ =
    rawscores_probes_vs_tmodels.bz<double,2>();
  const blitz::Array<double,2> rawscores_zprobes_vs_tmodels_ =
    rawscores_zprobes_vs_tmodels.bz<double,2>();
  const blitz::Array<bool,2> mask_zprobes_vs_tmodels_istruetrial_ =
    mask_zprobes_vs_tmodels_istruetrial.bz<bool,2>();

  // allocate output
  bob::python::ndarray ret(bob::io::base::array::t_float64, rawscores_probes_vs_models_.extent(0), rawscores_probes_vs_models_.extent(1));
  blitz::Array<double, 2> ret_ = ret.bz<double,2>();

  bob::learn::misc::ztNorm(rawscores_probes_vs_models_,
                       rawscores_zprobes_vs_models_,
                       rawscores_probes_vs_tmodels_,
                       rawscores_zprobes_vs_tmodels_,
                       mask_zprobes_vs_tmodels_istruetrial_,
                       ret_);

  return ret.self();
}

static object ztnorm2(
  bob::python::const_ndarray rawscores_probes_vs_models,
  bob::python::const_ndarray rawscores_zprobes_vs_models,
  bob::python::const_ndarray rawscores_probes_vs_tmodels,
  bob::python::const_ndarray rawscores_zprobes_vs_tmodels)
{
  const blitz::Array<double,2> rawscores_probes_vs_models_ =
    rawscores_probes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_zprobes_vs_models_ =
    rawscores_zprobes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_probes_vs_tmodels_ =
    rawscores_probes_vs_tmodels.bz<double,2>();
  const blitz::Array<double,2> rawscores_zprobes_vs_tmodels_ =
    rawscores_zprobes_vs_tmodels.bz<double,2>();

  // allocate output
  bob::python::ndarray ret(bob::io::base::array::t_float64, rawscores_probes_vs_models_.extent(0), rawscores_probes_vs_models_.extent(1));
  blitz::Array<double, 2> ret_ = ret.bz<double,2>();

  bob::learn::misc::ztNorm(rawscores_probes_vs_models_,
                       rawscores_zprobes_vs_models_,
                       rawscores_probes_vs_tmodels_,
                       rawscores_zprobes_vs_tmodels_,
                       ret_);

  return ret.self();
}

static object tnorm(
  bob::python::const_ndarray rawscores_probes_vs_models,
  bob::python::const_ndarray rawscores_probes_vs_tmodels)
{
  const blitz::Array<double,2> rawscores_probes_vs_models_ =
    rawscores_probes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_probes_vs_tmodels_ =
    rawscores_probes_vs_tmodels.bz<double,2>();

  // allocate output
  bob::python::ndarray ret(bob::io::base::array::t_float64, rawscores_probes_vs_models_.extent(0), rawscores_probes_vs_models_.extent(1));
  blitz::Array<double, 2> ret_ = ret.bz<double,2>();

  bob::learn::misc::tNorm(rawscores_probes_vs_models_,
                       rawscores_probes_vs_tmodels_,
                       ret_);

  return ret.self();
}

static object znorm(
  bob::python::const_ndarray rawscores_probes_vs_models,
  bob::python::const_ndarray rawscores_zprobes_vs_models)
{
  const blitz::Array<double,2> rawscores_probes_vs_models_ =
    rawscores_probes_vs_models.bz<double,2>();
  const blitz::Array<double,2> rawscores_zprobes_vs_models_ =
    rawscores_zprobes_vs_models.bz<double,2>();

  // allocate output
  bob::python::ndarray ret(bob::io::base::array::t_float64, rawscores_probes_vs_models_.extent(0), rawscores_probes_vs_models_.extent(1));
  blitz::Array<double, 2> ret_ = ret.bz<double,2>();

  bob::learn::misc::zNorm(rawscores_probes_vs_models_,
                       rawscores_zprobes_vs_models_,
                       ret_);

  return ret.self();
}

void bind_machine_ztnorm()
{
  def("ztnorm",
      ztnorm1,
      args("rawscores_probes_vs_models",
           "rawscores_zprobes_vs_models",
           "rawscores_probes_vs_tmodels",
           "rawscores_zprobes_vs_tmodels",
           "mask_zprobes_vs_tmodels_istruetrial"),
      "Normalise raw scores with ZT-Norm"
     );

  def("ztnorm",
      ztnorm2,
      args("rawscores_probes_vs_models",
           "rawscores_zprobes_vs_models",
           "rawscores_probes_vs_tmodels",
           "rawscores_zprobes_vs_tmodels"),
      "Normalise raw scores with ZT-Norm. Assume that znorm and tnorm have no common subject id."
     );

  def("tnorm",
      tnorm,
      args("rawscores_probes_vs_models",
           "rawscores_probes_vs_tmodels"),
      "Normalise raw scores with T-Norm."
     );

  def("znorm",
      znorm,
      args("rawscores_probes_vs_models",
           "rawscores_zprobes_vs_models"),
      "Normalise raw scores with Z-Norm."
     );

}
