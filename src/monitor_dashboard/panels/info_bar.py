"""Info bar panel for system information display."""

from textual.app import ComposeResult
from textual.widgets import Label

from monitor_dashboard.models.system_info import SystemInfo
from monitor_dashboard.panels.base import BasePanel


class InfoBar(BasePanel):
    """Panel displaying system information bar."""

    BORDER_TITLE = "● Info"

    def __init__(self, **kwargs) -> None:
        """Initialize info bar."""
        super().__init__(**kwargs)
        self._label: Label | None = None

    def compose(self) -> ComposeResult:
        """Compose the Info bar content."""
        self._label = Label("Loading...")
        yield self._label

    def update(self, info: SystemInfo | None) -> None:
        """Update info bar with system information.

        Args:
            info: System information, or None if unavailable.
        """
        if not self._label:
            return

        if not info:
            self._label.update("System info unavailable")
            return

        # Format uptime
        hours = info.uptime_seconds // 3600
        minutes = (info.uptime_seconds % 3600) // 60

        # Build info string
        info_text = f"{info.hostname} | {info.distro} | Kernel {info.kernel} | Uptime: {hours}h {minutes}m"
        self._label.update(info_text)
