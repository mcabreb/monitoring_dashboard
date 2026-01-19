"""Devices panel for battery, Bluetooth devices, and storage."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, ProgressBar

from monitor_dashboard.models.battery import BatteryStatus, BluetoothDevice
from monitor_dashboard.models.metrics import DiskInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes


class DevicesPanel(BasePanel):
    """Panel displaying device and storage information."""

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

        # Clear existing content
        self._container.remove_children()

        # Display laptop battery
        if battery and battery.is_present:
            self._container.mount(Label(f"Laptop: {int(battery.percent)}% ({battery.state.value})"))
            bar = ProgressBar(total=100, show_eta=False)
            bar.update(progress=battery.percent)
            self._container.mount(bar)

            if battery.time_remaining:
                hours = battery.time_remaining // 3600
                minutes = (battery.time_remaining % 3600) // 60
                self._container.mount(Label(f"Time: {hours}h {minutes}m"))
        else:
            self._container.mount(Label("Battery: Not present"))

        # Display Bluetooth devices
        if bluetooth_devices:
            self._container.mount(Label(""))
            self._container.mount(Label(f"Bluetooth: {len(bluetooth_devices)} device(s)"))
            for dev in bluetooth_devices:
                dev_label = f"  {dev.name}"
                if dev.battery_percent is not None:
                    dev_label += f" ({dev.battery_percent}%)"
                self._container.mount(Label(dev_label))
        else:
            self._container.mount(Label(""))
            self._container.mount(Label("Bluetooth: No devices"))

        # Display disk storage
        if disks:
            self._container.mount(Label(""))
            self._container.mount(Label("Storage:"))
            for disk in disks:
                used = format_bytes(disk.used)
                total = format_bytes(disk.total)
                label_text = f"  {disk.mount_point}: {used}/{total} ({int(disk.percent)}%)"

                label = Label(label_text)
                if disk.percent >= 90:
                    label.add_class("disk-critical")
                elif disk.percent >= 70:
                    label.add_class("disk-warning")
                else:
                    label.add_class("disk-ok")
                self._container.mount(label)
