.. role:: python(code)
    :language: python

The :code:`ImgProcessor` Class
==============================

The :class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>` is
the key class that controls the flow of image processing in MOSAICpy. Each
processor accepts a numpy array (the data) along with the metadata object, does
*something* with the data and/or metadata, then passes them both on to the next
processor.  MOSAICpy takes care of converting all
:class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>` s into a
graphical interface in the MOSAICpy GUI, by introspecting the :func:`__init__`
signature for parameter names, types, and default values.

All :class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`
subclasses should override the :func:`process` method.

A very simple
:class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`
might look something like this.

.. code:: python

    from llspy import ImgProcessor

    class Plugin(ImgProcessor):
        """ This Processor simply prints the shape of the
        data to the console."""

        def process(data, meta):
            print(f"The shape of this data is {data.shape}")
            return data, meta

:class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`
**options:**

- **verbose_name** - Provide a :code:`verbose_name` class attribute to change
  how the name of the processor appears in the GUI.  Otherwise, the name of the
  class will be used in the GUI with :code:`CamelCaseWord` split into
  :code:`Camel Case Word`
- **processing_verb** - Provide a :code:`processing_verb` class attribute to
  change the message shown in the status bar during processing.
- **gui_layout** - To override the way the widgets are laid out in the GUI,
  override the :code:`gui_layout` class attribute, providing a dict of
  :code:`{'parameter': (row,column)}` key-value pairs, where :code:`parameter`
  matches one of the arguments in the :func:`__init__` method.
- **valid_range** - To restrict the acceptable range of numeric parameters,
  override the :code:`valid_range` class attribute, providing a dict of
  :code:`{'parameter': (min, max)}` key-value pairs, where :code:`parameter`
  matches one of the arguments in the :func:`__init__` method, the tuple
  contains the min and max valid values accepted by that parameter.
- **guidoc:** - To provide a brief help string in the GUI, put the word
  :code:`guidoc:` (with the colon) anywhere in the class docstring.  Everything
  between the :code:`guidoc:` string and the line ending will be extracted and
  shown in the GUI.
- **verbose_help** - To provide more extensive documentation, provide a
  :code:`verbose_help` class attribute with a string value (can be a multiline
  string). If provided, a help button will appear at the top right of the
  widget, which, when clicked, will show a popup with the contents of
  :code:`verbose_help`

As an example, here is an
:class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`
as rendered in the GUI, and the corresponding python class

.. image:: ../img/medianfilter.png


.. code-block:: python

    from mosaicpy.camera import selectiveMedianFilter
    from mosaicpy import ImgProcessor

    class SelectiveMedianProcessor(ImgProcessor):
        """correct noisy pixels on sCMOS camera.

        guidoc: selective median filter as in Amat 2015
        """
        # ^ note - when "guidoc:" appears in the docstring, that line will
        # be extracted and will appear at the bottom right of the widget.

        # `verbose_name` changes the name as it appears in the gui
        verbose_name = 'Selective Median Filter'

        # `processing_verb` changes the feedback string during processing
        processing_verb = 'Performing Median Filter'

        # to override the way the widgets are laid out, provide a dict to
        # `gui_layout`, where the keys are the names of parameters in the
        # __init__ function, and the values are 2-tuples of (row, column)
        # where you want that widget to appear
        gui_layout = {
            'background': (0, 1),
            'median_range': (0, 0),
            'with_mean': (0, 2),
        }

        # to limit the possible values for numerical inputs, provide
        # `valid_range` with a dict of parameter name keys and two-tuples
        # of (min, max) valid values.
        valid_range = {
            'background': (0, 1000),
            'median_range': (1, 9),
        }

        def __init__(self, background=0, median_range=3, with_mean=True):
            """The gui generates the appropriate widget value type by
            introspecting the default values in the function signature.
            The __init__ method should not perform any actual processing.
            """
            super(SelectiveMedianProcessor, self).__init__()
            self.background = background
            self.median_range = median_range
            self.with_mean = with_mean

        def process(self, data, meta):
            """perform the actual processing"""
            nc = len(meta.get('c'))
            ny, nx = data.shape[-2:]
            if nc > 1:
                data = data.reshape(-1, ny, nx)
            data, _ = selectiveMedianFilter(
                data,
                self.background,
                self.median_range,
                self.with_mean
            )
            if nc > 1:
                data = data.reshape(nc, -1, ny, nx)
            return data, meta

How :code:`ImgProcessors` are registered in the GUI
---------------------------------------------------

- The main :class:`ImpListContainer` instance creates an instance of
  :class:`ImpListWidget <llspy.gui.implist.ImpListWidget>`
- The :class:`ImpListWidget <llspy.gui.implist.ImpListWidget>`
  maintains a list of active
  :class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>` s.
- For each active
  :class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`, an
  :class:`ImpFrame <llspy.gui.implist.ImpFrame>` is instantiated.
- The :class:`ImpFrame <llspy.gui.implist.ImpFrame>` class builds a
  simple GUI from the
  :class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`
  :func:`__init__` method signature.

ImgProcessors may be added to the list by clicking the "Add Processor" button.
This opens an :class:`ImgProcessSelector <llspy.gui.implistImgProcessSelector>`
window which imports all files in the plugins folder whose filename
ends in :code:`.py`.  It then inspects the module for subclasses of
:class:`ImgProcessor <llspy.imgprocessors.imgprocessors.ImgProcessor>`.  *Only
subclasses that declare a* :func:`process` *method will be imported.*  The user
can then select one or more processors to be added to the main window.


.. image:: ../img/implist.png


.. automodule:: llspy.gui.implist
    :members: ImgProcessSelector, ImpListWidget, ImpFrame


Built in :code:`ImgProcessors`
------------------------------

.. automodule:: llspy.imgprocessors.imgprocessors
    :members: ImgProcessor, ImgWriter
