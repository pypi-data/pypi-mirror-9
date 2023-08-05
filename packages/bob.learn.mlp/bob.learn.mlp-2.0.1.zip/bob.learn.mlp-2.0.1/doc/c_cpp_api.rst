.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.dos.anjos@gmail.com>
.. Tue 15 Oct 14:59:05 2013

=========
 C++ API
=========

The C++ API of ``bob.learn.mlp`` allows users to leverage from automatic
converters for classes in :py:class:`bob.learn.mlp`.  To use the C API,
clients should first, include the header file ``<bob.learn.mlp.h>`` on
their compilation units and then, make sure to call once
``import_bob_learn_mlp()`` at their module instantiation, as explained at
the `Python manual
<http://docs.python.org/2/extending/extending.html#using-capsules>`_.

Here is a dummy C example showing how to include the header and where to call
the import function:

.. code-block:: c++

   #include <bob.learn.mlp/api.h>

   PyMODINIT_FUNC initclient(void) {

     PyObject* m Py_InitModule("client", ClientMethods);

     if (!m) return 0;

     if (import_bob_blitz() < 0) return 0;
     if (import_bob_io() < 0) return 0;
     if (import_bob_learn_activation() < 0) return 0;
     if (import_bob_learn_mlp() < 0) return 0;

     return m;

   }


Machine
-------

.. cpp:type:: PyBobLearnMLPMachineObject

   The pythonic object representation for a :py:class:`bob.learn.mlp.Machine`
   object.

   .. code-block:: cpp

      typedef struct {
        PyObject_HEAD
        bob::learn::mlp::Machine* cxx;
      } PyBobLearnMLPMachineObject;

   .. cpp:member:: bob::learn::mlp::Machine* cxx

      A pointer to the machine implentation in C++.


.. cpp:function:: int PyBobLearnMLPMachine_Check(PyObject* o)

   Checks if the input object ``o`` is a
   :cpp:class:`PyBobLearnMLPMachineObject`.  Returns ``1`` if it is, and ``0``
   otherwise.


Cost
----

.. cpp:type:: PyBobLearnCostObject

   The pythonic object representation for a :py:class:`bob.learn.mlp.Cost`
   object.  It is the base class of all derive cost types available in
   |project|.

   .. code-block:: cpp

      typedef struct {
        PyObject_HEAD
        boost::shared_ptr<bob::learn::mlp::Cost> cxx;
      } PyBobLearnCostObject;

   .. cpp:member:: boost::shared_ptr<bob::learn::mlp::Cost> cxx

      A pointer to the cost object implemented in C++. The cost object is an
      abstract interface. You cannot instantiate a cost from scratch, but only
      through its inherited classes.

      We use a boost shared pointer to hold this pointer since it makes
      interaction with the C++ library and the management of responsibilities a
      bit easier.


.. cpp:function:: int PyBobLearnCost_Check(PyObject* o)

   Checks if the input object ``o`` is a :cpp:class:`PyBobLearnCostObject`.
   Returns ``1`` if it is, and ``0`` otherwise.


.. note::

   These are the cost object specializations you can use from Python:

   * :py:class:`bob.learn.mlp.SquareError`
   * :py:class:`bob.learn.mlp.CrossEntropyLoss`

   For each of those types, object types in C exist.


.. cpp:function:: PyObject* PyBobLearnCost_NewFromCost(boost::shared_ptr<bob::learn::mlp::Cost>)

   Builds a new cost object from a shared pointer to the C++ equivalent.

   Returns the object on success or a NULL pointer on failure.


Data Shuffler
-------------

.. cpp:type:: PyBobLearnDataShufflerObject

   The pythonic representation for a :py:class:`bob.learn.mlp.DataShuffler`
   object.

   .. code-block:: cpp

      typedef struct {
        PyObject_HEAD
        bob::learn::mlp::DataShuffler* cxx;
      } PyBobLearnCostObject;

   .. cpp:member:: bob::learn::mlp::DataShuffler* cxx

      A pointer to the data shuffler object implemented in C++.


.. cpp:function:: int PyBobLearnDataShuffler_Check(PyObject* o)

   Checks if the input object ``o`` is a
   :cpp:class:`PyBobLearnDataShufflerObject`.  Returns ``1`` if it is, and
   ``0`` otherwise.


Trainers
--------

.. cpp:type:: PyBobLearnMLPTrainerObject

   The pythonic representation for a :py:class:`bob.learn.mlp.Trainer` object.
   All back-propagation-based trainers should inherit from this type as it
   implements most of the basic functionality needed by such a learning
   technique.

   .. code-block:: cpp

      typedef struct {
        PyObject_HEAD
        bob::learn::mlp::Trainer* cxx;
      } PyBobLearnCostObject;

   .. cpp:member:: bob::learn::mlp::Trainer* cxx

      A pointer to the base trainer object implemented in C++.


.. cpp:function:: int PyBobLearnMLPTrainer_Check(PyObject* o)

   Checks if the input object ``o`` is a
   :cpp:class:`PyBobLearnMLPTrainerObject`.  Returns ``1`` if it is, and ``0``
   otherwise.


.. cpp:type:: PyBobLearnBackPropObject

   The pythonic representation for a :py:class:`bob.learn.mlp.BackProp` object.
   All back-propagation-based trainers should inherit from this type as it
   implements most of the basic functionality needed by such a learning
   technique.

   .. code-block:: cpp

      typedef struct {
        PyBobLearnMLPTrainerObject parent;
        bob::learn::mlp::BackProp* cxx;
      } PyBobLearnCostObject;

   .. cpp:member:: PyBobLearnMLPTrainerObject parent

      The parent abstract class pointer. Use ``parent.cxx`` to access the
      abstract C++ base interface.

   .. cpp:member:: bob::learn::mlp::BackProp* cxx

      A pointer to the derived trainer object implemented in C++.


.. cpp:function:: int PyBobLearnBackProp_Check(PyObject* o)

   Checks if the input object ``o`` is a
   :cpp:class:`PyBobLearnBackPropObject`.  Returns ``1`` if it is, and
   ``0`` otherwise.


.. cpp:type:: PyBobLearnRPropObject

   The pythonic representation for a :py:class:`bob.learn.mlp.RProp` object.
   All back-propagation-based trainers should inherit from this type as it
   implements most of the basic functionality needed by such a learning
   technique.

   .. code-block:: cpp

      typedef struct {
        PyBobLearnMLPTrainerObject parent;
        bob::learn::mlp::RProp* cxx;
      } PyBobLearnCostObject;

   .. cpp:member:: PyBobLearnMLPTrainerObject parent

      The parent abstract class pointer. Use ``parent.cxx`` to access the
      abstract C++ base interface.

   .. cpp:member:: bob::learn::mlp::RProp* cxx

      A pointer to the derived trainer object implemented in C++.


.. cpp:function:: int PyBobLearnRProp_Check(PyObject* o)

   Checks if the input object ``o`` is a :cpp:class:`PyBobLearnRPropObject`.
   Returns ``1`` if it is, and ``0`` otherwise.


Pure C/C++ API
--------------

As explained above, each ``PyObject`` produced by this library contains a
pointer to a pure C++ implementation of a similar object. The C++ of such
objects is described in this section.

.. todo::

   Describe the C++ API of this package.

.. include:: links.rst
