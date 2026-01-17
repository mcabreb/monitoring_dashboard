"""Devices panel for battery and Bluetooth devices."""

from textual.widgets import Label

from monitor_dashboard.panels.base import BasePanel


class DevicesPanel(BasePanel):
    """Panel displaying device information."""

    BORDER_TITLE = "● Devices"

    def compose(self):
        """Compose the Devices panel content."""
        yield Label("Devices - Coming Soon")
