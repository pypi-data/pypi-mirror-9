/**
 * @date Tue May 10 11:35:58 2011 +0200
 * @author Francois Moulin <Francois.Moulin@idiap.ch>
 *
 * @brief This class implements the E-step of the expectation-maximisation algorithm for a GMM Machine.
 * @details See Section 9.2.2 of Bishop, "Pattern recognition and machine learning", 2006
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_EM_GMMBASETRAINER_H
#define BOB_LEARN_EM_GMMBASETRAINER_H

#include <bob.learn.em/GMMMachine.h>
#include <bob.learn.em/GMMStats.h>
#include <limits>

namespace bob { namespace learn { namespace em {

/**
 * @brief This class implements the E-step of the expectation-maximisation
 * algorithm for a GMM Machine.
 * @details See Section 9.2.2 of Bishop,
 *   "Pattern recognition and machine learning", 2006
 */
class GMMBaseTrainer
{
  public:
    /**
     * @brief Default constructor
     */
    GMMBaseTrainer(const bool update_means=true,
                   const bool update_variances=false,
                   const bool update_weights=false,
                   const double mean_var_update_responsibilities_threshold = std::numeric_limits<double>::epsilon());

    /**
     * @brief Copy constructor
     */
    GMMBaseTrainer(const GMMBaseTrainer& other);

    /**
     * @brief Destructor
     */
    virtual ~GMMBaseTrainer();

    /**
     * @brief Initialization before the EM steps
     */
    void initialize(bob::learn::em::GMMMachine& gmm);

    /**
     * @brief Calculates and saves statistics across the dataset,
     * and saves these as m_ss. Calculates the average
     * log likelihood of the observations given the GMM,
     * and returns this in average_log_likelihood.
     *
     * The statistics, m_ss, will be used in the mStep() that follows.
     * Implements EMTrainer::eStep(double &)
     */
     void eStep(bob::learn::em::GMMMachine& gmm,
      const blitz::Array<double,2>& data);

    /**
     * @brief Computes the likelihood using current estimates of the latent
     * variables
     */
    double computeLikelihood(bob::learn::em::GMMMachine& gmm);


    /**
     * @brief Assigns from a different GMMBaseTrainer
     */
    GMMBaseTrainer& operator=(const GMMBaseTrainer &other);

    /**
     * @brief Equal to
     */
    bool operator==(const GMMBaseTrainer& b) const;

    /**
     * @brief Not equal to
     */
    bool operator!=(const GMMBaseTrainer& b) const;

    /**
     * @brief Similar to
     */
    bool is_similar_to(const GMMBaseTrainer& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief Returns the internal GMM statistics. Useful to parallelize the
     * E-step
     */
    const boost::shared_ptr<bob::learn::em::GMMStats> getGMMStats() const
    { return m_ss; }

    /**
     * @brief Sets the internal GMM statistics. Useful to parallelize the
     * E-step
     */
    void setGMMStats(boost::shared_ptr<bob::learn::em::GMMStats> stats);

    /**
     * update means on each iteration
     */
    bool getUpdateMeans()
    {return m_update_means;}

    /**
     * update variances on each iteration
     */
    bool getUpdateVariances()
    {return m_update_variances;}


    bool getUpdateWeights()
    {return m_update_weights;}


    double getMeanVarUpdateResponsibilitiesThreshold()
    {return m_mean_var_update_responsibilities_threshold;}


  private:

    /**
     * These are the sufficient statistics, calculated during the
     * E-step and used during the M-step
     */
    boost::shared_ptr<bob::learn::em::GMMStats> m_ss;


    /**
     * update means on each iteration
     */
    bool m_update_means;

    /**
     * update variances on each iteration
     */
    bool m_update_variances;

    /**
     * update weights on each iteration
     */
    bool m_update_weights;

    /**
     * threshold over the responsibilities of the Gaussians
     * Equations 9.24, 9.25 of Bishop, "Pattern recognition and machine learning", 2006
     * require a division by the responsibilities, which might be equal to zero
     * because of numerical issue. This threshold is used to avoid such divisions.
     */
    double m_mean_var_update_responsibilities_threshold;
};

} } } // namespaces

#endif // BOB_LEARN_EM_GMMBASETRAINER_H
