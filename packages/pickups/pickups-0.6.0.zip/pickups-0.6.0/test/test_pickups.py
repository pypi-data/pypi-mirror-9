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
    pickup = BambooPickup(configfile)
    assert isinstance(pickup, BambooPickup)


@pytest.mark.xfail(raises=ValueError)
def test_broken_config(broken_configfile):
    pickup = BambooPickup(broken_configfile)


@pytest.mark.xfail(raises=IOError)
def test_none_config():
    pickup = BambooPickup(None)


def test_cleanup(bamboopickup):
    bamboopickup.cleanup()


def test_update_status_not_running_successful(bamboopickup, mock_not_running_successful):
    actual = bamboopickup.update_status()
    expected = True
    assert actual == expected


def test_update_status_not_running_not_successful(bamboopickup, mock_not_running_not_successful):
    actual = bamboopickup.update_status()
    expected = True
    assert actual == expected


def test_update_status_running_successful(bamboopickup, mock_running_successful):
    actual = False
    expected = True

    with mock.patch.object(bamboopickup, '_is_a_build_running', return_value=AlmostAlwaysTrue(2)) as mockfoo:
        actual = bamboopickup.update_status()

    assert actual == expected


def test_update_status_running_not_successful(bamboopickup, mock_running_not_successful):
    actual = False
    expected = True

    with mock.patch.object(bamboopickup, '_is_a_build_running') as mockfoo:
        mockfoo.return_value = AlmostAlwaysTrue(2)
        actual = bamboopickup.update_status()
    assert actual == expected


def test_update_status_overall_timeout(bamboopickup, mock_status_update_overall_timeout):
    actual = bamboopickup.update_status()
    expected = False
    assert actual == expected


def test_update_status_buildstatus_timeout(bamboopickup, mock_status_update_buildstatus_timeout):
    actual = bamboopickup.update_status()
    expected = False
    assert actual == expected


def test_update_status_timeout_after_first_update(bamboopickup, mock_not_running_not_successful):
    actual = False
    expected = False

    with mock.patch.object(bamboopickup, 'update_data', return_value=AlmostAlwaysTrue(1)) as mockfoo:
        actual = bamboopickup.update_status()

    assert actual == expected


def test_update_status_timeout_while_running(bamboopickup, mock_running_not_successful):
    expected = False
    bamboopickup._is_a_build_running = mock.MagicMock(return_value=AlmostAlwaysTrue(2))
    bamboopickup._update_builds_status = mock.MagicMock(return_value=AlmostAlwaysTrue(1))
    actual = bamboopickup.update_status()
    assert actual == expected


def test_is_a_build_running(bamboopickup, mock_running_successful):
    expected = True
    actual = bamboopickup._is_a_build_running()
    assert actual == expected


def test_is_a_build_not_running(bamboopickup, mock_not_running_successful):
    expected = False
    actual = bamboopickup._is_a_build_running()
    assert actual == expected


@pytest.mark.xfail(raises=IOError)
def test_basepickup_no_configfile():
    bamboopickup = BambooPickup(None)


def test_get_status_on(bamboopickup, mock_get_status_on):
    expected = {1: 'on', 2: 'on', 3: 'on', 4: 'on'}
    actual = bamboopickup.feedback.get_status()
    assert actual == expected


def test_get_status_off(bamboopickup, mock_get_status_off):
    expected = {1: 'off', 2: 'off', 3: 'off', 4: 'off'}
    actual = bamboopickup.feedback.get_status()
    assert actual == expected
