"""Unit tests for HistoryBuffer."""

import pytest

from monitor_dashboard.utils.history_buffer import HistoryBuffer


def test_history_buffer_init_default():
    """Test HistoryBuffer initializes with default maxlen."""
    buf = HistoryBuffer()
    assert buf.get_values() == []


def test_history_buffer_init_custom_maxlen():
    """Test HistoryBuffer initializes with custom maxlen."""
    buf = HistoryBuffer(maxlen=10)
    assert buf.get_values() == []


def test_history_buffer_append_single():
    """Test appending a single value."""
    buf = HistoryBuffer()
    buf.append(42.0)
    assert buf.get_values() == [42.0]


def test_history_buffer_append_multiple():
    """Test appending multiple values."""
    buf = HistoryBuffer()
    buf.append(1.0)
    buf.append(2.0)
    buf.append(3.0)
    assert buf.get_values() == [1.0, 2.0, 3.0]


def test_history_buffer_maintains_max_size():
    """Test buffer evicts oldest values when maxlen is exceeded."""
    buf = HistoryBuffer(maxlen=5)
    for i in range(10):
        buf.append(float(i))
    assert len(buf.get_values()) == 5
    assert buf.get_values() == [5.0, 6.0, 7.0, 8.0, 9.0]


def test_history_buffer_clear():
    """Test clearing the buffer."""
    buf = HistoryBuffer()
    buf.append(1.0)
    buf.append(2.0)
    buf.append(3.0)
    buf.clear()
    assert buf.get_values() == []


def test_history_buffer_chronological_order():
    """Test values are returned in chronological order."""
    buf = HistoryBuffer()
    values = [10.5, 20.3, 30.1, 40.9]
    for val in values:
        buf.append(val)
    assert buf.get_values() == values
