from mosaicpy import ImgProcessor


class ExamplePlugin(ImgProcessor):
    """Just an example plugin.

    This docstring will be available in the "?" menu in the GUI. Put stuff here that will
    help the user understand what the parameters (declared in the __init__ method) mean.

    Args:
        greeting (str): This will be printed to the console during processing
        print_shape (bool): Whether to print the shape of the array to the console
    """

    def __init__(self, greeting="Hello!", print_shape=True):
        """The parameters in the __init__ function will be exposed to the user in the GUI.
        All parameters should be named (not positional), and should be given default values
        with the appropriate type.  MOSAICpy will use the type of the default argument to
        determine what type of widget to use in the gui (i.e. text field, checkbox, etc).
        """
        super().__init__()
        self.greeting = greeting
        self.print_shape = print_shape

    def process(self, data, meta):
        """The process method must be declared.

        It should accept two arguments: data, meta
        It can do anything in the body of the function, but it must return a two-tuple
        containing the data and the metadata, either/both of which may be changed in the
        process.
        """
        print(self.greeting)
        if self.print_shape:
            print(f"the shape of the data is {data.shape}")
        return data, meta
