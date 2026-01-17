"""Unit tests for SystemHealthCollector."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from monitor_dashboard.data_sources.system_health import SystemHealthCollector
from monitor_dashboard.models.metrics import SystemMetrics


def test_system_metrics_dataclass():
    """Verify SystemMetrics dataclass has correct fields."""
    now = datetime.now()
    metrics = SystemMetrics(
        timestamp=now,
        cpu_percent=45.5,
        cpu_per_core=(40.0, 50.0, 45.0, 48.0),
        memory_used=8_000_000_000,
        memory_total=16_000_000_000,
        memory_percent=50.0,
        load_avg=(1.5, 1.2, 1.0),
    )

    assert metrics.timestamp == now
    assert metrics.cpu_percent == 45.5
    assert metrics.cpu_per_core == (40.0, 50.0, 45.0, 48.0)
    assert metrics.memory_used == 8_000_000_000
    assert metrics.memory_total == 16_000_000_000
    assert metrics.memory_percent == 50.0
    assert metrics.load_avg == (1.5, 1.2, 1.0)


def test_system_metrics_is_frozen():
    """Verify SystemMetrics is immutable (frozen=True)."""
    metrics = SystemMetrics(
        timestamp=datetime.now(),
        cpu_percent=50.0,
        cpu_per_core=(50.0,),
        memory_used=8_000_000_000,
        memory_total=16_000_000_000,
        memory_percent=50.0,
        load_avg=(1.0, 1.0, 1.0),
    )

    # Attempt to modify should raise error
    with pytest.raises(AttributeError):
        metrics.cpu_percent = 75.0  # type: ignore


@patch("monitor_dashboard.data_sources.system_health.psutil")
def test_collect_returns_system_metrics(mock_psutil):
    """Verify collect() returns SystemMetrics with valid data."""
    # Mock psutil functions
    mock_psutil.cpu_percent.side_effect = [45.5, (40.0, 50.0, 45.0, 48.0)]
    mock_memory = Mock()
    mock_memory.used = 8_000_000_000
    mock_memory.total = 16_000_000_000
    mock_memory.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_memory
    mock_psutil.getloadavg.return_value = (1.5, 1.2, 1.0)

    collector = SystemHealthCollector()
    metrics = collector.collect()

    assert metrics is not None
    assert isinstance(metrics, SystemMetrics)
    assert isinstance(metrics.timestamp, datetime)
    assert metrics.cpu_percent == 45.5
    assert metrics.cpu_per_core == (40.0, 50.0, 45.0, 48.0)
    assert metrics.memory_used == 8_000_000_000
    assert metrics.memory_total == 16_000_000_000
    assert metrics.memory_percent == 50.0
    assert metrics.load_avg == (1.5, 1.2, 1.0)


@patch("monitor_dashboard.data_sources.system_health.psutil")
def test_collect_handles_exceptions(mock_psutil):
    """Verify collect() returns None when psutil raises exception."""
    # Make psutil raise an exception
    mock_psutil.cpu_percent.side_effect = Exception("psutil error")

    collector = SystemHealthCollector()
    metrics = collector.collect()

    assert metrics is None


@patch("monitor_dashboard.data_sources.system_health.psutil")
def test_collect_uses_non_blocking_cpu_call(mock_psutil):
    """Verify collect() uses cpu_percent with interval=None."""
    mock_psutil.cpu_percent.side_effect = [50.0, (50.0, 50.0)]
    mock_memory = Mock()
    mock_memory.used = 8_000_000_000
    mock_memory.total = 16_000_000_000
    mock_memory.percent = 50.0
    mock_psutil.virtual_memory.return_value = mock_memory
    mock_psutil.getloadavg.return_value = (1.0, 1.0, 1.0)

    collector = SystemHealthCollector()
    collector.collect()

    # Verify cpu_percent was called with interval=None (non-blocking)
    mock_psutil.cpu_percent.assert_any_call(interval=None)
    mock_psutil.cpu_percent.assert_any_call(interval=None, percpu=True)
