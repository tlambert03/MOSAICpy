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
you would like to speed up your extension, there are plenty of ways to do so:

* use a just-in-time compiler like `numba <http://numba.pydata.org/>`_ to
  to accelerate frequently-called functions that may be computationally
  intensive.
* use a python gpu-acceleration library like
  `cupy <https://cupy.chainer.org/>`_, `pytorch <https://pytorch.org/>`_, or 
  `gputools <https://github.com/maweigert/gputools>`_.
* write a python extension for C++ code using something like cython,
  pybind11, ctypes, swig, etc...
* just call some external binary using the subprocess module from the standard
  python library.