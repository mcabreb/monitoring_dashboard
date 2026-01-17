"""Battery and device data models."""

from dataclasses import dataclass
from enum import Enum


class BatteryState(Enum):
    """Battery charging state."""

    CHARGING = "charging"
    DISCHARGING = "discharging"
    FULL = "full"
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """Bluetooth device type."""

    HEADPHONES = "headphones"
    MOUSE = "mouse"
    KEYBOARD = "keyboard"
    SPEAKER = "speaker"
    PHONE = "phone"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BatteryStatus:
    """Laptop battery status information."""

    percent: float  # 0-100
    state: BatteryState
    time_remaining: int | None  # Seconds, None if unknown
    is_present: bool


@dataclass(frozen=True)
class BluetoothDevice:
    """Bluetooth device information."""

    name: str
    address: str
    device_type: DeviceType
    battery_percent: int | None  # 0-100, None if not available
    is_connected: bool
