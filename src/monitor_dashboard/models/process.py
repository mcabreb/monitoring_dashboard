"""Data models for process information."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProcessInfo:
    """Information about a running process."""

    pid: int
    user: str
    cpu_percent: float  # 0-100
    memory_percent: float  # 0-100
    time: str  # Cumulative CPU time (e.g., "01:23:45")
    command: str  # Command name or full command line
