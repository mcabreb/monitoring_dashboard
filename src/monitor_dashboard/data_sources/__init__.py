"""Data source collectors for system metrics."""

from monitor_dashboard.data_sources.battery import BatteryCollector
from monitor_dashboard.data_sources.bluetooth import BluetoothCollector
from monitor_dashboard.data_sources.logs import LogsCollector
from monitor_dashboard.data_sources.process import ProcessCollector
from monitor_dashboard.data_sources.storage import StorageCollector
from monitor_dashboard.data_sources.system_health import SystemHealthCollector
from monitor_dashboard.data_sources.system_info import SystemInfoCollector

__all__ = [
    "BatteryCollector",
    "BluetoothCollector",
    "LogsCollector",
    "ProcessCollector",
    "StorageCollector",
    "SystemHealthCollector",
    "SystemInfoCollector",
]
