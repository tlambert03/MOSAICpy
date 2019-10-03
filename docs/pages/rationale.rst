Rationale
=========


**Why would you do this in Python instead of** [*insert your favorite compiled
language here*] **?**

This is a classic
"`python as glue <https://www.python.org/doc/essays/omg-darpa-mcc-position/>`_"
app.  MOSAICpy itself is more of a framework for chaining individual image
processing steps together. Each processing step can actually be written in
whatever language you want, you just need to write a simple wrapper (a subclass
of :code:`ImgProcessor`) to hand control over to your subroutines.

On the other hand, using python as "glue" allows for rapid development of some
of the less computationally demanding parts of the image processing chain, such
as detecting the format of a data directory and parsing metadata.  It is also
open source and accessible, allowing anyone to write a simple extension.  If
you would like to speed up your extension, there are plenty of ways to do so.

Tips for writing faster extensions
----------------------------------

* Use a just-in-time compiler like `numba <http://numba.pydata.org/>`_ to
  to accelerate frequently-called functions that may be computationally
  intensive.  An example in this library is
  :func:`mosaicpy.camera.calc_correction`
* Use a python gpu-acceleration library like
  `cupy <https://cupy.chainer.org/>`_, `pytorch <https://pytorch.org/>`_, or
  `gputools <https://github.com/maweigert/gputools>`_.  I find
  `cupy <https://cupy.chainer.org/>`_ to be particularly nice, as it can often
  be used as a drop-in replacement for numpy, leveraging CUDA libraries in the
  background... Letting you develop in numpy, or fall-back to numpy when a GPU
  is not available.
* Write a python extension for C++ code using something like
  `cython <https://cython.org/>`_,
  `pybind11 <https://github.com/pybind/pybind11>`_,
  `ctypes <https://docs.python.org/3/library/ctypes.html>`_,
  `cffi <https://cffi.readthedocs.io/en/latest/>`_, etc...
  In this library, the :mod:`mosaicpy.libcudawrapper` module is an example of
  using ctypes to access compiled shared libraries written in C++ from within
  python.
* Just call some external binary using the
  `subprocess <https://docs.python.org/3.7/library/subprocess.html>`_ module
  from the standard python library.  While it will be hard to truly "chain"
  together mosaicpy.ImgProcessors written using subprocesses, it might be the
  simplest way to simply trigger some external program at some stage in the
  processing pipeline.
