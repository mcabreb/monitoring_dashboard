"""System Health panel for CPU, memory, and load metrics."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Label, ProgressBar, Static

from monitor_dashboard.models.metrics import SystemMetrics
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes, format_percent
from monitor_dashboard.widgets.sparkline import Sparkline


class SystemHealthPanel(BasePanel):
    """Panel displaying system health metrics."""

    BORDER_TITLE = "● System Health"

    def __init__(self, **kwargs) -> None:
        """Initialize system health panel."""
        super().__init__(**kwargs)
        self._cpu_label: Label | None = None
        self._cpu_bar: ProgressBar | None = None
        self._cpu_sparkline: Sparkline | None = None
        self._memory_label: Label | None = None
        self._memory_bar: ProgressBar | None = None
        self._memory_details: Label | None = None
        self._memory_sparkline: Sparkline | None = None
        self._load_label: Label | None = None

    def compose(self) -> ComposeResult:
        """Compose the System Health panel content."""
        with Vertical():
            self._cpu_label = Label("CPU: N/A", id="cpu-label")
            yield self._cpu_label
            self._cpu_bar = ProgressBar(total=100, show_eta=False, id="cpu-bar")
            yield self._cpu_bar
            self._cpu_sparkline = Sparkline(id="cpu-sparkline")
            yield self._cpu_sparkline
            yield Label("")  # Spacer
            self._memory_label = Label("Memory: N/A", id="memory-label")
            yield self._memory_label
            self._memory_bar = ProgressBar(total=100, show_eta=False, id="memory-bar")
            yield self._memory_bar
            self._memory_details = Label("", id="memory-details")
            yield self._memory_details
            self._memory_sparkline = Sparkline(id="memory-sparkline")
            yield self._memory_sparkline
            yield Label("")  # Spacer
            self._load_label = Label("Load: N/A", id="load-label")
            yield self._load_label

    def update(
        self,
        metrics: SystemMetrics | None,
        cpu_history: list[float] | None = None,
        memory_history: list[float] | None = None,
    ) -> None:
        """Update panel with new metrics.

        Args:
            metrics: Current system metrics, or None if unavailable.
            cpu_history: List of CPU percentage values for sparkline.
        """
        if metrics is None:
            self._show_unavailable()
            return

        # Update CPU display
        if self._cpu_label:
            self._cpu_label.update(f"CPU: {format_percent(metrics.cpu_percent)}")
        if self._cpu_bar:
            self._cpu_bar.update(progress=metrics.cpu_percent)

        # Update CPU sparkline
        if self._cpu_sparkline and cpu_history:
            self._cpu_sparkline.update_values(cpu_history)

        # Update memory display
        if self._memory_label:
            self._memory_label.update(f"Memory: {format_percent(metrics.memory_percent)}")
        if self._memory_bar:
            self._memory_bar.update(progress=metrics.memory_percent)
        if self._memory_details:
            used = format_bytes(metrics.memory_used)
            total = format_bytes(metrics.memory_total)
            self._memory_details.update(f"{used} / {total}")

        # Update memory sparkline
        if self._memory_sparkline and memory_history:
            self._memory_sparkline.update_values(memory_history)

        # Update load average
        if self._load_label:
            load_1, load_5, load_15 = metrics.load_avg
            self._load_label.update(f"Load: {load_1:.1f} (1m)  {load_5:.1f} (5m)  {load_15:.1f} (15m)")

    def _show_unavailable(self) -> None:
        """Show N/A for all metrics when data is unavailable."""
        if self._cpu_label:
            self._cpu_label.update("CPU: N/A")
        if self._cpu_bar:
            self._cpu_bar.update(progress=0)
        if self._memory_label:
            self._memory_label.update("Memory: N/A")
        if self._memory_bar:
            self._memory_bar.update(progress=0)
        if self._memory_details:
            self._memory_details.update("")
        if self._load_label:
            self._load_label.update("Load: N/A")
