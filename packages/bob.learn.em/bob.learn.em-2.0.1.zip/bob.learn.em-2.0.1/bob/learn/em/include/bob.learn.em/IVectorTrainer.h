/**
 * @date Sat Mar 30 20:55:00 2013 +0200
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_EM_IVECTOR_TRAINER_H
#define BOB_LEARN_EM_IVECTOR_TRAINER_H

#include <blitz/array.h>
#include <bob.learn.em/IVectorMachine.h>
#include <bob.learn.em/GMMStats.h>
#include <boost/shared_ptr.hpp>
#include <vector>
#include <bob.core/array_copy.h>
#include <boost/random.hpp>

#include <boost/random/mersenne_twister.hpp>

namespace bob { namespace learn { namespace em {

/**
 * @brief An IVectorTrainer to learn a Total Variability subspace \f$T\f$
 *  (and eventually a covariance matrix \f$\Sigma\f$).\n
 * Reference:\n
 * "Front-End Factor Analysis For Speaker Verification",
 *    N. Dehak, P. Kenny, R. Dehak, P. Dumouchel, P. Ouellet,
 *   IEEE Trans. on Audio, Speech and Language Processing
 */
class IVectorTrainer
{
  public:
    /**
     * @brief Default constructor. Builds an IVectorTrainer
     */
    IVectorTrainer(const bool update_sigma=false);

    /**
     * @brief Copy constructor
     */
    IVectorTrainer(const IVectorTrainer& other);

    /**
     * @brief Destructor
     */
    virtual ~IVectorTrainer();

    /**
     * @brief Initialization before the EM loop
     */
    virtual void initialize(bob::learn::em::IVectorMachine& ivector);

    /**
     * @brief Calculates statistics across the dataset,
     * and saves these as:
     * - m_acc_Nij_wij2
     * - m_acc_Fnormij_wij
     * - m_acc_Nij (only if update_sigma is enabled)
     * - m_acc_Snormij (only if update_sigma is enabled)
     *
     * These statistics will be used in the mStep() that follows.
     */
    virtual void eStep(bob::learn::em::IVectorMachine& ivector,
      const std::vector<bob::learn::em::GMMStats>& data);

    /**
     * @brief Maximisation step: Update the Total Variability matrix \f$T\f$
     * and \f$\Sigma\f$ if update_sigma is enabled.
     */
    virtual void mStep(bob::learn::em::IVectorMachine& ivector);


    /**
     * @brief Assigns from a different IVectorTrainer
     */
    IVectorTrainer& operator=(const IVectorTrainer &other);

    /**
     * @brief Equal to
     */
    bool operator==(const IVectorTrainer& b) const;

    /**
     * @brief Not equal to
     */
    bool operator!=(const IVectorTrainer& b) const;

    /**
     * @brief Similar to
     */
    bool is_similar_to(const IVectorTrainer& b, const double r_epsilon=1e-5,
      const double a_epsilon=1e-8) const;

    /**
     * @brief Getters for the accumulators
     */
    const blitz::Array<double,3>& getAccNijWij2() const
    { return m_acc_Nij_wij2; }
    const blitz::Array<double,3>& getAccFnormijWij() const
    { return m_acc_Fnormij_wij; }
    const blitz::Array<double,1>& getAccNij() const
    { return m_acc_Nij; }
    const blitz::Array<double,2>& getAccSnormij() const
    { return m_acc_Snormij; }

    /**
     * @brief Setters for the accumulators, Very useful if the e-Step needs
     * to be parallelized.
     */
    void setAccNijWij2(const blitz::Array<double,3>& acc)
    { bob::core::array::assertSameShape(acc, m_acc_Nij_wij2);
      m_acc_Nij_wij2 = acc; }
    void setAccFnormijWij(const blitz::Array<double,3>& acc)
    { bob::core::array::assertSameShape(acc, m_acc_Fnormij_wij);
      m_acc_Fnormij_wij = acc; }
    void setAccNij(const blitz::Array<double,1>& acc)
    { bob::core::array::assertSameShape(acc, m_acc_Nij);
      m_acc_Nij = acc; }
    void setAccSnormij(const blitz::Array<double,2>& acc)
    { bob::core::array::assertSameShape(acc, m_acc_Snormij);
      m_acc_Snormij = acc; }

    void setRng(boost::shared_ptr<boost::mt19937> rng){
      m_rng = rng;
    };

  protected:
    // Attributes
    bool m_update_sigma;

    // Acccumulators
    blitz::Array<double,3> m_acc_Nij_wij2;
    blitz::Array<double,3> m_acc_Fnormij_wij;
    blitz::Array<double,1> m_acc_Nij;
    blitz::Array<double,2> m_acc_Snormij;

    // Working arrays
    mutable blitz::Array<double,1> m_tmp_wij;
    mutable blitz::Array<double,2> m_tmp_wij2;
    mutable blitz::Array<double,1> m_tmp_d1;
    mutable blitz::Array<double,1> m_tmp_t1;
    mutable blitz::Array<double,2> m_tmp_dd1;
    mutable blitz::Array<double,2> m_tmp_dt1;
    mutable blitz::Array<double,2> m_tmp_tt1;
    mutable blitz::Array<double,2> m_tmp_tt2;

    /**
     * @brief The random number generator for the inialization
     */
    boost::shared_ptr<boost::mt19937> m_rng;
};

} } } // namespaces

#endif // BOB_LEARN_EM_IVECTOR_TRAINER_H
