"""System logs data collection using journalctl."""

import logging
import subprocess
from datetime import datetime

from monitor_dashboard.models.logs import LogEntry, LogSeverity

logger = logging.getLogger(__name__)


class LogsCollector:
    """Collects system logs using journalctl command."""

    # journalctl priority mapping
    PRIORITY_MAP = {
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
            List of LogEntry objects, most recent last.
        """
        try:
            # Use journalctl to get recent logs (more accessible than dmesg)
            result = subprocess.run(
                [
                    "journalctl",
                    "--no-pager",
                    "-n", str(max_entries),
                    "-p", "warning",  # warning and above (err, crit, alert, emerg)
                    "-o", "short-iso",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                # Fallback: try without priority filter
                result = subprocess.run(
                    [
                        "journalctl",
                        "--no-pager",
                        "-n", str(max_entries),
                        "-o", "short-iso",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

            if result.returncode != 0:
                return []

            lines = result.stdout.strip().split("\n")
            entries: list[LogEntry] = []

            for line in lines:
                entry = self._parse_journal_line(line)
                if entry:
                    entries.append(entry)

            return entries

        except FileNotFoundError:
            logger.debug("journalctl not found")
            return []
        except Exception as e:
            logger.debug(f"Failed to collect logs: {e}")
            return []

    def _parse_journal_line(self, line: str) -> LogEntry | None:
        """Parse a journalctl log line.

        Args:
            line: Raw log line from journalctl (short-iso format).

        Returns:
            LogEntry if parsing succeeded, None otherwise.
        """
        try:
            if not line.strip() or line.startswith("--"):
                return None

            # short-iso format: "2026-01-17T13:45:00+0100 hostname unit[pid]: message"
            parts = line.split(" ", 3)
            if len(parts) < 4:
                return None

            timestamp_str = parts[0]
            message = parts[3] if len(parts) > 3 else line

            # Parse timestamp
            try:
                # Handle timezone offset
                timestamp = datetime.fromisoformat(timestamp_str.replace("+0100", "+01:00").replace("+0000", "+00:00"))
            except:
                timestamp = datetime.now()

            # Determine severity from keywords in message
            severity = LogSeverity.INFO
            msg_lower = message.lower()
            if "error" in msg_lower or "fail" in msg_lower or "fatal" in msg_lower:
                severity = LogSeverity.ERROR
            elif "warn" in msg_lower:
                severity = LogSeverity.WARNING

            return LogEntry(
                timestamp=timestamp,
                severity=severity,
                message=message[:200],  # Truncate long messages
                raw=line,
            )

        except Exception:
            return None
