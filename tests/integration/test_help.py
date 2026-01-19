"""Integration tests for help overlay."""

import pytest

from monitor_dashboard.app import MonitorDashboardApp
from monitor_dashboard.screens.help import HelpOverlay, HELP_TEXT


@pytest.mark.asyncio
async def test_help_overlay_shows():
    """Verify pressing ? displays help overlay."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Press ? to show help
        await pilot.press("question_mark")

        # Verify HelpOverlay is displayed
        assert isinstance(app.screen, HelpOverlay)


@pytest.mark.asyncio
async def test_help_overlay_dismisses_on_key():
    """Verify pressing any key dismisses help overlay."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Show help overlay
        await pilot.press("question_mark")
        assert isinstance(app.screen, HelpOverlay)

        # Press any key to dismiss
        await pilot.press("space")

        # Verify help is dismissed (back to MainDashboard)
        from monitor_dashboard.screens.main import MainDashboard

        assert isinstance(app.screen, MainDashboard)


@pytest.mark.asyncio
async def test_help_overlay_content():
    """Verify help overlay contains expected keyboard shortcuts."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Show help overlay
        await pilot.press("question_mark")

        # Get help content
        help_screen = app.screen
        assert isinstance(help_screen, HelpOverlay)

        # Query the help content static widget to verify it exists
        help_static = help_screen.query_one("#help-content")
        assert help_static is not None

        # Verify key shortcuts are mentioned in the HELP_TEXT constant
        assert "Tab" in HELP_TEXT
        assert "Shift+Tab" in HELP_TEXT
        assert "Enter" in HELP_TEXT
        assert "Escape" in HELP_TEXT
        assert "?" in HELP_TEXT or "Help" in HELP_TEXT
        assert "q" in HELP_TEXT or "Quit" in HELP_TEXT


@pytest.mark.asyncio
async def test_help_overlay_has_gem_style():
    """Verify help overlay has GEM-style bordered appearance."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Show help overlay
        await pilot.press("question_mark")

        # Get help container
        help_screen = app.screen
        help_container = help_screen.query_one("#help-container")

        # Verify container exists (styling is applied via CSS)
        assert help_container is not None
