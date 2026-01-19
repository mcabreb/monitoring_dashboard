"""System Health panel for CPU, memory, and load metrics."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label

from monitor_dashboard.models.metrics import SystemMetrics
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes, format_percent


class SystemHealthPanel(BasePanel):
    """Panel displaying system health metrics as text."""

    BORDER_TITLE = "● System Health"

    def __init__(self, **kwargs) -> None:
        """Initialize system health panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None

    def compose(self) -> ComposeResult:
        """Compose the System Health panel content."""
        self._container = VerticalScroll()
        yield self._container

    def update(
        self,
        metrics: SystemMetrics | None,
        cpu_history: list[float] | None = None,
        memory_history: list[float] | None = None,
    ) -> None:
        """Update panel with new metrics.

        Args:
            metrics: Current system metrics, or None if unavailable.
            cpu_history: Unused, kept for API compatibility.
            memory_history: Unused, kept for API compatibility.
        """
        if not self._container:
            return

        self._container.remove_children()

        if metrics is None:
            self._container.mount(Label("System metrics unavailable"))
            return

        # CPU overall - white label, colored value
        cpu_color = self._get_percent_color(metrics.cpu_percent)
        cpu_value = f"[{cpu_color}]{format_percent(metrics.cpu_percent)}[/{cpu_color}]"
        self._container.mount(Label(f"CPU: {cpu_value}"))

        # CPU per core - display in rows of 4
        cores = metrics.cpu_per_core
        cores_per_row = 4
        for i in range(0, len(cores), cores_per_row):
            row_cores = cores[i : i + cores_per_row]
            core_strs = []
            for j, c in enumerate(row_cores):
                color = self._get_percent_color(c)
                core_strs.append(f"#{i + j}: [{color}]{format_percent(c)}[/{color}]")
            self._container.mount(Label("  " + "  ".join(core_strs)))

        # Blank line
        self._container.mount(Label(""))

        # Memory - white label, colored value
        used = format_bytes(metrics.memory_used)
        total = format_bytes(metrics.memory_total)
        mem_color = self._get_percent_color(metrics.memory_percent)
        mem_value = f"[{mem_color}]{format_percent(metrics.memory_percent)}[/{mem_color}]"
        self._container.mount(Label(f"Memory: {mem_value} ({used} / {total})"))

        # Blank line
        self._container.mount(Label(""))

        # Load average - white label, colored value
        num_cores = len(cores)
        load_1, load_5, load_15 = metrics.load_avg
        load_color = self._get_load_color(load_1, num_cores)
        load_value = f"[{load_color}]{load_1:.2f}[/{load_color}] (1m)  {load_5:.2f} (5m)  {load_15:.2f} (15m)"
        self._container.mount(Label(f"Load: {load_value}"))

    def _get_percent_color(self, percent: float) -> str:
        """Get color name for percentage value.

        Args:
            percent: Percentage value (0-100).

        Returns:
            Color name for Rich markup.
        """
        if percent >= 50:
            return "red"
        elif percent >= 20:
            return "yellow"
        else:
            return "green"

    def _get_load_color(self, load: float, num_cores: int) -> str:
        """Get color name for load average value.

        Args:
            load: Load average value.
            num_cores: Number of CPU cores.

        Returns:
            Color name for Rich markup.

        Thresholds:
            - Green: load < 70% of cores
            - Yellow: load 70-100% of cores
            - Red: load > 100% of cores
        """
        load_ratio = load / num_cores if num_cores > 0 else 0
        if load_ratio > 1.0:
            return "red"
        elif load_ratio >= 0.7:
            return "yellow"
        else:
            return "green"
