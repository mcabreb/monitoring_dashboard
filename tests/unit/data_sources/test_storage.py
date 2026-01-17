"""Unit tests for storage data collection."""

from unittest.mock import MagicMock, patch

import pytest

from monitor_dashboard.data_sources.storage import (
    PSEUDO_FS_TYPES,
    PSEUDO_MOUNT_PREFIXES,
    StorageCollector,
)
from monitor_dashboard.models.metrics import DiskInfo


def test_disk_info_dataclass_fields():
    """Test DiskInfo has all expected fields."""
    disk = DiskInfo(
        mount_point="/",
        device="/dev/sda1",
        fs_type="ext4",
        total=1000000000,
        used=500000000,
        free=500000000,
        percent=50.0,
    )

    assert disk.mount_point == "/"
    assert disk.device == "/dev/sda1"
    assert disk.fs_type == "ext4"
    assert disk.total == 1000000000
    assert disk.used == 500000000
    assert disk.free == 500000000
    assert disk.percent == 50.0


def test_disk_info_is_frozen():
    """Test DiskInfo is immutable (frozen dataclass)."""
    disk = DiskInfo(
        mount_point="/",
        device="/dev/sda1",
        fs_type="ext4",
        total=1000000000,
        used=500000000,
        free=500000000,
        percent=50.0,
    )

    with pytest.raises(AttributeError):
        disk.mount_point = "/home"


@patch("monitor_dashboard.data_sources.storage.psutil")
def test_storage_collector_returns_list(mock_psutil):
    """Test StorageCollector.collect() returns list of DiskInfo."""
    # Mock partition data
    mock_partition = MagicMock()
    mock_partition.mountpoint = "/"
    mock_partition.device = "/dev/sda1"
    mock_partition.fstype = "ext4"
    mock_psutil.disk_partitions.return_value = [mock_partition]

    # Mock usage data
    mock_usage = MagicMock()
    mock_usage.total = 1000000000
    mock_usage.used = 500000000
    mock_usage.free = 500000000
    mock_usage.percent = 50.0
    mock_psutil.disk_usage.return_value = mock_usage

    collector = StorageCollector()
    result = collector.collect()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], DiskInfo)
    assert result[0].mount_point == "/"


@patch("monitor_dashboard.data_sources.storage.psutil")
def test_storage_collector_filters_pseudo_filesystems(mock_psutil):
    """Test pseudo filesystems are filtered out."""
    # Create partitions with both real and pseudo filesystems
    real_partition = MagicMock()
    real_partition.mountpoint = "/"
    real_partition.device = "/dev/sda1"
    real_partition.fstype = "ext4"

    pseudo_partition = MagicMock()
    pseudo_partition.mountpoint = "/proc"
    pseudo_partition.device = "proc"
    pseudo_partition.fstype = "proc"

    mock_psutil.disk_partitions.return_value = [real_partition, pseudo_partition]

    # Mock usage for real partition only
    mock_usage = MagicMock()
    mock_usage.total = 1000000000
    mock_usage.used = 500000000
    mock_usage.free = 500000000
    mock_usage.percent = 50.0
    mock_psutil.disk_usage.return_value = mock_usage

    collector = StorageCollector()
    result = collector.collect()

    # Only the real partition should be included
    assert len(result) == 1
    assert result[0].fs_type == "ext4"


@patch("monitor_dashboard.data_sources.storage.psutil")
def test_storage_collector_handles_inaccessible_partition(mock_psutil):
    """Test inaccessible partitions are handled gracefully."""
    # Mock two partitions: one accessible, one not
    partition1 = MagicMock()
    partition1.mountpoint = "/"
    partition1.device = "/dev/sda1"
    partition1.fstype = "ext4"

    partition2 = MagicMock()
    partition2.mountpoint = "/mnt/restricted"
    partition2.device = "/dev/sdb1"
    partition2.fstype = "ext4"

    mock_psutil.disk_partitions.return_value = [partition1, partition2]

    # First call succeeds, second raises PermissionError
    mock_usage = MagicMock()
    mock_usage.total = 1000000000
    mock_usage.used = 500000000
    mock_usage.free = 500000000
    mock_usage.percent = 50.0

    mock_psutil.disk_usage.side_effect = [mock_usage, PermissionError("Access denied")]

    collector = StorageCollector()
    result = collector.collect()

    # Should return only the accessible partition
    assert len(result) == 1
    assert result[0].mount_point == "/"


@patch("monitor_dashboard.data_sources.storage.psutil")
def test_storage_collector_returns_empty_on_enumeration_failure(mock_psutil):
    """Test empty list is returned if partition enumeration fails."""
    mock_psutil.disk_partitions.side_effect = Exception("Enumeration failed")

    collector = StorageCollector()
    result = collector.collect()

    assert result == []


@patch("monitor_dashboard.data_sources.storage.psutil")
def test_storage_collector_sorts_by_mount_point(mock_psutil):
    """Test results are sorted by mount point."""
    # Create partitions in unsorted order
    partition1 = MagicMock()
    partition1.mountpoint = "/home"
    partition1.device = "/dev/sda2"
    partition1.fstype = "ext4"

    partition2 = MagicMock()
    partition2.mountpoint = "/"
    partition2.device = "/dev/sda1"
    partition2.fstype = "ext4"

    mock_psutil.disk_partitions.return_value = [partition1, partition2]

    # Mock usage
    mock_usage = MagicMock()
    mock_usage.total = 1000000000
    mock_usage.used = 500000000
    mock_usage.free = 500000000
    mock_usage.percent = 50.0
    mock_psutil.disk_usage.return_value = mock_usage

    collector = StorageCollector()
    result = collector.collect()

    # Should be sorted by mount point
    assert len(result) == 2
    assert result[0].mount_point == "/"
    assert result[1].mount_point == "/home"
