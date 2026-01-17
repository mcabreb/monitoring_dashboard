"""Help overlay screen displaying keyboard shortcuts."""

from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

HELP_TEXT = """[b]Keyboard Help[/b]

[green]Tab[/green]          Next panel
[green]Shift+Tab[/green]    Previous panel
[green]Enter[/green]        Expand/collapse panel
[green]Escape[/green]       Return to dashboard
[green]?[/green]            Show this help
[green]q[/green]            Quit application

[dim]Press any key to close[/dim]
"""


class HelpOverlay(ModalScreen):
    """Modal help screen showing keyboard shortcuts."""

    DEFAULT_CSS = """
    HelpOverlay {
        align: center middle;
    }

    #help-container {
        width: 50;
        height: auto;
        border: solid green;
        background: black;
        padding: 2;
    }

    #help-content {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: white;
    }
    """

    def compose(self):
        """Compose the help overlay content."""
        with Container(id="help-container"):
            yield Static(HELP_TEXT, id="help-content")

    def on_key(self, event) -> None:
        """Dismiss on any key press."""
        self.dismiss()
