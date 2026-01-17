"""LED status indicator widget."""

from enum import Enum

from textual.widgets import Static


class LEDStatus(Enum):
    """LED indicator status levels."""

    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class LEDIndicator(Static):
    """A colored LED-style status indicator using Unicode bullet character.

    Displays a colored dot (●) to indicate status:
    - Green (●) for OK status
    - Yellow (●) for WARNING status
    - Red (●) for CRITICAL status
    """

    def __init__(self, status: LEDStatus = LEDStatus.OK, **kwargs) -> None:
        """Initialize LED indicator.

        Args:
            status: Initial status level (default: OK).
            **kwargs: Additional arguments passed to Static.__init__.
        """
        super().__init__("●", **kwargs)
        self._status = status
        self._update_display()

    def set_status(self, status: LEDStatus) -> None:
        """Update the LED status.

        Args:
            status: New status level.
        """
        self._status = status
        self._update_display()

    def _update_display(self) -> None:
        """Update the LED display with appropriate color."""
        # Set CSS class based on status
        self.remove_class("led-ok", "led-warning", "led-critical")
        if self._status == LEDStatus.OK:
            self.add_class("led-ok")
        elif self._status == LEDStatus.WARNING:
            self.add_class("led-warning")
        elif self._status == LEDStatus.CRITICAL:
            self.add_class("led-critical")
