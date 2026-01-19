"""Expanded panel screen for full-screen view of a single panel."""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen

from monitor_dashboard.panels.devices import DevicesPanel
from monitor_dashboard.panels.logs import LogsPanel
from monitor_dashboard.panels.processes import ProcessesPanel
from monitor_dashboard.panels.system_health import SystemHealthPanel


class ExpandedPanelScreen(Screen):
    """Full-screen view of a single panel with more detail."""

    BINDINGS = [
        ("escape", "collapse", "Return to Dashboard"),
        ("enter", "collapse", "Return to Dashboard"),
    ]

    def __init__(self, panel_id: str, **kwargs) -> None:
        """Initialize expanded panel screen.

        Args:
            panel_id: ID of the panel to display in full-screen.
            **kwargs: Additional arguments passed to Screen.__init__.
        """
        super().__init__(**kwargs)
        self.panel_id = panel_id

    def compose(self) -> ComposeResult:
        """Compose the expanded panel screen."""
        with Container(id="expanded-container"):
            yield self._create_expanded_panel()

    def _create_expanded_panel(self):
        """Create the appropriate expanded panel based on panel_id.

        Returns:
            The panel widget for full-screen display.
        """
        match self.panel_id:
            case "system-health":
                return SystemHealthPanel(id=self.panel_id)
            case "processes":
                return ProcessesPanel(id=self.panel_id)
            case "devices":
                return DevicesPanel(id=self.panel_id)
            case "logs":
                return LogsPanel(id=self.panel_id)
            case _:
                # Default to system health if unknown panel ID
                return SystemHealthPanel(id="system-health")

    def action_collapse(self) -> None:
        """Return to the main dashboard."""
        self.app.pop_screen()
