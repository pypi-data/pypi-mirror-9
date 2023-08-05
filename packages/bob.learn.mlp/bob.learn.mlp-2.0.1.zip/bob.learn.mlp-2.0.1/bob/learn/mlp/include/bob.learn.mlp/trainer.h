/**
 * @date Tue May 14 12:00:03 CEST 2013
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_BASE_TRAINER_H
#define BOB_LEARN_MLP_BASE_TRAINER_H

#include <vector>
#include <boost/shared_ptr.hpp>

#include <bob.learn.mlp/machine.h>
#include <bob.learn.mlp/cost.h>

namespace bob { namespace learn { namespace mlp {

  /**
   * @brief Base class for training MLP. This provides forward and backward
   * functions over a batch of samples, as well as accessors to the internal
   * states of the networks.
   *
   * Here is an overview of the backprop algorithm executed by this trainer:
   *
   * -# Take the <em>local gradient</em> of a neuron
   *    @f[ b^{(l)} @f]
   *
   * -# Multiply that value by the <em>output</em> of the previous layer;
   *    @f[
   *    b^{(l)} \times a^{(l-1)}
   *    @f]
   *
   * -# Multiply the result of the previous step by the learning rate;
   *    @f[
   *    \eta \times b^{(l)} \times a^{(l-1)}
   *    @f]
   *
   * -# Add the result of the previous setup to the current weight,
   *    possibly weighting the sum with a momentum ponderator.
   *    @f[
   *    w_{n+1} = (1-\mu) \times (w_{n} + \eta \times b^{(l)}
   *    \times a^{(l-1)}) + (\mu) \times w_{n-1}
   *    @f]
   */
  class Trainer {

    public: //api

      /**
       * @brief Initializes a new Trainer trainer according to a given
       * training batch size.
       *
       * @param batch_size The number of examples passed at each iteration. If
       * you set this to 1, then you are implementing stochastic training.
       *
       * @param cost This is the cost function to use for the current training.
       *
       * @note Using this constructor, the internals of the trainer remain
       * uninitialized. You must call <code>initialize()</code> with a proper
       * Machine to initialize the trainer before using it.
       *
       * @note Using this constructor, you set biases training to
       * <code>true</code>
       *
       * @note Good values for batch sizes are tens of samples. This may affect
       * the convergence.
       */
      Trainer(size_t batch_size, boost::shared_ptr<Cost> cost);

      /**
       * @brief Initializes a new Trainer trainer according to a given
       * machine settings and a training batch size.
       *
       * @param batch_size The number of examples passed at each iteration. If
       * you set this to 1, then you are implementing stochastic training.
       *
       * @param cost This is the cost function to use for the current training.
       *
       * @param machine Clone this machine weights and prepare the trainer
       * internally mirroring machine properties.
       *
       * @note Using this constructor, you set biases training to
       * <code>true</code>
       *
       * @note Good values for batch sizes are tens of samples. This may affect
       * the convergence.
       */
      Trainer(size_t batch_size, boost::shared_ptr<Cost> cost,
          const Machine& machine);

      /**
       * @brief Initializes a new Trainer trainer according to a given
       * machine settings and a training batch size.
       *
       * @param batch_size The number of examples passed at each iteration. If
       * you set this to 1, then you are implementing stochastic training.
       *
       * @param cost This is the cost function to use for the current training.
       *
       * @param machine Clone this machine weights and prepare the trainer
       * internally mirroring machine properties.
       *
       * @param train_biases A boolean, indicating if we need to train the
       * biases or not.
       *
       * @note Good values for batch sizes are tens of samples. This may affect
       * the convergence.
       */
      Trainer(size_t batch_size, boost::shared_ptr<Cost> cost,
          const Machine& machine, bool train_biases);

      /**
       * @brief Destructor virtualisation
       */
      virtual ~Trainer();

      /**
       * @brief Copy construction.
       */
      Trainer(const Trainer& other);

      /**
       * @brief Copy operator
       */
      Trainer& operator=(const Trainer& other);

      /**
       * @brief Gets the batch size
       */
      size_t getBatchSize() const { return m_batch_size; }

      /**
       * @brief Sets the batch size
       */
      void setBatchSize(size_t batch_size);

      /**
       * @brief Gets the cost to be minimized
       */
      boost::shared_ptr<Cost> getCost() const { return m_cost; }

      /**
       * @brief Sets the cost to be minimized
       */
      void setCost(boost::shared_ptr<Cost> cost) { m_cost = cost; }

      /**
       * @brief Gets the current settings for bias training (defaults to true)
       */
      inline bool getTrainBiases() const { return m_train_bias; }

      /**
       * @brief Sets the bias training option
       */
      inline void setTrainBiases(bool v) { m_train_bias = v; }

      /**
       * @brief Checks if a given machine is compatible with my inner settings.
       */
      bool isCompatible(const Machine& machine) const;

      /**
       * @brief Returns the number of hidden layers on the target machine
       */
      size_t numberOfHiddenLayers() const { return m_H; }

      /**
       * @brief Forward step -- this is a second implementation of that used on
       * the MLP itself to allow access to some internal buffers. In our
       * current setup, we keep the "m_output"'s of every individual layer
       * separately as we are going to need them for the weight update.
       *
       * Another factor is the normalization normally applied at MLPs. We
       * ignore that here as the DataShuffler should be capable of handling
       * this in a more efficient way. You should make sure that the final MLP
       * does have the standard normalization settings applied if it was set to
       * automatically apply the standard normalization before giving me the
       * data.
       */
      void forward_step(const Machine& machine,
        const blitz::Array<double,2>& input);

      /**
       * @brief Backward step -- back-propagates the calculated error up to each
       * neuron on the first layer and calculates the cost w.r.t. to each
       * weight and bias on the network. This is explained on Bishop's formula
       * 5.55 and 5.56, at page 244 (see also figure 5.7 for a graphical
       * representation).
       */
      void backward_step(const Machine& machine,
        const blitz::Array<double,2>& input,
        const blitz::Array<double,2>& target);

      /**
       * @brief Calculates the cost for a given target.
       *
       * The cost for a given target is the sum of the individually calculated
       * costs for every output, averaged for all examples.
       *
       * This method assumes you have already called forward_step() before. If
       * that is not the case, use the next variant.
       *
       * @return The cost averaged over all targets
       */
      double cost(const blitz::Array<double,2>& target) const;

      /**
       * @brief Calculates the cost for a given target.
       *
       * The cost for a given target is the sum of the individually calculated
       * costs for every output, averaged for all examples.
       *
       * This method also calls forward_step(), so you can call backward_step()
       * just after it, if you wish to do so.
       *
       * @return The cost averaged over all targets
       */
      double cost(const Machine& machine,
        const blitz::Array<double,2>& input,
        const blitz::Array<double,2>& target);

      /**
       * @brief Initialize the internal buffers for the current machine
       */
      virtual void initialize(const Machine& machine);

      /**
       * @brief Returns the errors
       */
      const std::vector<blitz::Array<double,2> >& getError() const { return m_error; }
      /**
       * @brief Returns the outputs
       */
      const std::vector<blitz::Array<double,2> >& getOutput() const { return m_output; }
      /**
       * @brief Returns the derivatives of the cost wrt. the weights
       */
      const std::vector<blitz::Array<double,2> >& getDerivatives() const { return m_deriv; }
      /**
       * @brief Returns the derivatives of the cost wrt. the biases
       */
      const std::vector<blitz::Array<double,1> >& getBiasDerivatives() const { return m_deriv_bias; }
      /**
       * @brief Sets the error
       */
      void setError(const std::vector<blitz::Array<double,2> >& error);
      /**
       * @brief Sets the error of a given index
       */
      void setError(const blitz::Array<double,2>& error, const size_t index);
      /**
       * @brief Sets the outputs
       */
      void setOutput(const std::vector<blitz::Array<double,2> >& output);
      /**
       * @brief Sets the output of a given index
       */
      void setOutput(const blitz::Array<double,2>& output, const size_t index);
      /**
       * @brief Sets the derivatives of the cost
       */
      void setDerivatives(const std::vector<blitz::Array<double,2> >& deriv);
      /**
       * @brief Sets the derivatives of the cost of a given index
       */
      void setDerivative(const blitz::Array<double,2>& deriv, const size_t index);
      /**
       * @brief Sets the derivatives of the cost (biases)
       */
      void setBiasDerivatives(const std::vector<blitz::Array<double,1> >& deriv_bias);
      /**
       * @brief Sets the derivatives of the cost (biases) of a given index
       */
      void setBiasDerivative(const blitz::Array<double,1>& deriv_bias, const size_t index);

    private: //representation

      /**
       * @brief Resets the buffer to 0 value
       */
      void reset();

      /// training parameters:
      size_t m_batch_size; ///< the batch size
      boost::shared_ptr<Cost> m_cost; ///< cost function to be minimized
      bool m_train_bias; ///< shall we be training biases? (default: true)
      size_t m_H; ///< number of hidden layers on the target machine

      std::vector<blitz::Array<double,2> > m_deriv; ///< derivatives of the cost wrt. the weights
      std::vector<blitz::Array<double,1> > m_deriv_bias; ///< derivatives of the cost wrt. the biases

      /// buffers that are dependent on the batch_size
      std::vector<blitz::Array<double,2> > m_error; ///< error (+deltas)
      std::vector<blitz::Array<double,2> > m_output; ///< layer output
  };

}}}

#endif /* BOB_LEARN_MLP_BASE_TRAINER_H */
