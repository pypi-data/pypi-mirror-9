.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Wed Nov  5 19:56:23 CET 2014

.. _bob.example.faceverify:

===================================================
 Exemplary Face Verification Experiments Using Bob
===================================================

This example demonstrates how to use Bob_ to build three different face verification systems.
It includes examples with three different complexities:

* A simple eigenface based example
* An example using Gabor jets in a grid graph
* An example building an UBM/GMM model on top of DCT blocks.

The face verification experiments are executed using the protocols for the `AT&T`_  database implemented in :ref:`bob.db.atnt <bob.db.atnt>`.
However, the code is set up such that it will work with any other of the :ref:`verification_databases` as well.

.. warning::
   The `AT&T`_ database is a toy database that is perfectly useful for this example, but **not** to publish scientific papers.

.. toctree::
   :maxdepth: 2

   installation
   examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. _bob: https://www.idiap.ch/software/bob
.. _at&t: http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html

