"""Battery data collection using psutil."""

import logging

import psutil

from monitor_dashboard.models.battery import BatteryState, BatteryStatus

logger = logging.getLogger(__name__)


class BatteryCollector:
    """Collects laptop battery status using psutil."""

    def collect(self) -> BatteryStatus | None:
        """Gather current battery information.

        Returns:
            BatteryStatus with current values, or None if no battery present.
        """
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return BatteryStatus(
                    percent=0.0,
                    state=BatteryState.UNKNOWN,
                    time_remaining=None,
                    is_present=False,
                )

            # Determine battery state
            if battery.power_plugged:
                if battery.percent >= 99:
                    state = BatteryState.FULL
                else:
                    state = BatteryState.CHARGING
            else:
                state = BatteryState.DISCHARGING

            # Time remaining (-1 means unknown)
            time_remaining = battery.secsleft if battery.secsleft > 0 else None

            return BatteryStatus(
                percent=battery.percent,
                state=state,
                time_remaining=time_remaining,
                is_present=True,
            )

        except Exception as e:
            logger.error(f"Failed to collect battery metrics: {e}")
            return None
