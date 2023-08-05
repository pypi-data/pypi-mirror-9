.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Tue  1 Apr 12:32:06 2014 CEST


.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.ip.optflow.hornschunck/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.ip.optflow.hornschunck/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.ip.optflow.hornschunck.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.ip.optflow.hornschunck
.. image:: https://coveralls.io/repos/bioidiap/bob.ip.optflow.hornschunck/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.ip.optflow.hornschunck
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.ip.optflow.hornschunck/tree/master
.. image:: http://img.shields.io/pypi/v/bob.ip.optflow.hornschunck.png
   :target: https://pypi.python.org/pypi/bob.ip.optflow.hornschunck
.. image:: http://img.shields.io/pypi/dm/bob.ip.optflow.hornschunck.png
   :target: https://pypi.python.org/pypi/bob.ip.optflow.hornschunck

============================================================
 Python Bindings to Horn & Schunck's Optical Flow Framework
============================================================

This package is a simple Python wrapper to an open-source Optical Flow estimator based on the works by `Horn & Schunck`_::

  @article{Horn_Schunck_1981,
    author = {Horn, B. K. P. and Schunck, B. G.},
    title = {Determining optical flow},
    year = {1981},
    booktitle = {Artificial Intelligence},
    volume = {17},
    pages = {185--203},
  }

The implementation is purely based on Bob_::

  @inproceedings{Anjos_ACMMM_2012,
    author = {Anjos, Andr\'e AND El Shafey, Laurent AND Wallace, Roy AND G\"unther, Manuel AND McCool, Christopher AND Marcel, S\'ebastien},
    title = {Bob: a free signal processing and machine learning toolbox for researchers},
    year = {2012},
    month = oct,
    booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
    publisher = {ACM Press},
    url = {http://publications.idiap.ch/downloads/papers/2012/Anjos_Bob_ACMMM12.pdf},
  }

This package also provides a unit testing framework, to check on the accuracy of results produced in different platforms.
The testing framework also requires OpenCV_ for comparison purposes.


Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.ip.optflow.hornschunck/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.ip.optflow.hornschunck/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.

.. _bob: https://www.idiap.ch/software/bob
.. _opencv: http://opencv.org
.. _horn & schunck: https://en.wikipedia.org/wiki/Horn%E2%80%93Schunck_method

