"""Main application module for Monitor Dashboard."""

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from monitor_dashboard.data_sources import (
    BatteryCollector,
    BluetoothCollector,
    LogsCollector,
    StorageCollector,
    SystemHealthCollector,
    SystemInfoCollector,
)
from monitor_dashboard.panels.devices import DevicesPanel
from monitor_dashboard.panels.info_bar import InfoBar
from monitor_dashboard.panels.logs import LogsPanel
from monitor_dashboard.panels.storage import StoragePanel
from monitor_dashboard.panels.system_health import SystemHealthPanel
from monitor_dashboard.screens import ExpandedPanelScreen, HelpOverlay, MainDashboard
from monitor_dashboard.utils import HistoryBuffer


class MonitorDashboardApp(App):
    """Main Monitor Dashboard application with GEM-style panel layout."""

    CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

    BINDINGS = [
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Previous Panel"),
        Binding("enter", "toggle_expand", "Expand/Collapse"),
        Binding("escape", "collapse", "Return", show=False),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("left", "scroll_left", "Scroll Left", show=False),
        Binding("right", "scroll_right", "Scroll Right", show=False),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Initialize the app by pushing the main dashboard screen."""
        self.push_screen(MainDashboard())

        # Initialize data collectors and history buffers
        self._system_health_collector = SystemHealthCollector()
        self._storage_collector = StorageCollector()
        self._battery_collector = BatteryCollector()
        self._bluetooth_collector = BluetoothCollector()
        self._logs_collector = LogsCollector()
        self._system_info_collector = SystemInfoCollector()
        self._cpu_history = HistoryBuffer(maxlen=60)
        self._memory_history = HistoryBuffer(maxlen=60)

        # Store focused panel ID for restoration after expansion
        self._stored_focus_id: str | None = None

        # Start refresh timers
        # Fast refresh (1s): System health (CPU, memory, load)
        self.set_interval(1.0, self._refresh_system_health)
        # Slow refresh (10s): Storage, battery, Bluetooth, logs, system info
        self.set_interval(10.0, self._refresh_slow_data)
        # Initial slow data refresh
        self.call_later(self._refresh_slow_data)

    def _refresh_system_health(self) -> None:
        """Refresh system health data at 1 Hz."""
        try:
            # Collect system health metrics
            metrics = self._system_health_collector.collect()
            if metrics:
                self._cpu_history.append(metrics.cpu_percent)
                self._memory_history.append(metrics.memory_percent)

            # Update system health panel
            try:
                panel = self.screen.query_one("#system-health", SystemHealthPanel)
                panel.update(
                    metrics,
                    self._cpu_history.get_values(),
                    self._memory_history.get_values(),
                )
            except Exception:
                pass

        except Exception:
            pass

    def _refresh_slow_data(self) -> None:
        """Refresh slow-changing data every 10 seconds.

        Updates storage, battery, Bluetooth, logs, and system info panels.
        """
        try:
            # Collect storage metrics
            disks = self._storage_collector.collect()

            # Update storage panel
            try:
                panel = self.screen.query_one("#storage", StoragePanel)
                panel.update(disks)
            except Exception:
                pass

            # Collect battery and Bluetooth metrics
            battery = self._battery_collector.collect()
            bluetooth_devices = self._bluetooth_collector.collect()

            # Update devices panel
            try:
                panel = self.screen.query_one("#devices", DevicesPanel)
                panel.update(battery, bluetooth_devices)
            except Exception:
                pass

            # Collect logs
            logs = self._logs_collector.collect(max_entries=100)

            # Update logs panel
            try:
                panel = self.screen.query_one("#logs", LogsPanel)
                panel.update(logs)
            except Exception:
                pass

            # Collect system info
            system_info = self._system_info_collector.collect()

            # Update info bar
            try:
                panel = self.screen.query_one("#info-bar", InfoBar)
                panel.update(system_info)
            except Exception:
                pass

        except Exception:
            pass

    def action_focus_next(self) -> None:
        """Move focus to next panel in cycle."""
        # Skip tab navigation in expanded view
        if isinstance(self.screen, ExpandedPanelScreen):
            return

        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#storage"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
        ]

        # Find current focused panel and move to next
        try:
            current = self.focused
            if current in panels:
                current_idx = panels.index(current)
                next_idx = (current_idx + 1) % len(panels)
                panels[next_idx].focus()
            else:
                # If no panel focused, focus first one
                panels[0].focus()
        except Exception:
            # Fallback: focus first panel
            panels[0].focus()

    def action_focus_previous(self) -> None:
        """Move focus to previous panel in cycle."""
        # Skip tab navigation in expanded view
        if isinstance(self.screen, ExpandedPanelScreen):
            return

        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#storage"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
        ]

        # Find current focused panel and move to previous
        try:
            current = self.focused
            if current in panels:
                current_idx = panels.index(current)
                prev_idx = (current_idx - 1) % len(panels)
                panels[prev_idx].focus()
            else:
                # If no panel focused, focus last one
                panels[-1].focus()
        except Exception:
            # Fallback: focus last panel
            panels[-1].focus()

    def action_scroll_up(self) -> None:
        """Scroll up within focused panel (stub for future implementation)."""
        pass

    def action_scroll_down(self) -> None:
        """Scroll down within focused panel (stub for future implementation)."""
        pass

    def action_scroll_left(self) -> None:
        """Scroll left within focused panel (stub for future implementation)."""
        pass

    def action_scroll_right(self) -> None:
        """Scroll right within focused panel (stub for future implementation)."""
        pass

    def action_show_help(self) -> None:
        """Show the help overlay with keyboard shortcuts."""
        self.push_screen(HelpOverlay())

    def action_toggle_expand(self) -> None:
        """Toggle between expanded and normal view."""
        if isinstance(self.screen, ExpandedPanelScreen):
            # Already expanded, collapse back to main dashboard
            self.action_collapse()
        else:
            # Expand the currently focused panel
            if self.focused and hasattr(self.focused, "id"):
                panel_id = self.focused.id
                # Only expand if it's one of the main panels
                if panel_id in ["system-health", "storage", "devices", "logs"]:
                    self._stored_focus_id = panel_id
                    self.push_screen(ExpandedPanelScreen(panel_id))
                    # Trigger immediate refresh after screen transition
                    self.call_later(self._refresh_all)

    def action_collapse(self) -> None:
        """Return to main dashboard from expanded view."""
        if isinstance(self.screen, ExpandedPanelScreen):
            self.pop_screen()
            # Restore focus and refresh after screen transition
            self.call_later(self._restore_focus)
            self.call_later(self._refresh_all)

    def _restore_focus(self) -> None:
        """Restore focus to the previously focused panel."""
        if self._stored_focus_id:
            try:
                panel = self.screen.query_one(f"#{self._stored_focus_id}")
                panel.focus()
            except Exception:
                # Panel not found, ignore
                pass

    def _refresh_all(self) -> None:
        """Refresh all panel data immediately."""
        self._refresh_system_health()
        self._refresh_slow_data()
