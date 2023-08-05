"""Pickups is a library which helps building functionality to talk to buildservers and extreme feedback devices. As an
first example an implementation for an USB manageable powerplug and Atlassian Bamboo is supplied."""

# TODO: parse package.py and read these attributes
__version__ = '0.4.0'
__author__ = 'Maik Figura'
__email__ = 'maiksensi[at]gmail.com'
__description__ = 'Pickups delivers all neccessary tools to run Atlassian Bamboo with ' \
                  'RasberryPi based extreme feedback devices'

from . import helpers
from . import basepickup
from pickups.feedback import basefeedback
