.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Tue 13 May 09:30:06 2014 CEST
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. testsetup:: *

   import numpy
   import bob.learn.mlp
   import tempfile
   import os

   current_directory = os.path.realpath(os.curdir)
   temp_dir = tempfile.mkdtemp(prefix='bob_doctest_')
   os.chdir(temp_dir)

====================================================
 Multi-Layer Perceptron (MLP) Machines and Trainers
====================================================

A `multi-layer perceptron
<http://en.wikipedia.org/wiki/Multilayer_perceptron>`_ (MLP) is a neural
network architecture that has some well-defined characteristics such as a
feed-forward structure. You can create a new MLP using one of the trainers
described below. We start this tutorial by examplifying how to actually use an
MLP.

To instantiate a new (uninitialized) :py:class:`bob.learn.mlp.Machine` pass a
shape descriptor as a :py:func:`tuple`. The shape parameter should contain the
input size as the first parameter and the output size as the last parameter.
The parameters in between define the number of neurons in the hidden layers of
the MLP. For example ``(3, 3, 1)`` defines an MLP with 3 inputs, 1 single
hidden layer with 3 neurons and 1 output, whereas a shape like ``(10, 5, 3,
2)`` defines an MLP with 10 inputs, 5 neurons in the first hidden layer, 3
neurons in the second hidden layer and 2 outputs.  Here is an example:

.. doctest::

  >>> mlp = bob.learn.mlp.Machine((3, 3, 2, 1))

As it is, the network is uninitialized. For the sake of demonstrating how to use
MLPs, let's set the weight and biases manually (we would normally use a trainer
for this):

.. doctest::

  >>> input_to_hidden0 = numpy.ones((3,3), 'float64')
  >>> input_to_hidden0
  array([[ 1.,  1.,  1.],
         [ 1.,  1.,  1.],
         [ 1.,  1.,  1.]])
  >>> hidden0_to_hidden1 = 0.5*numpy.ones((3,2), 'float64')
  >>> hidden0_to_hidden1
  array([[ 0.5,  0.5],
         [ 0.5,  0.5],
         [ 0.5,  0.5]])
  >>> hidden1_to_output = numpy.array([0.3, 0.2], 'float64').reshape(2,1)
  >>> hidden1_to_output
  array([[ 0.3],
         [ 0.2]])
  >>> bias_hidden0 = numpy.array([-0.2, -0.3, -0.1], 'float64')
  >>> bias_hidden0
  array([-0.2, -0.3, -0.1])
  >>> bias_hidden1 = numpy.array([-0.7, 0.2], 'float64')
  >>> bias_hidden1
  array([-0.7,  0.2])
  >>> bias_output = numpy.array([0.5], 'float64')
  >>> bias_output
  array([ 0.5])
  >>> mlp.weights = (input_to_hidden0, hidden0_to_hidden1, hidden1_to_output)
  >>> mlp.biases = (bias_hidden0, bias_hidden1, bias_output)

At this point, a few things should be noted:

1. Weights should **always** be 2D arrays, even if they are connecting 1 neuron
   to many (or many to 1). You can use the NumPy_ ``reshape()`` array method
   for this purpose as shown above
2. Biases should **always** be 1D arrays.
3. By default, MLPs use the :py:class:`bob.learn.activation.HyperbolicTangent`
   as activation function. There are currently 4 other activation functions
   available in |project|:

   * The identity function: :py:class:`bob.learn.activation.Identity`;
   * The sigmoid function (also known as the `logistic function
     <http://mathworld.wolfram.com/SigmoidFunction.html>`_ function):
     :py:class:`bob.learn.activation.Logistic`;
   * A scaled version of the hyperbolic tangent function:
     :py:class:`bob.learn.activation.MultipliedHyperbolicTangent`; and
   * A scaled version of the identity activation:
     :py:class:`bob.learn.activation.Linear`

Let's try changing all of the activation functions to a simpler one, just for
this example:

.. doctest::

  >>> mlp.hidden_activation = bob.learn.activation.Identity()
  >>> mlp.output_activation = bob.learn.activation.Identity()

Once the network weights and biases are set, we can feed forward an example
through this machine. This is done using the ``()`` operator, like for a
:py:class:`bob.learn.linear.Machine`:

.. doctest::

  >>> mlp(numpy.array([0.1, -0.1, 0.2], 'float64'))
  array([ 0.33])

MLPs can be `trained` through backpropagation [2]_, which is a supervised
learning technique. This training procedure requires a set of features with
labels (or targets). Using |project|, this is passed to the `train()` method of
available MLP trainers in two different 2D `NumPy`_ arrays, one for the input
(features) and one for the output (targets).

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> d0 = numpy.array([[.3, .7, .5]]) # input
   >>> t0 = numpy.array([[.0]]) # target

The class used to train a MLP [1]_ with backpropagation [2]_ is
:py:class:`bob.learn.mlp.BackProp`. An example is shown below.


.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> trainer = bob.learn.mlp.BackProp(1, bob.learn.mlp.SquareError(mlp.output_activation), mlp, train_biases=False) #  Creates a BackProp trainer with a batch size of 1
   >>> trainer.train(mlp, d0, t0) # Performs the Back Propagation

.. note::

  The second parameter of the trainer defines the cost function to be used for
  the training. You can use two different types of pre-programmed costs in
  |project|: :py:class:`bob.learn.mlp.SquareError`, like before, or
  :py:class:`bob.learn.mlp.CrossEntropyLoss` (normally in association with
  :py:class:`bob.learn.activation.Logistic`). You can implement your own
  cost/loss functions. Nevertheless, to do so, you must do it using our
  C/C++-API and then bind it to Python in your own package.

Backpropagation [2]_ requires a learning rate to be set. In the previous
example, the default value ``0.1`` has been used. This might be updated using
the :py:attr:`bob.learn.mlp.BackProp.learning_rate` attribute.

Another training alternative exists referred to as **resilient propagation**
(R-Prop) [3]_, which dynamically computes an optimal learning rate. The
corresponding class is :py:class:`bob.learn.mlp.RProp`, and the overall
training procedure remains identical.

.. doctest::
   :options: +NORMALIZE_WHITESPACE

   >>> trainer = bob.learn.mlp.RProp(1, bob.learn.mlp.SquareError(mlp.output_activation), mlp, train_biases=False)
   >>> trainer.train(mlp, d0, t0)

.. note::

   The trainers are **not** re-initialized when you call it several times. This
   is done so as to allow you to implement your own stopping criteria. To reset
   an MLP trainer, use their ``reset`` method.

.. Place here your external references

.. include:: links.rst
.. [1] http://en.wikipedia.org/wiki/Multilayer_perceptron
.. [2] http://en.wikipedia.org/wiki/Backpropagation
.. [3] http://en.wikipedia.org/wiki/Rprop
