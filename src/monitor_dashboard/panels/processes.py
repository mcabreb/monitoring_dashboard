"""Processes panel for displaying active system processes."""

from enum import Enum

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.process import ProcessInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.selectable import SelectableMixin


class SortColumn(Enum):
    """Available sort columns for processes."""

    CPU = "cpu"
    MEM = "mem"
    PID = "pid"
    USER = "user"
    TIME = "time"
    COMMAND = "command"


# Column display order for cycling
SORT_COLUMNS = [
    SortColumn.CPU,
    SortColumn.MEM,
    SortColumn.TIME,
    SortColumn.COMMAND,
    SortColumn.PID,
    SortColumn.USER,
]


class ProcessesPanel(BasePanel, SelectableMixin):
    """Panel displaying active processes."""

    BORDER_TITLE = "● Processes"

    def __init__(self, **kwargs) -> None:
        """Initialize processes panel."""
        super().__init__(**kwargs)
        self.init_selection()
        self._container: VerticalScroll | None = None
        self._sort_column: SortColumn = SortColumn.CPU
        self._processes: list[ProcessInfo] | None = None
        self._sorted_processes: list[ProcessInfo] = []

    def compose(self) -> ComposeResult:
        """Compose the Processes panel content."""
        self._container = VerticalScroll()
        yield self._container

    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs (PIDs as strings)."""
        return [str(proc.pid) for proc in self._sorted_processes]

    def get_element_data(self, element_id: str) -> ProcessInfo | None:
        """Get process info for a PID."""
        try:
            pid = int(element_id)
            for proc in self._sorted_processes:
                if proc.pid == pid:
                    return proc
        except ValueError:
            pass
        return None

    def refresh_selection_display(self) -> None:
        """Re-render with selection styling."""
        self._display()

    def update(self, processes: list[ProcessInfo] | None) -> None:
        """Update panel with process information.

        Args:
            processes: List of process info objects, or None if unavailable.
        """
        # Store the cursor's current PID before updating
        cursor_pid = self.get_cursor_id()

        # Store processes for re-sorting
        self._processes = processes
        self._sorted_processes = self._sort_processes(processes or [])

        # Prune sticky selections for processes that no longer exist
        self.prune_invalid_sticky()

        # Restore cursor to same PID (if it still exists)
        if cursor_pid:
            self.adjust_cursor_for_id(cursor_pid)

        self._display()

    def _sort_processes(self, processes: list[ProcessInfo]) -> list[ProcessInfo]:
        """Sort processes by current sort column.

        Args:
            processes: List of processes to sort.

        Returns:
            Sorted list of processes.
        """
        if self._sort_column == SortColumn.CPU:
            return sorted(processes, key=lambda p: p.cpu_percent, reverse=True)
        elif self._sort_column == SortColumn.MEM:
            return sorted(processes, key=lambda p: p.memory_percent, reverse=True)
        elif self._sort_column == SortColumn.PID:
            return sorted(processes, key=lambda p: p.pid)
        elif self._sort_column == SortColumn.USER:
            return sorted(processes, key=lambda p: p.user.lower())
        elif self._sort_column == SortColumn.TIME:
            return sorted(processes, key=lambda p: p.time, reverse=True)
        elif self._sort_column == SortColumn.COMMAND:
            return sorted(processes, key=lambda p: p.command.lower())
        return processes

    def _get_header(self) -> str:
        """Get header row with sort indicator.

        Returns:
            Formatted header string with sort indicator on active column.
        """
        # Column headers with sort indicator
        pid = "PID▼" if self._sort_column == SortColumn.PID else "PID"
        user = "USER▼" if self._sort_column == SortColumn.USER else "USER"
        cpu = "CPU▼" if self._sort_column == SortColumn.CPU else "CPU"
        mem = "MEM▼" if self._sort_column == SortColumn.MEM else "MEM"
        time = "TIME▼" if self._sort_column == SortColumn.TIME else "TIME"
        cmd = "COMMAND▼" if self._sort_column == SortColumn.COMMAND else "COMMAND"

        return f"{pid:>7} {user:<10} {cpu:>5} {mem:>5} {time:>10} {cmd}"

    def _display(self) -> None:
        """Render the process list with current sort order."""
        if not self._container:
            return

        # Clear existing content
        self._container.remove_children()

        if not self._sorted_processes:
            self._container.mount(Label("No processes found"))
            return

        # Header row with sort indicator
        header_label = Label(self._get_header())
        header_label.add_class("process-header")
        self._container.mount(header_label)

        # Process rows
        for proc in self._sorted_processes:
            element_id = str(proc.pid)

            # Format each field - no truncation, let view handle clipping
            pid_str = f"{proc.pid:>7}"
            user_str = f"{proc.user[:10]:<10}"
            cpu_str = f"{proc.cpu_percent:>5.1f}"
            mem_str = f"{proc.memory_percent:>5.1f}"
            time_str = f"{proc.time:>10}"

            line = f"{pid_str} {user_str} {cpu_str} {mem_str} {time_str} {proc.command}"
            label = Label(line)

            # Apply selection styling first (takes precedence)
            selection_class = self.get_selection_class(element_id)
            if selection_class:
                label.add_class(selection_class)
            else:
                # Color code high CPU/memory usage only if not selected
                if proc.cpu_percent >= 50 or proc.memory_percent >= 50:
                    label.add_class("process-high")
                elif proc.cpu_percent >= 20 or proc.memory_percent >= 20:
                    label.add_class("process-medium")

            self._container.mount(label)

    def cycle_sort(self) -> None:
        """Cycle to the next sort column and re-render."""
        # Store cursor's current PID before re-sorting
        cursor_pid = self.get_cursor_id()

        current_idx = SORT_COLUMNS.index(self._sort_column)
        next_idx = (current_idx + 1) % len(SORT_COLUMNS)
        self._sort_column = SORT_COLUMNS[next_idx]

        # Re-sort the processes
        if self._processes:
            self._sorted_processes = self._sort_processes(self._processes)

        # Restore cursor to same PID after sorting
        if cursor_pid:
            self.adjust_cursor_for_id(cursor_pid)

        self._display()
