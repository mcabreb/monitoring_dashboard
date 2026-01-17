"""Main application module for Monitor Dashboard."""

from pathlib import Path

from textual.app import App
from textual.binding import Binding

from monitor_dashboard.screens import MainDashboard, HelpOverlay


class MonitorDashboardApp(App):
    """Main Monitor Dashboard application with GEM-style panel layout."""

    CSS_PATH = Path(__file__).parent / "styles" / "app.tcss"

    BINDINGS = [
        Binding("tab", "focus_next", "Next Panel"),
        Binding("shift+tab", "focus_previous", "Previous Panel"),
        Binding("up", "scroll_up", "Scroll Up", show=False),
        Binding("down", "scroll_down", "Scroll Down", show=False),
        Binding("left", "scroll_left", "Scroll Left", show=False),
        Binding("right", "scroll_right", "Scroll Right", show=False),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Initialize the app by pushing the main dashboard screen."""
        self.push_screen(MainDashboard())

    def action_focus_next(self) -> None:
        """Move focus to next panel in cycle."""
        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.query_one("#system-health", self.screen),
            self.query_one("#storage", self.screen),
            self.query_one("#devices", self.screen),
            self.query_one("#logs", self.screen),
        ]

        # Find current focused panel and move to next
        try:
            current = self.focused
            if current in panels:
                current_idx = panels.index(current)
                next_idx = (current_idx + 1) % len(panels)
                panels[next_idx].focus()
            else:
                # If no panel focused, focus first one
                panels[0].focus()
        except Exception:
            # Fallback: focus first panel
            panels[0].focus()

    def action_focus_previous(self) -> None:
        """Move focus to previous panel in cycle."""
        # Get all focusable panels (exclude InfoBar)
        panels = [
            self.query_one("#system-health", self.screen),
            self.query_one("#storage", self.screen),
            self.query_one("#devices", self.screen),
            self.query_one("#logs", self.screen),
        ]

        # Find current focused panel and move to previous
        try:
            current = self.focused
            if current in panels:
                current_idx = panels.index(current)
                prev_idx = (current_idx - 1) % len(panels)
                panels[prev_idx].focus()
            else:
                # If no panel focused, focus last one
                panels[-1].focus()
        except Exception:
            # Fallback: focus last panel
            panels[-1].focus()

    def action_scroll_up(self) -> None:
        """Scroll up within focused panel (stub for future implementation)."""
        pass

    def action_scroll_down(self) -> None:
        """Scroll down within focused panel (stub for future implementation)."""
        pass

    def action_scroll_left(self) -> None:
        """Scroll left within focused panel (stub for future implementation)."""
        pass

    def action_scroll_right(self) -> None:
        """Scroll right within focused panel (stub for future implementation)."""
        pass

    def action_show_help(self) -> None:
        """Show the help overlay with keyboard shortcuts."""
        self.push_screen(HelpOverlay())
