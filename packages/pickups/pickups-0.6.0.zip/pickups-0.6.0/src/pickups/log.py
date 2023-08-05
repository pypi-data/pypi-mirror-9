import logging
import sys

# Default log level defined for pickups
DEFAULT_LOGGING_LEVEL = logging.INFO
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)s()]: '%(message)s']"


def setup_pickups_logger():
    """Setup pickups top-level logger with a StreamHandler

    Logger's root name is `pickups`.

    :returns: None
    :rtype: None
    :raises: None
    """
    log = logging.getLogger("pickups")
    log.propagate = False
    handler = logging.StreamHandler(stream=sys.stdout)
    fmt = FORMAT
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    level = DEFAULT_LOGGING_LEVEL
    log.setLevel(level)


def get_logger(name, level=None):
    """ This method returns a logger for the given name, configured using the above defined defaults.
    One would use this in a module like::

        from pickups.log import get_logger
        log = get_logger(__name__)

    :param name: Name of the requested logger. Best is to stay with `__name__`. Pickups logger will append this to the
                 root name.
    :type name: str
    :param level: one of :mod:`logging` levels (eg. DEBUG, INFO, CRITICAL, ...)
    :type level: int
    :returns: Logger
    :rtype: logging.Logger
    :raises: None
    """
    log = logging.getLogger("pickups.%s" % name)
    if level is not None:
        log.setLevel(level)
    return log


setup_pickups_logger()
