"""Info bar panel for system information display."""

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Label

from monitor_dashboard.data_sources.apt import (
    CACHE_STALE_THRESHOLD,
    AptStatus,
    UpgradablePackage,
)
from monitor_dashboard.models.system_info import SystemInfo
from monitor_dashboard.panels.base import BasePanel
from monitor_dashboard.panels.selectable import SelectableMixin


class InfoBar(BasePanel, SelectableMixin):
    """Panel displaying system information bar."""

    BORDER_TITLE = "● Info"

    # Uptime thresholds in seconds
    _UPTIME_24H = 24 * 3600  # 24 hours
    _UPTIME_WEEK = 7 * 24 * 3600  # 1 week

    def __init__(self, **kwargs) -> None:
        """Initialize info bar."""
        super().__init__(**kwargs)
        self.init_selection()
        self._info_label: Label | None = None
        self._apt_label: Label | None = None
        self._packages_container: VerticalScroll | None = None
        self._system_info: SystemInfo | None = None
        self._apt_status: AptStatus | None = None

    def compose(self) -> ComposeResult:
        """Compose the Info bar content."""
        with Vertical(id="info-content"):
            self._info_label = Label("Loading...")
            yield self._info_label
            self._apt_label = Label("")
            yield self._apt_label
            # Scrollable container for package list (used in expanded mode)
            self._packages_container = VerticalScroll(id="packages-list")
            self._packages_container.display = False
            yield self._packages_container

    def _is_expanded(self) -> bool:
        """Check if panel is in expanded (full-screen) mode."""
        from monitor_dashboard.screens.expanded import ExpandedPanelScreen

        try:
            return isinstance(self.app.screen, ExpandedPanelScreen)
        except Exception:
            return False

    # SelectableMixin required methods
    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs (package names)."""
        if not self._apt_status or not self._apt_status.packages:
            return []
        return [pkg.name for pkg in self._apt_status.packages]

    def get_element_data(self, element_id: str) -> UpgradablePackage | None:
        """Get package data for a package name ID."""
        if not self._apt_status:
            return None
        for pkg in self._apt_status.packages:
            if pkg.name == element_id:
                return pkg
        return None

    def refresh_selection_display(self) -> None:
        """Re-render with selection styling."""
        self._display_packages()

    def update(self, info: SystemInfo | None) -> None:
        """Update info bar with system information.

        Args:
            info: System information, or None if unavailable.
        """
        self._system_info = info

        if not self._info_label:
            return

        if not info:
            self._info_label.update("System info unavailable")
            return

        # Format uptime
        hours = info.uptime_seconds // 3600
        minutes = (info.uptime_seconds % 3600) // 60
        uptime_str = f"{hours}h {minutes}m"

        # Color uptime based on thresholds
        uptime_color = self._get_uptime_color(info.uptime_seconds)
        colored_uptime = f"[{uptime_color}]{uptime_str}[/{uptime_color}]"

        # Build info string with colored uptime
        info_text = f"{info.hostname} | {info.distro} | Kernel {info.kernel} | Uptime: {colored_uptime}"
        self._info_label.update(info_text)

    def update_apt(self, apt_status: AptStatus | None) -> None:
        """Update info bar with apt upgrade status.

        Args:
            apt_status: Apt status information, or None if unavailable.
        """
        self._apt_status = apt_status

        if not self._apt_label:
            return

        if not apt_status or not apt_status.checked:
            self._apt_label.update("Updates: [yellow]checking...[/yellow]")
            self._hide_packages_container()
            return

        # Prune invalid sticky selections
        self.prune_invalid_sticky()

        is_expanded = self._is_expanded()

        if is_expanded and apt_status.packages:
            # Expanded mode with packages: show full list
            self._apt_label.display = False
            self._show_packages_container()
            self._display_packages()
        else:
            # Collapsed mode or no packages: show summary
            self._apt_label.display = True
            self._hide_packages_container()
            self._display_summary(apt_status)

    def _display_summary(self, apt_status: AptStatus) -> None:
        """Display summary line for apt status."""
        if not self._apt_label:
            return

        cache_info = self._format_cache_age(apt_status.cache_age_seconds)

        if apt_status.upgradable_count == 0:
            self._apt_label.update(f"Updates: [green]System is up to date[/green]{cache_info}")
        else:
            # Color based on whether there are security updates
            if apt_status.security_count > 0:
                color = "red"
                security_note = f" ({apt_status.security_count} security)"
            else:
                color = "yellow"
                security_note = ""

            count = apt_status.upgradable_count
            pkg_word = "package" if count == 1 else "packages"
            self._apt_label.update(
                f"Updates: [{color}]{count} {pkg_word} can be upgraded{security_note}[/{color}]{cache_info}"
            )

    def _display_packages(self) -> None:
        """Display full package list with selection styling."""
        if not self._packages_container or not self._apt_status:
            return

        self._packages_container.remove_children()

        if not self._apt_status.packages:
            self._packages_container.mount(Label("[green]System is up to date[/green]"))
            return

        # Header with cache info
        cache_info = self._format_cache_age(self._apt_status.cache_age_seconds)
        count = self._apt_status.upgradable_count
        security = self._apt_status.security_count
        header = f"[bold]{count} package{'s' if count != 1 else ''} can be upgraded"
        if security > 0:
            header += f" [red]({security} security)[/red]"
        header += f"[/bold]{cache_info}"
        self._packages_container.mount(Label(header))
        self._packages_container.mount(Label(""))  # Spacer

        # Track cursor widget for scrolling
        cursor_widget = None

        # Package list
        for pkg in self._apt_status.packages:
            element_id = pkg.name
            # Format: package_name: current -> new (repo)
            if pkg.is_security:
                line = f"[red]⚠ {pkg.name}[/red]: {pkg.current_version} → {pkg.new_version}"
            else:
                line = f"  {pkg.name}: {pkg.current_version} → {pkg.new_version}"

            label = Label(line)

            # Apply selection styling
            selection_class = self.get_selection_class(element_id)
            if selection_class:
                label.add_class(selection_class)
                if self.is_cursor(element_id):
                    cursor_widget = label

            self._packages_container.mount(label)

        # Scroll to keep cursor visible
        if cursor_widget is not None:
            container = self._packages_container
            container.call_later(
                lambda w=cursor_widget, c=container: c.scroll_to_widget(w, animate=False)
            )

    def _show_packages_container(self) -> None:
        """Show the packages container."""
        if self._packages_container:
            self._packages_container.display = True

    def _hide_packages_container(self) -> None:
        """Hide the packages container."""
        if self._packages_container:
            self._packages_container.display = False

    def _format_cache_age(self, cache_age_seconds: int | None) -> str:
        """Format cache age for display.

        Args:
            cache_age_seconds: Cache age in seconds, or None if unknown.

        Returns:
            Formatted string with cache age info.
        """
        if cache_age_seconds is None:
            return ""

        # Format the age
        if cache_age_seconds < 3600:
            minutes = cache_age_seconds // 60
            age_str = f"{minutes}m" if minutes > 0 else "<1m"
        elif cache_age_seconds < 86400:
            hours = cache_age_seconds // 3600
            age_str = f"{hours}h"
        else:
            days = cache_age_seconds // 86400
            age_str = f"{days}d"

        # Add warning if cache is stale
        if cache_age_seconds > CACHE_STALE_THRESHOLD:
            return f" [yellow](cache: {age_str} old ⚠)[/yellow]"
        else:
            return f" [dim](cache: {age_str})[/dim]"

    def _get_uptime_color(self, uptime_seconds: int) -> str:
        """Get color for uptime based on thresholds.

        Args:
            uptime_seconds: Uptime in seconds.

        Returns:
            Color name for Rich markup.

        Thresholds:
            - Green: < 24 hours
            - Yellow: 24 hours to 1 week
            - Red: > 1 week
        """
        if uptime_seconds > self._UPTIME_WEEK:
            return "red"
        elif uptime_seconds >= self._UPTIME_24H:
            return "yellow"
        else:
            return "green"
