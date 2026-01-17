"""Info bar panel for system information display."""

from textual.widgets import Label

from monitor_dashboard.panels.base import BasePanel


class InfoBar(BasePanel):
    """Panel displaying system information bar."""

    BORDER_TITLE = "● Info"

    def compose(self):
        """Compose the Info bar content."""
        yield Label("System Info - Coming Soon")
