/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 May 15:08:46 2013
 *
 * @brief Implements the concept of a 'cost' function for MLP training
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_COST_H
#define BOB_LEARN_MLP_COST_H

#include <string>
#include <boost/shared_ptr.hpp>

namespace bob { namespace learn { namespace mlp {

  /**
   * Base class for cost function used for Linear machine or MLP training
   * from this one.
   */
  class Cost {

    public:

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
      virtual double f (double output, double target) const =0;

      /**
       * Computes the derivative of the cost w.r.t. output.
       *
       * @param output Real output from the linear machine or MLP
       *
       * @param target Target output you are training to achieve
       *
       * @return The calculated error
       */
      virtual double f_prime (double output, double target) const =0;

      /**
       * Computes the back-propagated error for a given MLP <b>output</b>
       * layer, given its activation function and outputs - i.e., the
       * error back-propagated through the last layer neuron up to the
       * synapse connecting the last hidden layer to the output layer.
       *
       * This entry point allows for optimization in the calculation of the
       * back-propagated errors in cases where there is a possibility of
       * mathematical simplification when using a certain combination of
       * cost-function and activation. For example, using a ML-cost and a
       * logistic activation function.
       *
       * @param output Real output from the linear machine or MLP
       *
       * @param target Target output you are training to achieve
       *
       * @return The calculated error, backpropagated to before the output
       * neuron.
       */
      virtual double error (double output, double target) const =0;

      /**
       * Returns a stringified representation for this Activation function
       */
      virtual std::string str() const =0;

  };

}}}

#endif /* BOB_LEARN_MLP_COST_H */
