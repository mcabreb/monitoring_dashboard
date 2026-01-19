"""Logs panel for system log display."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.logs import LogEntry, LogSeverity
from monitor_dashboard.panels.base import BasePanel


class LogsPanel(BasePanel):
    """Panel displaying system logs."""

    BORDER_TITLE = "● Logs"

    def __init__(self, **kwargs) -> None:
        """Initialize logs panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None

    def compose(self) -> ComposeResult:
        """Compose the Logs panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(self, logs: list[LogEntry] | None) -> None:
        """Update panel with log entries.

        Args:
            logs: List of log entries, or None if unavailable.
        """
        if not self._container:
            return

        # Clear existing content
        self._container.remove_children()

        if not logs:
            self._container.mount(Label("No logs available"))
            return

        # Display logs (most recent first) - no truncation, let view handle clipping
        for log in reversed(logs[-30:]):  # Show last 30
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
