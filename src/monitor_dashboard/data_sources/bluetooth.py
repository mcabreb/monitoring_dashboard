"""Bluetooth device data collection using bluetoothctl and upower."""

import logging
import re
import subprocess

from monitor_dashboard.models.battery import BluetoothDevice, DeviceType

logger = logging.getLogger(__name__)


def _get_device_type_from_name(name: str) -> DeviceType:
    """Determine device type from device name.

    Args:
        name: Device name.

    Returns:
        DeviceType enum value.
    """
    name_lower = name.lower()

    if "keyboard" in name_lower:
        return DeviceType.KEYBOARD
    if "trackpad" in name_lower or "mouse" in name_lower:
        return DeviceType.MOUSE
    if "airpod" in name_lower or "headphone" in name_lower or "buds" in name_lower:
        return DeviceType.HEADPHONES
    if "speaker" in name_lower:
        return DeviceType.SPEAKER
    if "phone" in name_lower or "iphone" in name_lower or "android" in name_lower:
        return DeviceType.PHONE

    return DeviceType.UNKNOWN


def _get_upower_battery_levels() -> dict[str, int]:
    """Get battery levels for Bluetooth devices from upower.

    Returns:
        Dict mapping MAC address (lowercase, colon-separated) to battery percentage.
    """
    battery_levels = {}

    try:
        # List all upower devices
        result = subprocess.run(
            ["upower", "-e"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0:
            return battery_levels

        # Find HID battery devices (Bluetooth peripherals)
        for device_path in result.stdout.strip().split("\n"):
            if "hid" not in device_path or "battery" not in device_path:
                continue

            # Get device details
            info_result = subprocess.run(
                ["upower", "-i", device_path],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if info_result.returncode != 0:
                continue

            # Extract serial (MAC address) and percentage
            serial = None
            percentage = None

            for line in info_result.stdout.split("\n"):
                line = line.strip()
                if line.startswith("serial:"):
                    serial = line.split(":", 1)[1].strip().lower()
                elif line.startswith("percentage:"):
                    match = re.search(r"(\d+)%", line)
                    if match:
                        percentage = int(match.group(1))

            if serial and percentage is not None:
                battery_levels[serial] = percentage

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        logger.debug(f"Failed to get upower battery levels: {e}")

    return battery_levels


class BluetoothCollector:
    """Collects Bluetooth device information via bluetoothctl and upower."""

    def collect(self) -> list[BluetoothDevice]:
        """Gather connected Bluetooth devices.

        Returns:
            List of BluetoothDevice objects for connected devices.
        """
        devices = []

        # Get battery levels from upower first
        battery_levels = _get_upower_battery_levels()

        try:
            # Get connected devices using bluetoothctl
            result = subprocess.run(
                ["bluetoothctl", "devices", "Connected"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return devices

            # Parse output: "Device XX:XX:XX:XX:XX:XX DeviceName"
            for line in result.stdout.strip().split("\n"):
                if not line.startswith("Device "):
                    continue

                parts = line.split(" ", 2)
                if len(parts) < 3:
                    continue

                address = parts[1]
                name = parts[2]

                device_type = _get_device_type_from_name(name)

                # Look up battery level by MAC address
                battery_percent = battery_levels.get(address.lower())

                devices.append(
                    BluetoothDevice(
                        name=name,
                        address=address,
                        device_type=device_type,
                        battery_percent=battery_percent,
                        is_connected=True,
                    )
                )

        except subprocess.TimeoutExpired:
            logger.debug("bluetoothctl timed out")
        except FileNotFoundError:
            logger.debug("bluetoothctl not found")
        except Exception as e:
            logger.debug(f"Failed to collect Bluetooth devices: {e}")

        return devices
