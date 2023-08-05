.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Mon  4 Nov 20:58:04 2013 CET

.. testsetup:: *

   import bob.db.iris

=============
 Users Guide
=============

A description of the feature vector can be obtained using the attribute
:py:attr:`bob.db.iris.names`.

.. doctest::
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

   >>> descriptor_labels = bob.db.iris.names
   >>> descriptor_labels
   ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width']

The data (feature vectors) can be retrieved using the
:py:meth:`bob.db.iris.data` function. This returns a 3-key dictionary, with
3 :py:class:`numpy.ndarray` as values, one for each of the three species of
Iris flowers.

.. doctest::
   :options: +NORMALIZE_WHITESPACE, +ELLIPSIS

  >>> data = bob.db.iris.data()
  >>> type(data['setosa'])
  <... 'numpy.ndarray'>
  >>> data['setosa'].shape
  (50, 4)
  >>> list(data.keys()) # doctest: +SKIP
  ['setosa', 'versicolor', 'virginica']

Each :py:class:`numpy.ndarray` consists of 50 feature vectors of length four.

The database also contains statistics about the feature vectors, which can be
obtained using the :py:attr:`bob.db.iris.stats` dictionary. A description
of these statistics is provided by :py:attr:`bob.db.iris.stat_names`.


Classifying the Iris Flowers with LDA
-------------------------------------

As an exemplary use case, we provide a script ``./bin/iris_lda.py`` that computes a Linear Discriminant Analysis (LDA) using the :py:class:`bob.learn.linear.FisherLDATrainer` using all data vectors.
Afterward, it classifies all training data and plots histograms of the data projected on the first LDA component.
A detailed explanation of this example script is given :ref:`here <iris_example>`.

