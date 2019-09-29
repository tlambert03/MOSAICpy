from PyQt5 import QtCore
import logging
import os
from appdirs import user_data_dir
from llspy import __appname__

# platform independent settings file
QtCore.QCoreApplication.setOrganizationName("llspy")
QtCore.QCoreApplication.setOrganizationDomain("llspy.com")
QtCore.QCoreApplication.setApplicationName("LLSpy")

from .settings import SETTINGS  # noqa

# clear with:
# killall -u talley cfprefsd

logger = logging.getLogger()  # set root logger
# lhStdout = logger.handlers[0]   # grab console handler so we can delete later
ch = logging.StreamHandler()  # create new console handler
ch.setLevel(logging.DEBUG)  # with desired logging level
ch.addFilter(logging.Filter("llspy"))  # and any filters
logger.addHandler(ch)  # add it to the root logger
# logger.removeHandler(lhStdout)  # and delete the original streamhandler

APP_DIR = user_data_dir(__appname__)
IMP_DIR = os.path.join(APP_DIR, "plugins")
PLAN_DIR = os.path.join(APP_DIR, "process_plans")
REG_DIR = os.path.join(APP_DIR, "regfiles")
LOG_PATH = os.path.join(APP_DIR, "llspygui.log")

if not os.path.isdir(APP_DIR):
    os.mkdir(APP_DIR)
