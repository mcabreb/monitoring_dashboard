"""Main application module for Monitor Dashboard."""

import os
import signal
from datetime import datetime
from pathlib import Path

from textual.app import App
from textual.binding import Binding

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
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Initialize the app by pushing the main dashboard screen."""
        self.push_screen(MainDashboard())

        # Initialize data collectors and history buffers
        self._system_health_collector = SystemHealthCollector()
        self._storage_collector = StorageCollector()
        self._process_collector = ProcessCollector()
        self._battery_collector = BatteryCollector()
        self._bluetooth_collector = BluetoothCollector()
        self._logs_collector = LogsCollector()
        self._system_info_collector = SystemInfoCollector()
        self._apt_collector = AptCollector()
        self._cpu_history = HistoryBuffer(maxlen=60)
        self._memory_history = HistoryBuffer(maxlen=60)
        self._load_history = HistoryBuffer(maxlen=60)

        # Store focused panel ID for restoration after expansion
        self._stored_focus_id: str | None = None

        # Store selection states per panel for persistence across expand/collapse
        self._selection_states: dict[str, SelectionState] = {}

        # Track previous focused panel to clear selections on change
        self._previous_focused_panel_id: str | None = None

        # Start refresh timers
        # Fast refresh (1s): System health (CPU, memory, load)
        self.set_interval(1.0, self._refresh_system_health)
        # Slow refresh (10s): Storage, battery, Bluetooth, logs, system info
        self.set_interval(10.0, self._refresh_slow_data)
        # Very slow refresh (60 min): Apt upgrade check
        self.set_interval(3600.0, self._refresh_apt_status)
        # Initial data refresh
        self.call_later(self._refresh_slow_data)
        self.call_later(self._refresh_apt_status)

    def _get_focused_panel(self) -> SelectableMixin | None:
        """Get the currently focused panel if it supports selection.

        Returns:
            The focused panel with SelectableMixin, or None.
        """
        focused = self.focused
        if focused and isinstance(focused, SelectableMixin):
            return focused
        return None

    def _get_panel_by_id(self, panel_id: str) -> SelectableMixin | None:
        """Get a panel by its ID.

        Args:
            panel_id: The panel's ID.

        Returns:
            The panel with SelectableMixin, or None.
        """
        try:
            panel = self.screen.query_one(f"#{panel_id}")
            if isinstance(panel, SelectableMixin):
                return panel
        except Exception:
            pass
        return None

    def _clear_panel_selections(self, panel_id: str) -> None:
        """Clear all selections in a panel.

        Args:
            panel_id: The panel's ID.
        """
        panel = self._get_panel_by_id(panel_id)
        if panel:
            panel.clear_selections()
        # Also clear stored state
        if panel_id in self._selection_states:
            del self._selection_states[panel_id]

    def _save_panel_selection_state(self, panel_id: str) -> None:
        """Save a panel's selection state.

        Args:
            panel_id: The panel's ID.
        """
        panel = self._get_panel_by_id(panel_id)
        if panel:
            self._selection_states[panel_id] = panel.get_selection_state()

    def _restore_panel_selection_state(self, panel_id: str) -> None:
        """Restore a panel's selection state.

        Args:
            panel_id: The panel's ID.
        """
        if panel_id in self._selection_states:
            panel = self._get_panel_by_id(panel_id)
            if panel:
                panel.set_selection_state(self._selection_states[panel_id])

    def _on_panel_focus_changed(self, new_panel_id: str | None) -> None:
        """Handle focus changing to a new panel.

        Clears selections in the previously focused panel.

        Args:
            new_panel_id: ID of newly focused panel, or None.
        """
        if self._previous_focused_panel_id and self._previous_focused_panel_id != new_panel_id:
            self._clear_panel_selections(self._previous_focused_panel_id)
        self._previous_focused_panel_id = new_panel_id

    def _refresh_system_health(self) -> None:
        """Refresh system health data at 1 Hz."""
        try:
            # Collect system health metrics
            metrics = self._system_health_collector.collect()
            if metrics:
                self._cpu_history.append(metrics.cpu_percent)
                self._memory_history.append(metrics.memory_percent)
                # Track 1-minute load average
                self._load_history.append(metrics.load_avg[0])

            # Update system health panel
            try:
                panel = self.screen.query_one("#system-health", SystemHealthPanel)
                panel.update(
                    metrics,
                    self._cpu_history.get_values(),
                    self._memory_history.get_values(),
                    self._load_history.get_values(),
                )
            except Exception:
                pass

        except Exception:
            pass

    def _refresh_slow_data(self) -> None:
        """Refresh slow-changing data every 10 seconds.

        Updates processes, devices (storage/battery/Bluetooth), logs, and system info.
        """
        try:
            # Collect storage metrics (for devices panel)
            disks = self._storage_collector.collect()

            # Collect and update processes panel
            try:
                processes = self._process_collector.collect(max_processes=50)
                panel = self.screen.query_one("#processes", ProcessesPanel)
                panel.update(processes)
            except Exception:
                pass

            # Collect battery and Bluetooth metrics
            battery = self._battery_collector.collect()
            bluetooth_devices = self._bluetooth_collector.collect()

            # Update devices panel (now includes storage)
            try:
                panel = self.screen.query_one("#devices", DevicesPanel)
                panel.update(battery, bluetooth_devices, disks)
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

    def _refresh_apt_status(self) -> None:
        """Refresh apt upgrade status every 60 minutes."""
        try:
            apt_status = self._apt_collector.collect()

            # Update info bar with apt status
            try:
                panel = self.screen.query_one("#info-bar", InfoBar)
                panel.update_apt(apt_status)
            except Exception:
                pass

        except Exception:
            pass

    def action_focus_next(self) -> None:
        """Move focus to next panel in cycle."""
        # Collapse expanded view first, then navigate
        if isinstance(self.screen, ExpandedPanelScreen):
            self._save_panel_selection_state(self.screen.panel_id)
            self.pop_screen()
            self.call_later(self._refresh_all)

        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#processes"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
        ]

        # Find current focused panel and move to next
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
            # Fallback: focus first panel
            panels[0].focus()

    def action_focus_previous(self) -> None:
        """Move focus to previous panel in cycle."""
        # Collapse expanded view first, then navigate
        if isinstance(self.screen, ExpandedPanelScreen):
            self._save_panel_selection_state(self.screen.panel_id)
            self.pop_screen()
            self.call_later(self._refresh_all)

        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.screen.query_one("#system-health"),
            self.screen.query_one("#processes"),
            self.screen.query_one("#devices"),
            self.screen.query_one("#logs"),
        ]

        # Find current focused panel and move to previous
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
            # Fallback: focus last panel
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

        # Get selected elements (sticky if any, otherwise cursor)
        sticky_ids = panel.get_sticky_ids()
        cursor_id = panel.get_cursor_id()

        if sticky_ids:
            element_ids = list(sticky_ids)
        elif cursor_id:
            element_ids = [cursor_id]
        else:
            self.push_screen(ErrorPopup("No Selection", "No element selected"))
            return

        # Build info items
        items = []
        for element_id in element_ids:
            data = panel.get_element_data(element_id)
            if data:
                # Format based on data type
                if hasattr(data, "details") and data.details:
                    items.append({"label": getattr(data, "label", element_id), "details": data.details})
                elif hasattr(data, "__dict__"):
                    items.append({"label": element_id, "details": data.__dict__})
                else:
                    items.append({"label": element_id, "details": str(data)})

        if items:
            # Determine title based on panel type
            focused = self.focused
            if hasattr(focused, "id"):
                title = f"Info: {focused.id.replace('-', ' ').title()}"
            else:
                title = "Info"
            self.push_screen(InfoPopup(title, items))

    def action_export_logs(self) -> None:
        """Export logs to ~/Downloads."""
        # Only works in logs panel
        focused = self.focused
        if not hasattr(focused, "id") or focused.id != "logs":
            return

        try:
            panel = self.screen.query_one("#logs", LogsPanel)
        except Exception:
            return

        # Get logs to export
        sticky_ids = panel.get_sticky_ids()
        if sticky_ids:
            # Export only sticky-selected logs
            logs_to_export = []
            for log_id in sticky_ids:
                log = panel.get_element_data(log_id)
                if log:
                    logs_to_export.append(log)
        else:
            # Export all logs
            logs_to_export = panel.get_all_logs()

        if not logs_to_export:
            self.push_screen(ErrorPopup("No Logs", "No logs to export"))
            return

        # Create Downloads folder if needed
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"logs_{timestamp}.txt"
        filepath = downloads_dir / filename

        # Write logs
        try:
            with open(filepath, "w") as f:
                for log in logs_to_export:
                    f.write(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} {log.message}\n")
            self.push_screen(ExportSuccessPopup(str(filepath), len(logs_to_export)))
        except Exception as e:
            self.push_screen(ErrorPopup("Export Failed", str(e)))

    def action_kill_process(self) -> None:
        """Kill selected process (with confirmation)."""
        # Only works in processes panel
        focused = self.focused
        if not hasattr(focused, "id") or focused.id != "processes":
            return

        try:
            panel = self.screen.query_one("#processes", ProcessesPanel)
        except Exception:
            return

        # Check for sticky selections (not allowed for kill)
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

        # Get cursor selection
        cursor_id = panel.get_cursor_id()
        if not cursor_id:
            self.push_screen(ErrorPopup("No Selection", "No process selected"))
            return

        process = panel.get_element_data(cursor_id)
        if not process:
            return

        # Check if it's a user process (not root/system)
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

        # Show confirmation popup
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
            # Already expanded, collapse back to main dashboard
            self.action_collapse()
        else:
            # Expand the currently focused panel
            if self.focused and hasattr(self.focused, "id"):
                panel_id = self.focused.id
                # Only expand if it's one of the main panels
                if panel_id in ["system-health", "processes", "devices", "logs"]:
                    self._stored_focus_id = panel_id
                    # Clear selections before expanding (reset on zoom)
                    self._clear_panel_selections(panel_id)
                    self.push_screen(ExpandedPanelScreen(panel_id))
                    # Trigger immediate refresh after screen transition
                    self.call_later(self._refresh_all)

    def action_collapse(self) -> None:
        """Return to main dashboard from expanded view."""
        if isinstance(self.screen, ExpandedPanelScreen):
            panel_id = self.screen.panel_id
            # Clear selections before collapsing (reset on zoom)
            self._clear_panel_selections(panel_id)
            self.pop_screen()
            # Restore focus after screen transition
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
