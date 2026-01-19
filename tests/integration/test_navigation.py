"""Integration tests for keyboard navigation."""

import pytest

from monitor_dashboard.app import MonitorDashboardApp


@pytest.mark.asyncio
async def test_tab_cycles_focus_forward():
    """Verify Tab key cycles focus forward through panels."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Initially, the first panel should be focused (or we focus it manually)
        system_health = app.screen.query_one("#system-health")
        system_health.focus()

        # Verify initial focus
        assert app.focused is system_health

        # Press Tab - should move to Storage
        await pilot.press("tab")
        processes = app.screen.query_one("#processes")
        assert app.focused is processes

        # Press Tab - should move to Devices
        await pilot.press("tab")
        devices = app.screen.query_one("#devices")
        assert app.focused is devices

        # Press Tab - should move to Logs
        await pilot.press("tab")
        logs = app.screen.query_one("#logs")
        assert app.focused is logs

        # Press Tab - should cycle back to System Health
        await pilot.press("tab")
        assert app.focused is system_health


@pytest.mark.asyncio
async def test_shift_tab_cycles_focus_backward():
    """Verify Shift+Tab cycles focus backward through panels."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Start from Storage panel
        processes = app.screen.query_one("#processes")
        processes.focus()

        # Press Shift+Tab - should move to System Health
        await pilot.press("shift+tab")
        system_health = app.screen.query_one("#system-health")
        assert app.focused is system_health

        # Press Shift+Tab - should cycle to Logs (last panel)
        await pilot.press("shift+tab")
        logs = app.screen.query_one("#logs")
        assert app.focused is logs

        # Press Shift+Tab - should move to Devices
        await pilot.press("shift+tab")
        devices = app.screen.query_one("#devices")
        assert app.focused is devices


@pytest.mark.asyncio
async def test_focus_visual_indicator():
    """Verify focused panel has visual indicator (border change)."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Focus the system health panel
        system_health = app.screen.query_one("#system-health")
        system_health.focus()

        # Check that panel is focused
        assert app.focused is system_health

        # In a real visual test, we'd check the border style via CSS
        # For now, just verify that focus is working
        assert system_health.has_focus


@pytest.mark.asyncio
async def test_navigation_from_any_panel():
    """Verify Tab/Shift+Tab work from any panel (modeless)."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        # Test navigation from Devices panel
        devices = app.screen.query_one("#devices")
        devices.focus()

        await pilot.press("tab")
        logs = app.screen.query_one("#logs")
        assert app.focused is logs

        # Test backward navigation from same position
        logs.focus()
        await pilot.press("shift+tab")
        assert app.focused is devices


@pytest.mark.asyncio
async def test_arrow_keys_captured():
    """Verify arrow keys are bound and don't cause errors."""
    app = MonitorDashboardApp()
    async with app.run_test() as pilot:
        # Wait for screen to be ready
        await pilot.pause()

        system_health = app.screen.query_one("#system-health")
        system_health.focus()

        # Press arrow keys - should not cause errors (stub implementation)
        await pilot.press("up")
        await pilot.press("down")
        await pilot.press("left")
        await pilot.press("right")

        # Focus should remain on same panel
        assert app.focused is system_health
