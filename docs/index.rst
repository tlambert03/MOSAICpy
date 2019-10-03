Welcome to MOSAICpy's documentation!
====================================

.. note:: **This is an unfinished project, with lots of broken code**

    Most of the work so far has gone into establishing a framework for image
    processors and plans (pipelines), but many of the current
    :class:`ImgProcessors` are just stubs and do not work.

    If you are helping to test, please feel free to log requests or notes
    about bugs & broken bits in the
    `github issue tracker <https://github.com/tlambert03/MOSAICpy/issues>`_.

The Basic Idea
==============

MOSAICpy (i.e. "LLSpy2") is a modular image processing app written in Python.
The basic idea is to string together a series of processing steps
(see :ref:`img-processors`), each of which accept a multi-dimensional
numpy array and metadata as input, perform some actions on or with the image,
and pass it (or a modified version of it) down the chain for further
processing.  The actions may be standard image processing, like a flatfield
correction, cropping, or deconvolution, etc..., but they can be anything you
can code in python, such reading/writing to disk/network, or connecting to a
server.

MOSAICpy builds a GUI, even for user-written plugins, by introspecting the
function signature.  Hopefully, this will enable people to add custom steps to
their image processing pipeline without needing to request major changes to the
MOSAICpy program itself.

A series of :class:`ImgProcessors` is called a :class:`ProcessPlan` (see
:ref:`process-plans`).  The GUI lets you rearrange, activate/deactivate, add,
or remove :class:`ImgProcessors`.  Plans can be saved and reloaded, and shared
with others.

A concept still in development is modular :class:`DataReaders`, and
:class:`ImgWriters`.  DataReaders will recognize input data in some particular
format (i.e. a lattice light sheet dataset, or a 3D-SIM dataset) based on some
attribute present in the metadata, or file structure.  By adding
:class:`DataReaders`, MOSAICpy will gradually be able to handle data in a
greater number of formats (again, without rewriting the core program).
:class:`ImgWriters`, lie at the end of the :class:`ProcessPlan`, and take care
of output; for instance: writing a Tiff file to disc, or uploading to a server.

With the added flexibility will certainly come some hiccups and bugs, which I
hope to gradually work out, eventually developing some well-working
:class:`ProcessPlan`

.. image:: ../img/screen.png
    :align: center



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   pages/rationale
   pages/imgprocessors
   pages/processplans

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
