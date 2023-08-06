/**
 * @date Sat Mar 30 20:55:00 2013 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_EM_IVECTOR_MACHINE_H
#define BOB_LEARN_EM_IVECTOR_MACHINE_H

#include <blitz/array.h>
#include <bob.learn.em/GMMMachine.h>
#include <bob.learn.em/GMMStats.h>
#include <bob.io.base/HDF5File.h>

namespace bob { namespace learn { namespace em {

/**
 * @brief An IVectorMachine consists of a Total Variability subspace \f$T\f$
 *   and allows the extraction of IVector\n
 * Reference:\n
 * "Front-End Factor Analysis For Speaker Verification",
 *    N. Dehak, P. Kenny, R. Dehak, P. Dumouchel, P. Ouellet,
 *   IEEE Trans. on Audio, Speech and Language Processing
 */
class IVectorMachine
{
  public:
    /**
     * @brief Default constructor. Builds an IVectorMachine.
     * The Universal Background Model and the matrices \f$T\f$ and
     * \f$diag(\Sigma)\f$ are not initialized.
     */
    IVectorMachine();

    /**
     * @brief Constructor. Builds a new IVectorMachine.
     * The Universal Background Model and the matrices \f$T\f$ and
     * \f$diag(\Sigma)\f$ are not initialized.
     *
     * @param ubm The Universal Background Model
     * @param rt size of \f$T\f$ (CD x rt)
     * @param variance_threshold variance flooring threshold for the
     *   \f$\Sigma\f$ (diagonal) matrix
     * @warning rt SHOULD BE >= 1.
     */
    IVectorMachine(const boost::shared_ptr<bob::learn::em::GMMMachine> ubm,
      const size_t rt=1, const double variance_threshold=1e-10);

    /**
     * @brief Copy constructor
     */
    IVectorMachine(const IVectorMachine& other);

    /**
     * @brief Starts a new IVectorMachine from an existing Configuration object.
     */
    IVectorMachine(bob::io::base::HDF5File& config);

    /**
     * @brief Destructor
     */
    virtual ~IVectorMachine();

    /**
     * @brief Assigns from a different IVectorMachine
     */
    IVectorMachine& operator=(const IVectorMachine &other);

    /**
     * @brief Equal to
     */
    bool operator==(const IVectorMachine& b) const;

    /**
     * @brief Not equal to
     */
    bool operator!=(const IVectorMachine& b) const;

    /**
     * @brief Similar to
     */
    bool is_similar_to(const IVectorMachine& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief Saves model to an HDF5 file
     */
    void save(bob::io::base::HDF5File& config) const;

    /**
     * @brief Loads data from an existing configuration object. Resets
     * the current state.
     */
    void load(bob::io::base::HDF5File& config);

    /**
     * @brief Returns the UBM
     */
    const boost::shared_ptr<bob::learn::em::GMMMachine> getUbm() const
    { return m_ubm; }

    /**
     * @brief Returns the \f$T\f$ matrix
     */
    const blitz::Array<double,2>& getT() const
    { return m_T; }

    /**
     * @brief Returns the \f$\Sigma\f$ (diagonal) matrix as a 1D array
     */
    const blitz::Array<double,1>& getSigma() const
    { return m_sigma; }

    /**
     * @brief Gets the variance flooring threshold
     */
    const double getVarianceThreshold() const
    { return m_variance_threshold; }

    /**
     * @brief Returns the number of Gaussian components C.
     * @warning An exception is thrown if no Universal Background Model has
     *   been set yet.
     */
    const size_t getNGaussians() const
    { return m_ubm->getNGaussians(); }

    /**
     * @brief Returns the feature dimensionality D.
     * @warning An exception is thrown if no Universal Background Model has
     *   been set yet.
     */
    const size_t getNInputs() const
    { return m_ubm->getNInputs(); }

    /**
     * @brief Returns the supervector length CD.
     * (CxD: Number of Gaussian components by the feature dimensionality)
     * @warning An exception is thrown if no Universal Background Model has
     *   been set yet.
     */
    const size_t getSupervectorLength() const
    { return m_ubm->getNGaussians()*m_ubm->getNInputs(); }

    /**
     * @brief Returns the size/rank rt of the \f$T\f$ matrix
     */
    const size_t getDimRt() const
    { return m_rt; }

    /**
     * @brief Resets the dimensionality of the subspace \f$T\f$.
     * \f$T\f$ is hence uninitialized.
     */
    void resize(const size_t rt);

    /**
     * @brief Returns the \f$T\f$ matrix in order to update it.
     * @warning Should only be used by the trainer for efficiency reason,
     *   or for testing purpose.
     */
    blitz::Array<double,2>& updateT()
    { return m_T; }

    /**
     * @brief Returns the \f$\Sigma\f$ (diagonal) matrix in order to update it.
     * @warning Should only be used by the trainer for efficiency reason,
     *   or for testing purpose.
     */
    blitz::Array<double,1>& updateSigma()
    { return m_sigma; }

    /**
     * @brief Sets (the mean supervector of) the Universal Background Model.
     * \f$T\f$ and \f$\Sigma\f$ are uninitialized in case of dimensions update (C or D)
     */
    void setUbm(const boost::shared_ptr<bob::learn::em::GMMMachine> ubm);

    /**
     * @brief Sets the \f$T\f$ matrix
     */
    void setT(const blitz::Array<double,2>& T);

    /**
     * @brief Sets the \f$\Sigma\f$ (diagonal) matrix
     */
    void setSigma(const blitz::Array<double,1>& sigma);

    /**
     * @brief Set the variance flooring threshold
     */
    void setVarianceThreshold(const double value);

    /**
     * @brief Update arrays in cache
     * @warning It is only useful when using updateT() or updateSigma()
     * and should mostly be done by trainers
     */
    void precompute();

    /**
     * @brief Computes \f$(Id + \sum_{c=1}^{C} N_{i,j,c} T^{T} \Sigma_{c}^{-1} T)\f$
     * @warning No check is perform
     */
    void computeIdTtSigmaInvT(const bob::learn::em::GMMStats& input, blitz::Array<double,2>& output) const;

    /**
     * @brief Computes \f$T^{T} \Sigma^{-1} \sum_{c=1}^{C} (F_c - N_c ubmmean_{c})\f$
     * @warning No check is perform
     */
    void computeTtSigmaInvFnorm(const bob::learn::em::GMMStats& input, blitz::Array<double,1>& output) const;

    /**
     * @brief Extracts an ivector from the input GMM statistics
     *
     * @param input GMM statistics to be used by the machine
     * @param output I-vector computed by the machine
     */
    void forward(const bob::learn::em::GMMStats& input, blitz::Array<double,1>& output) const;

    /**
     * @brief Extracts an ivector from the input GMM statistics
     *
     * @param input GMM statistics to be used by the machine
     * @param output I-vector computed by the machine
     * @warning Inputs are NOT checked
     */
    void forward_(const bob::learn::em::GMMStats& input, blitz::Array<double,1>& output) const;

  private:
    /**
     * @brief Apply the variance flooring thresholds.
     * This method is called when using setVarianceThresholds()
     */
    void applyVarianceThreshold();

    /**
     * @brief Resize cache
     */
    void resizeCache();
    /**
     * @brief Resize working arrays
     */
    void resizeTmp();
    /**
     * @brief Resize cache and working arrays before updating cache
     */
    void resizePrecompute();

    // UBM
    boost::shared_ptr<bob::learn::em::GMMMachine> m_ubm;

    // dimensionality
    size_t m_rt; ///< size of \f$T\f$ (CD x rt)

    ///< \f$T\f$ and \f$Sigma\f$ matrices.
    ///< \f$Sigma\f$ is assumed to be diagonal, and only the diagonal is stored
    blitz::Array<double,2> m_T; ///< The total variability matrix \f$T\f$
    blitz::Array<double,1> m_sigma; ///< The diagonal covariance matrix \f$\Sigma\f$
    double m_variance_threshold; ///< The variance flooring threshold

    blitz::Array<double,3> m_cache_Tct_sigmacInv;
    blitz::Array<double,3> m_cache_Tct_sigmacInv_Tc;

    mutable blitz::Array<double,1> m_tmp_d;
    mutable blitz::Array<double,1> m_tmp_t1;
    mutable blitz::Array<double,1> m_tmp_t2;
    mutable blitz::Array<double,2> m_tmp_tt;
};

} } } // namespaces

#endif // BOB_LEARN_EM_IVECTOR_MACHINE_H
