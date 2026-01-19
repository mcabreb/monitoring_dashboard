"""Main dashboard screen with panel layout."""

from textual.containers import Container, Grid
from textual.screen import Screen

from monitor_dashboard.panels import (
    DevicesPanel,
    InfoBar,
    LogsPanel,
    ProcessesPanel,
    SystemHealthPanel,
)


class MainDashboard(Screen):
    """Main dashboard screen with tmux-style fixed panel layout."""

    def compose(self):
        """Compose the main dashboard layout."""
        with Container(id="dashboard-container"):
            with Grid(id="main-grid"):
                yield SystemHealthPanel(id="system-health")
                yield ProcessesPanel(id="processes")
                yield DevicesPanel(id="devices")
                yield LogsPanel(id="logs")
            yield InfoBar(id="info-bar")
