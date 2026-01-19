"""System Health panel for CPU, memory, and load metrics."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Label, Static

from monitor_dashboard.models.metrics import SystemMetrics
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.utils.formatting import format_bytes, format_percent


# Unicode block characters for graph (8 levels from empty to full)
GRAPH_BLOCKS = " ▁▂▃▄▅▆▇█"


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
        # Take the last GRAPH_WIDTH values for display
        data = self._history[-self.GRAPH_WIDTH :] if self._history else []

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
            for i in range(self.GRAPH_WIDTH):
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
                    line_parts.append(f"[{color} on white]{char}[/]")
                else:
                    # No data yet for this column - empty with grey background
                    line_parts.append("[on white] [/]")

            lines.append("".join(line_parts))

        self.update("\n".join(lines))


class SystemHealthPanel(BasePanel):
    """Panel displaying system health metrics as text."""

    BORDER_TITLE = "● System Health"

    def __init__(self, **kwargs) -> None:
        """Initialize system health panel."""
        super().__init__(**kwargs)
        self._container: VerticalScroll | None = None
        self._cpu_stats: Vertical | None = None
        self._cpu_graph: HistoryGraph | None = None
        self._mem_stats: Vertical | None = None
        self._mem_graph: HistoryGraph | None = None
        self._load_stats: Vertical | None = None
        self._load_graph: HistoryGraph | None = None

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
            yield Label("")

            # Load section: stats on left, graph on right
            with Horizontal(classes="stats-row"):
                self._load_stats = Vertical(classes="stats-col")
                yield self._load_stats
                self._load_graph = HistoryGraph(
                    threshold_type=HistoryGraph.THRESHOLD_LOAD, classes="graph"
                )
                yield self._load_graph

        yield self._container

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
        if not self._cpu_stats or not self._mem_stats or not self._load_stats:
            return

        # Clear all containers
        self._cpu_stats.remove_children()
        self._mem_stats.remove_children()
        self._load_stats.remove_children()

        if metrics is None:
            self._cpu_stats.mount(Label("System metrics unavailable"))
            return

        # CPU section
        cpu_color = self._get_percent_color(metrics.cpu_percent)
        cpu_value = f"[{cpu_color}]{format_percent(metrics.cpu_percent)}[/{cpu_color}]"
        self._cpu_stats.mount(Label(f"CPU: {cpu_value}"))

        # CPU per core - display in rows of 4
        cores = metrics.cpu_per_core
        cores_per_row = 4
        for i in range(0, len(cores), cores_per_row):
            row_cores = cores[i : i + cores_per_row]
            core_strs = []
            for j, c in enumerate(row_cores):
                color = self._get_percent_color(c)
                core_strs.append(f"#{i + j}: [{color}]{format_percent(c)}[/{color}]")
            self._cpu_stats.mount(Label("  " + "  ".join(core_strs)))

        # Memory section
        used = format_bytes(metrics.memory_used)
        total = format_bytes(metrics.memory_total)
        mem_color = self._get_memory_color(metrics.memory_percent)
        mem_value = f"[{mem_color}]{format_percent(metrics.memory_percent)}[/{mem_color}]"
        self._mem_stats.mount(Label(f"Memory: {mem_value} ({used} / {total})"))

        # Load section - color all three values
        num_cores = len(cores)
        load_1, load_5, load_15 = metrics.load_avg
        load_1_color = self._get_load_color(load_1, num_cores)
        load_5_color = self._get_load_color(load_5, num_cores)
        load_15_color = self._get_load_color(load_15, num_cores)
        load_value = (
            f"[{load_1_color}]{load_1:.2f}[/{load_1_color}] (1m)  "
            f"[{load_5_color}]{load_5:.2f}[/{load_5_color}] (5m)  "
            f"[{load_15_color}]{load_15:.2f}[/{load_15_color}] (15m)"
        )
        self._load_stats.mount(Label(f"Load: {load_value}"))

        # Update graphs
        if self._cpu_graph and cpu_history:
            self._cpu_graph.update_history(cpu_history)
        if self._mem_graph and memory_history:
            self._mem_graph.update_history(memory_history)
        if self._load_graph and load_history:
            self._load_graph.update_history(load_history, num_cores=num_cores)

    def _get_percent_color(self, percent: float) -> str:
        """Get color name for CPU percentage value.

        Args:
            percent: Percentage value (0-100).

        Returns:
            Color name for Rich markup.

        Thresholds:
            - Green: < 20%
            - Yellow: 20-50%
            - Red: >= 50%
        """
        if percent >= 50:
            return "red"
        elif percent >= 20:
            return "yellow"
        else:
            return "green"

    def _get_memory_color(self, percent: float) -> str:
        """Get color name for memory percentage value.

        Args:
            percent: Percentage value (0-100).

        Returns:
            Color name for Rich markup.

        Thresholds:
            - Green: <= 50%
            - Yellow: 50-80%
            - Red: > 80%
        """
        if percent > 80:
            return "red"
        elif percent > 50:
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
