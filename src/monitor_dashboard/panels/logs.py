"""Logs panel for system logs display."""

from textual.widgets import Label

from monitor_dashboard.panels.base import BasePanel


class LogsPanel(BasePanel):
    """Panel displaying system logs."""

    BORDER_TITLE = "● Logs"

    def compose(self):
        """Compose the Logs panel content."""
        yield Label("Logs - Coming Soon")
