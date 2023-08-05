import signal
import time

from pickups.log import get_logger

log = get_logger(__name__)


def register(cls, configfile, sign=signal.SIGTERM):
    """Register is a helper function to ease the process of registering a custom signal handler to handle signals like
    SIGTERM or other. Possible Signals are defined in :class:`signal` as constants.

    :param cls: The class to register.
    :param configfile: The configuration file containing (uh oh) configurations.
    :returns: None
    :raises: None
    """
    with InterruptHandler(cls(configfile), sig=sign) as h:
        log.info("successfully registered InterruptHandler with class %s", cls.__name__)
        while not h.interrupted:
            h.cls.update_status()
            time.sleep(h.cls.refresh_time)


class InterruptHandler(object):
    """InterruptHandler can be used as a decorator to register a custom signal handler on classes. """

    # TODO: make this so that it can handle multiple signals
    def __init__(self, cls, sig=signal.SIGTERM):
        log.info("registering custom signal handler (%s)", str(sig))
        self.cls = cls
        self.sig = sig
        self._interrupted = False
        self.released = False

    @property
    def interrupted(self):
        """Getter for the current status of interruption.

        :returns: True if interruption occurred.
        :rtype: Boolean
        :raises: None
        """
        return self._interrupted

    @interrupted.setter
    def interrupted(self, value):
        """Setter for the current status of interruption. This is merely an helper, but can be used to manually
        interrupt and thus force a cleanup using an actual implementation of
        :func:`pickups.basepickup.BasePickup.cleanup`.

        :param value: A value indicating the new status of interruption. Can either be ``True`` or ``False``.
        :type value: Boolean
        :returns: None
        :raises: None
        """
        self._interrupted = value if value is True or value is False else ValueError

    def __enter__(self):
        """Save the old signal handler and setup the new one. When using InterruptHandler as an decorator like
        :func:`pickups.helpers.register` this is automatically called. If One wants to manually register a custom
        signal handler, you'd have to call this manually.

        :returns: :class:`InterruptHandler`
        :raises: None
        """

        self._interrupted = False
        self.released = False

        # keep old handler for restoring purposes
        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            """Registers the new handler. Call :func:`InterruptHandler.release` on interruption. The params arent used
            but kept for clearance as this is the standard way to define a new handler.

            :returns: None
            :raises: None
            """
            log.info("received interrupt signal")
            self.release()
            self._interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        """When this handler is called with exit or when the decorator exits release all resources. The params arent
        used as we (for now) only call :func:`InterruptHandler.release`.

        :returns: None
        :raises: None
        """

        self.release()

    def release(self):
        """Release the bound resources by calling the actual implementation of
        :func:`pickups.basepickup.BasePickup.cleanup`.

        :returns: True if release worked.
        :rtype: Boolean
        :raises: None
        """

        if self.released:
            return False

        # call cleanup and do some cleanup
        log.info("calling cleanup to release feedbacks")
        self.cls.cleanup()

        # restore the old handler
        log.info("restoring original handler")
        signal.signal(self.sig, self.original_handler)

        self.released = True
        return True
