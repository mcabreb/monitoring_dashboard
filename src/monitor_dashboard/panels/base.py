"""Base panel widget for all monitoring panels."""

from textual.widgets import Static


class BasePanel(Static, can_focus=True):
    """Base class for all monitoring panels with GEM-style borders and titles."""

    BORDER_TITLE = "Panel"  # Override in subclass

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the base panel with border and title."""
        super().__init__(*args, **kwargs)
        self.border = "solid"
