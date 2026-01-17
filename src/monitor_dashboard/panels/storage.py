"""Storage panel for disk usage and mount points."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, ProgressBar, Static

from monitor_dashboard.models.metrics import DiskInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes, format_percent
from monitor_dashboard.widgets.led_indicator import LEDStatus


class StoragePanel(BasePanel):
    """Panel displaying storage information."""

    BORDER_TITLE = "● Storage"

    def __init__(self, **kwargs) -> None:
        """Initialize storage panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None

    def compose(self) -> ComposeResult:
        """Compose the Storage panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(self, disks: list[DiskInfo] | None) -> None:
        """Update panel with disk information.

        Args:
            disks: List of disk info objects, or None if unavailable.
        """
        if not self._container:
            return

        # Clear existing content
        self._container.remove_children()

        if not disks:
            self._container.mount(Label("No partitions found"))
            return

        # Display each disk
        for disk in disks:
            # Create label with mount point and usage
            used = format_bytes(disk.used)
            total = format_bytes(disk.total)
            label_text = f"{disk.mount_point} - {used} / {total} ({int(disk.percent)}%)"

            # Determine color class based on usage
            color_class = self._get_color_class(disk.percent)

            # Mount label and progress bar
            label = Label(label_text)
            label.add_class(color_class)
            self._container.mount(label)

            bar = ProgressBar(total=100, show_eta=False)
            bar.update(progress=disk.percent)
            bar.add_class(color_class)
            self._container.mount(bar)

            # Add spacer
            self._container.mount(Static(""))

    def _get_color_class(self, percent: float) -> str:
        """Get CSS class for disk usage color coding.

        Args:
            percent: Disk usage percentage (0-100).

        Returns:
            CSS class name.
        """
        if percent >= 90:
            return "disk-critical"
        elif percent >= 70:
            return "disk-warning"
        return "disk-ok"

    def get_worst_status(self, disks: list[DiskInfo] | None) -> LEDStatus:
        """Determine worst-case LED status from all disks.

        Args:
            disks: List of disk info objects.

        Returns:
            Worst LED status across all disks.
        """
        if not disks:
            return LEDStatus.OK

        max_percent = max(disk.percent for disk in disks)

        if max_percent >= 90:
            return LEDStatus.CRITICAL
        elif max_percent >= 70:
            return LEDStatus.WARNING
        return LEDStatus.OK
