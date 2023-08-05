"""
    airbrake-python
    ~~~~~~~~~~~~~~~

    Client for sending python exceptions to airbrake.io
"""

__version__ = "1.1.4"
__url__ = "https://github.com/airbrake/airbrake-python"
_notifier = {
    'name': 'airbrake-python',
    'version': __version__,
    'url': __url__
}

import inspect
import logging
import os

from airbrake import utils
from airbrake.notifier import Airbrake
from airbrake.handler import AirbrakeHandler

logging.basicConfig()


def getLogger(name=None, **kwargs):

    if not name:
        curframe = inspect.currentframe()
        callingpath = inspect.getouterframes(curframe, 2)[1][1]
        name = os.path.split(
            callingpath.rpartition('.')[0] or callingpath)[-1]
        name = "%s%s" % ('airbrake-python-', name)
    logger = logging.getLogger(name)

    if not has_airbrake_handler(logger):
        ab = AirbrakeHandler(**kwargs)
        logger.addHandler(ab)
        if logger.getEffectiveLevel() == logging.NOTSET:
            logger.setLevel(ab.level)
        elif not logger.isEnabledFor(ab.level):
            logger.setLevel(ab.level)

    return logger


def has_airbrake_handler(logger):
    return any([isinstance(handler, AirbrakeHandler)
                for handler in logger.handlers])
