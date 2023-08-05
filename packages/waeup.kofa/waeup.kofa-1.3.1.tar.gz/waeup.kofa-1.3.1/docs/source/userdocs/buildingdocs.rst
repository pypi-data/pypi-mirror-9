.. _building_documentation:

Building Documentation (Linux OS only)
**************************************

We use the excellent `Sphinx <http://sphinx.pocoo.org/>`_ Python
documentation generator to generate the docs as HTML pages.

Prerequisites
=============

We assume you already installed `waeup.kofa` as explained in
:ref:`installing_linux`. You ran ``bin/buildout`` and can find a script
``bin/waeupdocs``.

Building HTML docs
==================

The documentation of the :mod:`waeup.kofa` project can easily be
created doing::

  $ bin/waeupdocs

This will create a tree of HTML pages in
``docs/build/html`` which you can for
instance browse by pointing your browser to this location.

An 'official' place in internet for the whole docs is about to come
but not yet available.

Actually, ``waeupdocs`` is only a wrapper script around the real main
script ``sphinx-build``, which should also be located in your ``bin/``
directory.

You therefore can also run ``bin/sphinx-build`` manually, which will
give you more options, especially, if you want the output to be
created in a different location or similar.

Run::

   $ bin/sphinx-build --help

to get a list of options available.

Alternatively, you can also go to ``docs/build`` and run::

   $ make html

Other available formats are listed, when you run only::

   $ make

These other formats will include ``latex``, ``doctest``, ``linkcheck``
and more with a short explanation for each format.

Building PDF docs
=================

We're currently not prepared for PDF, but support is already planned.

Please be aware, that any PDF support will require a full TeX
installation on your system to work.
