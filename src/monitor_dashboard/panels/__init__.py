"""Panel widgets for the monitor dashboard."""

from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.system_health import SystemHealthPanel
from monitor_dashboard.panels.storage import StoragePanel
from monitor_dashboard.panels.devices import DevicesPanel
from monitor_dashboard.panels.logs import LogsPanel
from monitor_dashboard.panels.info_bar import InfoBar

__all__ = [
    "BasePanel",
    "SystemHealthPanel",
    "StoragePanel",
    "DevicesPanel",
    "LogsPanel",
    "InfoBar",
]
