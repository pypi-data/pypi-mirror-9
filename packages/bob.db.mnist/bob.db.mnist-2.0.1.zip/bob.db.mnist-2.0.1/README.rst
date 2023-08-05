.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Fri Oct 31 14:18:57 CET 2014

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.db.mnist/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.db.mnist/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.db.mnist.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.db.mnist
.. image:: https://coveralls.io/repos/bioidiap/bob.db.mnist/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.db.mnist
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.db.mnist/tree/master
.. image:: http://img.shields.io/pypi/v/bob.db.mnist.png
   :target: https://pypi.python.org/pypi/bob.db.mnist
.. image:: http://img.shields.io/pypi/dm/bob.db.mnist.png
   :target: https://pypi.python.org/pypi/bob.db.mnist
.. image:: https://img.shields.io/badge/original-data--files-a000a0.png
   :target: http://yann.lecun.com/exdb/mnist

==================================
 MNIST Database Interface for Bob
==================================

The MNIST_ database is a database of handwritten digits, which consists of a training set of 60,000 examples, and a test set of 10,000 examples.
It was made available by Yann Le Cun and Corinna Cortes.
The data was originally extracted from a larger set made available by NIST_, before being size-normalized and centered in a fixed-size image (28x28 pixels).

This package only contains the Bob_ accessor methods to use this database directly from Python.
It does not contain the original raw data files, which need to be obtained through the link above.

Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.db.mnist/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.db.mnist/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.

.. _bob: https://www.idiap.ch/software/bob
.. _mnist: http://yann.lecun.com/exdb/mnist
.. _nist: http://www.nist.gov




