/**
 * @date Tue May 10 11:35:58 2011 +0200
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.em/KMeansMachine.h>

#include <bob.core/assert.h>
#include <bob.core/check.h>
#include <bob.core/array_copy.h>
#include <limits>

bob::learn::em::KMeansMachine::KMeansMachine():
  m_n_means(0), m_n_inputs(0), m_means(0,0),
  m_cache_means(0,0)
{
  m_means = 0;
}

bob::learn::em::KMeansMachine::KMeansMachine(const size_t n_means, const size_t n_inputs):
  m_n_means(n_means), m_n_inputs(n_inputs), m_means(n_means, n_inputs),
  m_cache_means(n_means, n_inputs)
{
  m_means = 0;
}

bob::learn::em::KMeansMachine::KMeansMachine(const blitz::Array<double,2>& means):
  m_n_means(means.extent(0)), m_n_inputs(means.extent(1)),
  m_means(bob::core::array::ccopy(means)),
  m_cache_means(means.shape())
{
}

bob::learn::em::KMeansMachine::KMeansMachine(const bob::learn::em::KMeansMachine& other):
  m_n_means(other.m_n_means), m_n_inputs(other.m_n_inputs),
  m_means(bob::core::array::ccopy(other.m_means)),
  m_cache_means(other.m_cache_means.shape())
{
}

bob::learn::em::KMeansMachine::KMeansMachine(bob::io::base::HDF5File& config)
{
  load(config);
}

bob::learn::em::KMeansMachine::~KMeansMachine() { }

bob::learn::em::KMeansMachine& bob::learn::em::KMeansMachine::operator=
(const bob::learn::em::KMeansMachine& other)
{
  if(this != &other)
  {
    m_n_means = other.m_n_means;
    m_n_inputs = other.m_n_inputs;
    m_means.reference(bob::core::array::ccopy(other.m_means));
    m_cache_means.resize(other.m_means.shape());
  }
  return *this;
}

bool bob::learn::em::KMeansMachine::operator==(const bob::learn::em::KMeansMachine& b) const
{
  return m_n_inputs == b.m_n_inputs && m_n_means == b.m_n_means &&
         bob::core::array::isEqual(m_means, b.m_means);
}

bool bob::learn::em::KMeansMachine::operator!=(const bob::learn::em::KMeansMachine& b) const
{
  return !(this->operator==(b));
}

bool bob::learn::em::KMeansMachine::is_similar_to(const bob::learn::em::KMeansMachine& b,
  const double r_epsilon, const double a_epsilon) const
{
  return m_n_inputs == b.m_n_inputs && m_n_means == b.m_n_means &&
         bob::core::array::isClose(m_means, b.m_means, r_epsilon, a_epsilon);
}

void bob::learn::em::KMeansMachine::load(bob::io::base::HDF5File& config)
{
  //reads all data directly into the member variables
  m_means.reference(config.readArray<double,2>("means"));
  m_n_means = m_means.extent(0);
  m_n_inputs = m_means.extent(1);
  m_cache_means.resize(m_n_means, m_n_inputs);
}

void bob::learn::em::KMeansMachine::save(bob::io::base::HDF5File& config) const
{
  config.setArray("means", m_means);
}

void bob::learn::em::KMeansMachine::setMeans(const blitz::Array<double,2> &means)
{
  bob::core::array::assertSameShape(means, m_means);
  m_means = means;
}

void bob::learn::em::KMeansMachine::setMean(const size_t i, const blitz::Array<double,1> &mean)
{
  if(i>=m_n_means) {
    boost::format m("cannot set mean with index %lu: out of bounds [0,%lu[");
    m % i % m_n_means;
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameDimensionLength(mean.extent(0), m_means.extent(1));
  m_means(i,blitz::Range::all()) = mean;
}

const blitz::Array<double,1> bob::learn::em::KMeansMachine::getMean(const size_t i) const
{
  if(i>=m_n_means) {
    boost::format m("cannot get mean with index %lu: out of bounds [0,%lu[");
    m % i % m_n_means;
    throw std::runtime_error(m.str());
  }

  return m_means(i,blitz::Range::all());

}

double bob::learn::em::KMeansMachine::getDistanceFromMean(const blitz::Array<double,1> &x,
  const size_t i) const
{
  return blitz::sum(blitz::pow2(m_means(i,blitz::Range::all()) - x));
}

void bob::learn::em::KMeansMachine::getClosestMean(const blitz::Array<double,1> &x,
  size_t &closest_mean, double &min_distance) const
{
  min_distance = std::numeric_limits<double>::max();

  for(size_t i=0; i<m_n_means; ++i) {
    double this_distance = getDistanceFromMean(x,i);
    if(this_distance < min_distance) {
      min_distance = this_distance;
      closest_mean = i;
    }
  }
}

double bob::learn::em::KMeansMachine::getMinDistance(const blitz::Array<double,1>& input) const
{
  size_t closest_mean = 0;
  double min_distance = 0;
  getClosestMean(input,closest_mean,min_distance);
  return min_distance;
}

void bob::learn::em::KMeansMachine::getVariancesAndWeightsForEachClusterInit(blitz::Array<double,2>& variances, blitz::Array<double,1>& weights) const
{
  // check arguments
  bob::core::array::assertSameShape(variances, m_means);
  bob::core::array::assertSameDimensionLength(weights.extent(0), m_n_means);

  // initialise output arrays
  bob::core::array::assertSameShape(variances, m_means);
  bob::core::array::assertSameDimensionLength(weights.extent(0), m_n_means);
  variances = 0;
  weights = 0;

  // initialise (temporary) mean array
  m_cache_means = 0;
}

void bob::learn::em::KMeansMachine::getVariancesAndWeightsForEachClusterAcc(const blitz::Array<double,2>& data, blitz::Array<double,2>& variances, blitz::Array<double,1>& weights) const
{
  // check arguments
  bob::core::array::assertSameShape(variances, m_means);
  bob::core::array::assertSameDimensionLength(weights.extent(0), m_n_means);

  // iterate over data
  blitz::Range a = blitz::Range::all();
  for(int i=0; i<data.extent(0); ++i) {
    // - get example
    blitz::Array<double,1> x(data(i,a));

    // - find closest mean
    size_t closest_mean = 0;
    double min_distance = 0;
    getClosestMean(x,closest_mean,min_distance);

    // - accumulate stats
    m_cache_means(closest_mean, blitz::Range::all()) += x;
    variances(closest_mean, blitz::Range::all()) += blitz::pow2(x);
    ++weights(closest_mean);
  }
}

void bob::learn::em::KMeansMachine::getVariancesAndWeightsForEachClusterFin(blitz::Array<double,2>& variances, blitz::Array<double,1>& weights) const
{
  // check arguments
  bob::core::array::assertSameShape(variances, m_means);
  bob::core::array::assertSameDimensionLength(weights.extent(0), m_n_means);

  // calculate final variances and weights
  blitz::firstIndex idx1;
  blitz::secondIndex idx2;

  // find means
  m_cache_means = m_cache_means(idx1,idx2) / weights(idx1);

  // find variances
  variances = variances(idx1,idx2) / weights(idx1);
  variances -= blitz::pow2(m_cache_means);

  // find weights
  weights = weights / blitz::sum(weights);
}

void bob::learn::em::KMeansMachine::setCacheMeans(const blitz::Array<double,2> &cache_means)
{
  bob::core::array::assertSameShape(cache_means, m_cache_means);
  m_cache_means = cache_means;
}

void bob::learn::em::KMeansMachine::getVariancesAndWeightsForEachCluster(const blitz::Array<double,2>& data, blitz::Array<double,2>& variances, blitz::Array<double,1>& weights) const
{
  // initialise
  getVariancesAndWeightsForEachClusterInit(variances, weights);
  // accumulate
  getVariancesAndWeightsForEachClusterAcc(data, variances, weights);
  // merge/finalize
  getVariancesAndWeightsForEachClusterFin(variances, weights);
}

void bob::learn::em::KMeansMachine::forward(const blitz::Array<double,1>& input, double& output) const
{
  if(static_cast<size_t>(input.extent(0)) != m_n_inputs) {
    boost::format m("machine input size (%u) does not match the size of input array (%d)");
    m % m_n_inputs % input.extent(0);
    throw std::runtime_error(m.str());
  }
  forward_(input,output);
}

void bob::learn::em::KMeansMachine::forward_(const blitz::Array<double,1>& input, double& output) const
{
  output = getMinDistance(input);
}

void bob::learn::em::KMeansMachine::resize(const size_t n_means, const size_t n_inputs)
{
  m_n_means = n_means;
  m_n_inputs = n_inputs;
  m_means.resizeAndPreserve(n_means, n_inputs);
  m_cache_means.resizeAndPreserve(n_means, n_inputs);
}

namespace bob { namespace learn { namespace em {
  std::ostream& operator<<(std::ostream& os, const KMeansMachine& km) {
    os << "Means = " << km.m_means << std::endl;
    return os;
  }
} } }
