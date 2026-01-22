"""Main application module for Monitor Dashboard."""

import os
import signal
from datetime import datetime
from pathlib import Path

from textual.app import App
from textual.binding import Binding

from monitor_dashboard.constants import (
    REFRESH_APT_CACHE_AGE,
    REFRESH_APT_PACKAGES,
    REFRESH_BATTERY,
    REFRESH_CPU,
    REFRESH_LOAD,
    REFRESH_LOGS,
    REFRESH_MEMORY,
    REFRESH_PROCESSES,
    REFRESH_STORAGE,
    REFRESH_SYSTEM_INFO,
    REFRESH_UPTIME,
)
from monitor_dashboard.data_sources import (
    AptCollector,
    BatteryCollector,
    BluetoothCollector,
    LogsCollector,
    ProcessCollector,
    StorageCollector,
    SystemHealthCollector,
    SystemInfoCollector,
)
from monitor_dashboard.panels.devices import DevicesPanel
from monitor_dashboard.panels.info_bar import InfoBar
from monitor_dashboard.panels.logs import LogsPanel
from monitor_dashboard.panels.processes import ProcessesPanel
from monitor_dashboard.panels.selectable import SelectableMixin, SelectionState
from monitor_dashboard.panels.system_health import SystemHealthPanel
from monitor_dashboard.screens import (
    ExpandedPanelScreen,
    ErrorPopup,
    ExportSuccessPopup,
    HelpOverlay,
    InfoPopup,
    KillConfirmPopup,
    MainDashboard,
)
from monitor_dashboard.utils import HistoryBuffer


class MonitorDashboardApp(App):
    """Main Monitor Dashboard application with GEM-style panel layout."""

    CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

    BINDINGS = [
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Previous Panel"),
        Binding("enter", "toggle_expand", "Expand/Collapse"),
        Binding("escape", "collapse", "Return", show=False),
        Binding("up", "select_previous", "Select Previous", show=False),
        Binding("down", "select_next", "Select Next", show=False),
        Binding("home", "select_first", "Select First", show=False),
        Binding("end", "select_last", "Select Last", show=False),
        Binding("space", "toggle_sticky", "Toggle Sticky", show=False),
        Binding("c", "clear_sticky", "Clear Sticky", show=False),
        Binding("p", "cycle_process_sort", "Sort Processes"),
        Binding("i", "show_info", "Show Info", show=False),
        Binding("l", "export_logs", "Export Logs", show=False),
        Binding("k", "kill_process", "Kill Process", show=False),
        Binding("question_mark", "show_help", "Help"),
        Binding("w", "resize_window", "Resize Window", show=False),
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Initialize the app by pushing the main dashboard screen."""
        # Resize terminal window to preferred size
        self.action_resize_window()

        self.push_screen(MainDashboard())

        # Initialize data collectors
        self._system_health_collector = SystemHealthCollector()
        self._storage_collector = StorageCollector()
        self._process_collector = ProcessCollector()
        self._battery_collector = BatteryCollector()
        self._bluetooth_collector = BluetoothCollector()
        self._logs_collector = LogsCollector()
        self._system_info_collector = SystemInfoCollector()
        self._apt_collector = AptCollector()

        # History buffers for graphs
        self._cpu_history = HistoryBuffer(maxlen=60)
        self._memory_history = HistoryBuffer(maxlen=60)
        self._load_history = HistoryBuffer(maxlen=60)

        # Cached data for panels that need multiple data sources
        self._cached_battery = None
        self._cached_bluetooth = None
        self._cached_storage = None
        self._cached_system_info = None
        self._cached_apt_status = None

        # Store focused panel ID for restoration after expansion
        self._stored_focus_id: str | None = None

        # Store selection states per panel for persistence across expand/collapse
        self._selection_states: dict[str, SelectionState] = {}

        # Track previous focused panel to clear selections on change
        self._previous_focused_panel_id: str | None = None

        # =====================================================================
        # Set up refresh timers with prime number intervals from constants.py
        # =====================================================================

        # System Health Panel timers
        self.set_interval(REFRESH_CPU, self._refresh_cpu)
        self.set_interval(REFRESH_MEMORY, self._refresh_memory)
        self.set_interval(REFRESH_LOAD, self._refresh_load)

        # Processes Panel timer
        self.set_interval(REFRESH_PROCESSES, self._refresh_processes)

        # Devices Panel timers
        self.set_interval(REFRESH_BATTERY, self._refresh_battery)
        self.set_interval(REFRESH_STORAGE, self._refresh_storage)

        # Logs Panel timer
        self.set_interval(REFRESH_LOGS, self._refresh_logs)

        # Info Panel timers
        self.set_interval(REFRESH_SYSTEM_INFO, self._refresh_system_info)
        self.set_interval(REFRESH_UPTIME, self._refresh_uptime)
        self.set_interval(REFRESH_APT_PACKAGES, self._refresh_apt_packages)
        self.set_interval(REFRESH_APT_CACHE_AGE, self._refresh_apt_cache_age)

        # =====================================================================
        # Initial data refresh (order: Info, System Health, Devices, Processes, Logs)
        # =====================================================================
        self.call_later(self._initial_refresh)

    def _initial_refresh(self) -> None:
        """Perform initial data refresh in specified order."""
        # Order: Info, System Health, Devices, Processes, Logs

        # 1. Info Panel
        self._refresh_system_info()
        self._refresh_uptime()
        self._refresh_apt_packages()

        # 2. System Health Panel
        self._refresh_cpu()
        self._refresh_memory()
        self._refresh_load()

        # 3. Devices Panel
        self._refresh_battery()
        self._refresh_storage()

        # 4. Processes Panel
        self._refresh_processes()

        # 5. Logs Panel
        self._refresh_logs()

    # =========================================================================
    # System Health Panel refresh methods
    # =========================================================================

    def _refresh_cpu(self) -> None:
        """Refresh CPU data."""
        try:
            metrics = self._system_health_collector.collect()
            if metrics:
                self._cpu_history.append(metrics.cpu_percent)
                self._update_system_health_panel()
        except Exception:
            pass

    def _refresh_memory(self) -> None:
        """Refresh memory data."""
        try:
            metrics = self._system_health_collector.collect()
            if metrics:
                self._memory_history.append(metrics.memory_percent)
                self._update_system_health_panel()
        except Exception:
            pass

    def _refresh_load(self) -> None:
        """Refresh load average data."""
        try:
            metrics = self._system_health_collector.collect()
            if metrics:
                self._load_history.append(metrics.load_avg[0])
                self._update_system_health_panel()
        except Exception:
            pass

    def _update_system_health_panel(self) -> None:
        """Update the system health panel with current data."""
        try:
            metrics = self._system_health_collector.collect()
            panel = self.screen.query_one("#system-health", SystemHealthPanel)
            panel.update(
                metrics,
                self._cpu_history.get_values(),
                self._memory_history.get_values(),
                self._load_history.get_values(),
            )
        except Exception:
            pass

    # =========================================================================
    # Processes Panel refresh methods
    # =========================================================================

    def _refresh_processes(self) -> None:
        """Refresh process list."""
        try:
            panel = self.screen.query_one("#processes", ProcessesPanel)
            # Calculate max_processes based on panel height (1 row per process + 1 header)
            # Use minimum of 50 to ensure reasonable coverage even when panel is small
            panel_height = panel.content_size.height if panel.content_size else 50
            max_processes = max(50, panel_height + 10)  # Add buffer for scrolling
            processes = self._process_collector.collect(max_processes=max_processes)
            panel.update(processes)
        except Exception:
            pass

    # =========================================================================
    # Devices Panel refresh methods
    # =========================================================================

    def _refresh_battery(self) -> None:
        """Refresh battery and Bluetooth data."""
        try:
            self._cached_battery = self._battery_collector.collect()
            self._cached_bluetooth = self._bluetooth_collector.collect()
            self._update_devices_panel()
        except Exception:
            pass

    def _refresh_storage(self) -> None:
        """Refresh storage/disk data."""
        try:
            self._cached_storage = self._storage_collector.collect()
            self._update_devices_panel()
        except Exception:
            pass

    def _update_devices_panel(self) -> None:
        """Update the devices panel with cached data."""
        try:
            panel = self.screen.query_one("#devices", DevicesPanel)
            panel.update(
                self._cached_battery,
                self._cached_bluetooth,
                self._cached_storage,
            )
        except Exception:
            pass

    # =========================================================================
    # Logs Panel refresh methods
    # =========================================================================

    def _refresh_logs(self) -> None:
        """Refresh system logs."""
        try:
            logs = self._logs_collector.collect(max_entries=100)
            panel = self.screen.query_one("#logs", LogsPanel)
            panel.update(logs)
        except Exception:
            pass

    # =========================================================================
    # Info Panel refresh methods
    # =========================================================================

    def _refresh_system_info(self) -> None:
        """Refresh system info (hostname, distro, kernel)."""
        try:
            self._cached_system_info = self._system_info_collector.collect()
            self._update_info_panel()
        except Exception:
            pass

    def _refresh_uptime(self) -> None:
        """Refresh uptime display."""
        try:
            # Recalculate uptime from cached boot_time
            if self._cached_system_info and self._cached_system_info.boot_time:
                from monitor_dashboard.models.system_info import SystemInfo

                uptime_seconds = int(
                    (datetime.now() - self._cached_system_info.boot_time).total_seconds()
                )
                # Create updated SystemInfo with new uptime
                self._cached_system_info = SystemInfo(
                    hostname=self._cached_system_info.hostname,
                    kernel=self._cached_system_info.kernel,
                    distro=self._cached_system_info.distro,
                    uptime_seconds=uptime_seconds,
                    boot_time=self._cached_system_info.boot_time,
                )
                self._update_info_panel()
        except Exception:
            pass

    def _refresh_apt_packages(self) -> None:
        """Refresh apt upgradable packages list."""
        try:
            self._cached_apt_status = self._apt_collector.collect()
            self._update_info_panel_apt()
        except Exception:
            pass

    def _refresh_apt_cache_age(self) -> None:
        """Refresh apt cache age display."""
        try:
            if self._cached_apt_status:
                # Recalculate cache age
                cache_age = self._apt_collector._get_cache_age()
                from monitor_dashboard.data_sources.apt import AptStatus

                self._cached_apt_status = AptStatus(
                    packages=self._cached_apt_status.packages,
                    checked=self._cached_apt_status.checked,
                    cache_age_seconds=cache_age,
                )
                self._update_info_panel_apt()
        except Exception:
            pass

    def _update_info_panel(self) -> None:
        """Update info panel with system info."""
        try:
            panel = self.screen.query_one("#info-bar", InfoBar)
            panel.update(self._cached_system_info)
        except Exception:
            pass

    def _update_info_panel_apt(self) -> None:
        """Update info panel with apt status."""
        try:
            panel = self.screen.query_one("#info-bar", InfoBar)
            panel.update_apt(self._cached_apt_status)
        except Exception:
            pass

    # =========================================================================
    # Panel selection and focus management
    # =========================================================================

    def _get_focused_panel(self) -> SelectableMixin | None:
        """Get the currently focused panel if it supports selection."""
        focused = self.focused
        if focused and isinstance(focused, SelectableMixin):
            return focused
        return None

    def _get_panel_by_id(self, panel_id: str) -> SelectableMixin | None:
        """Get a panel by its ID."""
        try:
            panel = self.screen.query_one(f"#{panel_id}")
            if isinstance(panel, SelectableMixin):
                return panel
        except Exception:
            pass
        return None

    def _clear_panel_selections(self, panel_id: str) -> None:
        """Clear all selections in a panel."""
        panel = self._get_panel_by_id(panel_id)
        if panel:
            panel.clear_selections()
        if panel_id in self._selection_states:
            del self._selection_states[panel_id]

    def _save_panel_selection_state(self, panel_id: str) -> None:
        """Save a panel's selection state."""
        panel = self._get_panel_by_id(panel_id)
        if panel:
            self._selection_states[panel_id] = panel.get_selection_state()

    def _restore_panel_selection_state(self, panel_id: str) -> None:
        """Restore a panel's selection state."""
        if panel_id in self._selection_states:
            panel = self._get_panel_by_id(panel_id)
            if panel:
                panel.set_selection_state(self._selection_states[panel_id])

    def _on_panel_focus_changed(self, new_panel_id: str | None) -> None:
        """Handle focus changing to a new panel."""
        if self._previous_focused_panel_id and self._previous_focused_panel_id != new_panel_id:
            self._clear_panel_selections(self._previous_focused_panel_id)
        self._previous_focused_panel_id = new_panel_id

    # =========================================================================
    # Key bindings / actions
    # =========================================================================

    def action_focus_next(self) -> None:
        """Move focus to next panel in cycle."""
        if isinstance(self.screen, ExpandedPanelScreen):
            self._save_panel_selection_state(self.screen.panel_id)
            self.pop_screen()
            self.call_later(self._refresh_all)

        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#processes"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
            self.screen.query_one("#info-bar"),
        ]

        try:
            current_id = self._stored_focus_id
            current_idx = next(
                (i for i, p in enumerate(panels) if p.id == current_id), -1
            )
            if current_idx >= 0:
                next_idx = (current_idx + 1) % len(panels)
            else:
                current = self.focused
                if current in panels:
                    current_idx = panels.index(current)
                    next_idx = (current_idx + 1) % len(panels)
                else:
                    next_idx = 0
            self._stored_focus_id = panels[next_idx].id
            self._on_panel_focus_changed(panels[next_idx].id)
            panels[next_idx].focus()
        except Exception:
            panels[0].focus()

    def action_focus_previous(self) -> None:
        """Move focus to previous panel in cycle."""
        if isinstance(self.screen, ExpandedPanelScreen):
            self._save_panel_selection_state(self.screen.panel_id)
            self.pop_screen()
            self.call_later(self._refresh_all)

        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#processes"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
            self.screen.query_one("#info-bar"),
        ]

        try:
            current_id = self._stored_focus_id
            current_idx = next(
                (i for i, p in enumerate(panels) if p.id == current_id), -1
            )
            if current_idx >= 0:
                prev_idx = (current_idx - 1) % len(panels)
            else:
                current = self.focused
                if current in panels:
                    current_idx = panels.index(current)
                    prev_idx = (current_idx - 1) % len(panels)
                else:
                    prev_idx = -1
            self._stored_focus_id = panels[prev_idx].id
            self._on_panel_focus_changed(panels[prev_idx].id)
            panels[prev_idx].focus()
        except Exception:
            panels[-1].focus()

    def action_select_next(self) -> None:
        """Select next element in focused panel."""
        panel = self._get_focused_panel()
        if panel:
            panel.select_next()

    def action_select_previous(self) -> None:
        """Select previous element in focused panel."""
        panel = self._get_focused_panel()
        if panel:
            panel.select_previous()

    def action_toggle_sticky(self) -> None:
        """Toggle sticky selection on current element."""
        panel = self._get_focused_panel()
        if panel:
            panel.toggle_sticky()

    def action_clear_sticky(self) -> None:
        """Clear all sticky selections in focused panel."""
        panel = self._get_focused_panel()
        if panel:
            panel.clear_sticky_selections()

    def action_select_first(self) -> None:
        """Select first element in focused panel."""
        panel = self._get_focused_panel()
        if panel:
            panel.select_first()

    def action_select_last(self) -> None:
        """Select last element in focused panel."""
        panel = self._get_focused_panel()
        if panel:
            panel.select_last()

    def action_show_help(self) -> None:
        """Show the help overlay with keyboard shortcuts."""
        self.push_screen(HelpOverlay())

    def action_cycle_process_sort(self) -> None:
        """Cycle the sort column in the Processes panel."""
        try:
            panel = self.screen.query_one("#processes", ProcessesPanel)
            panel.cycle_sort()
        except Exception:
            pass

    def action_show_info(self) -> None:
        """Show info popup for selected elements in focused panel."""
        panel = self._get_focused_panel()
        if not panel:
            return

        sticky_ids = panel.get_sticky_ids()
        cursor_id = panel.get_cursor_id()

        if sticky_ids:
            element_ids = list(sticky_ids)
        elif cursor_id:
            element_ids = [cursor_id]
        else:
            self.push_screen(ErrorPopup("No Selection", "No element selected"))
            return

        items = []
        for element_id in element_ids:
            data = panel.get_element_data(element_id)
            if data:
                if hasattr(data, "details") and data.details:
                    items.append({"label": getattr(data, "label", element_id), "details": data.details})
                elif hasattr(data, "__dict__"):
                    items.append({"label": element_id, "details": data.__dict__})
                else:
                    items.append({"label": element_id, "details": str(data)})

        if items:
            focused = self.focused
            if hasattr(focused, "id"):
                title = f"Info: {focused.id.replace('-', ' ').title()}"
            else:
                title = "Info"

            search_query = None
            if hasattr(focused, "id") and focused.id == "logs":
                first_data = panel.get_element_data(element_ids[0])
                if first_data and hasattr(first_data, "message"):
                    search_query = first_data.message

            self.push_screen(InfoPopup(title, items, search_query=search_query))

    def action_export_logs(self) -> None:
        """Export logs to ~/Downloads."""
        focused = self.focused
        if not hasattr(focused, "id") or focused.id != "logs":
            return

        try:
            panel = self.screen.query_one("#logs", LogsPanel)
        except Exception:
            return

        sticky_ids = panel.get_sticky_ids()
        if sticky_ids:
            logs_to_export = []
            for log_id in sticky_ids:
                log = panel.get_element_data(log_id)
                if log:
                    logs_to_export.append(log)
        else:
            logs_to_export = panel.get_all_logs()

        if not logs_to_export:
            self.push_screen(ErrorPopup("No Logs", "No logs to export"))
            return

        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"logs_{timestamp}.txt"
        filepath = downloads_dir / filename

        try:
            with open(filepath, "w") as f:
                for log in logs_to_export:
                    f.write(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} {log.message}\n")
            self.push_screen(ExportSuccessPopup(str(filepath), len(logs_to_export)))
        except Exception as e:
            self.push_screen(ErrorPopup("Export Failed", str(e)))

    def action_kill_process(self) -> None:
        """Kill selected process (with confirmation)."""
        focused = self.focused
        if not hasattr(focused, "id") or focused.id != "processes":
            return

        try:
            panel = self.screen.query_one("#processes", ProcessesPanel)
        except Exception:
            return

        sticky_ids = panel.get_sticky_ids()
        if sticky_ids:
            self.push_screen(
                ErrorPopup(
                    "Cannot Kill Multiple",
                    "Kill only works on cursor selection, not sticky selections.\n"
                    "Use SPACE to remove sticky selections first.",
                )
            )
            return

        cursor_id = panel.get_cursor_id()
        if not cursor_id:
            self.push_screen(ErrorPopup("No Selection", "No process selected"))
            return

        process = panel.get_element_data(cursor_id)
        if not process:
            return

        current_user = os.getenv("USER", "")
        if process.user != current_user:
            self.push_screen(
                ErrorPopup(
                    "Cannot Kill",
                    f"Cannot kill process owned by '{process.user}'.\n"
                    f"Only processes owned by '{current_user}' can be killed.",
                )
            )
            return

        def handle_kill_confirm(confirmed: bool) -> None:
            if confirmed:
                try:
                    os.kill(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    self.push_screen(ErrorPopup("Process Not Found", f"Process {process.pid} no longer exists"))
                except PermissionError:
                    self.push_screen(ErrorPopup("Permission Denied", f"Cannot kill process {process.pid}"))
                except Exception as e:
                    self.push_screen(ErrorPopup("Kill Failed", str(e)))

        self.push_screen(KillConfirmPopup(process.pid, process.command[:30]), handle_kill_confirm)

    def action_toggle_expand(self) -> None:
        """Toggle between expanded and normal view."""
        if isinstance(self.screen, ExpandedPanelScreen):
            self.action_collapse()
        else:
            if self.focused and hasattr(self.focused, "id"):
                panel_id = self.focused.id
                if panel_id in ["system-health", "processes", "devices", "logs", "info-bar"]:
                    self._stored_focus_id = panel_id
                    self._clear_panel_selections(panel_id)
                    self.push_screen(ExpandedPanelScreen(panel_id))
                    self.call_later(self._refresh_all)

    def action_collapse(self) -> None:
        """Return to main dashboard from expanded view."""
        if isinstance(self.screen, ExpandedPanelScreen):
            panel_id = self.screen.panel_id
            self._clear_panel_selections(panel_id)
            self.pop_screen()
            self.call_later(self._restore_focus)
            self.call_later(self._refresh_all)

    def _restore_focus(self) -> None:
        """Restore focus to the previously focused panel."""
        if self._stored_focus_id:
            try:
                panel = self.screen.query_one(f"#{self._stored_focus_id}")
                panel.focus()
            except Exception:
                pass

    def _refresh_all(self) -> None:
        """Refresh all panel data immediately."""
        self._initial_refresh()

    def action_resize_window(self) -> None:
        """Resize the terminal window using escape sequences (works on Wayland)."""
        import os

        # Write directly to terminal device, bypassing Textual's stdout capture
        # Use xterm-style escape sequence for pixel resize: ESC[4;height;widtht
        try:
            with open("/dev/tty", "w") as tty:
                tty.write("\x1b[4;370;3200t")
                tty.flush()
        except OSError:
            # Fallback: try stdout if /dev/tty fails
            os.write(1, b"\x1b[4;370;32:3200t")
