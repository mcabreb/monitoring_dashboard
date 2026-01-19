"""Integration tests for panel layout."""

import pytest
from textual.widgets import Label

from monitor_dashboard.app import MonitorDashboardApp
from monitor_dashboard.panels import (
    DevicesPanel,
    InfoBar,
    LogsPanel,
    ProcessesPanel,
    SystemHealthPanel,
)


@pytest.mark.asyncio
async def test_all_panels_present():
    """Verify all 5 panels are present in widget tree."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Check that all panels are present
        assert app.screen.query_one(SystemHealthPanel)
        assert app.screen.query_one(ProcessesPanel)
        assert app.screen.query_one(DevicesPanel)
        assert app.screen.query_one(LogsPanel)
        assert app.screen.query_one(InfoBar)


@pytest.mark.asyncio
async def test_panel_titles():
    """Verify each panel has correct title."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Verify panel titles contain expected text
        system_health = app.screen.query_one(SystemHealthPanel)
        assert "System Health" in system_health.BORDER_TITLE

        processes = app.screen.query_one(ProcessesPanel)
        assert "Processes" in processes.BORDER_TITLE

        devices = app.screen.query_one(DevicesPanel)
        assert "Devices" in devices.BORDER_TITLE

        logs = app.screen.query_one(LogsPanel)
        assert "Logs" in logs.BORDER_TITLE

        info = app.screen.query_one(InfoBar)
        assert "Info" in info.BORDER_TITLE


@pytest.mark.asyncio
async def test_panels_have_borders():
    """Verify panels have visible borders."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Check that panels have border attribute set
        system_health = app.screen.query_one(SystemHealthPanel)
        assert system_health.border == "solid"

        processes = app.screen.query_one(ProcessesPanel)
        assert processes.border == "solid"

        devices = app.screen.query_one(DevicesPanel)
        assert devices.border == "solid"

        logs = app.screen.query_one(LogsPanel)
        assert logs.border == "solid"

        info = app.screen.query_one(InfoBar)
        assert info.border == "solid"


@pytest.mark.asyncio
async def test_placeholder_content():
    """Verify panels contain content after data refresh."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen and data refresh (labels are populated dynamically)
        await pilot.pause()
        # Trigger manual refresh and wait for it to complete
        app._refresh_system_health()
        app._refresh_slow_data()
        await pilot.pause()

        # Check that panels have Label widgets after refresh
        system_health = app.screen.query_one(SystemHealthPanel)
        labels = system_health.query(Label)
        assert len(labels) > 0
