import abc

from pickups.log import get_logger

log = get_logger(__name__)


class BasePickup(object):
    """BasePickup is an abstract metaclass defining behaviours for specialized pickup classes. A child class inherits
    from BasePickup and implements the defined methods to work as an interface between a buildserver (Bamboo, Jenkins,
    ...) and the pickups package.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, configfile):
        """Child classes should delegate the reading in of a config file to BasePickup using `super`. A config file
        is mandatory and usually contains at least an IP address pointing to the buildserver.

        :param configfile: A config file in the stile of `key = value`.
        :raises: IOError if no config file is given.
        """
        if configfile is None:
            raise IOError('no configuration file given')

        self.config = {}
        log.info("reading configfile %s", configfile)
        with open(configfile) as f:
            exec(f.read(), self.config)

    @abc.abstractmethod
    def cleanup(self):
        """Cleanup method, used by `:func:pickups.helpers.register`. Usually one would turn off feedback devices etc.
        here in case a interruption occurs.
        """

    @abc.abstractmethod
    def update_data(self):
        """Receives updated data from the buildserver. The received data should contain information on build-statuses.
        Often one can use a REST-API, provided by the buildserver to receive this data.
        """

    @abc.abstractmethod
    def update_status(self):
        """Updates feedback devices according to data received from the buildserver. Common implementations dictate to
        use three devices (for example coloured lamps). Common logic is to update the devices as follows:

        * Build is running: yellow light is flashing.
        * Build is successful: green light is illuminated.
        * Build is not successful: red light is illuminated.
        """
