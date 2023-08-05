/**
 * @date Mon Jul 18 18:11:22 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief Implementation of the BackProp algorithm for MLP training.
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#include <algorithm>
#include <bob.core/check.h>
#include <bob.math/linear.h>

#include <bob.learn.mlp/backprop.h>

bob::learn::mlp::BackProp::BackProp(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost):
  bob::learn::mlp::Trainer(batch_size, cost),
  m_learning_rate(0.1),
  m_momentum(0.0),
  m_prev_deriv(numberOfHiddenLayers() + 1),
  m_prev_deriv_bias(numberOfHiddenLayers() + 1)
{
  reset();
}

bob::learn::mlp::BackProp::BackProp(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost,
    const bob::learn::mlp::Machine& machine):
  bob::learn::mlp::Trainer(batch_size, cost, machine),
  m_learning_rate(0.1),
  m_momentum(0.0),
  m_prev_deriv(numberOfHiddenLayers() + 1),
  m_prev_deriv_bias(numberOfHiddenLayers() + 1)
{
  initialize(machine);
}

bob::learn::mlp::BackProp::BackProp(size_t batch_size,
    boost::shared_ptr<bob::learn::mlp::Cost> cost,
    const bob::learn::mlp::Machine& machine, bool train_biases):
  bob::learn::mlp::Trainer(batch_size, cost, machine, train_biases),
  m_learning_rate(0.1),
  m_momentum(0.0),
  m_prev_deriv(numberOfHiddenLayers() + 1),
  m_prev_deriv_bias(numberOfHiddenLayers() + 1)
{
  initialize(machine);
}

bob::learn::mlp::BackProp::~BackProp() { }

bob::learn::mlp::BackProp::BackProp(const BackProp& other):
  bob::learn::mlp::Trainer(other),
  m_learning_rate(other.m_learning_rate),
  m_momentum(other.m_momentum)
{
  bob::core::array::ccopy(other.m_prev_deriv, m_prev_deriv);
  bob::core::array::ccopy(other.m_prev_deriv_bias, m_prev_deriv_bias);
}

bob::learn::mlp::BackProp& bob::learn::mlp::BackProp::operator=
(const bob::learn::mlp::BackProp& other) {
  if (this != &other)
  {
    bob::learn::mlp::Trainer::operator=(other);
    m_learning_rate = other.m_learning_rate;
    m_momentum = other.m_momentum;

    bob::core::array::ccopy(other.m_prev_deriv, m_prev_deriv);
    bob::core::array::ccopy(other.m_prev_deriv_bias, m_prev_deriv_bias);
  }
  return *this;
}

void bob::learn::mlp::BackProp::reset() {
  for (size_t k=0; k<(numberOfHiddenLayers() + 1); ++k) {
    m_prev_deriv[k] = 0;
    m_prev_deriv_bias[k] = 0;
  }
}

void bob::learn::mlp::BackProp::backprop_weight_update(bob::learn::mlp::Machine& machine,
  const blitz::Array<double,2>& input)
{
  std::vector<blitz::Array<double,2> >& machine_weight =
    machine.updateWeights();
  std::vector<blitz::Array<double,1> >& machine_bias =
    machine.updateBiases();
  const std::vector<blitz::Array<double,2> >& deriv = getDerivatives();
  for (size_t k=0; k<machine_weight.size(); ++k) { //for all layers
    machine_weight[k] -= (((1-m_momentum)*m_learning_rate*deriv[k]) +
      (m_momentum*m_prev_deriv[k]));
    m_prev_deriv[k] = m_learning_rate*deriv[k];

    // Here we decide if we should train the biases or not
    if (!getTrainBiases()) continue;

    const std::vector<blitz::Array<double,1> >& deriv_bias = getBiasDerivatives();
    // We do the same for the biases, with the exception that biases can be
    // considered as input neurons connecting the respective layers, with a
    // fixed input = +1. This means we only need to probe for the error at
    // layer k.
    machine_bias[k] -= (((1-m_momentum)*m_learning_rate*deriv_bias[k]) +
      (m_momentum*m_prev_deriv_bias[k]));
    m_prev_deriv_bias[k] = m_learning_rate*deriv_bias[k];
  }
}

void bob::learn::mlp::BackProp::setPreviousDerivatives(const std::vector<blitz::Array<double,2> >& v) {
  bob::core::array::assertSameDimensionLength(v.size(), m_prev_deriv.size());
  for (size_t k=0; k<v.size(); ++k) {
    bob::core::array::assertSameShape(v[k], m_prev_deriv[k]);
    m_prev_deriv[k] = v[k];
  }
}

void bob::learn::mlp::BackProp::setPreviousDerivative(const blitz::Array<double,2>& v, const size_t k) {
  if (k >= m_prev_deriv.size()) {
    boost::format m("MLPRPropTrainer: index for setting previous derivative array %lu is not on the expected range of [0, %lu]");
    m % k % (m_prev_deriv.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(v, m_prev_deriv[k]);
  m_prev_deriv[k] = v;
}

void bob::learn::mlp::BackProp::setPreviousBiasDerivatives(const std::vector<blitz::Array<double,1> >& v) {
  bob::core::array::assertSameDimensionLength(v.size(), m_prev_deriv_bias.size());
  for (size_t k=0; k<v.size(); ++k)
  {
    bob::core::array::assertSameShape(v[k], m_prev_deriv_bias[k]);
    m_prev_deriv_bias[k] = v[k];
  }
}

void bob::learn::mlp::BackProp::setPreviousBiasDerivative(const blitz::Array<double,1>& v, const size_t k) {
  if (k >= m_prev_deriv_bias.size()) {
    boost::format m("MLPRPropTrainer: index for setting previous bias derivative array %lu is not on the expected range of [0, %lu]");
    m % k % (m_prev_deriv_bias.size()-1);
    throw std::runtime_error(m.str());
  }
  bob::core::array::assertSameShape(v, m_prev_deriv_bias[k]);
  m_prev_deriv_bias[k] = v;
}

void bob::learn::mlp::BackProp::initialize(const bob::learn::mlp::Machine& machine)
{
  bob::learn::mlp::Trainer::initialize(machine);

  const std::vector<blitz::Array<double,2> >& machine_weight =
    machine.getWeights();
  const std::vector<blitz::Array<double,1> >& machine_bias =
    machine.getBiases();

  m_prev_deriv.resize(numberOfHiddenLayers() + 1);
  m_prev_deriv_bias.resize(numberOfHiddenLayers() + 1);
  for (size_t k=0; k<(numberOfHiddenLayers() + 1); ++k) {
    m_prev_deriv[k].reference(blitz::Array<double,2>(machine_weight[k].shape()));
    m_prev_deriv_bias[k].reference(blitz::Array<double,1>(machine_bias[k].shape()));
  }

  reset();
}

void bob::learn::mlp::BackProp::train(bob::learn::mlp::Machine& machine,
    const blitz::Array<double,2>& input,
    const blitz::Array<double,2>& target) {
  if (!isCompatible(machine)) {
    throw std::runtime_error("input machine is incompatible with this trainer");
  }
  bob::core::array::assertSameDimensionLength(getBatchSize(), input.extent(0));
  bob::core::array::assertSameDimensionLength(getBatchSize(), target.extent(0));
  bob::core::array::assertSameDimensionLength(machine.inputSize(), input.extent(1));
  bob::core::array::assertSameDimensionLength(machine.outputSize(), target.extent(1));
  train_(machine, input, target);
}

void bob::learn::mlp::BackProp::train_(bob::learn::mlp::Machine& machine,
    const blitz::Array<double,2>& input,
    const blitz::Array<double,2>& target) {
  // To be called in this sequence for a general backprop algorithm
  forward_step(machine, input);
  backward_step(machine, input, target);
  backprop_weight_update(machine, input);
}
