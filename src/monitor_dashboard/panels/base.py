"""Base panel widget for all monitoring panels."""

from textual.events import Click
from textual.widgets import Static


class BasePanel(Static, can_focus=True):
    """Base class for all monitoring panels with GEM-style borders and titles."""

    BORDER_TITLE = "Panel"  # Override in subclass

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the base panel with border and title."""
        super().__init__(*args, **kwargs)
        self.border = "solid"

    def on_click(self, event: Click) -> None:
        """Handle click events to ensure panel gets focus.

        Child widgets like VerticalScroll may capture clicks and focus themselves.
        This handler ensures the panel itself receives focus when clicked anywhere.
        """
        self.focus()
