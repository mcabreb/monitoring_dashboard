"""Popup screens for info display, confirmations, and errors."""

from typing import Any

from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Label, Static
from textual.worker import Worker, WorkerState

from monitor_dashboard.utils.formatting import format_bytes


def _format_info_value(key: str, value: Any) -> str:
    """Format a value for display in the info popup.

    Args:
        key: The key/field name (used to determine formatting).
        value: The value to format.

    Returns:
        Formatted string representation.
    """
    if value is None:
        return "N/A"

    key_lower = key.lower()

    # Percent values - format with 2 decimals and %
    if "percent" in key_lower:
        if isinstance(value, (int, float)):
            return f"{value:.2f}%"

    # Byte values - format as human readable
    if key_lower in ("total", "used", "free", "memory_used", "memory_total"):
        if isinstance(value, (int, float)):
            return format_bytes(int(value))

    # Time remaining (seconds) - format as hours/minutes
    if key_lower == "time_remaining":
        if isinstance(value, (int, float)) and value > 0:
            hours = int(value) // 3600
            minutes = (int(value) % 3600) // 60
            if hours > 0:
                return f"{hours}h {minutes}m"
            return f"{minutes}m"
        return "N/A"

    # Load values - format with 2 decimals
    if key_lower.startswith("load_"):
        if isinstance(value, (int, float)):
            return f"{value:.2f}"

    # Core count
    if key_lower == "num_cores":
        if isinstance(value, int):
            return f"{value} cores"

    # Boolean values
    if isinstance(value, bool):
        return "Yes" if value else "No"

    return str(value)


class InfoPopup(ModalScreen):
    """Modal popup displaying information about selected elements."""

    DEFAULT_CSS = """
    InfoPopup {
        align: center middle;
    }

    #info-popup-container {
        width: 80%;
        height: 80%;
        max-width: 100;
        max-height: 40;
        border: solid cyan;
        background: black;
        padding: 1 2;
    }

    #info-popup-title {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
        color: cyan;
        margin-bottom: 1;
    }

    #info-popup-content {
        width: 100%;
        height: 1fr;
        color: white;
    }

    #info-popup-content Label {
        width: 100%;
        height: auto;
        content-align: left middle;
    }

    #info-popup-footer {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: gray;
        margin-top: 1;
    }

    .search-result-title {
        color: yellow;
        text-style: bold;
    }

    .search-result-snippet {
        color: white;
    }

    .search-status {
        color: cyan;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("enter", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
    ]

    def __init__(
        self,
        title: str,
        items: list[dict[str, Any]],
        search_query: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize info popup.

        Args:
            title: Popup title.
            items: List of item dicts with 'label' and 'details' keys.
            search_query: Optional query for web search (enables 's' key).
        """
        super().__init__(**kwargs)
        self._title = title
        self._items = items
        self._search_query = search_query
        self._search_performed = False

    def compose(self):
        """Compose the info popup content."""
        with Container(id="info-popup-container"):
            yield Static(self._title, id="info-popup-title")
            with VerticalScroll(id="info-popup-content"):
                for item in self._items:
                    # Item header
                    label = item.get("label", "Unknown")
                    yield Label(f"[bold cyan]{label}[/bold cyan]")

                    # Item details
                    details = item.get("details", {})
                    if isinstance(details, dict):
                        for key, value in details.items():
                            formatted_value = _format_info_value(key, value)
                            yield Label(f"  {key}: {formatted_value}")
                    else:
                        yield Label(f"  {details}")

                    yield Label("")  # Spacer between items

            # Footer with search hint if available
            if self._search_query:
                yield Static(
                    "[dim]Press [bold]s[/bold] to search  |  any other key to close[/dim]",
                    id="info-popup-footer",
                )
            else:
                yield Static("[dim]Press any key to close[/dim]", id="info-popup-footer")

    def on_key(self, event) -> None:
        """Handle key press - search on 's', dismiss on other keys."""
        event.stop()

        # Handle 's' key for search
        if event.key == "s" and self._search_query and not self._search_performed:
            self._perform_search()
            return

        self.dismiss()

    def _perform_search(self) -> None:
        """Perform web search and display results."""
        # Update UI to show searching status
        content = self.query_one("#info-popup-content", VerticalScroll)

        # Add searching indicator
        content.mount(Label("[cyan]Searching...[/cyan]", classes="search-status"))

        # Run search in background to not block UI
        self.run_worker(self._do_search, exclusive=True, thread=True)

    def _do_search(self) -> list:
        """Background worker to perform search (runs in thread)."""
        from monitor_dashboard.utils.web_search import search_for_error

        return search_for_error(self._search_query, max_results=3)

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Handle worker completion."""
        if event.worker.name == "_do_search" and event.state == WorkerState.SUCCESS:
            self._display_search_results(event.worker.result)

    def _display_search_results(self, results) -> None:
        """Display search results in the popup."""
        self._search_performed = True

        content = self.query_one("#info-popup-content", VerticalScroll)

        # Remove the "Searching..." label
        for child in content.query(".search-status"):
            child.remove()

        # Add search results header
        content.mount(Label("[bold yellow]--- Web Search ---[/bold yellow]"))

        if not results:
            content.mount(Label("[dim]No relevant results found[/dim]"))
        else:
            result = results[0]  # Show only first result

            # Title
            title = result.title[:80] + "..." if len(result.title) > 80 else result.title
            content.mount(Label(f"[yellow]{title}[/yellow]", classes="search-result-title"))

            # Snippet (allow more text for single result)
            snippet = result.snippet[:250] + "..." if len(result.snippet) > 250 else result.snippet
            content.mount(Label(f"  {snippet}", classes="search-result-snippet"))

        # Update footer
        footer = self.query_one("#info-popup-footer", Static)
        footer.update("[dim]Press any key to close[/dim]")


class ErrorPopup(ModalScreen):
    """Modal popup displaying an error message."""

    DEFAULT_CSS = """
    ErrorPopup {
        align: center middle;
    }

    #error-popup-container {
        width: auto;
        height: auto;
        min-width: 40;
        max-width: 80;
        border: solid red;
        background: black;
        padding: 1 2;
    }

    #error-popup-title {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
        color: red;
        margin-bottom: 1;
    }

    #error-popup-message {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: white;
    }

    #error-popup-footer {
        width: 100%;
        height: 1;
        content-align: center middle;
        color: gray;
        margin-top: 1;
    }
    """

    def __init__(self, title: str, message: str, **kwargs) -> None:
        """Initialize error popup.

        Args:
            title: Error title.
            message: Error message.
        """
        super().__init__(**kwargs)
        self._title = title
        self._message = message

    def compose(self):
        """Compose the error popup content."""
        with Container(id="error-popup-container"):
            yield Static(self._title, id="error-popup-title")
            yield Label(self._message, id="error-popup-message")
            yield Static("[dim]Press any key to close[/dim]", id="error-popup-footer")

    def on_key(self, event) -> None:
        """Dismiss on any key press."""
        event.stop()
        self.dismiss()


class KillConfirmPopup(ModalScreen[bool]):
    """Modal popup confirming process kill."""

    DEFAULT_CSS = """
    KillConfirmPopup {
        align: center middle;
    }

    #kill-popup-container {
        width: auto;
        height: auto;
        min-width: 50;
        border: solid yellow;
        background: black;
        padding: 1 2;
    }

    #kill-popup-title {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
        color: yellow;
        margin-bottom: 1;
    }

    #kill-popup-message {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: white;
    }

    #kill-popup-warning {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: red;
        margin-top: 1;
    }

    #kill-popup-footer {
        width: 100%;
        height: 1;
        content-align: center middle;
        color: gray;
        margin-top: 1;
    }
    """

    def __init__(self, pid: int, process_name: str, **kwargs) -> None:
        """Initialize kill confirm popup.

        Args:
            pid: Process ID to kill.
            process_name: Name of the process.
        """
        super().__init__(**kwargs)
        self._pid = pid
        self._process_name = process_name

    def compose(self):
        """Compose the kill confirm popup content."""
        with Container(id="kill-popup-container"):
            yield Static("Kill Process?", id="kill-popup-title")
            yield Label(
                f"PID: [bold]{self._pid}[/bold]  Name: [bold]{self._process_name}[/bold]",
                id="kill-popup-message",
            )
            yield Label(
                "[red]This action cannot be undone![/red]",
                id="kill-popup-warning",
            )
            yield Static(
                "[dim]Press [bold]Y[/bold] to confirm, any other key to cancel[/dim]",
                id="kill-popup-footer",
            )

    def on_key(self, event) -> None:
        """Handle key press for confirmation."""
        event.stop()
        if event.key.lower() == "y":
            self.dismiss(True)
        else:
            self.dismiss(False)


class ExportSuccessPopup(ModalScreen):
    """Modal popup confirming successful log export."""

    DEFAULT_CSS = """
    ExportSuccessPopup {
        align: center middle;
    }

    #export-popup-container {
        width: auto;
        height: auto;
        min-width: 50;
        max-width: 80;
        border: solid green;
        background: black;
        padding: 1 2;
    }

    #export-popup-title {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-style: bold;
        color: green;
        margin-bottom: 1;
    }

    #export-popup-message {
        width: 100%;
        height: auto;
        content-align: center middle;
        color: white;
    }

    #export-popup-footer {
        width: 100%;
        height: 1;
        content-align: center middle;
        color: gray;
        margin-top: 1;
    }
    """

    def __init__(self, filepath: str, count: int, **kwargs) -> None:
        """Initialize export success popup.

        Args:
            filepath: Path where logs were exported.
            count: Number of logs exported.
        """
        super().__init__(**kwargs)
        self._filepath = filepath
        self._count = count

    def compose(self):
        """Compose the export success popup content."""
        with Container(id="export-popup-container"):
            yield Static("Logs Exported", id="export-popup-title")
            yield Label(
                f"Exported [bold]{self._count}[/bold] log entries to:",
                id="export-popup-message",
            )
            yield Label(f"[cyan]{self._filepath}[/cyan]")
            yield Static("[dim]Press any key to close[/dim]", id="export-popup-footer")

    def on_key(self, event) -> None:
        """Dismiss on any key press."""
        event.stop()
        self.dismiss()
