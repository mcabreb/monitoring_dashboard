"""System information data collection."""

import logging
import platform
import socket
from datetime import datetime

import psutil

from monitor_dashboard.models.system_info import SystemInfo

logger = logging.getLogger(__name__)


class SystemInfoCollector:
    """Collects system information (hostname, kernel, distro, uptime)."""

    def collect(self) -> SystemInfo | None:
        """Gather system information.

        Returns:
            SystemInfo with current values, or None on failure.
        """
        try:
            hostname = socket.gethostname()
            kernel = platform.release()

            # Get distro info
            try:
                import distro

                distro_name = distro.name(pretty=True)
            except:
                distro_name = platform.system()

            # Get uptime
            boot_time_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_time_timestamp)
            uptime_seconds = int((datetime.now() - boot_time).total_seconds())

            return SystemInfo(
                hostname=hostname,
                kernel=kernel,
                distro=distro_name,
                uptime_seconds=uptime_seconds,
                boot_time=boot_time,
            )

        except Exception as e:
            logger.error(f"Failed to collect system info: {e}")
            return None
