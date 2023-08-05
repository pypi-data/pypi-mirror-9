/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 May 15:08:46 2013
 *
 * @brief Implements the Square Error Cost function
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_SQUAREERROR_H
#define BOB_LEARN_MLP_SQUAREERROR_H

#include <bob.learn.mlp/cost.h>
#include <bob.learn.activation/Activation.h>

namespace bob { namespace learn { namespace mlp {

  /**
   * Calculates the Square-Error between output and target. The square error is
   * defined as follows:
   *
   * \f[
   *    J = \frac{(\hat{y} - y)^2}{2}
   * \f]
   *
   * where \f$\hat{y}\f$ is the output estimated by your machine and \f$y\f$ is
   * the expected output.
   */
  class SquareError: public Cost {

    public:

      /**
       * Builds a SquareError functor with an existing activation function.
       */
      SquareError(boost::shared_ptr<bob::learn::activation::Activation> actfun);

      /**
       * Virtualized destructor
       */
      virtual ~SquareError();

      /**
       * Computes cost, given the current output of the linear machine or MLP
       * and the expected output.
       *
       * @param output Real output from the linear machine or MLP
       *
       * @param target Target output you are training to achieve
       *
       * @return The cost
       */
      virtual double f (double output, double target) const;

      /**
       * Computes the derivative of the cost w.r.t. output.
       *
       * @param output Real output from the linear machine or MLP
       *
       * @param target Target output you are training to achieve
       *
       * @return The calculated error
       */
      virtual double f_prime (double output, double target) const;

      /**
       * Computes the back-propagated errors for a given MLP <b>output</b>
       * layer, given its activation function and activation values - i.e., the
       * error back-propagated through the last layer neurons up to the
       * synapses connecting the last hidden layer to the output layer.
       *
       * This entry point allows for optimization in the calculation of the
       * back-propagated errors in cases where there is a possibility of
       * mathematical simplification when using a certain combination of
       * cost-function and activation. For example, using a ML-cost and a
       * logistic activation function.
       *
       * @param output Real output from the linear machine or MLP
       * @param target Target output you are training to achieve
       *
       * @return The calculated error, backpropagated to before the output
       * neuron.
       */
      virtual double error (double output, double target) const;

      /**
       * Returns a stringified representation for this Cost function
       */
      virtual std::string str() const;

    private: //representation

      boost::shared_ptr<bob::learn::activation::Activation> m_actfun; //act. function

  };

}}}

#endif /* BOB_LEARN_MLP_SQUAREERROR_H */
