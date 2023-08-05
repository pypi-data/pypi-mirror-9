/**
 * @date Tue May 14 12:04:51 CEST 2013
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <algorithm>
#include <bob.core/assert.h>
#include <bob.core/check.h>
#include <bob.math/linear.h>

#include <bob.learn.mlp/trainer.h>

bob::learn::mlp::Trainer::Trainer(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost):
  m_batch_size(batch_size),
  m_cost(cost),
  m_train_bias(true),
  m_H(0), ///< handy!
  m_deriv(1),
  m_deriv_bias(1),
  m_error(1),
  m_output(1)
{
  m_deriv[0].reference(blitz::Array<double,2>(0,0));
  m_deriv_bias[0].reference(blitz::Array<double,1>(0));
  m_error[0].reference(blitz::Array<double,2>(0,0));
  m_output[0].reference(blitz::Array<double,2>(0,0));
  reset();
}

bob::learn::mlp::Trainer::Trainer(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost,
    const bob::learn::mlp::Machine& machine):
  m_batch_size(batch_size),
  m_cost(cost),
  m_train_bias(true),
  m_H(machine.numOfHiddenLayers()), ///< handy!
  m_deriv(m_H + 1),
  m_deriv_bias(m_H + 1),
  m_error(m_H + 1),
  m_output(m_H + 1)
{
  initialize(machine);
}

bob::learn::mlp::Trainer::Trainer(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost,
    const bob::learn::mlp::Machine& machine,
    bool train_biases):
  m_batch_size(batch_size),
  m_cost(cost),
  m_train_bias(train_biases),
  m_H(machine.numOfHiddenLayers()), ///< handy!
  m_deriv(m_H + 1),
  m_deriv_bias(m_H + 1),
  m_error(m_H + 1),
  m_output(m_H + 1)
{
  initialize(machine);
}

bob::learn::mlp::Trainer::~Trainer() { }

bob::learn::mlp::Trainer::Trainer(const Trainer& other):
  m_batch_size(other.m_batch_size),
  m_cost(other.m_cost),
  m_train_bias(other.m_train_bias),
  m_H(other.m_H)
{
  bob::core::array::ccopy(other.m_deriv, m_deriv);
  bob::core::array::ccopy(other.m_deriv_bias, m_deriv_bias);
  bob::core::array::ccopy(other.m_error, m_error);
  bob::core::array::ccopy(other.m_output, m_output);
}

bob::learn::mlp::Trainer& bob::learn::mlp::Trainer::operator=
(const bob::learn::mlp::Trainer& other) {
  if (this != &other)
  {
    m_batch_size = other.m_batch_size;
    m_cost = other.m_cost;
    m_train_bias = other.m_train_bias;
    m_H = other.m_H;

    bob::core::array::ccopy(other.m_deriv, m_deriv);
    bob::core::array::ccopy(other.m_deriv_bias, m_deriv_bias);
    bob::core::array::ccopy(other.m_error, m_error);
    bob::core::array::ccopy(other.m_output, m_output);
  }
  return *this;
}

void bob::learn::mlp::Trainer::setBatchSize (size_t batch_size) {
  // m_output: values after the activation function
  // m_error: error values;

  m_batch_size = batch_size;

  for (size_t k=0; k<m_output.size(); ++k) {
    m_output[k].resize(batch_size, m_deriv[k].extent(1));
  }

  for (size_t k=0; k<m_error.size(); ++k) {
    m_error[k].resize(batch_size, m_deriv[k].extent(1));
  }
}

bool bob::learn::mlp::Trainer::isCompatible(const bob::learn::mlp::Machine& machine) const
{
  if (m_H != machine.numOfHiddenLayers()) return false;

  if (m_deriv.back().extent(1) != (int)machine.outputSize()) return false;

  if (m_deriv[0].extent(0) != (int)machine.inputSize()) return false;

  //also, each layer should be of the same size
  for (size_t k=0; k<(m_H + 1); ++k) {
    if (!bob::core::array::hasSameShape(m_deriv[k], machine.getWeights()[k])) return false;
  }

  //if you get to this point, you can only return true
  return true;
}

void bob::learn::mlp::Trainer::forward_step(const bob::learn::mlp::Machine& machine,
  const blitz::Array<double,2>& input)
{
  const std::vector<blitz::Array<double,2> >& machine_weight = machine.getWeights();
  const std::vector<blitz::Array<double,1> >& machine_bias = machine.getBiases();

  boost::shared_ptr<bob::learn::activation::Activation> hidden_actfun = machine.getHiddenActivation();
  boost::shared_ptr<bob::learn::activation::Activation> output_actfun = machine.getOutputActivation();

  for (size_t k=0; k<machine_weight.size(); ++k) { //for all layers
    if (k == 0) bob::math::prod_(input, machine_weight[k], m_output[k]);
    else bob::math::prod_(m_output[k-1], machine_weight[k], m_output[k]);
    boost::shared_ptr<bob::learn::activation::Activation> cur_actfun =
      (k == (machine_weight.size()-1) ? output_actfun : hidden_actfun );
    for (int i=0; i<(int)m_batch_size; ++i) { //for every example
      for (int j=0; j<m_output[k].extent(1); ++j) { //for all variables
        m_output[k](i,j) = cur_actfun->f(m_output[k](i,j) + machine_bias[k](j));
      }
    }
  }
}

void bob::learn::mlp::Trainer::backward_step
(const bob::learn::mlp::Machine& machine,
 const blitz::Array<double,2>& input, const blitz::Array<double,2>& target)
{
  const std::vector<blitz::Array<double,2> >& machine_weight = machine.getWeights();

  //last layer
  boost::shared_ptr<bob::learn::activation::Activation> output_actfun = machine.getOutputActivation();
  for (int i=0; i<(int)m_batch_size; ++i) { //for every example
    for (int j=0; j<m_error[m_H].extent(1); ++j) { //for all variables
      m_error[m_H](i,j) = m_cost->error(m_output[m_H](i,j), target(i,j));
    }
  }

  //all other layers
  boost::shared_ptr<bob::learn::activation::Activation> hidden_actfun = machine.getHiddenActivation();
  for (size_t k=m_H; k>0; --k) {
    bob::math::prod_(m_error[k], machine_weight[k].transpose(1,0), m_error[k-1]);
    for (int i=0; i<(int)m_batch_size; ++i) { //for every example
      for (int j=0; j<m_error[k-1].extent(1); ++j) { //for all variables
        m_error[k-1](i,j) *= hidden_actfun->f_prime_from_f(m_output[k-1](i,j));
      }
    }
  }

  //calculate the derivatives of the cost w.r.t. the weights and biases
  for (size_t k=0; k<machine_weight.size(); ++k) { //for all layers
    // For the weights
    if (k == 0) bob::math::prod_(input.transpose(1,0), m_error[k], m_deriv[k]);
    else bob::math::prod_(m_output[k-1].transpose(1,0), m_error[k], m_deriv[k]);
    m_deriv[k] /= m_batch_size;
    // For the biases
    blitz::secondIndex bj;
    m_deriv_bias[k] = blitz::mean(m_error[k].transpose(1,0), bj);
  }
}

double bob::learn::mlp::Trainer::cost
(const blitz::Array<double,2>& target) const {
  bob::core::array::assertSameShape(m_output[m_H], target);
  double retval = 0.0;
  for (int i=0; i<target.extent(0); ++i) { //for every example
    for (int j=0; j<target.extent(1); ++j) { //for all variables
      retval += m_cost->f(m_output[m_H](i,j), target(i,j));
    }
  }
  return retval / target.extent(0);
}

double bob::learn::mlp::Trainer::cost
(const bob::learn::mlp::Machine& machine, const blitz::Array<double,2>& input,
 const blitz::Array<double,2>& target) {
  forward_step(machine, input);
  return cost(target);
}

void bob::learn::mlp::Trainer::initialize(const bob::learn::mlp::Machine& machine)
{
  const std::vector<blitz::Array<double,2> >& machine_weight =
    machine.getWeights();
  const std::vector<blitz::Array<double,1> >& machine_bias =
    machine.getBiases();

  m_H = machine.numOfHiddenLayers();
  m_deriv.resize(m_H + 1);
  m_deriv_bias.resize(m_H + 1);
  m_output.resize(m_H + 1);
  m_error.resize(m_H + 1);
  for (size_t k=0; k<(m_H + 1); ++k) {
    m_deriv[k].reference(blitz::Array<double,2>(machine_weight[k].shape()));
    m_deriv_bias[k].reference(blitz::Array<double,1>(machine_bias[k].shape()));
    m_output[k].resize(m_batch_size, m_deriv[k].extent(1));
    m_error[k].resize(m_batch_size, m_deriv[k].extent(1));
  }

  reset();
}

void bob::learn::mlp::Trainer::setError(const std::vector<blitz::Array<double,2> >& error) {
  bob::core::array::assertSameDimensionLength(error.size(), m_error.size());
  for (size_t k=0; k<error.size(); ++k)
  {
    bob::core::array::assertSameShape(error[k], m_error[k]);
    m_error[k] = error[k];
  }
}

void bob::learn::mlp::Trainer::setError(const blitz::Array<double,2>& error, const size_t id) {
  if (id >= m_error.size()) {
    boost::format m("Trainer: index for setting error array %lu is not on the expected range of [0, %lu]");
    m % id % (m_error.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(error, m_error[id]);
  m_error[id] = error;
}

void bob::learn::mlp::Trainer::setOutput(const std::vector<blitz::Array<double,2> >& output) {
  bob::core::array::assertSameDimensionLength(output.size(), m_output.size());
  for (size_t k=0; k<output.size(); ++k)
  {
    bob::core::array::assertSameShape(output[k], m_output[k]);
    m_output[k] = output[k];
  }
}

void bob::learn::mlp::Trainer::setOutput(const blitz::Array<double,2>& output, const size_t id) {
  if (id >= m_output.size()) {
    boost::format m("Trainer: index for setting output array %lu is not on the expected range of [0, %lu]");
    m % id % (m_output.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(output, m_output[id]);
  m_output[id] = output;
}

void bob::learn::mlp::Trainer::setDerivatives(const std::vector<blitz::Array<double,2> >& deriv) {
  bob::core::array::assertSameDimensionLength(deriv.size(), m_deriv.size());
  for (size_t k=0; k<deriv.size(); ++k)
  {
    bob::core::array::assertSameShape(deriv[k], m_deriv[k]);
    m_deriv[k] = deriv[k];
  }
}

void bob::learn::mlp::Trainer::setDerivative(const blitz::Array<double,2>& deriv, const size_t id) {
  if (id >= m_deriv.size()) {
    boost::format m("Trainer: index for setting derivative array %lu is not on the expected range of [0, %lu]");
    m % id % (m_deriv.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(deriv, m_deriv[id]);
  m_deriv[id] = deriv;
}

void bob::learn::mlp::Trainer::setBiasDerivatives(const std::vector<blitz::Array<double,1> >& deriv_bias) {
  bob::core::array::assertSameDimensionLength(deriv_bias.size(), m_deriv_bias.size());
  for (size_t k=0; k<deriv_bias.size(); ++k)
  {
    bob::core::array::assertSameShape(deriv_bias[k], m_deriv_bias[k]);
    m_deriv_bias[k] = deriv_bias[k];
  }
}

void bob::learn::mlp::Trainer::setBiasDerivative(const blitz::Array<double,1>& deriv_bias, const size_t id) {
  if (id >= m_deriv_bias.size()) {
    boost::format m("Trainer: index for setting bias derivative array %lu is not on the expected range of [0, %lu]");
    m % id % (m_deriv_bias.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(deriv_bias, m_deriv_bias[id]);
  m_deriv_bias[id] = deriv_bias;
}

void bob::learn::mlp::Trainer::reset() {
  for (size_t k=0; k<(m_H + 1); ++k) {
    m_deriv[k] = 0.;
    m_deriv_bias[k] = 0.;
    m_error[k] = 0.;
    m_output[k] = 0.;
  }
}
