"""
Tests for `helpers` module.
"""
import mock
import pytest

import pickups


def test_set_interrupted_true():
    ih = pickups.helpers.InterruptHandler(mock.Mock())
    ih.interrupted = True
    expected = ih.interrupted
    actual = True
    assert actual == expected


def test_set_interrupted_false():
    ih = pickups.helpers.InterruptHandler(mock.Mock())
    ih.interrupted = False
    expected = ih.interrupted
    actual = False
    assert actual == expected


@pytest.mark.xfail(raises=ValueError)
def test_set_interrupted_none():
    ih = pickups.helpers.InterruptHandler(mock.Mock())
    ih.interrupted = None


def test_register(configfile, mock_not_running_successful):
    with mock.patch('pickups.helpers.InterruptHandler.interrupted') as mockfoo:
        mockfoo.return_value = False
        assert None == pickups.helpers.register(mock.MagicMock(), configfile)


def test_handler(configfile):
    ih = pickups.helpers.InterruptHandler(mock.Mock())
    ih.__enter__()
    ih.__exit__(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())
    actual = ih.released
    expected = True
    assert actual == expected


def test_handler_release():
    ih = pickups.helpers.InterruptHandler(mock.Mock())
    ih.__enter__()
    ih.released = True
    actual = ih.release()
    expected = False
    assert actual == expected
