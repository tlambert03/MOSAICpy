from qtpy import QtCore, QT_VERSION

# from raven import Client, fetch_git_sha, fetch_package_version, breadcrumbs

import sentry_sdk
from sentry_sdk.integrations.logging import ignore_logger

import traceback
import mosaicpy
import sys
import platform
import re
import os
import uuid
import logging
from mosaicpy.gui import settings, SETTINGS

logger = logging.getLogger(__name__)

try:
    from urllib.request import urlopen
except ImportError:
    from urllib import urlopen


def fetch_package_version(dist_name):
    """
    >>> fetch_package_version('sentry')
    """
    try:
        # Importing pkg_resources can be slow, so only import it
        # if we need it.
        import pkg_resources
    except ImportError:
        # pkg_resource is not available on Google App Engine
        raise NotImplementedError(
            "pkg_resources is not available " "on this Python install"
        )
    try:
        dist = pkg_resources.get_distribution(dist_name)
        return dist.version
    except pkg_resources.DistributionNotFound:
        return "Not Found"


def fetch_git_sha(path, head=None):
    """
    >>> fetch_git_sha(os.path.dirname(__file__))
    """
    if not head:
        head_path = os.path.join(path, ".git", "HEAD")
        if not os.path.exists(head_path):
            raise Exception("Cannot identify HEAD for git repository at %s" % (path,))

        with open(head_path, "r") as fp:
            head = str(fp.read()).strip()

        if head.startswith("ref: "):
            head = head[5:]
            revision_file = os.path.join(path, ".git", *head.split("/"))
        else:
            return head
    else:
        revision_file = os.path.join(path, ".git", "refs", "heads", head)

    if not os.path.exists(revision_file):
        if not os.path.exists(os.path.join(path, ".git")):
            raise Exception(
                "%s does not seem to be the root of a git repository" % (path,)
            )

        packed_file = os.path.join(path, ".git", "packed-refs")
        if os.path.exists(packed_file):
            with open(packed_file) as fh:
                for line in fh:
                    line = line.rstrip()
                    if line and line[:1] not in ("#", "^"):
                        try:
                            revision, ref = line.split(" ", 1)
                        except ValueError:
                            continue
                        if ref == head:
                            return str(revision)

        raise Exception('Unable to find ref to head "%s" in repository' % (head,))

    with open(revision_file) as fh:
        return str(fh.read()).strip()


tags = {}
env = "development"
if hasattr(sys, "_MEIPASS"):
    env = "pyinstaller"
elif "CONDA_PREFIX" in os.environ:
    env = "conda"

try:
    tags["revision"] = fetch_git_sha(
        os.path.dirname(os.path.dirname(sys.modules["mosaicpy"].__file__))
    )[:12]
except Exception:
    pass

if sys.platform.startswith("darwin"):
    tags["os"] = "OSX_{}".format(platform.mac_ver()[0])
elif sys.platform.startswith("win32"):
    tags["os"] = "Windows_{}".format(platform.win32_ver()[1])
else:
    tags["os"] = "{}".format(platform.linux_distribution()[0])

# try:
#     tags['gpu'] = gpulist()
# except CUDAbinException:
#     tags['gpu'] = 'no_cudabin'
#     logger.error("CUDAbinException: Could not get gpulist")

tags["pyqt"] = QT_VERSION
for p in ("numpy", "pyopencl", "pyopengl", "spimagine", "gputools", "mosaicpy"):
    try:
        tags[p] = fetch_package_version(p)
    except Exception:
        pass

ip = ""
try:
    ip = re.search('"([0-9.]*)"', str(urlopen("http://ip.jsontest.com/").read())).group(
        1
    )
except Exception:
    pass

if SETTINGS.value(settings.ALLOW_BUGREPORT.key):
    logger.info("Initializing Sentry Bug Logging")
    sentry_sdk.init(
        "https://95509a56f3a745cea2cd1d782d547916:e0dfd1659afc4eec83169b7c9bf66e33@sentry.io/221111",
        release=mosaicpy.__version__,
        in_app_include=["mosaicpy", "spimagine", "gputools"],
        environment=env,
    )
    with sentry_sdk.configure_scope() as scope:
        scope.user = {"id": uuid.getnode(), "ip_address": ip}
        for key, value in tags.items():
            scope.set_tag(key, value)

ignore_logger("OpenGL.GL.shaders")
ignore_logger("PIL.PngImagePlugin")


def camel2spaces(string):
    return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-R,T-Z](?=[a-z]))", r" \1", string)


class MOSAICpyError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, msg=None, detail=""):
        if msg is None:
            msg = "An unexpected error occured in MOSAICpy"
        super(MOSAICpyError, self).__init__(msg)
        self.msg = msg
        self.detail = detail


class InvalidSettingsError(MOSAICpyError):
    """Exception raised when something is not set correctly in the GUI."""

    pass


class MissingBinaryError(MOSAICpyError):
    """Unable to find executable or shared library dependency."""

    pass


class RegistrationError(MOSAICpyError):
    """Unable to find executable or shared library dependency."""

    pass


class ExceptionHandler(QtCore.QObject):
    """General class to handle all raise exception errors in the GUI"""

    # error message, title, more info, detail (e.g. traceback)
    errorMessage = QtCore.Signal(str, str, str, str)

    def __init__(self):
        super(ExceptionHandler, self).__init__()

    def handler(self, etype, value, tb):
        err_info = (etype, value, tb)
        if isinstance(value, MOSAICpyError):
            self.handleMOSAICpyError(*err_info)
        elif isinstance(value, mosaicpy.processplan.ProcessPlan.ProcessError):
            self.handleProcessError(*err_info)
        elif "0xe06d7363" in str(value).lower():
            self.handleCUDA_CL_Error(*err_info)
        else:  # uncaught exceptions go to sentry
            self.send_to_sentry(err_info)
            detail = "".join(traceback.format_exception(*err_info))
            self.errorMessage.emit(str(value), etype.__name__, "", detail)
            print("\n" + "!" * 50)
            traceback.print_exception(*err_info)

    def send_to_sentry(self, err_info):
        if SETTINGS.value(settings.ALLOW_BUGREPORT.key, True):
            logger.info("Sending bug report")
            try:
                sentry_sdk.capture_exception(err_info)
            except Exception:
                pass

    def handleMOSAICpyError(self, etype, value, tb):
        tbstring = "".join(traceback.format_exception(etype, value, tb))
        title = camel2spaces(etype.__name__).strip(" Error")
        self.errorMessage.emit(value.msg, title, value.detail, tbstring)

    def handleCUDA_CL_Error(self, etype, value, tb):
        if SETTINGS.value(settings.ALLOW_BUGREPORT.key, True):
            logger.info("Sending bug report")
            sentry_sdk.capture_exception((etype, value, tb))
        tbstring = "".join(traceback.format_exception(etype, value, tb))
        self.errorMessage.emit(
            "Sorry, it looks like CUDA and OpenCL are not "
            "getting along on your system",
            "CUDA/OpenCL clash",
            "If you continue to get this error, please "
            'click the "disable Spimagine" checkbox in the config tab '
            "and restart MOSAICpy.  To report this bug or get updates on a fix, "
            "please go to https://github.com/tlambert03/MOSAICpy/issues/2 and "
            "include your system configuration in any reports.  Thanks!",
            tbstring,
        )

    def handleProcessError(self, etype, value, tb):
        self.send_to_sentry((etype, value, tb))
        title = "ProcessError"
        tbstring = "".join(traceback.format_exception(etype, value, tb))
        info = str(value.__cause__ or value)
        info += (
            f"\n\nIf the {value.imp.name()} processor is a custom plugin, you may "
            + "want to send the author the stack trace in the details below."
        )
        self.errorMessage.emit(str(value), title, info, tbstring)
