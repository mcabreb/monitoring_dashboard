"""Devices panel for battery and storage information."""

from dataclasses import dataclass
from typing import Any

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.battery import BatteryStatus, BluetoothDevice
from monitor_dashboard.models.metrics import DiskInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.selectable import SelectableMixin
from monitor_dashboard.utils.formatting import format_bytes


@dataclass
class DeviceItem:
    """Data for a selectable device item."""

    id: str
    label: str
    value: str
    color: str
    item_type: str  # "battery", "bluetooth", "disk"
    details: dict[str, Any] | None = None


class DevicesPanel(BasePanel, SelectableMixin):
    """Panel displaying battery and storage information."""

    BORDER_TITLE = "● Devices"

    def __init__(self, **kwargs) -> None:
        """Initialize devices panel."""
        super().__init__(**kwargs)
        self.init_selection()
        self._container: VerticalScroll | None = None
        self._device_items: list[DeviceItem] = []
        # Store raw data for rebuilding
        self._battery: BatteryStatus | None = None
        self._bluetooth_devices: list[BluetoothDevice] | None = None
        self._disks: list[DiskInfo] | None = None

    def compose(self) -> ComposeResult:
        """Compose the Devices panel content."""
        self._container = VerticalScroll()
        yield self._container

    def on_mount(self) -> None:
        """Handle mount event - display any stored data."""
        if self._battery is not None or self._bluetooth_devices is not None or self._disks is not None:
            self._build_device_items()
            self._display()

    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs."""
        return [item.id for item in self._device_items]

    def get_element_data(self, element_id: str) -> DeviceItem | None:
        """Get device item data for an element ID."""
        for item in self._device_items:
            if item.id == element_id:
                return item
        return None

    def refresh_selection_display(self) -> None:
        """Re-render with selection styling."""
        self._display()

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
        self._battery = battery
        self._bluetooth_devices = bluetooth_devices
        self._disks = disks

        self._build_device_items()

        # Prune sticky selections for items that no longer exist
        self.prune_invalid_sticky()

        self._display()

    def _build_device_items(self) -> None:
        """Build list of selectable device items."""
        self._device_items = []

        # Battery section
        if self._battery and self._battery.is_present:
            bat_color = self._get_battery_color(self._battery.percent)
            time_str = ""
            if self._battery.time_remaining:
                hours = self._battery.time_remaining // 3600
                minutes = (self._battery.time_remaining % 3600) // 60
                time_str = f" - {hours}h {minutes}m"

            self._device_items.append(DeviceItem(
                id="battery-laptop",
                label="Laptop",
                value=f"{int(self._battery.percent)}% ({self._battery.state.value}){time_str}",
                color=bat_color,
                item_type="battery",
                details={
                    "percent": self._battery.percent,
                    "state": self._battery.state.value,
                    "time_remaining": self._battery.time_remaining,
                    "is_present": True,
                },
            ))
        else:
            self._device_items.append(DeviceItem(
                id="battery-laptop",
                label="Laptop",
                value="Not present",
                color="white",
                item_type="battery",
                details={"is_present": False},
            ))

        # Bluetooth devices
        if self._bluetooth_devices:
            for dev in self._bluetooth_devices:
                device_id = f"bt-{dev.address.replace(':', '-')}"
                if dev.battery_percent is not None:
                    bat_color = self._get_battery_color(dev.battery_percent)
                    value = f"{dev.battery_percent}%"
                else:
                    bat_color = "white"
                    value = "connected"

                self._device_items.append(DeviceItem(
                    id=device_id,
                    label=dev.name,
                    value=value,
                    color=bat_color,
                    item_type="bluetooth",
                    details={
                        "name": dev.name,
                        "address": dev.address,
                        "battery_percent": dev.battery_percent,
                        "connected": dev.is_connected,
                    },
                ))

        # Storage disks
        if self._disks:
            for disk in self._disks:
                # Use mount point as ID (sanitized)
                disk_id = f"disk-{disk.mount_point.replace('/', '-')}"
                used = format_bytes(disk.used)
                total = format_bytes(disk.total)
                disk_color = self._get_disk_color(disk.percent)

                self._device_items.append(DeviceItem(
                    id=disk_id,
                    label=disk.mount_point,
                    value=f"{used}/{total} ({int(disk.percent)}%)",
                    color=disk_color,
                    item_type="disk",
                    details={
                        "mount_point": disk.mount_point,
                        "device": disk.device,
                        "fstype": disk.fs_type,
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": disk.percent,
                    },
                ))

    def _display(self) -> None:
        """Render the panel with current data and selection styling."""
        if not self._container:
            return

        self._container.remove_children()

        # === BATTERY SECTION ===
        self._container.mount(Label("Battery:"))

        # Find battery items
        battery_items = [i for i in self._device_items if i.item_type == "battery"]
        bluetooth_items = [i for i in self._device_items if i.item_type == "bluetooth"]
        disk_items = [i for i in self._device_items if i.item_type == "disk"]

        # Laptop battery
        for item in battery_items:
            text = f"  {item.label}: [{item.color}]{item.value}[/{item.color}]"
            label = self._create_label(text, item.id)
            self._container.mount(label)

        # Bluetooth devices
        if bluetooth_items:
            for item in bluetooth_items:
                text = f"  {item.label}: [{item.color}]{item.value}[/{item.color}]"
                label = self._create_label(text, item.id)
                self._container.mount(label)
        else:
            self._container.mount(Label("  No Bluetooth devices"))

        # === SEPARATOR ===
        self._container.mount(Label(""))

        # === STORAGE SECTION ===
        self._container.mount(Label("Storage:"))

        if disk_items:
            for item in disk_items:
                text = f"  {item.label}: [{item.color}]{item.value}[/{item.color}]"
                label = self._create_label(text, item.id)
                self._container.mount(label)
        else:
            self._container.mount(Label("  No storage info"))

    def _create_label(self, text: str, element_id: str) -> Label:
        """Create a label with selection styling.

        Args:
            text: Label text content.
            element_id: Element ID for selection tracking.

        Returns:
            Configured Label widget.
        """
        label = Label(text)
        selection_class = self.get_selection_class(element_id)
        if selection_class:
            label.add_class(selection_class)
        return label

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
