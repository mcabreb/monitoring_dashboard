"""Logs panel for system log display."""

from collections import deque

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.logs import LogEntry, LogSeverity
from monitor_dashboard.panels.base import BasePanel


class LogsPanel(BasePanel):
    """Panel displaying system logs."""

    BORDER_TITLE = "● Logs"
    MAX_LOGS = 100

    def __init__(self, **kwargs) -> None:
        """Initialize logs panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None
        self._logs: deque[LogEntry] = deque(maxlen=self.MAX_LOGS)
        self._seen_raws: set[str] = set()

    def compose(self) -> ComposeResult:
        """Compose the Logs panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(self, logs: list[LogEntry] | None) -> None:
        """Update panel with log entries.

        Merges new logs with existing buffer, keeping last 100 unique entries.

        Args:
            logs: List of log entries, or None if unavailable.
        """
        if not self._container:
            return

        if logs:
            # Add new unique logs to buffer
            for log in logs:
                if log.raw not in self._seen_raws:
                    self._logs.append(log)
                    self._seen_raws.add(log.raw)
                    # Keep seen set bounded
                    if len(self._seen_raws) > self.MAX_LOGS * 2:
                        self._seen_raws = {entry.raw for entry in self._logs}

        # Clear existing content
        self._container.remove_children()

        if not self._logs:
            self._container.mount(Label("No logs available"))
            return

        # Display all logs (most recent first)
        for log in reversed(self._logs):
            color_class = self._get_severity_class(log.severity)
            label = Label(f"{log.timestamp.strftime('%H:%M:%S')} {log.message}")
            label.add_class(color_class)
            self._container.mount(label)

    def _get_severity_class(self, severity: LogSeverity) -> str:
        """Get CSS class for log severity.

        Args:
            severity: Log severity level.

        Returns:
            CSS class name.
        """
        if severity in [
            LogSeverity.EMERGENCY,
            LogSeverity.ALERT,
            LogSeverity.CRITICAL,
            LogSeverity.ERROR,
        ]:
            return "log-error"
        elif severity == LogSeverity.WARNING:
            return "log-warning"
        return "log-info"
