"""Processes panel for displaying active system processes."""

from enum import Enum

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.process import ProcessInfo
from monitor_dashboard.panels.base import BasePanel


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


class ProcessesPanel(BasePanel):
    """Panel displaying active processes."""

    BORDER_TITLE = "● Processes"

    def __init__(self, **kwargs) -> None:
        """Initialize processes panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None
        self._sort_column: SortColumn = SortColumn.CPU
        self._processes: list[ProcessInfo] | None = None

    def compose(self) -> ComposeResult:
        """Compose the Processes panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(self, processes: list[ProcessInfo] | None) -> None:
        """Update panel with process information.

        Args:
            processes: List of process info objects, or None if unavailable.
        """
        # Store processes for re-sorting
        self._processes = processes
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

        if not self._processes:
            self._container.mount(Label("No processes found"))
            return

        # Sort processes
        sorted_processes = self._sort_processes(self._processes)

        # Header row with sort indicator
        header_label = Label(self._get_header())
        header_label.add_class("process-header")
        self._container.mount(header_label)

        # Process rows
        for proc in sorted_processes:
            # Format each field
            pid_str = f"{proc.pid:>7}"
            user_str = f"{proc.user[:10]:<10}"
            cpu_str = f"{proc.cpu_percent:>5.1f}"
            mem_str = f"{proc.memory_percent:>5.1f}"
            time_str = f"{proc.time:>10}"
            cmd_str = proc.command[:30]  # Truncate command for display

            line = f"{pid_str} {user_str} {cpu_str} {mem_str} {time_str} {cmd_str}"
            label = Label(line)

            # Color code high CPU/memory usage
            if proc.cpu_percent >= 50 or proc.memory_percent >= 50:
                label.add_class("process-high")
            elif proc.cpu_percent >= 20 or proc.memory_percent >= 20:
                label.add_class("process-medium")

            self._container.mount(label)

    def cycle_sort(self) -> None:
        """Cycle to the next sort column and re-render."""
        current_idx = SORT_COLUMNS.index(self._sort_column)
        next_idx = (current_idx + 1) % len(SORT_COLUMNS)
        self._sort_column = SORT_COLUMNS[next_idx]
        self._display()
