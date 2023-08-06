/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 May 23:52:08 2013 CEST
 *
 * @brief Implementation of the cross entropy loss function
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <bob.learn.mlp/cross_entropy.h>

namespace bob { namespace learn { namespace mlp {

  CrossEntropyLoss::CrossEntropyLoss(boost::shared_ptr<bob::learn::activation::Activation> actfun)
    : m_actfun(actfun),
      m_logistic_activation(m_actfun->unique_identifier() == "bob.learn.activation.Activation.Logistic") {}

  CrossEntropyLoss::~CrossEntropyLoss() {}

  double CrossEntropyLoss::f (double output, double target) const {
    return - (target * std::log(output)) - ((1-target)*std::log(1-output));
  }

  double CrossEntropyLoss::f_prime (double output, double target) const {
    return (output-target) / (output * (1-output));
  }

  double CrossEntropyLoss::error (double output, double target) const {
    return m_logistic_activation? (output - target) : m_actfun->f_prime_from_f(output) * f_prime(output, target);
  }

  std::string CrossEntropyLoss::str() const {
    std::string retval = "J = - target*log(output) - (1-target)*log(1-output) (cross-entropy loss)";
    if (m_logistic_activation) retval += " [+ logistic activation]";
    else retval += " [+ unknown activation]";
    return retval;
  }

}}}
