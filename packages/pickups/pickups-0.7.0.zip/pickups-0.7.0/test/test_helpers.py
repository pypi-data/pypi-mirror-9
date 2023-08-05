"""
Tests for `helpers` module.
"""
import mock
import pytest

import pickups


def test_set_interrupted_true():
    """Interrupt handler should get interrupted."""
    mock_obj = mock.MagicMock()
    mock_obj.__name__ = 'MockClass'
    ih = pickups.helpers.InterruptHandler(mock_obj)
    ih.interrupted = True
    expected = ih.interrupted
    actual = True
    assert actual == expected


def test_set_interrupted_false():
    """Interrupt Handler should not be interrupted."""
    mock_obj = mock.MagicMock()
    mock_obj.__name__ = 'MockClass'
    ih = pickups.helpers.InterruptHandler(mock_obj)
    ih.interrupted = False
    expected = ih.interrupted
    actual = False
    assert actual == expected


@pytest.mark.xfail(raises=ValueError)
def test_set_interrupted_none():
    """Should raise a value error, as ``None`` is not allowed as status."""
    mock_obj = mock.MagicMock()
    mock_obj.__name__ = 'MockClass'
    ih = pickups.helpers.InterruptHandler(mock_obj)
    ih.interrupted = None


def test_register(configfile, mock_not_running_successful):
    """Is registering a custom interrupt handler working."""
    with mock.patch('pickups.helpers.InterruptHandler.interrupted') as mockfoo:
        mock_obj = mock.MagicMock()
        mock_obj.__name__ = 'MockClass'
        assert None == pickups.helpers.register(mock_obj, configfile)


def test_handler(configfile):
    """Test whether registering a interrupt handler and releasing it by using ``__exit__`` works."""
    mock_obj = mock.MagicMock()
    mock_obj.__name__ = 'MockClass'
    ih = pickups.helpers.InterruptHandler(mock_obj)
    ih.__enter__()
    ih.__exit__(mock.MagicMock(), mock.MagicMock(), mock.MagicMock())
    actual = ih.released
    expected = True
    assert actual == expected


def test_handler_release():
    """Test whether releasing resources works."""
    mock_obj = mock.MagicMock()
    mock_obj.__name__ = 'MockClass'
    ih = pickups.helpers.InterruptHandler(mock_obj)
    ih.__enter__()
    ih.released = True
    actual = ih.release()
    expected = False
    assert actual == expected
