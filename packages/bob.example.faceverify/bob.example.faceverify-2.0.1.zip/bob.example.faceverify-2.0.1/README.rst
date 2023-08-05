.. vim: set fileencoding=utf-8 :
.. Manuel Guenther <manuel.guenther@idiap.ch>
.. Thu Sep  4 11:35:05 CEST 2014

.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.example.faceverify/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.example.faceverify/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.example.faceverify.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.example.faceverify
.. image:: https://coveralls.io/repos/bioidiap/bob.example.faceverify/badge.png
   :target: https://coveralls.io/r/bioidiap/bob.example.faceverify
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.example.faceverify/tree/master
.. image:: http://img.shields.io/pypi/v/bob.example.faceverify.png
   :target: https://pypi.python.org/pypi/bob.example.faceverify
.. image:: http://img.shields.io/pypi/dm/bob.example.faceverify.png
   :target: https://pypi.python.org/pypi/bob.example.faceverify

===================================================
 Exemplary Face Verification Experiments Using Bob
===================================================

This example demonstrates how to use Bob to build three different face verification systems.
It includes examples with three different complexities:

* A simple eigenface based example
* An example using Gabor jets in a grid graph
* An example building an UBM/GMM model on top of DCT blocks.

The face verification experiments are executed on the `AT&T`_ database, which is a toy database that is perfectly useful for this example, but **not** to publish scientific papers.
Anyways, the functionality inside this package will work with any other face verification database of Bob_.


Installation
------------
To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_.
For Bob_ to be able to work properly, some dependent packages are required to be installed.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------
For further documentation on this package, please read the `Stable Version <http://pythonhosted.org/bob.example.faceverify/index.html>`_ or the `Latest Version <https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.example.faceverify/master/index.html>`_ of the documentation.
For a list of tutorials on this or the other packages ob Bob_, or information on submitting issues, asking questions and starting discussions, please visit its website.

.. _bob: https://www.idiap.ch/software/bob
.. _at&t: http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html


