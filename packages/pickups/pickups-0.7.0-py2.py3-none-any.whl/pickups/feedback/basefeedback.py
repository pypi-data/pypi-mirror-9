import abc


class BaseFeedback(object):
    """BaseFeedback is an abstract metaclass defining what functionality a feedback device class should have to work
    with a pickups class. A pickups class will use the implemented methods of a child of BaseFeedback to handle an
    actual feedback device.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self):
        """Initialize the feedback device."""

    @abc.abstractmethod
    def turn_on_success(self):
        """Turn the success indicating thing on. One could use this in connection with :func:`turn_off_failure`"""

    @abc.abstractmethod
    def turn_off_success(self):
        """Turn off the success indicating thing. One could use this in connection with :func:`turn_on_failure`."""

    @abc.abstractmethod
    def turn_on_failure(self):
        """Turn on a failure indicating thing. One could use this in connection with :func:`turn_off_success`."""

    @abc.abstractmethod
    def turn_off_failure(self):
        """Turn off a failure indicating thing. One could use this in connection with :func:`turn_on_success`.
        """

    @abc.abstractmethod
    def turn_on_running(self):
        """Turn on a thing whenever a build is running. One could turn off all other lamps while a build is running."""

    @abc.abstractmethod
    def turn_off_running(self):
        """Turn off a thing whenever no build is currently running. After turning off the indicator for running builds
        one could turn on either :func:`turn_on_success` or :func:`turn_on_failure`.
        """

    @abc.abstractmethod
    def get_status(self):
        """Return the overall status of a extreme feedback device."""
