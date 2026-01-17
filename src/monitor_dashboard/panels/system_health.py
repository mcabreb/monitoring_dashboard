"""System Health panel for CPU, memory, and load metrics."""

from textual.widgets import Label

from monitor_dashboard.panels.base import BasePanel


class SystemHealthPanel(BasePanel):
    """Panel displaying system health metrics."""

    BORDER_TITLE = "● System Health"

    def compose(self):
        """Compose the System Health panel content."""
        yield Label("System Health - Coming Soon")
