"""System health data collection using psutil."""

import logging
from datetime import datetime

import psutil

from monitor_dashboard.models.metrics import SystemMetrics

logger = logging.getLogger(__name__)


class SystemHealthCollector:
    """Collects CPU, memory, and load average metrics using psutil."""

    def collect(self) -> SystemMetrics | None:
        """Gather current system health data.

        Uses non-blocking psutil calls to collect:
        - CPU percentage (overall and per-core)
        - Memory usage (used, total, percent)
        - Load average (1, 5, 15 minute)

        Returns:
            SystemMetrics with current values, or None on failure.

        Note:
            First call to cpu_percent may return 0.0 as it needs
            a previous call for comparison.
        """
        try:
            # Collect CPU metrics (non-blocking with interval=None)
            cpu = psutil.cpu_percent(interval=None)
            cpu_per_core = tuple(psutil.cpu_percent(interval=None, percpu=True))

            # Collect memory metrics
            mem = psutil.virtual_memory()

            # Collect load average
            load = psutil.getloadavg()

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu,
                cpu_per_core=cpu_per_core,
                memory_used=mem.used,
                memory_total=mem.total,
                memory_percent=mem.percent,
                load_avg=load,
            )

        except Exception as e:
            logger.error(f"Failed to collect system health metrics: {e}")
            return None
