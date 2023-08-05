"""
Tests for `pickups` module.
"""

import sys
from test.conftest import AlmostAlwaysTrue

import pytest

import pickups
from pickups.bamboo.bamboopickup import BambooPickup

# seems as the builtin check is broken
if sys.version_info[0] >= 3:
    import unittest.mock as mock
else:
    import mock as mock


def test_bamboo_pickup(configfile):
    """Assert that by creating a BambooPickup object one is actually created."""
    pickup = BambooPickup(configfile)
    assert isinstance(pickup, BambooPickup)


@pytest.mark.xfail(raises=ValueError)
def test_broken_config(broken_configfile):
    """Only let instantiation happen, if a proper config file is supplied."""
    pickup = BambooPickup(broken_configfile)


@pytest.mark.xfail(raises=IOError)
def test_none_config():
    """Only let instantiation happen, if a config file is supplied."""
    pickup = BambooPickup(None)


def test_cleanup(bamboopickup):
    """Cleanup everything (turn lamps off). The idea here is not to crash in any case, even if cleanup doesnt work.
    We never want the daemon to crash because a lamp or the underlying daemon to toggle lamps is not responding.
    """
    bamboopickup.cleanup()


def test_update_status_not_running_successful(bamboopickup, mock_not_running_successful):
    """Try updating the status. No build is currently running. All builds are successfully finished."""
    actual = bamboopickup.update_status()
    expected = True
    assert actual == expected


def test_update_status_not_running_not_successful(bamboopickup, mock_not_running_not_successful):
    """Try updating the status. No build is currently running. At least one built did not finish successfully."""
    actual = bamboopickup.update_status()
    expected = True
    assert actual == expected


def test_update_status_running_successful(bamboopickup, mock_running_successful):
    """Try updating the status. A build is currently running. All previous builds finished successfully."""
    actual = False
    expected = True

    # notice the ``return_value``, where we override the builtin True/False evaluation. See :class:`AlmostAlwaysTrue`.
    with mock.patch.object(bamboopickup, '_is_a_build_running', return_value=AlmostAlwaysTrue(2)) as mockfoo:
        actual = bamboopickup.update_status()

    assert actual == expected


def test_update_status_running_not_successful(bamboopickup, mock_running_not_successful):
    """Try updating the status. A build is currently running. A previous build did not finish successfully."""
    actual = False
    expected = True

    with mock.patch.object(bamboopickup, '_is_a_build_running') as mockfoo:
        mockfoo.return_value = AlmostAlwaysTrue(2)
        actual = bamboopickup.update_status()
    assert actual == expected


def test_update_status_overall_timeout(bamboopickup, mock_status_update_overall_timeout):
    """Update overall status does not work (and thus update status), when it times out on a request."""
    actual = bamboopickup.update_status()
    expected = False
    assert actual == expected


def test_update_status_buildstatus_timeout(bamboopickup, mock_status_update_buildstatus_timeout):
    """Update buildstatus does not work (and thus update status), when it times out on a request."""
    actual = bamboopickup.update_status()
    expected = False
    assert actual == expected


def test_update_status_timeout_after_first_update(bamboopickup, mock_not_running_not_successful):
    """Test whether update status behaves correctly even if one update works"""
    actual = False
    expected = False

    with mock.patch.object(bamboopickup, 'update_data', return_value=AlmostAlwaysTrue(1)) as mockfoo:
        actual = bamboopickup.update_status()

    assert actual == expected


def test_update_status_timeout_while_running(bamboopickup, mock_running_not_successful):
    """Test whether update status behaves correctly even if a request times out. Also daemon shouldnt crash in this case
    we rather want to log this event.
    """
    expected = False
    bamboopickup._is_a_build_running = mock.MagicMock(return_value=AlmostAlwaysTrue(2))
    bamboopickup._update_builds_status = mock.MagicMock(return_value=AlmostAlwaysTrue(1))
    actual = bamboopickup.update_status()
    assert actual == expected


def test_is_a_build_running(bamboopickup, mock_running_successful):
    """When a build is running, is ``_is_a_build_running`` behaving correctly."""
    expected = True
    actual = bamboopickup._is_a_build_running()
    assert actual == expected


def test_is_a_build_not_running(bamboopickup, mock_not_running_successful):
    """When no build is running, is ``_is_a_build_running`` behaving correctly."""
    expected = False
    actual = bamboopickup._is_a_build_running()
    assert actual == expected


@pytest.mark.xfail(raises=IOError)
def test_basepickup_no_configfile():
    """One should always supply a configuration file."""
    bamboopickup = BambooPickup(None)


def test_get_status_on(bamboopickup, mock_get_status_on):
    """Test correct behaviour of ``get_status``"""
    expected = {1: 'on', 2: 'on', 3: 'on', 4: 'on'}
    actual = bamboopickup.feedback.get_status()
    assert actual == expected


def test_get_status_off(bamboopickup, mock_get_status_off):
    """Test correct behaviour of ``get_status``"""
    expected = {1: 'off', 2: 'off', 3: 'off', 4: 'off'}
    actual = bamboopickup.feedback.get_status()
    assert actual == expected
