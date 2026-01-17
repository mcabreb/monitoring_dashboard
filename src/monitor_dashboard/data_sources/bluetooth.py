"""Bluetooth device data collection (stub for MVP)."""

import logging

from monitor_dashboard.models.battery import BluetoothDevice

logger = logging.getLogger(__name__)


class BluetoothCollector:
    """Collects Bluetooth device information.

    Note: D-Bus integration for actual Bluetooth scanning will be
    implemented in a future iteration. This is a stub returning
    empty list for MVP.
    """

    def collect(self) -> list[BluetoothDevice]:
        """Gather connected Bluetooth devices.

        Returns:
            List of BluetoothDevice objects. Empty for MVP stub.
        """
        # TODO: Implement D-Bus scanning via pydbus
        # For MVP, return empty list
        return []
