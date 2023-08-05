/**
 * @date Tue May 10 11:35:58 2011 +0200
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.em/GMMStats.h>
#include <bob.core/logging.h>
#include <bob.core/check.h>

bob::learn::em::GMMStats::GMMStats() {
  resize(0,0);
}

bob::learn::em::GMMStats::GMMStats(const size_t n_gaussians, const size_t n_inputs) {
  resize(n_gaussians,n_inputs);
}

bob::learn::em::GMMStats::GMMStats(bob::io::base::HDF5File& config) {
  load(config);
}

bob::learn::em::GMMStats::GMMStats(const bob::learn::em::GMMStats& other) {
  copy(other);
}

bob::learn::em::GMMStats::~GMMStats() {
}

bob::learn::em::GMMStats&
bob::learn::em::GMMStats::operator=(const bob::learn::em::GMMStats& other) {
  // protect against invalid self-assignment
  if (this != &other)
    copy(other);

  // by convention, always return *this
  return *this;
}

bool bob::learn::em::GMMStats::operator==(const bob::learn::em::GMMStats& b) const
{
  return (T == b.T && log_likelihood == b.log_likelihood &&
          bob::core::array::isEqual(n, b.n) &&
          bob::core::array::isEqual(sumPx, b.sumPx) &&
          bob::core::array::isEqual(sumPxx, b.sumPxx));
}

bool
bob::learn::em::GMMStats::operator!=(const bob::learn::em::GMMStats& b) const
{
  return !(this->operator==(b));
}

bool bob::learn::em::GMMStats::is_similar_to(const bob::learn::em::GMMStats& b,
  const double r_epsilon, const double a_epsilon) const
{
  return (T == b.T &&
          bob::core::isClose(log_likelihood, b.log_likelihood, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(n, b.n, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(sumPx, b.sumPx, r_epsilon, a_epsilon) &&
          bob::core::array::isClose(sumPxx, b.sumPxx, r_epsilon, a_epsilon));
}


void bob::learn::em::GMMStats::operator+=(const bob::learn::em::GMMStats& b) {
  // Check dimensions
  if(n.extent(0) != b.n.extent(0) ||
      sumPx.extent(0) != b.sumPx.extent(0) || sumPx.extent(1) != b.sumPx.extent(1) ||
      sumPxx.extent(0) != b.sumPxx.extent(0) || sumPxx.extent(1) != b.sumPxx.extent(1))
    // TODO: add a specialized exception
    throw std::runtime_error("if you see this exception, fill a bug report");

  // Update GMMStats object with the content of the other one
  T += b.T;
  log_likelihood += b.log_likelihood;
  n += b.n;
  sumPx += b.sumPx;
  sumPxx += b.sumPxx;
}

void bob::learn::em::GMMStats::copy(const GMMStats& other) {
  // Resize arrays
  resize(other.sumPx.extent(0),other.sumPx.extent(1));
  // Copy content
  T = other.T;
  log_likelihood = other.log_likelihood;
  n = other.n;
  sumPx = other.sumPx;
  sumPxx = other.sumPxx;
}

void bob::learn::em::GMMStats::resize(const size_t n_gaussians, const size_t n_inputs) {
  n.resize(n_gaussians);
  sumPx.resize(n_gaussians, n_inputs);
  sumPxx.resize(n_gaussians, n_inputs);
  init();
}

void bob::learn::em::GMMStats::init() {
  log_likelihood = 0;
  T = 0;
  n = 0.0;
  sumPx = 0.0;
  sumPxx = 0.0;
}

void bob::learn::em::GMMStats::save(bob::io::base::HDF5File& config) const {
  //please note we fix the output values to be of a precise type so they can be
  //retrieved at any platform with the exact same precision.
  // TODO: add versioning, replace int64_t by uint64_t and log_liklihood by log_likelihood
  int64_t sumpx_shape_0 = sumPx.shape()[0];
  int64_t sumpx_shape_1 = sumPx.shape()[1];
  config.set("n_gaussians", sumpx_shape_0);
  config.set("n_inputs", sumpx_shape_1);
  config.set("log_liklihood", log_likelihood); //double
  config.set("T", static_cast<int64_t>(T));
  config.setArray("n", n); //Array1d
  config.setArray("sumPx", sumPx); //Array2d
  config.setArray("sumPxx", sumPxx); //Array2d
}

void bob::learn::em::GMMStats::load(bob::io::base::HDF5File& config) {
  log_likelihood = config.read<double>("log_liklihood");
  int64_t n_gaussians = config.read<int64_t>("n_gaussians");
  int64_t n_inputs = config.read<int64_t>("n_inputs");
  T = static_cast<size_t>(config.read<int64_t>("T"));

  //resize arrays to prepare for HDF5 readout
  n.resize(n_gaussians);
  sumPx.resize(n_gaussians, n_inputs);
  sumPxx.resize(n_gaussians, n_inputs);

  //load data
  config.readArray("n", n);
  config.readArray("sumPx", sumPx);
  config.readArray("sumPxx", sumPxx);
}

namespace bob { namespace learn { namespace em {
  std::ostream& operator<<(std::ostream& os, const GMMStats& g) {
    os << "log_likelihood = " << g.log_likelihood << std::endl;
    os << "T = " << g.T << std::endl;
    os << "n = " << g.n;
    os << "sumPx = " << g.sumPx;
    os << "sumPxx = " << g.sumPxx;

    return os;
  }
} } }
