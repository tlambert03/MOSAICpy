from mosaicpy.imgprocessors import ImgProcessor, ImgWriter
from mosaicpy.llsdir import LLSdir


class ProcessPlan(object):
    """A class to store the processing plan for a given data directory and set of Imps

    The ProcessPlan is responsible for accepting a data direcory, an ordered list of
    ImgProcessors, and an optional t_range and c_range for processing.  It also creates
    the self.meta dict, which will hold and pass metadata throughout the processing chain.

    Args:
        llsdir (LLSdir): instance of LLSdir, the data directory.
        imps (list): A list of 3 or 4-tuples, where each item contains:
            1. (ImgProcessor) The image processor class (uninstantiated)
            2. (dict) - The params dict that will be passed to ImgProcessor on instantiation
            3. (bool) - Whether the ImgProcessor is active or not
            4. (bool, optional) - Whether the ImgProcessor is collapsed in the GUI
        t_range (list): a list of timepoints to process.  Defaults to all timepoints
        c_range (list): a list of channels to process.  Defaults to all channels
    """

    def __init__(self, llsdir, imps=[], t_range=None, c_range=None):
        if not isinstance(llsdir, LLSdir):
            raise ValueError("First argument to ProcessPlan must be an LLSdir")
        assert isinstance(imps, (list, tuple)), (
            "imps argument must be a " "list or tuple"
        )
        for imp in imps:
            if not len(imp) >= 3:
                raise ValueError('all items in "imps" must have a length of >= 3')
            if not issubclass(imp[0], ImgProcessor):
                raise ValueError('imp item "{}" is not an ImgProcessor'.format(imp))
        self.llsdir = llsdir
        self.imp_classes = imps
        self.t_range = t_range or list(range(llsdir.params.nt))
        self.c_range = c_range or list(range(llsdir.params.nc))
        self.aborted = False
        self.meta = None

    @property
    def ready(self):
        return hasattr(self, "imps") and len(self.imps)

    def check_sanity(self):
        # sanity checkes go here...
        warnings = []
        writers = [
            issubclass(imp, ImgWriter) for imp, p, act, _ in self.imp_classes if act
        ]
        if not any(writers):
            warnings.append("No Image writer/output detected.")
        try:
            idx_of_last_writer = list(reversed(writers)).index(True)
        except ValueError:
            idx_of_last_writer = False
        if idx_of_last_writer:
            warnings.append("You have image processors after the last Writer")

        if warnings:
            raise self.PlanWarning("\n".join(warnings))

    def plan(self, skip_warnings=False):
        """This actually instantiates the ImgProcessors (but does not run them).

        Unless explicitly skipped, it runs check_sanity() to look for potential
        problems in the plan.  Then in instantiates all active image processors,
        by calling the ImgProcessor.from_llsdir() class method.

        It also creates the self.meta object that will be passed through the processing
        chain.

        Raises:
            self.PlanWarning: if check_sanity() fails
            self.PlanError: if ImgProcessor instantiation fails
        """
        if not skip_warnings:
            self.check_sanity()

        errors = []
        self.imps = []  # will hold instantiated imps
        for imp_tup in self.imp_classes:
            imp, params, active = imp_tup[:3]
            if not active:
                continue
            try:
                self.imps.append(imp.from_llsdir(self.llsdir, **params))
            except imp.ImgProcessorError as e:
                errors.append("%s:  " % imp.name() + str(e))
            except Exception as e:
                import traceback

                traceback.print_exc()
                errors.append("%s:  " % imp.name() + str(e))

        if errors:
            # FIXME: should probably only clobber broken imps, not all imps
            self.imps = []
            raise self.PlanError(
                "Cannot process .../{} due the following errors:\n\n".format(
                    self.llsdir.path.name
                )
                + "\n\n".join(errors)
            )
        self.meta = {
            "c": self.c_range,
            "nc": len(self.c_range),
            "nt": len(self.t_range),
            "w": [self.llsdir.params.wavelengths[i] for i in self.c_range],
            "params": self.llsdir.params,
            "has_background": True,  # whether background has been subtracted yet
            "axes": None,
        }

    def setup_t(self, data):
        """Called before all ImgProcs, at every timepoint."""
        for n, imp in enumerate(self.imps):
            try:
                imp.setup_t(data, self.meta)
            except Exception as err:
                raise self.SetupError(imp, n) from err

    def teardown_t(self, data):
        """Called after every ImgProcs, at every timepoint."""
        for n, imp in enumerate(self.imps):
            try:
                imp.teardown_t(data, self.meta)
            except Exception as err:
                raise self.TeardownError(imp, n) from err

    def execute(self):
        """executes the processing plan, iterating over timepoints"""
        for t in self.t_range:
            if self.aborted:
                break
            data = self.llsdir.data.asarray(t=t, c=self.c_range)
            self.meta["t"] = t
            self.meta["axes"] = data.axes
            self.setup_t(data)
            try:
                yield self._execute_t(data)
            finally:
                self.teardown_t(data)

    def _execute_t(self, data):
        return self._iterimps(data)

    def _iterimps(self, data):
        for n, imp in enumerate(self.imps):
            try:
                data, self.meta = imp(data, self.meta)
            except Exception as err:
                raise self.ProcessError(imp, n) from err
        return data, self.meta

    class PlanError(Exception):
        """ hard error if the plan cannot be executed as requested """

        pass

    class PlanWarning(Exception):
        """ light error, if a plan has ill-advised steps """

        pass

    class ProcessError(Exception):
        """ error occured during processing """

        def __init__(self, imp, position=None):
            self.msg = f"ProcessError in ImgProcessor <{imp.name()}>"
            self.msg += f" at position {position + 1}" if position is not None else ""
            super().__init__(self.msg)
            self.imp = imp  # the img processor that cause the error
            self.position = position  # the position of the Imp that cause the problem

    class SetupError(ProcessError):
        pass

    class TeardownError(ProcessError):
        pass


class PreviewPlan(ProcessPlan):
    """ Subclass of ProcessPlan that strips all ImgWriters and turns
    execute into a generator
    """

    def __init__(self, *args, **kwargs):
        super(PreviewPlan, self).__init__(*args, **kwargs)
        # remove any writers
        self.imp_classes = [
            i for i in self.imp_classes if not issubclass(i[0], ImgWriter)
        ]

    def check_sanity(self):
        # overwriting parent method that looks for writers
        pass
