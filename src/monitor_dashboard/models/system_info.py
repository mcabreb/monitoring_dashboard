"""System information data models."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SystemInfo:
    """System information snapshot."""

    hostname: str
    kernel: str
    distro: str
    uptime_seconds: int
    boot_time: datetime
