/**
 * @author Laurent El Shafey <laurent.el-shafey@idiap.ch>
 * @date Sat Sep 1 19:16:00 2012 +0100
 *
 * @brief Linear Logistic Regression trainer using a conjugate gradient
 * approach.
 *
 * Copyright (C) Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_LINEAR_LOGREG_H
#define BOB_LEARN_LINEAR_LOGREG_H

#include <boost/format.hpp>
#include <bob.learn.linear/machine.h>

namespace bob { namespace learn { namespace linear {

  /**
   * Trains a Linear Logistic Regression model using a conjugate gradient
   * approach. The objective function is normalized with respect to the
   * proportion of elements in class 1 to the ones in class 2, and
   * then weighted with respect to a given synthetic prior, P, as this is
   * done in the FoCal toolkit.
   * References:
   *   1/ "A comparison of numerical optimizers for logistic regression",
   *   T. Minka, Unpublished draft, 2003 (revision in 2007),
   *   http://research.microsoft.com/en-us/um/people/minka/papers/logreg/
   *   2/ FoCal, http://www.dsp.sun.ac.za/~nbrummer/focal/
   */
  class CGLogRegTrainer {

    public: //api

      /**
       * Default constructor.
       * @param prior The synthetic prior. It should be in the range ]0.,1.[
       * @param convergence_threshold The threshold to detect the convergence
       *           of the iterative conjugate gradient algorithm
       * @param max_iterations The maximum number of iterations of the
       *           iterative conjugate gradient algorithm (0 <-> infinity)
       * @param lambda The regularization factor
       * @param mean_std_norm Compute mean and standard deviation in training
       *           data and set the input_subtract and input_divide parameters
       *           of the resulting machine
       */
      CGLogRegTrainer(const double prior=0.5,
        const double convergence_threshold=1e-5,
        const size_t max_iterations=10000,
        const double lambda=0.,
        const bool mean_std_norm=false);

      /**
       * Copy constructor
       */
      CGLogRegTrainer(const CGLogRegTrainer& other);

      /**
       * Destructor
       */
      virtual ~CGLogRegTrainer();

      /**
       * Assignment operator
       */
      CGLogRegTrainer& operator=(const CGLogRegTrainer& other);

      /**
       * @brief Equal to
       */
      bool operator==(const CGLogRegTrainer& b) const;
      /**
       * @brief Not equal to
       */
      bool operator!=(const CGLogRegTrainer& b) const;

      /**
       * Getters
       */
      double getPrior() const { return m_prior; }
      double getConvergenceThreshold() const { return m_convergence_threshold; }
      size_t getMaxIterations() const { return m_max_iterations; }
      double getLambda() const { return m_lambda; }
      bool getNorm() const { return m_mean_std_norm; }

      /**
       * Setters
       */
      void setPrior(const double prior)
      { if(prior<=0. || prior>=1.)
        {
          boost::format m("Prior (%f) not in the range ]0,1[.");
          m % prior;
          throw std::runtime_error(m.str());
        }
        m_prior = prior; }
      void setConvergenceThreshold(const double convergence_threshold)
      { m_convergence_threshold = convergence_threshold; }
      void setMaxIterations(const size_t max_iterations)
      { m_max_iterations = max_iterations; }
      void setLambda(const double lambda)
      { m_lambda = lambda; }
      void setNorm(const bool mean_std_norm) { m_mean_std_norm = mean_std_norm; }

      /**
       * Trains the LinearMachine to perform Linear Logistic Regression
       */
      virtual void train(Machine& machine,
          const blitz::Array<double,2>& negatives,
          const blitz::Array<double,2>& positives) const;

    private:
      // Attributes
      double m_prior;
      double m_convergence_threshold;
      size_t m_max_iterations;
      double m_lambda;
      bool m_mean_std_norm;
  };

}}}

#endif /* BOB_LEARN_LINEAR_LOGREG_H */
