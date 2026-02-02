"""Help overlay screen displaying keyboard shortcuts."""

from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

HELP_TEXT = """[b]Keyboard Help[/b]

[cyan]Navigation[/cyan]
[green]Tab[/green]          Next panel
[green]Shift+Tab[/green]    Previous panel
[green]Enter[/green]        Expand/collapse panel
[green]Escape[/green]       Return to dashboard

[cyan]Selection[/cyan]
[green]Up/Down[/green]      Select element
[green]Home/End[/green]     First/last element
[green]Space[/green]        Toggle sticky selection
[green]c[/green]            Clear sticky selections
[green]i[/green]            Show info for selection

[cyan]Actions[/cyan]
[green]p[/green]            Cycle process sort column
[green]k[/green]            Kill process (Processes only)
[green]l[/green]            Export logs (Logs only)
[green]z[/green]            Toggle zoom mode
[green]w[/green]            Resize window

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
        event.stop()
        self.dismiss()
