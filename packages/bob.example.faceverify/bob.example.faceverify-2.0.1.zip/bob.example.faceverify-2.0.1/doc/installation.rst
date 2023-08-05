.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Wed Nov  5 19:56:23 CET 2014

==============
 Installation
==============

.. note::

  To follow these instructions locally you will need a local copy of this package.
  Please go to the `PyPI page of this package <http://pypi.python.org/pypi/bob.example.faceverify>`_ and download the ``.zip`` file using the ``Download`` button in the top-right of the page.
  Unzip the package in a directory of your choice and open a console window in this directory.

  You also might want to use the latest version of this package, which you can obtain from GitHub_:

  .. code-block:: sh

    $ git clone https://github.com/bioidiap/bob.example.faceverify.git
    $ cd bob.example.faceverify

Installation of this example uses the `buildout <http://www.buildout.org/>`_ building environment.
You don't need to understand its inner workings to use this package.
Here is a recipe to get you started:

.. code-block:: sh

  $ python bootstrap.py
  $ ./bin/buildout

These 2 commands should download and install all non-installed dependencies and get you a fully operational test and development environment.
Particularly, it will download and compile all required packages of Bob_.
Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ of Bob_ for your operating system.

.. note::
   Compiling the packages of Bob_ might take a while.


Download the Test Database
~~~~~~~~~~~~~~~~~~~~~~~~~~
The images that are required to run the test are not included in this package, but they are freely downloadable from http://www.cl.cam.ac.uk/research/dtg/attarchive/facedatabase.html

Unpack the database in a directory that fits you.
The easiest solution is to create a sub-directory ``Database`` in this package.
If you decide to put the data somewhere else, please remember the image directory.


Verify your Installation
~~~~~~~~~~~~~~~~~~~~~~~~
To verify your installation, you might want to run the unit tests that are provided with this package.
For this, the AT&T database is required to be either in the ``Database`` sub-directory of this package (see above), or that the ``ATNT_DATABASE_DIRECTORY`` environment variable points to your database directory.
At Idiap, you might want to use:

.. code-block:: sh

  $ export ATNT_DATABASE_DIRECTORY=/YOUR/ATNT/IMAGE/DIRECTORY
  $ bin/nosetests -v

.. _bob: https://www.idiap.ch/software/bob
.. _github: https://www.github.com
