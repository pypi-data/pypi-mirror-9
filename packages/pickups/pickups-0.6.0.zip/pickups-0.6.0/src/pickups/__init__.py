"""Pickups is a library which helps building functionality to talk to buildservers and extreme feedback devices. As an
first example an implementation for an USB manageable powerplug and Atlassian Bamboo is supplied."""

from . import helpers
from . import basepickup
from pickups.feedback import basefeedback

import os
here = os.path.abspath(os.path.dirname(__file__))
about = {}
packagefile = os.path.join(here, '_package.py')
with open(packagefile) as fp:
    exec(fp.read(), about)

__version__ = about['__version__']
__author__ = about['__author__']
__email__ = about['__email__']
__description__ = about['__description__']

