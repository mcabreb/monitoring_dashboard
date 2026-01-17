"""Integration tests for panel layout."""

import pytest
from textual.widgets import Label

from monitor_dashboard.app import MonitorDashboardApp
from monitor_dashboard.panels import (
    SystemHealthPanel,
    StoragePanel,
    DevicesPanel,
    LogsPanel,
    InfoBar,
)


@pytest.mark.asyncio
async def test_all_panels_present():
    """Verify all 5 panels are present in widget tree."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Check that all panels are present
        assert app.query_one(SystemHealthPanel)
        assert app.query_one(StoragePanel)
        assert app.query_one(DevicesPanel)
        assert app.query_one(LogsPanel)
        assert app.query_one(InfoBar)


@pytest.mark.asyncio
async def test_panel_titles():
    """Verify each panel has correct title."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Verify panel titles contain expected text
        system_health = app.query_one(SystemHealthPanel)
        assert "System Health" in system_health.BORDER_TITLE

        storage = app.query_one(StoragePanel)
        assert "Storage" in storage.BORDER_TITLE

        devices = app.query_one(DevicesPanel)
        assert "Devices" in devices.BORDER_TITLE

        logs = app.query_one(LogsPanel)
        assert "Logs" in logs.BORDER_TITLE

        info = app.query_one(InfoBar)
        assert "Info" in info.BORDER_TITLE


@pytest.mark.asyncio
async def test_panels_have_borders():
    """Verify panels have visible borders."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Check that panels have border attribute set
        system_health = app.query_one(SystemHealthPanel)
        assert system_health.border == "solid"

        storage = app.query_one(StoragePanel)
        assert storage.border == "solid"

        devices = app.query_one(DevicesPanel)
        assert devices.border == "solid"

        logs = app.query_one(LogsPanel)
        assert logs.border == "solid"

        info = app.query_one(InfoBar)
        assert info.border == "solid"


@pytest.mark.asyncio
async def test_placeholder_content():
    """Verify panels contain placeholder text."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Check that panels have Label widgets with "Coming Soon" text
        system_health = app.query_one(SystemHealthPanel)
        labels = system_health.query(Label)
        assert len(labels) > 0
        assert any("Coming Soon" in str(label.renderable) for label in labels)
