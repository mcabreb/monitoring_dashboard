"""Devices panel for battery and Bluetooth devices."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, ProgressBar

from monitor_dashboard.models.battery import BatteryStatus, BluetoothDevice
from monitor_dashboard.panels.base import BasePanel


class DevicesPanel(BasePanel):
    """Panel displaying device information."""

    BORDER_TITLE = "● Devices"

    def __init__(self, **kwargs) -> None:
        """Initialize devices panel."""
        super().__init__(**kwargs)
        self._container: Vertical | None = None

    def compose(self) -> ComposeResult:
        """Compose the Devices panel content."""
        self._container = Vertical()
        yield self._container

    def update(
        self,
        battery: BatteryStatus | None,
        bluetooth_devices: list[BluetoothDevice] | None,
    ) -> None:
        """Update panel with device information.

        Args:
            battery: Battery status, or None if unavailable.
            bluetooth_devices: List of Bluetooth devices, or None if unavailable.
        """
        if not self._container:
            return

        # Clear existing content
        self._container.remove_children()

        # Display battery
        if battery and battery.is_present:
            self._container.mount(Label(f"Battery: {int(battery.percent)}% ({battery.state.value})"))
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
                dev_label = f"{dev.name}"
                if dev.battery_percent is not None:
                    dev_label += f" ({dev.battery_percent}%)"
                self._container.mount(Label(dev_label))
        else:
            self._container.mount(Label(""))
            self._container.mount(Label("Bluetooth: No devices"))
