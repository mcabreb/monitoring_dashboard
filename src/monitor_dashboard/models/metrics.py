"""Data models for system metrics."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SystemMetrics:
    """Snapshot of system health metrics."""

    timestamp: datetime
    cpu_percent: float  # 0-100
    cpu_per_core: tuple[float, ...]  # Per-core percentages
    memory_used: int  # Bytes
    memory_total: int  # Bytes
    memory_percent: float  # 0-100
    load_avg: tuple[float, float, float]  # 1, 5, 15 minute averages


@dataclass(frozen=True)
class DiskInfo:
    """Information about a mounted disk partition."""

    mount_point: str  # e.g., "/", "/home"
    device: str  # e.g., "/dev/sda1"
    fs_type: str  # e.g., "ext4", "btrfs"
    total: int  # Total bytes
    used: int  # Used bytes
    free: int  # Free bytes
    percent: float  # Usage percentage (0-100)
