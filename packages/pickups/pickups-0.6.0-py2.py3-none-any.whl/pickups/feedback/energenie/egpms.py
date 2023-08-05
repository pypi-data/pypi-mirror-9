import os
import re
import subprocess

import pickups
from pickups.log import get_logger

log = get_logger(__name__)


class Egpms(pickups.basefeedback.BaseFeedback):
    """Implements all methods from the baseclass to manage an USB EnerGenie EG-PMS2. The powersocket has four
    individually callable sockets."""

    def __init__(self):
        """Construct a feedback object which can be used in childs of :class:`pickups.basefeedback.BaseFeedback`."""
        log.info("initializing feedback %s", self.__class__.__name__)
        super(Egpms, self).__init__()

    def turn_on_success(self):
        """Turn on powersocket four to indicate successful builds. Write output of the powersocket daemon to
        ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning on success feedback")
            subprocess.call(['sispmctl', '-o', '4'], stdout=f, stderr=f)

    def turn_off_success(self):
        """Turn off powersocket four. Write output of the powersocket daemon to ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning off success feedback")
            subprocess.call(['sispmctl', '-f', '4'], stdout=f, stderr=f)

    def turn_on_failure(self):
        """Turn on powersocket two to turn on the failure indicating lamp. Write output of the powersocket daemon to
        ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning on failure feedback")
            subprocess.call(['sispmctl', '-o', '2'], stdout=f, stderr=f)

    def turn_off_failure(self):
        """Turn off powersocket two to turn off failure lamp. Write output of the powersocket daemon to ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning off failure feedback")
            subprocess.call(['sispmctl', '-f', '2'], stdout=f, stderr=f)

    def turn_on_running(self):
        """Turn on powersocket three, when a build is running Write output of the powersocket daemon to ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning on running feedback")
            subprocess.call(['sispmctl', '-o', '3'], stdout=f, stderr=f)

    def turn_off_running(self):
        """Turn on powersocket three indicating nothing is running. Write output of the powersocket daemon to
        ``/dev/null``.

        :returns: None
        :raises: None
        """
        with open(os.devnull, "w") as f:
            log.debug("turning off running feedback")
            subprocess.call(['sispmctl', '-f', '3'], stdout=f, stderr=f)

    def get_status(self):
        """Get status of all manageable powersockets.

        :returns: A key, value style dictionary indicating the status of each powersocket like ``{1: 'on', 2: 'off'}``
        :rtype: Dictionary
        :raises: None
        """
        status = {}
        for i in range(1, 5):  # check each power-socket 1 - 4
            log.debug("getting status of powersocket %s", i)
            socket_status = subprocess.check_output(['sispmctl', '-g', str(i)])
            log.debug("status of powersocket %s is %s", i, socket_status)
            # from output like: 'Accessing Gembird #0 USB device 005 Status of outlet 4:\toff\n'
            # extract status 'on' or 'off'
            toggle = re.search(r'(?<=\t)[a-zA-Z]+(?=\n)', socket_status).group(0)
            status.update({i: toggle})
        return status
