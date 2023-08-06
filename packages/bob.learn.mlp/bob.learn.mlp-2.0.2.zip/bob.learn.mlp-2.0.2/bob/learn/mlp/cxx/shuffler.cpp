/**
 * @date Wed Jul 13 16:58:26 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Implementation of the DataShuffler.
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <stdexcept>
#include <sys/time.h>
#include <boost/format.hpp>

#include <bob.core/assert.h>
#include <bob.core/array_copy.h>

#include <bob.learn.mlp/shuffler.h>

bob::learn::mlp::DataShuffler::DataShuffler
(const std::vector<blitz::Array<double,2> >& data,
 const std::vector<blitz::Array<double,1> >& target):
  m_data(data.size()),
  m_target(target.size()),
  m_range(),
  m_do_stdnorm(false),
  m_mean(),
  m_stddev()
{
  if (data.size() == 0)
    throw std::runtime_error("data vector cannot be empty");
  if (target.size() == 0)
    throw std::runtime_error("target vector cannot be empty");

  bob::core::array::assertSameDimensionLength(data.size(), target.size());

  // checks shapes, minimum number of examples
  for (size_t k=0; k<data.size(); ++k) {
    if (data[k].size() == 0) {
      boost::format m("class %u has no samples");
      m % k;
      throw std::runtime_error(m.str());
    }
    //this may also trigger if I cannot get doubles from the Arrayset
    bob::core::array::assertSameDimensionLength(data[0].extent(1), data[k].extent(1));
    bob::core::array::assertSameShape(target[0], target[k]);
  }

  // set save values for the mean and stddev (even if not used at start)
  m_mean.resize(data[0].extent(1));
  m_mean = 0.;
  m_stddev.resize(data[0].extent(1));
  m_stddev = 1.;

  // copies the target data to my own variable
  for (size_t k=0; k<target.size(); ++k) {
    m_data[k].reference(bob::core::array::ccopy(data[k]));
    m_target[k].reference(bob::core::array::ccopy(target[k]));
  }

  // creates one range tailored for the range of each data object
  for (size_t i=0; i<data.size(); ++i) {
    m_range.push_back(boost::uniform_int<size_t>(0, m_data[i].extent(0)-1));
  }
}

bob::learn::mlp::DataShuffler::DataShuffler(const bob::learn::mlp::DataShuffler& other):
  m_data(other.m_data.size()),
  m_target(other.m_target.size()),
  m_range(other.m_range),
  m_do_stdnorm(other.m_do_stdnorm),
  m_mean(bob::core::array::ccopy(other.m_mean)),
  m_stddev(bob::core::array::ccopy(other.m_stddev))
{
  for (size_t k=0; k<m_target.size(); ++k) {
    m_data[k].reference(bob::core::array::ccopy(other.m_data[k]));
    m_target[k].reference(bob::core::array::ccopy(other.m_target[k]));
  }
}

bob::learn::mlp::DataShuffler::~DataShuffler() { }

bob::learn::mlp::DataShuffler& bob::learn::mlp::DataShuffler::operator=(const bob::learn::mlp::DataShuffler& other) {

  m_data.resize(other.m_data.size());
  m_target.resize(other.m_target.size());

  for (size_t k=0; k<m_target.size(); ++k) {
    m_data[k].reference(bob::core::array::ccopy(other.m_data[k]));
    m_target[k].reference(bob::core::array::ccopy(other.m_target[k]));
  }

  m_range = other.m_range;

  m_mean.reference(bob::core::array::ccopy(other.m_mean));
  m_stddev.reference(bob::core::array::ccopy(other.m_stddev));
  m_do_stdnorm = other.m_do_stdnorm;

  return *this;
}

/**
 * Calculates mean and std.dev. in a single loop.
 * see: http://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
 */
void evaluateStdNormParameters(const std::vector<blitz::Array<double,2> >& data,
    blitz::Array<double,1>& mean, blitz::Array<double,1>& stddev) {

  mean = 0.;
  stddev = 0.; ///< temporarily used to accumulate square sum!
  double samples = 0;

  blitz::Range all = blitz::Range::all();
  for (size_t k=0; k<data.size(); ++k) {
    for (int i=0; i<data[k].extent(0); ++i) {
      mean += data[k](i,all);
      stddev += blitz::pow2(data[k](i,all));
      ++samples;
    }
  }
  stddev -= blitz::pow2(mean) / samples;
  stddev /= (samples-1); ///< note: unbiased sample variance
  stddev = blitz::sqrt(stddev);

  mean /= (samples);
}

/**
 * Applies standard normalization parameters to all data arrays given
 */
void applyStdNormParameters(std::vector<blitz::Array<double,2> >& data,
    const blitz::Array<double,1>& mean, const blitz::Array<double,1>& stddev) {
  blitz::Range all = blitz::Range::all();
  for (size_t k=0; k<data.size(); ++k) {
    for (int i=0; i<data[k].extent(0); ++i) {
      data[k](i,all) = (data[k](i,all) - mean) / stddev;
    }
  }
}

/**
 * Inverts the application of std normalization parameters
 */
void invertApplyStdNormParameters(std::vector<blitz::Array<double,2> >& data,
    const blitz::Array<double,1>& mean, const blitz::Array<double,1>& stddev) {
  blitz::Range all = blitz::Range::all();
  for (size_t k=0; k<data.size(); ++k) {
    for (int i=0; i<data[k].extent(0); ++i) {
      data[k](i,all) = (data[k](i,all) * stddev) + mean;
    }
  }
}

void bob::learn::mlp::DataShuffler::setAutoStdNorm(bool s) {
  if (s && !m_do_stdnorm) {
    evaluateStdNormParameters(m_data, m_mean, m_stddev);
    applyStdNormParameters(m_data, m_mean, m_stddev);
  }
  if (!s && m_do_stdnorm) {
    invertApplyStdNormParameters(m_data, m_mean, m_stddev);
    m_mean = 0.;
    m_stddev = 1.;
  }
  m_do_stdnorm = s;
}

void bob::learn::mlp::DataShuffler::getStdNorm(blitz::Array<double,1>& mean,
    blitz::Array<double,1>& stddev) const {
  bob::core::array::assertSameShape(mean, m_mean);
  bob::core::array::assertSameShape(stddev, m_stddev);
  if (m_do_stdnorm) {
    mean = m_mean;
    stddev = m_stddev;
  }
  else {
    evaluateStdNormParameters(m_data, mean, stddev);
  }
}

void bob::learn::mlp::DataShuffler::operator() (boost::mt19937& rng,
    blitz::Array<double,2>& data, blitz::Array<double,2>& target) {

  bob::core::array::assertSameDimensionLength(data.extent(0), target.extent(0));

  size_t counter = 0;
  size_t max = data.extent(0);
  blitz::Range all = blitz::Range::all();
  while (true) {
    for (size_t i=0; i<m_data.size(); ++i) { //for all classes
      size_t index = m_range[i](rng); //pick a random position within class
      data(counter,all) = m_data[i](index,all);
      target(counter,all) = m_target[i];
      ++counter;
      if (counter >= max) break;
    }
    if (counter >= max) break;
  }

}

void bob::learn::mlp::DataShuffler::operator() (blitz::Array<double,2>& data,
    blitz::Array<double,2>& target) {
  struct timeval tv;
  gettimeofday(&tv, 0);
  boost::mt19937 rng(tv.tv_sec + tv.tv_usec);
  operator()(rng, data, target);
}
