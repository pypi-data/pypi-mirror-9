/**
 * @date Fri Oct 14 18:07:56 2011 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief Machines that implements the Probabilistic Linear Discriminant
 *   Analysis Model of Prince and Helder,
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_EM_PLDAMACHINE_H
#define BOB_LEARN_EM_PLDAMACHINE_H

#include <blitz/array.h>
#include <bob.io.base/HDF5File.h>
#include <map>
#include <iostream>
#include <stdexcept>

namespace bob { namespace learn { namespace em {

/**
 * @brief This class is a container for the \f$F\f$, \f$G\f$ and \f$\Sigma\f$
 * matrices and the mean vector \f$\mu\f$ of a PLDA model. This also
 * precomputes useful matrices to make the model scalable.\n
 * References:\n
 * 1. 'A Scalable Formulation of Probabilistic Linear Discriminant Analysis:
 *     Applied to Face Recognition', Laurent El Shafey, Chris McCool,
 *     Roy Wallace, Sebastien Marcel, TPAMI'2013
 * 2. 'Probabilistic Linear Discriminant Analysis for Inference About
 *     Identity', Prince and Elder, ICCV'2007\n
 * 3. 'Probabilistic Models for Inference about Identity', Li, Fu, Mohammed,
 *     Elder and Prince, TPAMI'2012
 */
class PLDABase
{
  public:
    /**
     * @brief Default constructor.\n Builds an otherwise invalid 0x0x0
     * PLDABase.
     */
    PLDABase();
    /**
     * @brief Constructor, builds a new PLDABase.\n \f$F\f$, \f$G\f$
     * and \f$\Sigma\f$ are initialized to the 'eye' matrix (matrix with 1's
     * on the diagonal and 0 outside), and \f$\mu\f$ is initialized to 0.
     *
     * @param dim_d Dimensionality of the feature vector
     * @param dim_f size of \f$F\f$ (dim_d x dim_f)
     * @param dim_g size of \f$G\f$ (dim_d x dim_g)
     * @param variance_threshold The smallest possible value of the variance
     *                           (Ignored if set to 0.)
     */
    PLDABase(const size_t dim_d, const size_t dim_f,
      const size_t dim_g, const double variance_threshold=0.);
    /**
     * @brief Copies another PLDABase
     */
    PLDABase(const PLDABase& other);
    /**
     * @brief Starts a new PLDABase from an existing configuration
     * object.
     * @param config HDF5 configuration file
     */
    PLDABase(bob::io::base::HDF5File& config);

    /**
     * @brief Just to virtualize the destructor
     */
    virtual ~PLDABase();

    /**
     * @brief Assigns from a different PLDABase
     */
    PLDABase& operator=(const PLDABase &other);

    /**
     * @brief Equal to.\n Even precomputed members such as \f$\alpha\f$,
     * \f$\beta\f$ and \f$\gamma_a\f$'s are compared!
     */
    bool operator==(const PLDABase& b) const;
    /**
     * @brief Not equal to.\n Defined as the negation of operator==
     */
    bool operator!=(const PLDABase& b) const;
    /**
     * @brief Similar to.\n Even precomputed members such as \f$\alpha\f$,
     * \f$\beta\f$ and \f$\gamma_a\f$'s are compared!
     */
    bool is_similar_to(const PLDABase& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief Loads data from an existing configuration object. Resets the
     * current state.
     * @param config HDF5 configuration file
     */
    void load(bob::io::base::HDF5File& config);
    /**
     * @brief Saves an existing machine to a configuration object.
     * @param config HDF5 configuration file
     */
    void save(bob::io::base::HDF5File& config) const;

    /**
     * @brief Resizes the PLDABase.
     * @warning \f$F\f$, \f$G\f$, \f$\Sigma\f$, \f$\mu\f$ and the variance
     * flooring thresholds will be reinitialized!
     * @param dim_d Dimensionality of the feature vector
     * @param dim_f Rank of \f$F\f$ (dim_d x dim_f)
     * @param dim_g Rank of \f$G\f$ (dim_d x dim_g)
     */
    void resize(const size_t dim_d, const size_t dim_f, const size_t dim_g);

    /**
     * @brief Gets the \f$F\f$ subspace/matrix of the PLDA model
     */
    const blitz::Array<double,2>& getF() const
    { return m_F; }
    /**
     * @brief Sets the \f$F\f$ subspace/matrix of the PLDA model
     */
    void setF(const blitz::Array<double,2>& F);
    /**
     * @brief Returns the current \f$F\f$ matrix/subspace of the PLDA model
     * in order to be updated.
     * @warning Use with care. Only trainers should use this function for
     * efficiency reasons.
     */
    blitz::Array<double,2>& updateF()
    { return m_F; }

    /**
     * @brief Gets the \f$G\f$ subspace/matrix of the PLDA model
     */
    const blitz::Array<double,2>& getG() const
    { return m_G; }
    /**
     * @brief Sets the \f$G\f$ subspace/matrix of the PLDA model
     */
    void setG(const blitz::Array<double,2>& G);
    /**
     * @brief Returns the current \f$G\f$ subspace/matrix of the PLDA model
     * in order to be updated.
     * @warning Use with care. Only trainers should use this function for
     * efficiency reasons.
     */
    blitz::Array<double,2>& updateG()
    { return m_G; }

    /**
     * @brief Gets the \f$\Sigma\f$ (diagonal) covariance matrix of the PLDA
     * model
     */
    const blitz::Array<double,1>& getSigma() const
    { return m_sigma; }
    /**
     * @brief Sets the \f$\Sigma\f$ (diagonal) covariance matrix of the PLDA
     * model
     */
    void setSigma(const blitz::Array<double,1>& s);
    /**
     * @brief Returns the current \f$\Sigma\f$ (diagonal) covariance matrix of
     * the PLDA model in order to be updated.
     * @warning Use with care. Only trainers should use this function for
     * efficiency reasons. Variance threshold should be applied after
     * updating \f$\Sigma\f$!
     */
    blitz::Array<double,1>& updateSigma()
    { return m_sigma; }

    /**
     * @brief Gets the \f$\mu\f$ mean vector of the PLDA model
     */
    const blitz::Array<double,1>& getMu() const
    { return m_mu; }
    /**
     * @brief Sets the \f$\mu\f$ mean vector of the PLDA model
     */
    void setMu(const blitz::Array<double,1>& mu);
    /**
     * @brief Returns the current \f$\mu\f$ mean vector of the PLDA model
     * in order to be updated.
     * @warning Use with care. Only trainers should use this function for
     * efficiency reasons.
     */
    blitz::Array<double,1>& updateMu()
    { return m_mu; }

    /**
     * @brief Gets the variance flooring threshold
     */
    double getVarianceThreshold() const
    { return m_variance_threshold; }
    /**
     * @brief Sets the variance flooring threshold
     */
    void setVarianceThreshold(const double value);
    /**
     * @brief Apply the variance flooring thresholds.
     * This method is automatically called when using setVarianceThresholds().
     * @warning It is only useful when using updateVarianceThreshods(),
     * and should mostly be done by trainers
     */
    void applyVarianceThreshold();

    /**
     * @brief Gets the feature dimensionality
     */
    size_t getDimD() const
    { return m_dim_d; }
    /**
     * @brief Gets the size/rank the \f$F\f$ subspace/matrix of the PLDA model
     */
    size_t getDimF() const
    { return m_dim_f; }
    /**
     * @brief Gets the size/rank the \f$G\f$ subspace/matrix of the PLDA model
     */
    size_t getDimG() const
    { return m_dim_g; }

    /**
     * @brief Precomputes useful values such as \f$\Sigma^{-1}\f$,
     * \f$G^{T}\Sigma^{-1}\f$, \f$\alpha\f$, \f$\beta\f$, and
     * \f$F^{T}\beta\f$.
     * @warning Previous \f$\gamma_a\f$ values and log likelihood constant
     * terms are cleared.
     */
    void precompute();
    /**
     * @brief Precomputes useful values for the log likelihood
     * \f$\log(\det(\alpha))\f$ and \f$\log(\det(\Sigma))\f$.
     */
    void precomputeLogLike();
    /**
     * @brief Gets the inverse vector/diagonal matrix of \f$\Sigma^{-1}\f$
     */
    const blitz::Array<double,1>& getISigma() const
    { return m_cache_isigma; }
    /**
     * @brief Gets the \f$\alpha\f$ matrix.
     * \f$\alpha = (Id + G^T \Sigma^{-1} G)^{-1} = \mathcal{G}\f$
     */
    const blitz::Array<double,2>& getAlpha() const
    { return m_cache_alpha; }
    /**
     * @brief Gets the \f$\beta\f$ matrix
     * \f$\beta = (\Sigma + G G^T)^{-1} = \mathcal{S} =
     *    \Sigma^{-1} - \Sigma^{-1} G \mathcal{G} G^{T} \Sigma^{-1}\f$
     */
    const blitz::Array<double,2>& getBeta() const
    { return m_cache_beta; }
    /**
     * @brief Gets the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number of
     * samples).
     * \f$\gamma_{a} = (Id + a F^T \beta F)^{-1} = \mathcal{F}_{a}\f$
     * @warning an exception is thrown if \f$\gamma_a\f$ does not exists
     */
    const blitz::Array<double,2>& getGamma(const size_t a) const;
    /**
     * @brief Gets the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number of
     * samples).
     * \f$\gamma_a = (Id + a F^T \beta F)^{-1} = \mathcal{F}_{a}\f$
     * @warning The matrix is computed if it does not already exists
     */
    const blitz::Array<double,2>& getAddGamma(const size_t a);
    /**
     * @brief Gets the \f$F^T \beta\f$ matrix
     */
    const blitz::Array<double,2>& getFtBeta() const
    { return m_cache_Ft_beta; }
    /**
     * @brief Gets the \f$G^T \Sigma^{-1}\f$ matrix
     */
    const blitz::Array<double,2>& getGtISigma() const
    { return m_cache_Gt_isigma; }
    /**
     * @brief Gets \f$\log(\det(\alpha))\f$
     */
    double getLogDetAlpha() const
    { return m_cache_logdet_alpha; }
    /**
     * @brief Gets \f$\log(\det(\Sigma))\f$
     */
    double getLogDetSigma() const
    { return m_cache_logdet_sigma; }
    /**
     * @brief Computes the log likelihood constant term for a given \f$a\f$
     * (number of samples), given the provided \f$\gamma_a\f$ matrix
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     */
    double computeLogLikeConstTerm(const size_t a,
      const blitz::Array<double,2>& gamma_a) const;
    /**
     * @brief Computes the log likelihood constant term for a given \f$a\f$
     * (number of samples)
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     * @warning: gamma_a will be computed and added if it does
     *  not already exists
     */
    double computeLogLikeConstTerm(const size_t a);
    /**
     * @brief Tells if the log likelihood constant term for a given \f$a\f$
     * (number of samples) exists
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     */
    bool hasLogLikeConstTerm(const size_t a) const
    { return (m_cache_loglike_constterm.find(a) != m_cache_loglike_constterm.end()); }
    /**
     * @brief Gets the log likelihood constant term for a given \f$a\f$
     * (number of samples)
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     * @warning an exception is thrown if the value does not exists
     */
    double getLogLikeConstTerm(const size_t a) const;
    /**
     * @brief Gets the log likelihood constant term for a given \f$a\f$
     * (number of samples)
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     * @warning The value is computed if it does not already exists
     */
    double getAddLogLikeConstTerm(const size_t a);

    /**
     * @brief Computes the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number
     * of samples) and put the result in the provided array.
     * \f$\gamma_a = (Id + a F^T \beta F)^{-1}\f$
     */
    void computeGamma(const size_t a, blitz::Array<double,2> res) const;
    /**
     * @brief Tells if the \f$\gamma_a\f$ matrix for a given a (number of
     * samples) exists.
     * \f$\gamma_a = (Id + a F^T \beta F)^{-1}\f$
     */
    bool hasGamma(const size_t a) const
    { return (m_cache_gamma.find(a) != m_cache_gamma.end()); }

    /**
     * @brief Clears the maps (\f$\gamma_a\f$ and loglike_constterm_a).
     */
    void clearMaps();

    /**
     * @brief Gets the log-likelihood of an observation, given the current model
     * and the latent variables (point estimate).\n
     * This will basically compute \f$p(x_{ij} | h_{i}, w_{ij}, \Theta)\f$\n
     * , given by \n
     * \f$\mathcal{N}(x_{ij}|[\mu + F h_{i} + G w_{ij} + \epsilon_{ij}, \Sigma])\f$\n
     * , which is in logarithm, \n
     * \f$-\frac{D}{2} log(2\pi) -\frac{1}{2} log(det(\Sigma)) -\frac{1}{2} {(x_{ij}-(\mu+F h_{i}+G w_{ij}))^{T}\Sigma^{-1}(x_{ij}-(\mu+F h_{i}+G w_{ij}))}\f$.
     */
    double computeLogLikelihoodPointEstimate(const blitz::Array<double,1>& xij,
      const blitz::Array<double,1>& hi, const blitz::Array<double,1>& wij) const;

    // Friend method declaration
    friend std::ostream& operator<<(std::ostream& os, const PLDABase& m);


  private:
    // Attributes
    size_t m_dim_d; ///< Dimensionality of the input feature vector
    size_t m_dim_f; ///< Size/rank of the \f$F\f$ subspace
    size_t m_dim_g; ///< Size/rank of the \f$G\f$ subspace
    blitz::Array<double,2> m_F; ///< \f$F\f$ subspace of the PLDA model
    blitz::Array<double,2> m_G; ///< \f$G\f$ subspace of the PLDA model
    /**
     * @brief \f$\Sigma\f$ diagonal (by assumption) covariance matrix of the
     * PLDA model
     */
    blitz::Array<double,1> m_sigma;
    blitz::Array<double,1> m_mu; ///< \f$\mu\f$ mean vector of the PLDA model
    /**
     * @brief The variance flooring thresholds, i.e. the minimum allowed
     * value of variance m_sigma in each dimension.
     * The variance will be set to this value if an attempt is made
     * to set it to a smaller value.
     */
    double m_variance_threshold;

    // Internal values very useful used to optimize the code
    blitz::Array<double,1> m_cache_isigma; ///< \f$\Sigma^{-1}\f$
    blitz::Array<double,2> m_cache_alpha; ///< \f$\alpha = (Id + G^T \Sigma^{-1} G)^{-1}\f$
    /**
     * @brief \f$\beta = (\Sigma+G G^T)^{-1} = (\Sigma^{-1} - \Sigma^{-1} G \alpha G^T \Sigma^{-1})^{-1}\f$
     */
    blitz::Array<double,2> m_cache_beta;
    std::map<size_t, blitz::Array<double,2> > m_cache_gamma; ///< \f$\gamma_{a} = (Id + a F^T \beta F)^{-1}\f$
    blitz::Array<double,2> m_cache_Ft_beta; ///< \f$F^{T} \beta \f$
    blitz::Array<double,2> m_cache_Gt_isigma; ///< \f$G^{T} \Sigma^{-1} \f$
    double m_cache_logdet_alpha; ///< \f$\log(\det(\alpha))\f$
    double m_cache_logdet_sigma; ///< \f$\log(\det(\Sigma))\f$
    /**
     * @brief \f$l_{a} = \frac{a}{2} ( -D log(2*\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     */
    std::map<size_t, double> m_cache_loglike_constterm;

    // working arrays
    mutable blitz::Array<double,1> m_tmp_d_1; ///< Cache vector of size dim_d
    mutable blitz::Array<double,1> m_tmp_d_2; ///< Cache vector of size dim_d
    mutable blitz::Array<double,2> m_tmp_d_ng_1; ///< Cache matrix of size dim_d x dim_g
    mutable blitz::Array<double,2> m_tmp_nf_nf_1; ///< Cache matrix of size dim_f x dim_f
    mutable blitz::Array<double,2> m_tmp_ng_ng_1; ///< Cache matrix of size dim_g x dim_g

    // private methods
    void resizeNoInit(const size_t dim_d, const size_t dim_f, const size_t dim_g);
    void resizeTmp();
    void initMuFGSigma();
    void precomputeISigma();
    void precomputeAlpha();
    void precomputeBeta();
    void precomputeGamma(const size_t a);
    void precomputeFtBeta();
    void precomputeGtISigma();
    void precomputeLogDetAlpha();
    void precomputeLogDetSigma();
    void precomputeLogLikeConstTerm(const size_t a);
};


/**
 * @brief This class is a container for an enrolled identity/class. It
 * contains information extracted from the enrollment samples. It should
 * be used in combination with a PLDABase instance.\n
 * References:\n
 * 1. 'A Scalable Formulation of Probabilistic Linear Discriminant Analysis:
 *     Applied to Face Recognition', Laurent El Shafey, Chris McCool,
 *     Roy Wallace, Sebastien Marcel, TPAMI'2013
 * 2. 'Probabilistic Linear Discriminant Analysis for Inference About
 *     Identity', Prince and Elder, ICCV'2007\n
 * 3. 'Probabilistic Models for Inference about Identity', Li, Fu, Mohammed,
 *     Elder and Prince, TPAMI'2012
 */
class PLDAMachine
{
  public:
    /**
     * @brief Default constructor.\n
     * Builds an otherwise invalid (No attached PLDABase) PLDAMachine.
     */
    PLDAMachine();
    /**
     * @brief Constructor, builds a new PLDAMachine, setting a
     * PLDABase.
     */
    PLDAMachine(const boost::shared_ptr<bob::learn::em::PLDABase> pldabase);
    /**
     * @brief Copies another PLDAMachine.\n Both PLDAMachine's will point
     * to the same PLDABase.
     */
    PLDAMachine(const PLDAMachine& other);
    /**
     * @brief Starts a new PLDAMachine from an existing configuration object,
     * and a PLDABase.
     */
    PLDAMachine(bob::io::base::HDF5File& config,
      const boost::shared_ptr<bob::learn::em::PLDABase> pldabase);

    /**
     * @brief Just to virtualise the destructor
     */
    virtual ~PLDAMachine();

    /**
     * @brief Assigns from a different machine
     */
    PLDAMachine& operator=(const PLDAMachine &other);

    /**
     * @brief Equal to.\n The two PLDAMachine's should have the same
     * PLDABase. Precomputed members such as \f$\gamma_a\f$'s
     * are compared!
     */
    bool operator==(const PLDAMachine& b) const;
    /**
     * @brief Not equal to.\n Defined as the negation of operator==
     */
    bool operator!=(const PLDAMachine& b) const;
    /**
     * @brief Equal to.\n The two PLDAMachine's should have the same
     * PLDABase. Precomputed members such as \f$\gamma_a\f$'s
     * are compared!
     */
    bool is_similar_to(const PLDAMachine& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief Loads data from an existing configuration object. Resets the
     * current state.
     */
    void load(bob::io::base::HDF5File& config);
    /**
     * @brief Saves an existing machine to a configuration object.
     */
    void save(bob::io::base::HDF5File& config) const;

    /**
     * @brief Gets the attached PLDABase
     */
    const boost::shared_ptr<PLDABase> getPLDABase() const
    { return m_plda_base; }
    /**
     * @brief Sets the attached PLDABase
     */
    void setPLDABase(const boost::shared_ptr<bob::learn::em::PLDABase> plda_base);

    /**
     * @brief Gets the feature dimensionality
     */
    size_t getDimD() const
    { if (!m_plda_base) throw std::runtime_error("No PLDABase set to this machine");
      return m_plda_base->getDimD(); }
    /**
     * @brief Gets the size/rank the \f$F\f$ subspace/matrix of the PLDA model
     */
    size_t getDimF() const
    { if (!m_plda_base) throw std::runtime_error("No PLDABase set to this machine");
      return m_plda_base->getDimF(); }
    /**
     * @brief Gets the size/rank the \f$G\f$ subspace/matrix of the PLDA model
     */
    size_t getDimG() const
    { if (!m_plda_base) throw std::runtime_error("No PLDABase set to this machine");
      return m_plda_base->getDimG(); }

    /**
     * @brief Gets the number of enrolled samples
     */
    uint64_t getNSamples() const
    { return m_n_samples; }
    /**
     * @brief Sets the number of enrolled samples
     */
    void setNSamples(const uint64_t n_samples)
    { m_n_samples = n_samples; }
    /**
     * @brief Gets the \f$A = -0.5 \sum_{i} x_{i}^T \beta x_{i}\f$ value
     */
    double getWSumXitBetaXi() const
    { return m_nh_sum_xit_beta_xi; }
    /**
     * @brief Sets the \f$A = -0.5 \sum_{i} x_{i}^T \beta x_{i}\f$ value
     */
    void setWSumXitBetaXi(const double val)
    { m_nh_sum_xit_beta_xi = val; }
    /**
     * @brief Gets the current \f$\sum_{i} F^T \beta x_{i}\f$ value
     */
    const blitz::Array<double,1>& getWeightedSum() const
    { return m_weighted_sum; }
    /**
     * @brief Sets the \f$\sum_{i} F^T \beta x_{i}\f$ value
     */
    void setWeightedSum(const blitz::Array<double,1>& weighted_sum);
    /**
     * @brief Returns the current \f$\sum_{i} F^T \beta x_{i}\f$ value
     * in order to be updated.
     * @warning Use with care. Only trainers should use this function for
     * efficiency reasons.
     */
    blitz::Array<double,1>& updateWeightedSum()
    { return m_weighted_sum; }
    /**
     * @brief Gets the log likelihood of the enrollment samples
     */
    double getLogLikelihood() const
    { return m_loglikelihood; }
    /**
     * @brief Sets the log likelihood of the enrollment samples
     */
    void setLogLikelihood(const double val)
    { m_loglikelihood = val; }

    /**
     * @brief Tells if the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number
     * of samples) exists in this machine (does not check the base machine)
     * \f$\gamma_a = (Id + a F^T \beta F)^{-1} = \mathcal{F}_{a}\f$
     */
    bool hasGamma(const size_t a) const
    { return (m_cache_gamma.find(a) != m_cache_gamma.end()); }
    /**
     * @brief Gets the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number of
     * samples) \f$\gamma_a = (Id + a F^T \beta F)^{-1} = \mathcal{F}_{a}\f$
     * Tries to find it from the base machine and then from this machine
     * @warning an exception is thrown if gamma does not exists
     */
    const blitz::Array<double,2>& getGamma(const size_t a) const;
    /**
     * @brief Gets the \f$\gamma_a\f$ matrix for a given \f$a\f$ (number of
     * samples) \f$\gamma_a = (Id + a F^T \beta F)^{-1} = \mathcal{F}_{a}\f$
     * Tries to find it from the base machine and then from this machine
     * @warning The matrix is computed if it does not already exists,
     *   and stored in this machine
     */
    const blitz::Array<double,2>& getAddGamma(const size_t a);

    /**
     * @brief Tells if the log likelihood constant term for a given \f$a\f$
     * (number of samples) exists in this machine
     * (does not check the base machine)
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     */
    bool hasLogLikeConstTerm(const size_t a) const
    { return (m_cache_loglike_constterm.find(a) != m_cache_loglike_constterm.end()); }
    /**
     * @brief Gets the log likelihood constant term for a given \f$a\f$
     * (number of samples)
     * Tries to find it from the base machine and then from this machine
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     * @warning an exception is thrown if the value does not exists
     */
    double getLogLikeConstTerm(const size_t a) const;
    /**
     * @brief Gets the log likelihood constant term for a given \f$a\f$
     * (number of samples)
     * Tries to find it from the base machine and then from this machine
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     * @warning The value is computed if it does not already exists
     */
    double getAddLogLikeConstTerm(const size_t a);

    /**
     * @brief Clears the maps (\f$\gamma_a\f$ and loglike_constterm[a]).
     */
    void clearMaps();


    /**
     * @brief Compute the log-likelihood of the given sample and (optionally)
     * the enrolled samples
     */
    double computeLogLikelihood(const blitz::Array<double,1>& sample,
      bool with_enrolled_samples=true) const;
    /**
     * @brief Compute the log-likelihood of the given samples and (optionally)
     * the enrolled samples
     */
    double computeLogLikelihood(const blitz::Array<double,2>& samples,
      bool with_enrolled_samples=true) const;

    /**
     * @brief Computes a log likelihood ratio from a 1D or 2D blitz::Array
     */
    double forward(const blitz::Array<double,1>& sample);
    double forward_(const blitz::Array<double,1>& sample);
    double forward(const blitz::Array<double,2>& samples);


  private:
    /**
     * @brief Associated PLDABase containing the model (\f$\mu\f$,
     * \f$F\f$, \f$G\f$ and \f$\Sigma\f$)
     */
    boost::shared_ptr<PLDABase> m_plda_base;
    uint64_t m_n_samples; ///< Number of enrollment samples
    /**
     * @brief Contains the value:\n
     * \f$A = -0.5 (\sum_{i} x_{i}^{T} \Sigma^{-1} x_{i} - x_{i}^T \Sigma^{-1} G \alpha G^{T} \Sigma^{-1} x_{i})\f$\n
     * \f$A = -0.5 \sum_{i} x_{i}^T \beta x_{i}\f$\n
     * used in the likelihood computation (first \f$x_{i}\f$ dependent term)
     */
    double m_nh_sum_xit_beta_xi;
    /**
     * @brief Contains the value \f$\sum_{i} F^T \beta x_{i}\f$ used in the
     * likelihood computation (for the second \f$x_{i}\f$ dependent term)
     */
    blitz::Array<double,1> m_weighted_sum;
    double m_loglikelihood; ///< Log likelihood of the enrollment samples
    /**
     * @brief \f$\gamma_a\f$ balues which are not already in the
     * PLDABase \f$\gamma_a = (Id + a F^T \beta F)^{-1}\f$
     * (depend on the number of samples \f$a\f$)
     */
    std::map<size_t, blitz::Array<double,2> > m_cache_gamma;
    /**
     * @brief Log likelihood constant terms which depend on the number of
     * samples \f$a\f$
     * \f$l_{a} = \frac{a}{2} ( -D log(2\pi) -log|\Sigma| +log|\alpha| +log|\gamma_a|)\f$
     */
    std::map<size_t, double> m_cache_loglike_constterm;


    // working arrays
    mutable blitz::Array<double,1> m_tmp_d_1; ///< Cache vector of size dim_d
    mutable blitz::Array<double,1> m_tmp_d_2; ///< Cache vector of size dim_d
    mutable blitz::Array<double,1> m_tmp_nf_1; ///< Cache vector of size dim_f
    mutable blitz::Array<double,1> m_tmp_nf_2; ///< Cache vector of size dim_f
    mutable blitz::Array<double,2> m_tmp_nf_nf_1; ///< Cache vector of size dim_f dim_f

    /**
     * @brief Resizes the PLDAMachine
     */
    void resize(const size_t dim_d, const size_t dim_f, const size_t dim_g);
    /**
     * @brief Resize working arrays
     */
    void resizeTmp();
};

} } } // namespaces

#endif // BOB_LEARN_EM_PLDAMACHINE_H
