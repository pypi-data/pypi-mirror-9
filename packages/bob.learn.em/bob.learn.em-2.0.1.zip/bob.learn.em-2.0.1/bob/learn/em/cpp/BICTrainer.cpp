/**
 * @date Wed Jun  6 10:29:09 CEST 2012
 * @author Manuel Guenther <Manuel.Guenther@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.em/BICTrainer.h>
#include <bob.learn.linear/pca.h>
#include <bob.learn.linear/machine.h>

static double sqr(const double& x){
  return x*x;
}

/**
 * This function trains one of the classes of the given machine with the given data.
 * It computes either BIC projection matrices, or IEC mean and variance.
 *
 * @param  clazz    false for the intrapersonal class, true for the extrapersonal one.
 * @param  machine  The machine to be trained.
 * @param  differences  A set of (intra/extra)-personal difference vectors that should be trained.
 */
void bob::learn::em::BICTrainer::train_single(bool clazz, bob::learn::em::BICMachine& machine, const blitz::Array<double,2>& differences) const {
  int subspace_dim = clazz ? m_M_E : m_M_I;
  int input_dim = differences.extent(1);
  int data_count = differences.extent(0);
  blitz::Range a = blitz::Range::all();

  if (subspace_dim){
    // train the class using BIC

    // Compute PCA on the given dataset
    bob::learn::linear::PCATrainer trainer;
    const int n_eigs = trainer.output_size(differences);
    bob::learn::linear::Machine pca(input_dim, n_eigs);
    blitz::Array<double,1> variances(n_eigs);
    trainer.train(pca, variances, differences);

    // compute rho
    double rho = 0.;
    int non_zero_eigenvalues = std::min(input_dim, data_count-1);
    // assert that the number of kept eigenvalues is not chosen to big
    if (subspace_dim >= non_zero_eigenvalues)
      throw std::runtime_error((boost::format("The chosen subspace dimension %d is larger than the theoretical number of nonzero eigenvalues %d")%subspace_dim%non_zero_eigenvalues).str());
    // compute the average of the reminding eigenvalues
    for (int i = subspace_dim; i < non_zero_eigenvalues; ++i){
      rho += variances(i);
    }
    rho /= non_zero_eigenvalues - subspace_dim;

    // limit dimensionalities
    pca.resize(input_dim, subspace_dim);
    variances.resizeAndPreserve(subspace_dim);

    // check that all variances are meaningful
    for (int i = 0; i < subspace_dim; ++i){
      if (variances(i) < 1e-12)
        throw std::runtime_error((boost::format("The chosen subspace dimension is %d, but the %dth eigenvalue is already to small")%subspace_dim%i).str());
    }

    // initialize the machine
    blitz::Array<double, 2> projection = pca.getWeights();
    blitz::Array<double, 1> mean = pca.getInputSubtraction();
    machine.setBIC(clazz, mean, variances, projection, rho);
  } else {
    // train the class using IEC
    // => compute mean and variance only
    blitz::Array<double,1> mean(input_dim), variance(input_dim);

    // compute mean and variance
    mean = 0.;
    variance = 0.;
    for (int n = data_count; n--;){
      const blitz::Array<double,1>& diff = differences(n,a);
      assert(diff.shape()[0] == input_dim);
      for (int i = input_dim; i--;){
        mean(i) += diff(i);
        variance(i) += sqr(diff(i));
      }
    }
    // normalize mean and variances
    for (int i = 0; i < input_dim; ++i){
      // intrapersonal
      variance(i) = (variance(i) - sqr(mean(i)) / data_count) / (data_count - 1.);
      mean(i) /= data_count;
      if (variance(i) < 1e-12)
        throw std::runtime_error((boost::format("The variance of the %dth dimension is too small. Check your data!")%i).str());
    }

    // set the results to the machine
    machine.setIEC(clazz, mean, variance);
  }
}
