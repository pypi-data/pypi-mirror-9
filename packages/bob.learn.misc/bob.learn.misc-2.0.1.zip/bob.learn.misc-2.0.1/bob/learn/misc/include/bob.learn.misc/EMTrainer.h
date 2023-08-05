/**
 * @date Tue Jan 18 17:07:26 2011 +0100
 * @author André Anjos <andre.anjos@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief Base class for Expectation-Maximization-like algorithms
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */


#ifndef BOB_LEARN_MISC_EMTRAINER_H
#define BOB_LEARN_MISC_EMTRAINER_H

#include <bob.learn.misc/Trainer.h>

#include <limits>
#include <bob.core/check.h>
#include <bob.core/logging.h>
#include <boost/shared_ptr.hpp>
#include <boost/random.hpp>


namespace bob { namespace learn { namespace misc {
  /**
   * @brief This class implements the general Expectation-maximization algorithm.
   * @details See Section 9.3 of Bishop, "Pattern recognition and machine learning", 2006
   * Derived classes must implement the initialize(), eStep(), mStep() and finalize() methods.
   */
  template<class T_machine, class T_sampler>
  class EMTrainer: virtual public Trainer<T_machine, T_sampler>
  {
  public:
    /**
     * @brief Destructor
     */
    virtual ~EMTrainer() {}

    /**
     * @brief Assignment operator
     */
    EMTrainer& operator=(const EMTrainer& other)
    {
      if(this != &other)
      {
        m_compute_likelihood = other.m_compute_likelihood;
        m_convergence_threshold = other.m_convergence_threshold;
        m_max_iterations = other.m_max_iterations;
        m_rng = other.m_rng;
      }
      return *this;
    }

    /**
     * @brief Equal to
     */
    bool operator==(const EMTrainer& b) const {
      return m_compute_likelihood == b.m_compute_likelihood &&
             m_convergence_threshold == b.m_convergence_threshold &&
             m_max_iterations == b.m_max_iterations &&
             *m_rng == *(b.m_rng);
    }

    /**
     * @brief Not equal to
     */
    bool operator!=(const EMTrainer& b) const
    { return !(this->operator==(b)); }

    /**
     * @brief Similarity operator
     */
    bool is_similar_to(const EMTrainer& b,
      const double r_epsilon=1e-5, const double a_epsilon=1e-8) const
    {
      return m_compute_likelihood == b.m_compute_likelihood &&
             bob::core::isClose(m_convergence_threshold, b.m_convergence_threshold, r_epsilon, a_epsilon) &&
             m_max_iterations == b.m_max_iterations &&
             *m_rng == *(b.m_rng);
    }

    /**
     * @brief The name for this trainer
     */
    virtual std::string name() const { return "EMTrainer"; }

    /**
     * @brief The main method to train a machine using an EM-based algorithm
     */
    virtual void train(T_machine& machine, const T_sampler& sampler)
    {
      bob::core::info << "# " << name() << ":" << std::endl;

      /*
      // Check that the machine and dataset have the same feature dimensionality
      if (!checkForDimensionalityMatch())
      {
        bob::core::error << "mismatch in dimensionality of dataset and machine" << endl;
        return false;
      }
      */

      // Initialization
      initialize(machine, sampler);
      // Do the Expectation-Maximization algorithm
      double average_output_previous;
      double average_output = - std::numeric_limits<double>::max();

      // - eStep
      eStep(machine, sampler);

      if(m_compute_likelihood)
        average_output = computeLikelihood(machine);

      // - iterates...
      for(size_t iter=0; ; ++iter) {

        // - saves average output from last iteration
        average_output_previous = average_output;

        // - mStep
        mStep(machine, sampler);

        // - eStep
        eStep(machine, sampler);

        // - Computes log likelihood if required
        if(m_compute_likelihood) {
          average_output = computeLikelihood(machine);

          bob::core::info << "# Iteration " << iter+1 << ": "
            << average_output_previous << " -> "
            << average_output << std::endl;

          // - Terminates if converged (and likelihood computation is set)
          if(fabs((average_output_previous - average_output)/average_output_previous) <= m_convergence_threshold) {
            bob::core::info << "# EM terminated: likelihood converged" << std::endl;
            break;
          }
        }
        else
          bob::core::info << "# Iteration " << iter+1 << std::endl;

        // - Terminates if maximum number of iterations has been reached
        if(m_max_iterations > 0 && iter+1 >= m_max_iterations) {
          bob::core::info << "# EM terminated: maximum number of iterations reached." << std::endl;
          break;
        }
      }

      // Finalization
      finalize(machine, sampler);
    }

    /**
     * @brief This method is called before the EM algorithm to initialize
     * variables.
     */
    virtual void initialize(T_machine& machine, const T_sampler& sampler) = 0;

    /**
     * @brief Computes the hidden variable distribution (or the sufficient
     * statistics) given the Machine parameters.
     */
    virtual void eStep(T_machine& machine, const T_sampler& sampler) = 0;

    /**
     * @brief Updates the Machine parameters given the hidden variable
     * distribution (or the sufficient statistics).
     */
    virtual void mStep(T_machine& machine, const T_sampler& sampler) = 0;

    /**
     * @return The average output of the Machine across the dataset.
     *     The EM algorithm will terminate once the change in average_output
     *     is less than the convergence_threshold.
     */
    virtual double computeLikelihood(T_machine& machine) = 0;

    /**
     * @brief This method is called after the EM-loop
     */
    virtual void finalize(T_machine& machine, const T_sampler& sampler) = 0;

    /**
     * @brief Sets whether the likelihood is computed or not at each iteration
     */
    void setComputeLikelihood(bool compute)
    { m_compute_likelihood = compute; }

    /**
     * @brief Tells whether the likelihood is computed or not at each iteration
     */
    bool getComputeLikelihood() const
    { return m_compute_likelihood; }

    /**
     * @brief Sets the convergence threshold
     */
    void setConvergenceThreshold(double threshold)
    { m_convergence_threshold = threshold; }

    /**
     * @brief Gets the convergence threshold
     */
    double getConvergenceThreshold() const
    { return m_convergence_threshold; }

    /**
     * @brief Sets the maximum number of EM iterations
     */
    void setMaxIterations(size_t max_iterations)
    { m_max_iterations = max_iterations; }

    /**
     * @brief Gets the maximum number of EM iterations
     */
    size_t getMaxIterations() const
    { return m_max_iterations; }

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

  protected:
    bool m_compute_likelihood; ///< whether lilelihood is computed during the EM loop or not
    double m_convergence_threshold; ///< convergence threshold
    size_t m_max_iterations; ///< maximum number of EM iterations
    boost::shared_ptr<boost::mt19937> m_rng; ///< The random number generator for the inialization

    /**
     * @brief Protected constructor to be called in the constructor of derived
     * classes
     */
    EMTrainer(const double convergence_threshold = 0.001,
        const size_t max_iterations = 10, const bool compute_likelihood = true):
      m_compute_likelihood(compute_likelihood),
      m_convergence_threshold(convergence_threshold),
      m_max_iterations(max_iterations),
      m_rng(new boost::mt19937())
    {
    }
  };

} } } // namespaces

#endif // BOB_LEARN_MISC_EMTRAINER_H
