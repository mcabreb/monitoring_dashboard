"""Storage panel for disk usage and mount points."""

from textual.widgets import Label

from monitor_dashboard.panels.base import BasePanel


class StoragePanel(BasePanel):
    """Panel displaying storage information."""

    BORDER_TITLE = "● Storage"

    def compose(self):
        """Compose the Storage panel content."""
        yield Label("Storage - Coming Soon")
