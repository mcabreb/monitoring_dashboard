"""Panel widgets for the monitor dashboard."""

from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.devices import DevicesPanel
from monitor_dashboard.panels.info_bar import InfoBar
from monitor_dashboard.panels.logs import LogsPanel
from monitor_dashboard.panels.processes import ProcessesPanel
from monitor_dashboard.panels.system_health import SystemHealthPanel

__all__ = [
    "BasePanel",
    "DevicesPanel",
    "InfoBar",
    "LogsPanel",
    "ProcessesPanel",
    "SystemHealthPanel",
]
