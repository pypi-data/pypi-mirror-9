/**
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @date Fri 31 May 18:07:53 2013
 *
 * @brief Implementation of the squared error cost function
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <cmath>

#include <bob.learn.mlp/square_error.h>

namespace bob { namespace learn { namespace mlp {

  SquareError::SquareError(boost::shared_ptr<bob::learn::activation::Activation> actfun):
  m_actfun(actfun) {}

  SquareError::~SquareError() {}

  double SquareError::f (double output, double target) const {
    return 0.5 * std::pow(output-target, 2);
  }

  double SquareError::f_prime (double output, double target) const {
    return output - target;
  }

  double SquareError::error (double output, double target) const {
    return m_actfun->f_prime_from_f(output) * f_prime(output, target);
  }

  std::string SquareError::str() const {
    return "J = (output-target)^2 / 2 (square error)";
  }

}}}
