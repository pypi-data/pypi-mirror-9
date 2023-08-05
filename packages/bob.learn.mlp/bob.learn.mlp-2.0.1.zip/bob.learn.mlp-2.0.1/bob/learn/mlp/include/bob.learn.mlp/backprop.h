/**
 * @date Mon Jul 18 18:11:22 2011 +0200
 * @author Andre Anjos <andre.anjos@idiap.ch>
 * @author Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
 *
 * @brief A MLP trainer based on vanilla back-propagation. You can get an
 * overview of this method at "Pattern Recognition and Machine Learning"
 * by C.M. Bishop (Chapter 5).
 *
 * Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland
 */

#ifndef BOB_LEARN_MLP_BACKPROP_H
#define BOB_LEARN_MLP_BACKPROP_H

#include <vector>
#include <boost/function.hpp>

#include <bob.learn.mlp/machine.h>
#include <bob.learn.mlp/trainer.h>

namespace bob { namespace learn { namespace mlp {

  /**
   * @brief Sets an MLP to perform discrimination based on vanilla error
   * back-propagation as defined in "Pattern Recognition and Machine Learning"
   * by C.M. Bishop, chapter 5.
   */
  class BackProp: public Trainer {

    public: //api

      /**
       * @brief Initializes a new BackProp trainer according to a
       * given machine settings and a training batch size.
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
       *
       * You can also change default values for the learning rate and momentum.
       * By default we train w/o any momenta.
       *
       * If you want to adjust a potential learning rate decay, you can and
       * should do it outside the scope of this trainer, in your own way.
       */
      BackProp(size_t batch_size, boost::shared_ptr<Cost> cost);

      /**
       * @brief Initializes a new BackProp trainer according to a
       * given machine settings and a training batch size.
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
       *
       * You can also change default values for the learning rate and momentum.
       * By default we train w/o any momenta.
       *
       * If you want to adjust a potential learning rate decay, you can and
       * should do it outside the scope of this trainer, in your own way.
       */
      BackProp(size_t batch_size, boost::shared_ptr<Cost> cost,
          const Machine& machine);

      /**
       * @brief Initializes a new BackProp trainer according to a
       * given machine settings and a training batch size.
       *
       * @param batch_size The number of examples passed at each iteration. If
       * you set this to 1, then you are implementing stochastic training.
       *
       * @param cost This is the cost function to use for the current training.
       *
       * @param machine Clone this machine weights and prepare the trainer
       * internally mirroring machine properties.
       *
       * @note Good values for batch sizes are tens of samples. BackProp is not
       * necessarily a "batch" training algorithm, but performs in a smoother
       * if the batch size is larger. This may also affect the convergence.
       *
       * @param train_biases A boolean, indicating if we need to train the
       * biases or not.
       *
       * You can also change default values for the learning rate and momentum.
       * By default we train w/o any momenta.
       *
       * If you want to adjust a potential learning rate decay, you can and
       * should do it outside the scope of this trainer, in your own way.
       */
      BackProp(size_t batch_size, boost::shared_ptr<Cost> cost,
          const Machine& machine, bool train_biases);

      /**
       * @brief Destructor virtualisation
       */
      virtual ~BackProp();

      /**
       * @brief Copy construction.
       */
      BackProp(const BackProp& other);

      /**
       * @brief Copy operator
       */
      BackProp& operator=(const BackProp& other);

      /**
       * @brief Re-initializes the whole training apparatus to start training a
       * new machine. This will effectively reset all Delta matrices to their
       * intial values and set the previous derivatives to zero.
       */
      void reset();

      /**
       * @brief Gets the current learning rate
       */
      double getLearningRate() const { return m_learning_rate; }

      /**
       * @brief Sets the current learning rate
       */
      void setLearningRate(double v) { m_learning_rate = v; }

      /**
       * @brief Gets the current momentum
       */
      double getMomentum() const { return m_momentum; }

      /**
       * @brief Sets the current momentum
       */
      void setMomentum(double v) { m_momentum = v; }

      /**
       * @brief Returns the derivatives of the cost wrt. the weights
       */
      const std::vector<blitz::Array<double,2> >& getPreviousDerivatives() const { return m_prev_deriv; }

      /**
       * @brief Returns the derivatives of the cost wrt. the biases
       */
      const std::vector<blitz::Array<double,1> >& getPreviousBiasDerivatives() const { return m_prev_deriv_bias; }

      /**
       * @brief Sets the previous derivatives of the cost
       */
      void setPreviousDerivatives(const std::vector<blitz::Array<double,2> >& v);

      /**
       * @brief Sets the previous derivatives of the cost of a given index
       */
      void setPreviousDerivative(const blitz::Array<double,2>& v, const size_t index);

      /**
       * @brief Sets the previous derivatives of the cost (biases)
       */
      void setPreviousBiasDerivatives(const std::vector<blitz::Array<double,1> >& v);

      /**
       * @brief Sets the previous derivatives of the cost (biases) of a given
       * index
       */
      void setPreviousBiasDerivative(const blitz::Array<double,1>& v, const size_t index);

      /**
       * @brief Initialize the internal buffers for the current machine
       */
      virtual void initialize(const Machine& machine);

      /**
       * @brief Trains the MLP to perform discrimination. The training is
       * executed outside the machine context, but uses all the current
       * machine layout. The given machine is updated with new weights and
       * biases on the end of the training that is performed a single time.
       * Iterate as much as you want to refine the training.
       *
       * The machine given as input is checked for compatibility with the
       * current initialized settings. If the two are not compatible, an
       * exception is thrown.
       *
       * Note: In BackProp, training may be done in batches. The number of rows
       * in the input (and target) determines the batch size. If the batch size
       * currently set is incompatible with the given data an exception is
       * raised.
       *
       * Note2: The machine is not initialized randomly at each train() call.
       * It is your task to call MLP::randomize() once on the machine you want
       * to train and then call train() as many times as you think are
       * necessary. This design allows for a training criteria to be encoded
       * outside the scope of this trainer and to this type to focus only on
       * input, target applying the training when requested to.
       */
      void train(Machine& machine,
          const blitz::Array<double,2>& input,
          const blitz::Array<double,2>& target);

      /**
       * @brief This is a version of the train() method above, which does no
       * compatibility check on the input machine.
       */
      void train_(Machine& machine,
          const blitz::Array<double,2>& input,
          const blitz::Array<double,2>& target);

    private:
      /**
       * Weight update -- calculates the weight-update using derivatives as
       * required by back-prop.
       */
      void backprop_weight_update(Machine& machine,
        const blitz::Array<double,2>& input);

      /// training parameters:
      double m_learning_rate;
      double m_momentum;

      std::vector<blitz::Array<double,2> > m_prev_deriv; ///< prev.weight derivs
      std::vector<blitz::Array<double,1> > m_prev_deriv_bias; ///< prev. bias derivs
  };

}}}

#endif /* BOB_LEARN_MLP_BACKPROP_H */
