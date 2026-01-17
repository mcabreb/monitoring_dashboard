"""System logs data collection using dmesg."""

import logging
import re
import subprocess
from datetime import datetime

from monitor_dashboard.models.logs import LogEntry, LogSeverity

logger = logging.getLogger(__name__)


class LogsCollector:
    """Collects system logs using dmesg command."""

    # Regex to parse dmesg output with severity
    DMESG_PATTERN = re.compile(r"\[.*?\]\s*<(\d)>\s*(.*)")

    # Severity level mapping (kernel log levels)
    SEVERITY_MAP = {
        "0": LogSeverity.EMERGENCY,
        "1": LogSeverity.ALERT,
        "2": LogSeverity.CRITICAL,
        "3": LogSeverity.ERROR,
        "4": LogSeverity.WARNING,
        "5": LogSeverity.NOTICE,
        "6": LogSeverity.INFO,
        "7": LogSeverity.DEBUG,
    }

    def collect(self, max_entries: int = 100) -> list[LogEntry]:
        """Collect recent system logs.

        Args:
            max_entries: Maximum number of log entries to return.

        Returns:
            List of LogEntry objects, most recent first.
        """
        try:
            # Run dmesg with human-readable timestamps
            result = subprocess.run(
                ["dmesg", "-T", "-l", "err,warn,info"],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode != 0:
                logger.warning(f"dmesg failed: {result.stderr}")
                return []

            lines = result.stdout.strip().split("\n")
            entries: list[LogEntry] = []

            for line in lines[-max_entries:]:
                entry = self._parse_log_line(line)
                if entry:
                    entries.append(entry)

            return entries

        except PermissionError:
            logger.warning("Permission denied accessing dmesg")
            return []
        except FileNotFoundError:
            logger.warning("dmesg command not found")
            return []
        except Exception as e:
            logger.error(f"Failed to collect logs: {e}")
            return []

    def _parse_log_line(self, line: str) -> LogEntry | None:
        """Parse a single dmesg log line.

        Args:
            line: Raw log line from dmesg.

        Returns:
            LogEntry if parsing succeeded, None otherwise.
        """
        try:
            # Simple parsing: extract timestamp and message
            # Format: [timestamp] message
            if not line.strip():
                return None

            # For simplicity, assume INFO severity if can't determine
            severity = LogSeverity.INFO
            message = line

            # Try to extract timestamp (dmesg -T format)
            if line.startswith("["):
                parts = line.split("]", 1)
                if len(parts) == 2:
                    timestamp_str = parts[0][1:].strip()
                    message = parts[1].strip()

                    # Parse timestamp
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %Y")
                    except:
                        timestamp = datetime.now()
                else:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()

            return LogEntry(
                timestamp=timestamp,
                severity=severity,
                message=message,
                raw=line,
            )

        except Exception:
            return None
