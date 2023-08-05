/**
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 * @date Wed Jul 13 16:00:04 2011 +0200
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include "ndarray.h"

#include <vector>
#include <bob.learn.misc/LinearScoring.h>
#include <boost/python/stl_iterator.hpp>

using namespace boost::python;

static void convertGMMMeanList(object models, std::vector<blitz::Array<double,1> >& models_c) {
  stl_input_iterator<bob::python::const_ndarray> dbegin(models), dend;
  std::vector<bob::python::const_ndarray> vmodels(dbegin, dend);

  for(std::vector<bob::python::const_ndarray>::iterator it=vmodels.begin();
      it!=vmodels.end(); ++it)
    models_c.push_back(it->bz<double,1>());
}

static void convertGMMStatsList(object test_stats, std::vector<boost::shared_ptr<const bob::learn::misc::GMMStats> >& test_stats_c) {
  stl_input_iterator<boost::shared_ptr<bob::learn::misc::GMMStats> > dbegin(test_stats), dend;
  test_stats_c.assign(dbegin, dend);
}

static void convertChannelOffsetList(object test_channelOffset, std::vector<blitz::Array<double,1> >& test_channelOffset_c) {
  stl_input_iterator<bob::python::const_ndarray> dbegin(test_channelOffset), dend;
  std::vector<bob::python::const_ndarray> vtest_channelOffset(dbegin, dend);

  for(std::vector<bob::python::const_ndarray>::iterator it=vtest_channelOffset.begin();
      it!=vtest_channelOffset.end(); ++it)
    test_channelOffset_c.push_back(it->bz<double,1>());
}

static void convertGMMMachineList(object models, std::vector<boost::shared_ptr<const bob::learn::misc::GMMMachine> >& models_c) {
  stl_input_iterator<boost::shared_ptr<bob::learn::misc::GMMMachine> > dbegin(models), dend;
  models_c.assign(dbegin, dend);
}

static object linearScoring1(object models,
    bob::python::const_ndarray ubm_mean, bob::python::const_ndarray ubm_variance,
    object test_stats, object test_channelOffset = list(), // Empty list
    bool frame_length_normalisation = false)
{
  blitz::Array<double,1> ubm_mean_ = ubm_mean.bz<double,1>();
  blitz::Array<double,1> ubm_variance_ = ubm_variance.bz<double,1>();

  std::vector<blitz::Array<double,1> > models_c;
  convertGMMMeanList(models, models_c);

  std::vector<boost::shared_ptr<const bob::learn::misc::GMMStats> > test_stats_c;
  convertGMMStatsList(test_stats, test_stats_c);

  bob::python::ndarray ret(bob::io::base::array::t_float64, models_c.size(), test_stats_c.size());
  blitz::Array<double,2> ret_ = ret.bz<double,2>();
  if (test_channelOffset.ptr() == Py_None || len(test_channelOffset) == 0) { //list is empty
    bob::learn::misc::linearScoring(models_c, ubm_mean_, ubm_variance_, test_stats_c, frame_length_normalisation, ret_);
  }
  else {
    std::vector<blitz::Array<double,1> > test_channelOffset_c;
    convertChannelOffsetList(test_channelOffset, test_channelOffset_c);
    bob::learn::misc::linearScoring(models_c, ubm_mean_, ubm_variance_, test_stats_c, test_channelOffset_c, frame_length_normalisation, ret_);
  }

  return ret.self();
}

static object linearScoring2(object models,
    bob::learn::misc::GMMMachine& ubm,
    object test_stats, object test_channelOffset = list(), // Empty list
    bool frame_length_normalisation = false)
{
  std::vector<boost::shared_ptr<const bob::learn::misc::GMMMachine> > models_c;
  convertGMMMachineList(models, models_c);

  std::vector<boost::shared_ptr<const bob::learn::misc::GMMStats> > test_stats_c;
  convertGMMStatsList(test_stats, test_stats_c);

  bob::python::ndarray ret(bob::io::base::array::t_float64, models_c.size(), test_stats_c.size());
  blitz::Array<double,2> ret_ = ret.bz<double,2>();
  if (test_channelOffset.ptr() == Py_None || len(test_channelOffset) == 0) { //list is empty
    bob::learn::misc::linearScoring(models_c, ubm, test_stats_c, frame_length_normalisation, ret_);
  }
  else {
    std::vector<blitz::Array<double,1> > test_channelOffset_c;
    convertChannelOffsetList(test_channelOffset, test_channelOffset_c);
    bob::learn::misc::linearScoring(models_c, ubm, test_stats_c, test_channelOffset_c, frame_length_normalisation, ret_);
  }

  return ret.self();
}

static double linearScoring3(bob::python::const_ndarray model,
  bob::python::const_ndarray ubm_mean, bob::python::const_ndarray ubm_var,
  const bob::learn::misc::GMMStats& test_stats, bob::python::const_ndarray test_channelOffset,
  const bool frame_length_normalisation = false)
{
  return bob::learn::misc::linearScoring(model.bz<double,1>(), ubm_mean.bz<double,1>(),
          ubm_var.bz<double,1>(), test_stats, test_channelOffset.bz<double,1>(), frame_length_normalisation);
}

BOOST_PYTHON_FUNCTION_OVERLOADS(linearScoring1_overloads, linearScoring1, 4, 6)
BOOST_PYTHON_FUNCTION_OVERLOADS(linearScoring2_overloads, linearScoring2, 3, 5)
BOOST_PYTHON_FUNCTION_OVERLOADS(linearScoring3_overloads, linearScoring3, 5, 6)

void bind_machine_linear_scoring() {
  def("linear_scoring", linearScoring1, linearScoring1_overloads(args("models", "ubm_mean", "ubm_variance", "test_stats", "test_channelOffset", "frame_length_normalisation"),
    "Compute a matrix of scores using linear scoring.\n"
    "Return a 2D matrix of scores, scores[m, s] is the score for model m against statistics s\n"
    "\n"
    "Warning Each GMM must have the same size.\n"
    "\n"
    "models       -- list of mean supervectors for the client models\n"
    "ubm_mean     -- mean supervector for the world model\n"
    "ubm_variance -- variance supervector for the world model\n"
    "test_stats   -- list of accumulate statistics for each test trial\n"
    "test_channelOffset -- \n"
    "frame_length_normlisation -- perform a normalisation by the number of feature vectors\n"
    ));
  def("linear_scoring", linearScoring2, linearScoring2_overloads(args("models", "ubm", "test_stats", "test_channel_offset", "frame_length_normalisation"),
    "Compute a matrix of scores using linear scoring.\n"
    "Return a 2D matrix of scores, scores[m, s] is the score for model m against statistics s\n"
    "\n"
    "Warning Each GMM must have the same size.\n"
    "\n"
    "models      -- list of client models\n"
    "ubm         -- world model\n"
    "test_stats  -- list of accumulate statistics for each test trial\n"
    "test_channel_offset -- \n"
    "frame_length_normlisation -- perform a normalisation by the number of feature vectors\n"
    ));
  def("linear_scoring", linearScoring3, linearScoring3_overloads(args("model", "ubm_mean", "ubm_variance", "test_stats", "test_channelOffset", "frame_length_normalisation"),
    "Compute a score using linear scoring.\n"
    "\n"
    "model        -- mean supervectors for the client model\n"
    "ubm_mean     -- mean supervector for the world model\n"
    "ubm_variance -- variance supervector for the world model\n"
    "test_stats   -- accumulate statistics for each test trial\n"
    "test_channelOffset -- \n"
    "frame_length_normlisation -- perform a normalisation by the number of feature vectors\n"
    ));
}
