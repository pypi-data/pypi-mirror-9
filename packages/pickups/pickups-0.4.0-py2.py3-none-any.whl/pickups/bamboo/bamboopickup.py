import time

import requests

import pickups
import pickups.feedback.energenie.egpms as powerplug


class BambooPickup(pickups.basepickup.BasePickup):
    """As a child class of BasePickup, BambooPickup implements all methods needed to update extreme feedback devices
    using an Atlassian Bamboo buildserver and a RasberryPi with a manageable USB-Powersocket. BambooPickup is using
    Bamboo's REST-API to acquire all needed information on builds.
    """

    def __init__(self, configfile):
        """Initialize a BambooPickup object reading build statuses and updating connected feedback devices,
        according to the logic defined in :func:`update_status`.

        :param configfile: A config file which is passed to the baseclass to read it in.
        :returns: None
        :raises: None
        """

        super(BambooPickup, self).__init__(configfile)
        self.refresh_time = float(self.config['refresh_time'])
        self.blinker_time = float(self.config['blinker_time'])
        self.overall_status_url = 'http://' + self.config['base_url'] + '/rest/api/latest/result.json'
        self.builds_status_url = 'http://' + self.config['base_url'] + '/rest/api/latest/plan.json?expand=plans.plan'

        # get powerplug feedback device
        self.feedback = powerplug.Egpms()

    @property
    def overall_status(self):
        """Getter for the overall status of the builds.

        :returns: A list filtered by the result status of each build possibly looking like
            ``[{'buildState': 'Successful'}, {'buildState': 'Successful'}]``. Valid statuses are ``Successful``,
            ``Failed`` and ``Unknown``.
        :raises: None
        """

        return self._update_overall_data()

    @property
    def builds_status(self):
        """Getter for the current status of the builds.

        :returns: List, filtered by plans possibly looking like ``[{'isBuilding': False}, {'isBuilding': True}]``. Valid
            current statuses are:

            * ``True`` if a build is currently running
            * ``False`` if a build is currently not running.

        :raises: None
        """

        return self._update_builds_status()

    def cleanup(self):
        """Turn off all lamps if system is interrupted somehow. Using :func:`pickups.helpers.register` ensures this is
        called when a SIGTERM is sent.

        :returns: None
        :raises: None
        """

        self.feedback.turn_off_failure()
        self.feedback.turn_off_running()
        self.feedback.turn_off_success()

    def update_status(self):
        """Updates the status of feedback device. An initial state is received, then depending on whether a
        build is running, the status is updated following the logic described in :class:`BasePickup`.

        :returns: True if updating feedback devices was successful.
        :rtype: Boolean
        :raises: None
        """

        # get initial state
        self.update_data()
        running = self._is_a_build_running()

        # turn on and off running powerplug while building
        while running:
            self.feedback.turn_off_success()
            self.feedback.turn_on_running()
            time.sleep(self.blinker_time)
            self.feedback.turn_off_running()
            self._update_builds_status()
            running = self._is_a_build_running()

        # data may have changed now, update
        self.update_data()
        successful = self._is_every_build_successful()

        # all builds finished successfully
        if successful and not running:
            self.feedback.turn_on_success()
            self.feedback.turn_off_running()
            self.feedback.turn_off_failure()
            return True

        # a build failed
        if not successful and not running:
            self.feedback.turn_off_success()
            self.feedback.turn_off_running()
            self.feedback.turn_on_failure()
            return True

    def _update_overall_data(self):
        """This internal helper method should never be called from outside. It serves as a filter for the dictionary
        returned by the server GET request.

        :returns: A dictionary, containing all results from all builds.
        :rtype: Dictionary
        :raises: None
        """

        return requests.get(self.overall_status_url, timeout=3).json()['results']['result']

    def _update_builds_status(self):
        """Receives a fresh copy of all build statuses by using a GET request and filtering it by each plan.

        :returns: A list containing the build status of each build.
        :rtype: List
        :raises: None
        """

        return requests.get(self.builds_status_url, timeout=3).json()['plans']['plan']

    def update_data(self):
        """Updates all data.

        :returns: True if updating data (refresh data) from the buildserver was successful.
        :rtype: Boolean
        :raises: None
        """

        # requests will raise a timeout exception here
        self.overall_status
        self.builds_status
        return True

    def _is_every_build_successful(self):
        """Internal helper to determine whether all builds are successful.

        :returns: True if all builds ran and where successful.
        :rtype: Boolean
        :raises: None
        """

        builds_successful = []
        # for each build determine whether it is successful
        for build in self.overall_status:
            builds_successful.append(True) if build['buildState'] == 'Successful' else builds_successful.append(False)

        # if there is a unsuccessful build in the list, at least one build was not successful
        return False if False in builds_successful else True

    def _is_a_build_running(self):
        """Internal helper to determine whether a build is currently running.

        :returns: True if at least one build is currently running.
        :rtype: Boolean
        :raises: None
        """

        for plan in self.builds_status:
            if plan['isBuilding'] is True:
                return True
        return False
