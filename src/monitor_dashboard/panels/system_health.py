"""System Health panel for CPU, memory, and load metrics."""

from dataclasses import dataclass
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Static

from monitor_dashboard.models.metrics import SystemMetrics
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.selectable import SelectableMixin
from monitor_dashboard.utils.formatting import format_bytes, format_percent


# Unicode block characters for graph (8 levels from empty to full)
GRAPH_BLOCKS = " ▁▂▃▄▅▆▇█"

# Selection colors for Rich markup
CURSOR_BG = "on cyan"
STICKY_BG = "on dark_cyan"


@dataclass
class MetricItem:
    """Data for a selectable metric item."""

    id: str
    label: str
    value: str
    color: str
    details: dict[str, Any] | None = None


class HistoryGraph(Static):
    """Widget displaying metric history as a line graph with threshold colors."""

    # Graph dimensions
    GRAPH_HEIGHT = 3  # Number of rows
    GRAPH_WIDTH = 30  # Number of columns (data points)

    # Threshold types
    THRESHOLD_CPU = "cpu"  # green <20%, yellow 20-50%, red >=50%
    THRESHOLD_MEM = "mem"  # green <=50%, yellow 50-80%, red >80%
    THRESHOLD_LOAD = "load"  # green <70%, yellow 70-100%, red >100% (of cores)

    def __init__(self, threshold_type: str = THRESHOLD_CPU, num_cores: int = 1, **kwargs) -> None:
        """Initialize history graph widget.

        Args:
            threshold_type: Type of threshold coloring ("cpu", "mem", or "load").
            num_cores: Number of CPU cores (used for load threshold calculations).
        """
        super().__init__(**kwargs)
        self._history: list[float] = []
        self._threshold_type = threshold_type
        self._num_cores = num_cores
        self._graph_width = self.GRAPH_WIDTH

    def update_history(self, history: list[float], num_cores: int | None = None) -> None:
        """Update the graph with new history data.

        Args:
            history: List of percentage values (0-100), or load values for load graph.
            num_cores: Number of CPU cores (updates internal value if provided).
        """
        self._history = history
        if num_cores is not None:
            self._num_cores = num_cores
        self._render_graph()

    def set_width(self, width: int) -> None:
        """Change the graph width (number of data columns) and update CSS."""
        self._graph_width = width
        self.styles.width = width
        self._render_graph()

    def _get_color_for_value(self, value: float) -> str:
        """Get threshold color for a value.

        Args:
            value: Percentage value (0-100), or load value for load graph.

        Returns:
            Color name for Rich markup.
        """
        if self._threshold_type == self.THRESHOLD_MEM:
            # Memory: green <=50%, yellow 50-80%, red >80%
            if value > 80:
                return "red"
            elif value > 50:
                return "yellow"
            else:
                return "green"
        elif self._threshold_type == self.THRESHOLD_LOAD:
            # Load: based on ratio to cores
            # green <70% of cores, yellow 70-100%, red >100%
            load_ratio = value / self._num_cores if self._num_cores > 0 else 0
            if load_ratio > 1.0:
                return "red"
            elif load_ratio >= 0.7:
                return "yellow"
            else:
                return "green"
        else:
            # CPU: green <20%, yellow 20-50%, red >=50%
            if value >= 50:
                return "red"
            elif value >= 20:
                return "yellow"
            else:
                return "green"

    def _render_graph(self) -> None:
        """Render the history graph with threshold-based colors."""
        # Take the last graph_width values for display
        data = self._history[-self._graph_width :] if self._history else []

        # For load graphs, scale is 0 to 2*num_cores (200% of capacity)
        # For CPU/memory, scale is 0 to 100
        if self._threshold_type == self.THRESHOLD_LOAD:
            max_value = 2.0 * self._num_cores  # Show up to 200% of cores
        else:
            max_value = 100.0

        # Build graph from top to bottom
        lines = []
        for row in range(self.GRAPH_HEIGHT):
            # Calculate the value range this row represents
            row_from_bottom = self.GRAPH_HEIGHT - 1 - row
            row_min = (row_from_bottom / self.GRAPH_HEIGHT) * max_value
            row_max = ((row_from_bottom + 1) / self.GRAPH_HEIGHT) * max_value

            line_parts = []
            # Data grows left to right: empty space on the RIGHT if not enough data
            for i in range(self._graph_width):
                if i < len(data):
                    value = data[i]
                    color = self._get_color_for_value(value)
                    if value >= row_max:
                        # Full block - value is above this row's range
                        char = GRAPH_BLOCKS[8]
                    elif value <= row_min:
                        # Empty - value is below this row's range
                        char = " "
                    else:
                        # Partial block - value is within this row's range
                        fraction = (value - row_min) / (row_max - row_min)
                        block_idx = int(fraction * 8)
                        block_idx = min(block_idx, 8)
                        char = GRAPH_BLOCKS[block_idx]
                    # Each character gets its own color based on the data value
                    line_parts.append(f"[{color} on #d0d0d0]{char}[/]")
                else:
                    # No data yet for this column - empty with grey background
                    line_parts.append("[on #d0d0d0] [/]")

            lines.append("".join(line_parts))

        self.update("\n".join(lines))


class SystemHealthPanel(BasePanel, SelectableMixin):
    """Panel displaying system health metrics as text."""

    BORDER_TITLE = "● System Health"

    def __init__(self, **kwargs) -> None:
        """Initialize system health panel."""
        super().__init__(**kwargs)
        self.init_selection()
        self._container: VerticalScroll | None = None
        self._cpu_stats: Vertical | None = None
        self._cpu_graph: HistoryGraph | None = None
        self._mem_stats: Vertical | None = None
        self._mem_graph: HistoryGraph | None = None
        self._load_stats: Vertical | None = None
        self._load_graph: HistoryGraph | None = None
        self._load_spacer: Label | None = None
        self._load_row: Horizontal | None = None
        # Store metrics for selection data access
        self._metrics: SystemMetrics | None = None
        self._metric_items: list[MetricItem] = []
        self._cpu_history: list[float] = []
        self._memory_history: list[float] = []
        self._load_history: list[float] = []
        self._compact: bool = False

    def compose(self) -> ComposeResult:
        """Compose the System Health panel content."""
        self._container = VerticalScroll()
        with self._container:
            # CPU section: stats on left, graph on right
            with Horizontal(classes="stats-row"):
                self._cpu_stats = Vertical(classes="stats-col")
                yield self._cpu_stats
                self._cpu_graph = HistoryGraph(
                    threshold_type=HistoryGraph.THRESHOLD_CPU, classes="graph"
                )
                yield self._cpu_graph

            # Spacer between graphs
            yield Label("")

            # Memory section: stats on left, graph on right
            with Horizontal(classes="stats-row"):
                self._mem_stats = Vertical(classes="stats-col")
                yield self._mem_stats
                self._mem_graph = HistoryGraph(
                    threshold_type=HistoryGraph.THRESHOLD_MEM, classes="graph"
                )
                yield self._mem_graph

            # Spacer before load
            self._load_spacer = Label("")
            yield self._load_spacer

            # Load section: stats on left, graph on right
            self._load_row = Horizontal(classes="stats-row")
            with self._load_row:
                self._load_stats = Vertical(classes="stats-col")
                yield self._load_stats
                self._load_graph = HistoryGraph(
                    threshold_type=HistoryGraph.THRESHOLD_LOAD, classes="graph"
                )
                yield self._load_graph

        yield self._container

    def set_compact(self, enabled: bool) -> None:
        """Toggle compact mode — hides per-core CPU rows and load section."""
        self._compact = enabled
        if self._load_spacer:
            self._load_spacer.display = not enabled
        if self._load_row:
            self._load_row.display = not enabled
        # Resize graphs to half width in compact mode
        graph_width = HistoryGraph.GRAPH_WIDTH // 2 if enabled else HistoryGraph.GRAPH_WIDTH
        if self._cpu_graph:
            self._cpu_graph.set_width(graph_width)
        if self._mem_graph:
            self._mem_graph.set_width(graph_width)
        # Rebuild metric items and re-render
        self._build_metric_items()
        self._display()

    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs."""
        return [item.id for item in self._metric_items]

    def get_element_data(self, element_id: str) -> MetricItem | None:
        """Get metric item data for an element ID."""
        for item in self._metric_items:
            if item.id == element_id:
                return item
        return None

    def refresh_selection_display(self) -> None:
        """Re-render with selection styling."""
        self._display()

    def update(
        self,
        metrics: SystemMetrics | None,
        cpu_history: list[float] | None = None,
        memory_history: list[float] | None = None,
        load_history: list[float] | None = None,
    ) -> None:
        """Update panel with new metrics.

        Args:
            metrics: Current system metrics, or None if unavailable.
            cpu_history: List of historical CPU percentages for graph.
            memory_history: List of historical memory percentages for graph.
            load_history: List of historical load averages (1m) for graph.
        """
        self._metrics = metrics
        if cpu_history:
            self._cpu_history = cpu_history
        if memory_history:
            self._memory_history = memory_history
        if load_history:
            self._load_history = load_history

        self._build_metric_items()
        self._display()

    def _build_metric_items(self) -> None:
        """Build list of selectable metric items from current metrics."""
        self._metric_items = []
        if not self._metrics:
            return

        metrics = self._metrics

        # CPU overall
        cpu_color = self._get_percent_color(metrics.cpu_percent)
        self._metric_items.append(MetricItem(
            id="cpu",
            label="CPU",
            value=format_percent(metrics.cpu_percent),
            color=cpu_color,
            details={"type": "cpu", "percent": metrics.cpu_percent},
        ))

        # CPU per core (skip in compact mode)
        if not self._compact:
            for i, core_pct in enumerate(metrics.cpu_per_core):
                color = self._get_percent_color(core_pct)
                self._metric_items.append(MetricItem(
                    id=f"core-{i}",
                    label=f"#{i}",
                    value=format_percent(core_pct),
                    color=color,
                    details={"type": "core", "core_num": i, "percent": core_pct},
                ))

        # Memory
        mem_color = self._get_memory_color(metrics.memory_percent)
        used = format_bytes(metrics.memory_used)
        total = format_bytes(metrics.memory_total)
        self._metric_items.append(MetricItem(
            id="memory",
            label="Memory",
            value=f"{format_percent(metrics.memory_percent)} ({used} / {total})",
            color=mem_color,
            details={
                "type": "memory",
                "percent": metrics.memory_percent,
                "used": metrics.memory_used,
                "total": metrics.memory_total,
            },
        ))

        # Load (skip in compact mode)
        if not self._compact:
            num_cores = len(metrics.cpu_per_core)
            load_1, load_5, load_15 = metrics.load_avg
            load_color = self._get_load_color(load_1, num_cores)
            self._metric_items.append(MetricItem(
                id="load",
                label="Load",
                value=f"{load_1:.2f} (1m)  {load_5:.2f} (5m)  {load_15:.2f} (15m)",
                color=load_color,
                details={
                    "type": "load",
                    "load_1m": load_1,
                    "load_5m": load_5,
                    "load_15m": load_15,
                    "num_cores": num_cores,
                },
            ))

        # Prune sticky selections for items that no longer exist
        self.prune_invalid_sticky()

    def _get_selection_markup(self, element_id: str) -> tuple[str, str]:
        """Get Rich markup prefix/suffix for selection state.

        Args:
            element_id: Element to check.

        Returns:
            Tuple of (prefix, suffix) for Rich markup.
        """
        if self.is_cursor(element_id):
            return f"[black {CURSOR_BG}]", "[/]"
        elif self.is_sticky(element_id):
            return f"[white {STICKY_BG}]", "[/]"
        return "", ""

    def _display(self) -> None:
        """Render the panel with current data and selection styling."""
        if not self._cpu_stats or not self._mem_stats or not self._load_stats:
            return

        # Clear all containers
        self._cpu_stats.remove_children()
        self._mem_stats.remove_children()
        self._load_stats.remove_children()

        if not self._metrics:
            self._cpu_stats.mount(Label("System metrics unavailable"))
            return

        metrics = self._metrics

        # Track cursor widget for scrolling
        cursor_widget = None

        # CPU section - overall
        cpu_item = self.get_element_data("cpu")
        if cpu_item:
            prefix, suffix = self._get_selection_markup("cpu")
            text = f"{prefix}CPU:{suffix} [{cpu_item.color}]{cpu_item.value}[/{cpu_item.color}]"
            label = Label(text)
            if self.is_cursor("cpu"):
                cursor_widget = label
            self._cpu_stats.mount(label)

        # CPU per core - display in rows of 4 (skip in compact mode)
        if not self._compact:
            cores = metrics.cpu_per_core
            cores_per_row = 4
            for i in range(0, len(cores), cores_per_row):
                row_cores = cores[i : i + cores_per_row]
                core_strs = []
                row_has_cursor = False
                for j, c in enumerate(row_cores):
                    core_idx = i + j
                    core_id = f"core-{core_idx}"
                    core_item = self.get_element_data(core_id)
                    if core_item:
                        prefix, suffix = self._get_selection_markup(core_id)
                        color = core_item.color
                        # Selection only on the identifier part, not the percentage
                        core_strs.append(f"{prefix}#{core_idx}:{suffix} [{color}]{format_percent(c)}[/{color}]")
                        if self.is_cursor(core_id):
                            row_has_cursor = True
                label = Label("  " + "  ".join(core_strs))
                if row_has_cursor:
                    cursor_widget = label
                self._cpu_stats.mount(label)

        # Memory section
        mem_item = self.get_element_data("memory")
        if mem_item:
            prefix, suffix = self._get_selection_markup("memory")
            text = f"{prefix}Memory:{suffix} [{mem_item.color}]{mem_item.value}[/{mem_item.color}]"
            label = Label(text)
            if self.is_cursor("memory"):
                cursor_widget = label
            self._mem_stats.mount(label)

        # Load section (skip in compact mode)
        if not self._compact:
            load_item = self.get_element_data("load")
            if load_item:
                # Color each load value individually
                num_cores = len(metrics.cpu_per_core)
                load_1, load_5, load_15 = metrics.load_avg
                load_1_color = self._get_load_color(load_1, num_cores)
                load_5_color = self._get_load_color(load_5, num_cores)
                load_15_color = self._get_load_color(load_15, num_cores)
                prefix, suffix = self._get_selection_markup("load")
                load_text = (
                    f"{prefix}Load:{suffix} [{load_1_color}]{load_1:.2f}[/{load_1_color}] (1m)  "
                    f"[{load_5_color}]{load_5:.2f}[/{load_5_color}] (5m)  "
                    f"[{load_15_color}]{load_15:.2f}[/{load_15_color}] (15m)"
                )
                label = Label(load_text)
                if self.is_cursor("load"):
                    cursor_widget = label
                self._load_stats.mount(label)

        # Update graphs
        if self._cpu_graph and self._cpu_history:
            self._cpu_graph.update_history(self._cpu_history)
        if self._mem_graph and self._memory_history:
            self._mem_graph.update_history(self._memory_history)
        if not self._compact and self._load_graph and self._load_history:
            num_cores = len(metrics.cpu_per_core)
            self._load_graph.update_history(self._load_history, num_cores=num_cores)

        # Scroll to keep cursor visible (use default args to capture current values)
        if cursor_widget is not None and self._container is not None:
            container = self._container
            container.call_later(lambda w=cursor_widget, c=container: c.scroll_to_widget(w, animate=False))

    def _get_percent_color(self, percent: float) -> str:
        """Get color name for CPU percentage value."""
        if percent >= 50:
            return "red"
        elif percent >= 20:
            return "yellow"
        else:
            return "green"

    def _get_memory_color(self, percent: float) -> str:
        """Get color name for memory percentage value."""
        if percent > 80:
            return "red"
        elif percent > 50:
            return "yellow"
        else:
            return "green"

    def _get_load_color(self, load: float, num_cores: int) -> str:
        """Get color name for load average value."""
        load_ratio = load / num_cores if num_cores > 0 else 0
        if load_ratio > 1.0:
            return "red"
        elif load_ratio >= 0.7:
            return "yellow"
        else:
            return "green"
