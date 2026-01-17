"""Log entry data models."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogSeverity(Enum):
    """Log severity levels matching dmesg."""

    EMERGENCY = "emerg"
    ALERT = "alert"
    CRITICAL = "crit"
    ERROR = "err"
    WARNING = "warn"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"


@dataclass(frozen=True)
class LogEntry:
    """A single log entry from system logs."""

    timestamp: datetime
    severity: LogSeverity
    message: str
    raw: str  # Original raw log line
