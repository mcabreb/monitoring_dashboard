"""Logs panel for system log display."""

from collections import deque

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.logs import LogEntry, LogSeverity
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.selectable import SelectableMixin


class LogsPanel(BasePanel, SelectableMixin):
    """Panel displaying system logs."""

    BORDER_TITLE = "● Logs"
    MAX_LOGS = 100

    def __init__(self, **kwargs) -> None:
        """Initialize logs panel."""
        super().__init__(**kwargs)
        self.init_selection()
        self._container: VerticalScroll | None = None
        self._logs: deque[LogEntry] = deque(maxlen=self.MAX_LOGS)
        self._seen_raws: set[str] = set()
        # Store logs as list for indexed access (most recent first for display)
        self._display_logs: list[LogEntry] = []

    def compose(self) -> ComposeResult:
        """Compose the Logs panel content."""
        self._container = VerticalScroll()
        yield self._container

    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs (raw log lines)."""
        return [log.raw for log in self._display_logs]

    def get_element_data(self, element_id: str) -> LogEntry | None:
        """Get log entry for a raw log line ID."""
        for log in self._display_logs:
            if log.raw == element_id:
                return log
        return None

    def refresh_selection_display(self) -> None:
        """Re-render with selection styling."""
        self._display()

    def get_all_logs(self) -> list[LogEntry]:
        """Get all stored logs for export.

        Returns:
            List of all log entries in chronological order.
        """
        return list(self._logs)

    def update(self, logs: list[LogEntry] | None) -> None:
        """Update panel with log entries.

        Merges new logs with existing buffer, keeping last 100 unique entries.

        Args:
            logs: List of log entries, or None if unavailable.
        """
        if logs:
            # Add new unique logs to buffer
            for log in logs:
                if log.raw not in self._seen_raws:
                    self._logs.append(log)
                    self._seen_raws.add(log.raw)
                    # Keep seen set bounded
                    if len(self._seen_raws) > self.MAX_LOGS * 2:
                        self._seen_raws = {entry.raw for entry in self._logs}

        # Build display list (most recent first)
        self._display_logs = list(reversed(self._logs))

        # Prune sticky selections for logs that no longer exist
        self.prune_invalid_sticky()

        self._display()

    def _display(self) -> None:
        """Render the panel with current data and selection styling."""
        if not self._container:
            return

        # Clear existing content
        self._container.remove_children()

        if not self._display_logs:
            self._container.mount(Label("No logs available"))
            return

        # Display all logs (most recent first)
        for log in self._display_logs:
            element_id = log.raw
            text = f"{log.timestamp.strftime('%H:%M:%S')} {log.message}"
            label = Label(text)

            # Apply selection styling first (takes precedence)
            selection_class = self.get_selection_class(element_id)
            if selection_class:
                label.add_class(selection_class)
            else:
                # Apply severity color if not selected
                color_class = self._get_severity_class(log.severity)
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
