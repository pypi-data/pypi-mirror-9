.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu  3 Apr 13:47:28 2014 CEST
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _bob.ip.optflow.hornschunck:

============================================================
 Python Bindings to Horn & Schunck's Optical Flow Framework
============================================================

.. todolist::

This package is a simple Python wrapper to an open-source Optical Flow estimator based on the works by `Horn & Schunck`_:

.. code-block:: latex

  @article{Horn_Schunck_1981,
    author = {Horn, B. K. P. and Schunck, B. G.},
    title = {Determining optical flow},
    year = {1981},
    booktitle = {Artificial Intelligence},
    volume = {17},
    pages = {185--203},
  }

The implementation is purely based on Bob_:

.. code-block:: latex

  @inproceedings{Anjos_ACMMM_2012,
    author = {Anjos, Andr\'e AND El Shafey, Laurent AND Wallace, Roy AND G\"unther, Manuel AND McCool, Christopher AND Marcel, S\'ebastien},
    title = {Bob: a free signal processing and machine learning toolbox for researchers},
    year = {2012},
    month = oct,
    booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
    publisher = {ACM Press},
    url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
  }

Documentation
-------------

.. toctree::
   :maxdepth: 2

   guide
   py_api

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. include:: links.rst

.. Place your references here:

.. _horn & schunck: https://en.wikipedia.org/wiki/Horn%E2%80%93Schunck_method
