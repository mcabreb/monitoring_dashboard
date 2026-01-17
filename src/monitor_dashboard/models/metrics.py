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
