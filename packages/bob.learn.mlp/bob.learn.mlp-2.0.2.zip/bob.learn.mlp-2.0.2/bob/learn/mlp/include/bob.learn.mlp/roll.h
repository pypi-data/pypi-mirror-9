/**
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 * @date Tue Jun 25 18:48:20 CEST 2013
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_ROLL_H
#define BOB_LEARN_MLP_ROLL_H

#include <vector>
#include <blitz/array.h>

#include <bob.learn.mlp/machine.h>

namespace bob { namespace learn { namespace mlp {

namespace detail {
  /**
   * @brief Returns the number of parameters (weights and biases) in an
   * MLP.
   */
  int getNbParameters(const bob::learn::mlp::Machine& machine);
  /**
   * @brief Returns the number of parameters (weights and biases).
   */
  int getNbParameters(const std::vector<blitz::Array<double,2> >& weights,
    const std::vector<blitz::Array<double,1> >& biases);
}

/**
 * @brief Puts the parameters (weights and biases) of the machine in a
 * large single 1D vector
 */
void unroll(const bob::learn::mlp::Machine& machine, blitz::Array<double,1>& vec);
/**
 * @brief Puts the parameters (weights and biases) in a large single 1D vector
 */
void unroll(const std::vector<blitz::Array<double,2> >& weights,
  const std::vector<blitz::Array<double,1> >& biases,
  blitz::Array<double,1>& vec);

/**
 * @brief Sets the parameters (weights and biases) of the machine from a
 * large single 1D vector
 */
void roll(bob::learn::mlp::Machine& machine, const blitz::Array<double,1>& vec);

/**
 * @brief Sets the parameters (weights and biases) from a
 * large single 1D vector
 */
void roll(std::vector<blitz::Array<double,2> >& weights,
  std::vector<blitz::Array<double,1> >& biases,
  const blitz::Array<double,1>& vec);

}}}

#endif /* BOB_LEARN_MLP_ROLL_H */
