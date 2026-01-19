"""Devices panel for battery and storage information."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.battery import BatteryStatus, BluetoothDevice
from monitor_dashboard.models.metrics import DiskInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes


class DevicesPanel(BasePanel):
    """Panel displaying battery and storage information."""

    BORDER_TITLE = "● Devices"

    def __init__(self, **kwargs) -> None:
        """Initialize devices panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None

    def compose(self) -> ComposeResult:
        """Compose the Devices panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(
        self,
        battery: BatteryStatus | None,
        bluetooth_devices: list[BluetoothDevice] | None,
        disks: list[DiskInfo] | None = None,
    ) -> None:
        """Update panel with device and storage information.

        Args:
            battery: Battery status, or None if unavailable.
            bluetooth_devices: List of Bluetooth devices, or None if unavailable.
            disks: List of disk info objects, or None if unavailable.
        """
        if not self._container:
            return

        self._container.remove_children()

        # === BATTERY SECTION ===
        self._container.mount(Label("Battery:"))

        # Laptop battery - white label, colored value
        if battery and battery.is_present:
            bat_color = self._get_battery_color(battery.percent)
            bat_value = f"[{bat_color}]{int(battery.percent)}% ({battery.state.value})[/{bat_color}]"
            status_text = f"  Laptop: {bat_value}"
            if battery.time_remaining:
                hours = battery.time_remaining // 3600
                minutes = (battery.time_remaining % 3600) // 60
                status_text += f" - {hours}h {minutes}m"
            self._container.mount(Label(status_text))
        else:
            self._container.mount(Label("  Laptop: Not present"))

        # Bluetooth devices with battery info - white label, colored value
        if bluetooth_devices:
            for dev in bluetooth_devices:
                if dev.battery_percent is not None:
                    bat_color = self._get_battery_color(dev.battery_percent)
                    bat_value = f"[{bat_color}]{dev.battery_percent}%[/{bat_color}]"
                    self._container.mount(Label(f"  {dev.name}: {bat_value}"))
                else:
                    self._container.mount(Label(f"  {dev.name}: connected"))
        else:
            self._container.mount(Label("  No Bluetooth devices"))

        # === SEPARATOR ===
        self._container.mount(Label(""))

        # === STORAGE SECTION ===
        self._container.mount(Label("Storage:"))

        if disks:
            for disk in disks:
                used = format_bytes(disk.used)
                total = format_bytes(disk.total)
                disk_color = self._get_disk_color(disk.percent)
                disk_value = f"[{disk_color}]{used}/{total} ({int(disk.percent)}%)[/{disk_color}]"
                self._container.mount(Label(f"  {disk.mount_point}: {disk_value}"))
        else:
            self._container.mount(Label("  No storage info"))

    def _get_battery_color(self, percent: float) -> str:
        """Get color for battery percentage.

        Args:
            percent: Battery percentage (0-100).

        Returns:
            Color name for Rich markup.
        """
        if percent > 50:
            return "green"
        elif percent >= 20:
            return "yellow"
        else:
            return "red"

    def _get_disk_color(self, percent: float) -> str:
        """Get color for disk usage percentage.

        Args:
            percent: Disk usage percentage (0-100).

        Returns:
            Color name for Rich markup.
        """
        if percent >= 90:
            return "red"
        elif percent >= 70:
            return "yellow"
        else:
            return "green"
