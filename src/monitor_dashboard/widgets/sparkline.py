"""Sparkline widget for rendering time-series data as a simple text chart."""

from textual.widgets import Static


class Sparkline(Static):
    """A simple text-based sparkline chart using Unicode block characters.

    Renders a list of numeric values (0-100) as a sparkline chart using
    Unicode block elements ▁▂▃▄▅▆▇█.

    Attributes:
        SPARK_CHARS: Unicode characters for rendering (8 levels).
    """

    SPARK_CHARS = "▁▂▃▄▅▆▇█"

    def __init__(self, values: list[float] | None = None, **kwargs) -> None:
        """Initialize sparkline widget.

        Args:
            values: List of values between 0-100. Defaults to empty list.
            **kwargs: Additional arguments passed to Static.__init__.
        """
        super().__init__("", **kwargs)
        self._values: list[float] = values or []
        self._update_display()

    def update_values(self, values: list[float]) -> None:
        """Update the sparkline with new values.

        Args:
            values: List of values between 0-100.
        """
        self._values = values
        self._update_display()

    def _update_display(self) -> None:
        """Render the sparkline as text."""
        if not self._values:
            self.update("")
            return

        # Map values (0-100) to character index (0-7)
        chars = []
        for value in self._values:
            # Clamp value to 0-100 range
            clamped = max(0.0, min(100.0, value))
            # Map to index 0-7
            index = int(clamped / 100.0 * 7)
            chars.append(self.SPARK_CHARS[index])

        self.update("".join(chars))
