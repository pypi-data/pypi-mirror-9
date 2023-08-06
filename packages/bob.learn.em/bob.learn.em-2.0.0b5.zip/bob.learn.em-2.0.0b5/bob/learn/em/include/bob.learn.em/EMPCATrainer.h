/**
 * @date Tue Oct 11 12:18:23 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief Expectation Maximization Algorithm for Principal Component
 * Analysis
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_EM_EMPCA_TRAINER_H
#define BOB_LEARN_EM_EMPCA_TRAINER_H

#include <bob.learn.linear/machine.h>
#include <blitz/array.h>

namespace bob { namespace learn { namespace em {

/**
 * @brief Trains a linear machine using an Expectation-Maximization algorithm
 * on the given dataset.\n
 * References:\n
 *  1. "Probabilistic Principal Component Analysis",
 *     Michael Tipping and Christopher Bishop,
 *     Journal of the Royal Statistical Society,
 *      Series B, 61, Part 3, pp. 611–622\n
 *  2. "EM Algorithms for PCA and SPCA",
 *     Sam Roweis, Neural Information Processing Systems 10 (NIPS'97),
 *     pp.626-632 (Sensible Principal Component Analysis part)\n
 *
 * Notations used are the ones from reference 1.\n
 * The probabilistic model is given by: \f$t = W x + \mu + \epsilon\f$\n
 *  - \f$t\f$ is the observed data (dimension \f$f\f$)\n
 *  - \f$W\f$ is a  projection matrix (dimension \f$f \times d\f$)\n
 *  - \f$x\f$ is the projected data (dimension \f$d < f\f$)\n
 *  - \f$\mu\f$ is the mean of the data (dimension \f$f\f$)\n
 *  - \f$\epsilon\f$ is the noise of the data (dimension \f$f\f$)
 *      Gaussian with zero-mean and covariance matrix \f$\sigma^2 Id\f$
 */
class EMPCATrainer
{
  public: //api
    /**
     * @brief Initializes a new EM PCA trainer. The training stage will place the
     * resulting components in the linear machine and set it up to
     * extract the variable means automatically.
     */
    EMPCATrainer(bool compute_likelihood=true);

    /**
     * @brief Copy constructor
     */
    EMPCATrainer(const EMPCATrainer& other);

    /**
     * @brief (virtual) Destructor
     */
    virtual ~EMPCATrainer();

    /**
     * @brief Assignment operator
     */
    EMPCATrainer& operator=(const EMPCATrainer& other);

    /**
     * @brief Equal to
     */
    bool operator==(const EMPCATrainer& b) const;

    /**
     * @brief Not equal to
     */
    bool operator!=(const EMPCATrainer& b) const;

    /**
     * @brief Similar to
     */
    bool is_similar_to(const EMPCATrainer& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief This methods performs some initialization before the EM loop.
     */
    virtual void initialize(bob::learn::linear::Machine& machine,
      const blitz::Array<double,2>& ar);

    /**
     * @brief Calculates and saves statistics across the dataset, and saves
     * these as m_z_{first,second}_order.
     *
     * The statistics will be used in the mStep() that follows.
     */
    virtual void eStep(bob::learn::linear::Machine& machine,
      const blitz::Array<double,2>& ar);

    /**
     * @brief Performs a maximization step to update the parameters of the
     * factor analysis model.
     */
    virtual void mStep(bob::learn::linear::Machine& machine,
       const blitz::Array<double,2>& ar);

    /**
     * @brief Computes the average log likelihood using the current estimates
     * of the latent variables.
     */
    virtual double computeLikelihood(bob::learn::linear::Machine& machine);

    /**
     * @brief Sets \f$\sigma^2\f$ (Mostly for test purpose)
     */
    void setSigma2(double sigma2) { m_sigma2 = sigma2; }

    /**
     * @brief Gets \f$\sigma^2\f$ (Mostly for test purpose)
     */
    double getSigma2() const { return m_sigma2; }

    /**
     * @brief Sets the Random Number Generator
     */
    void setRng(const boost::shared_ptr<boost::mt19937> rng)
    { m_rng = rng; }

    /**
     * @brief Gets the Random Number Generator
     */
    const boost::shared_ptr<boost::mt19937> getRng() const
    { return m_rng; }


  private: //representation

    bool m_compute_likelihood;
    boost::shared_ptr<boost::mt19937> m_rng;

    blitz::Array<double,2> m_S; /// Covariance of the training data (required only if we need to compute the log likelihood)
    blitz::Array<double,2> m_z_first_order; /// Current mean of the \f$z_{n}\f$ latent variable
    blitz::Array<double,3> m_z_second_order; /// Current covariance of the \f$z_{n}\f$ latent variable
    blitz::Array<double,2> m_inW; /// The matrix product \f$W^T W\f$
    blitz::Array<double,2> m_invM; /// The matrix \f$inv(M)\f$, where \f$M = W^T W + \sigma^2 Id\f$
    double m_sigma2; /// The variance \f$sigma^2\f$ of the noise epsilon of the probabilistic model
    double m_f_log2pi; /// The constant \f$n_{features} log(2*\pi)\f$ used during the likelihood computation

    // Working arrays
    mutable blitz::Array<double,2> m_tmp_dxf; /// size dimensionality x n_features
    mutable blitz::Array<double,1> m_tmp_d; /// size dimensionality
    mutable blitz::Array<double,1> m_tmp_f; /// size n_features
    mutable blitz::Array<double,2> m_tmp_dxd_1; /// size dimensionality x dimensionality
    mutable blitz::Array<double,2> m_tmp_dxd_2; /// size dimensionality x dimensionality
    mutable blitz::Array<double,2> m_tmp_fxd_1; /// size n_features x dimensionality
    mutable blitz::Array<double,2> m_tmp_fxd_2; /// size n_features x dimensionality
    mutable blitz::Array<double,2> m_tmp_fxf_1; /// size n_features x n_features
    mutable blitz::Array<double,2> m_tmp_fxf_2; /// size n_features x n_features


    /**
     * @brief Initializes/resizes the (array) members
     */
    void initMembers(const bob::learn::linear::Machine& machine,
      const blitz::Array<double,2>& ar);
    /**
     * @brief Computes the mean and the variance (if required) of the training
     * data
     */
    void computeMeanVariance(bob::learn::linear::Machine& machine,
      const blitz::Array<double,2>& ar);
    /**
     * @brief Random initialization of \f$W\f$ and \f$sigma^2\f$.
     * W is the projection matrix (from the LinearMachine)
     */
    void initRandomWSigma2(bob::learn::linear::Machine& machine);
    /**
     * @brief Computes the product \f$W^T W\f$.
     * \f$W\f$ is the projection matrix (from the LinearMachine)
     */
    void computeWtW(bob::learn::linear::Machine& machine);
    /**
     * @brief Computes the inverse of \f$M\f$ matrix, where
     *   \f$M = W^T W + \sigma^2 Id\f$.
     *   \f$W\f$ is the projection matrix (from the LinearMachine)
     */
    void computeInvM();
    /**
     * @brief M-Step (part 1): Computes the new estimate of \f$W\f$ using the
     * new estimated statistics.
     */
    void updateW(bob::learn::linear::Machine& machine,
       const blitz::Array<double,2>& ar);
    /**
     * @brief M-Step (part 2): Computes the new estimate of \f$\sigma^2\f$ using
     * the new estimated statistics.
     */
    void updateSigma2(bob::learn::linear::Machine& machine,
       const blitz::Array<double,2>& ar);
};

} } } // namespaces

#endif /* BOB_LEARN_EM_EMPCA_TRAINER_H */
