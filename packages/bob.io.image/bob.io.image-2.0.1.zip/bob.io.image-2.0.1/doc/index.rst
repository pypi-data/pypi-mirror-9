.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Wed 14 May 15:22:33 2014 CEST
..
.. Copyright (C) 2011-2014 Idiap Research Institute, Martigny, Switzerland

.. _bob.io.image:

===============================================
 Bob's I/O Routines for Images of Various type
===============================================

.. todolist::

This module provides a plugin for :py:mod:`bob.io.base` that allows |project|
to read and write images using its native API (:py:func:`bob.io.base.load` and
:py:func:`bob.io.base.save`).

At present, this plugin provides support for the following types of images:

* TIFF
* JPEG
* GIF
* PNG
* BMP
* Netpbm images (PGM, PPM, PBM)

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
