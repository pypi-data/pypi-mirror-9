/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 May 15:08:46 2013
 *
 * @brief Implements the Cross Entropy Loss function
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_CROSSENTROPYLOSS_H
#define BOB_LEARN_MLP_CROSSENTROPYLOSS_H

#include <bob.learn.mlp/cost.h>
#include <bob.learn.activation/Activation.h>

namespace bob { namespace learn { namespace mlp {

  /**
   * Calculates the Cross-Entropy Loss between output and target. The cross
   * entropy loss is defined as follows:
   *
   * \f[
   *    J = - y \cdot \log{(\hat{y})} - (1-y) \log{(1-\hat{y})}
   * \f]
   *
   * where \f$\hat{y}\f$ is the output estimated by your machine and \f$y\f$ is
   * the expected output.
   */
  class CrossEntropyLoss: public Cost {

    public:

      /**
       * Constructor
       *
       * @param actfun Sets the underlying activation function used for error
       * calculation. A special case is foreseen for using this loss function
       * with a logistic activation. In this case, a mathematical
       * simplification is possible in which error() can benefit increasing the
       * numerical stability of the training process. The simplification goes
       * as follows:
       *
       * \f[
       *    b = \delta \cdot \varphi'(z)
       * \f]
       *
       * But, for the CrossEntropyLoss:
       *
       * \f[
       *    \delta = \frac{\hat{y} - y}{\hat{y}(1 - \hat{y}}
       * \f]
       *
       * and \f$\varphi'(z) = \hat{y} - (1 - \hat{y})\f$, so:
       *
       * \f[
       *    b = \hat{y} - y
       * \f]
       */
      CrossEntropyLoss(boost::shared_ptr<bob::learn::activation::Activation> actfun);

      /**
       * Virtualized destructor
       */
      virtual ~CrossEntropyLoss();

      /**
       * Tells if this CrossEntropyLoss is set to operate together with a
       * bob::learn::activation::LogisticActivation.
       */
      bool logistic_activation() const { return m_logistic_activation; }

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
      bool m_logistic_activation; ///< if 'true', simplify backprop_error()

  };

}}}

#endif /* BOB_LEARN_MLP_CROSSENTROPYLOSS_H */
