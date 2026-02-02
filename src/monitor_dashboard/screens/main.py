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

    def set_zoom_mode(self, enabled: bool) -> None:
        """Toggle between zoom layout (1-col vertical stack) and normal (2x2 grid)."""
        try:
            grid = self.query_one("#main-grid", Grid)
            devices = self.query_one("#devices", DevicesPanel)
            logs = self.query_one("#logs", LogsPanel)
            info_bar = self.query_one("#info-bar", InfoBar)
        except Exception:
            return

        if enabled:
            devices.display = False
            logs.display = False
            info_bar.display = False
            grid.styles.grid_size_columns = 1
            grid.styles.grid_size_rows = 2
        else:
            devices.display = True
            logs.display = True
            info_bar.display = True
            grid.styles.grid_size_columns = 2
            grid.styles.grid_size_rows = 2
