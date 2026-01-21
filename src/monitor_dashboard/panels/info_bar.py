"""Info bar panel for system information display."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label

from monitor_dashboard.data_sources.apt import CACHE_STALE_THRESHOLD, AptStatus
from monitor_dashboard.models.system_info import SystemInfo
from monitor_dashboard.panels.base import BasePanel


class InfoBar(BasePanel):
    """Panel displaying system information bar."""

    BORDER_TITLE = "● Info"

    # Uptime thresholds in seconds
    _UPTIME_24H = 24 * 3600  # 24 hours
    _UPTIME_WEEK = 7 * 24 * 3600  # 1 week

    def __init__(self, **kwargs) -> None:
        """Initialize info bar."""
        super().__init__(**kwargs)
        self._info_label: Label | None = None
        self._apt_label: Label | None = None

    def compose(self) -> ComposeResult:
        """Compose the Info bar content."""
        with Vertical():
            self._info_label = Label("Loading...")
            yield self._info_label
            self._apt_label = Label("")
            yield self._apt_label

    def update(self, info: SystemInfo | None) -> None:
        """Update info bar with system information.

        Args:
            info: System information, or None if unavailable.
        """
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
        if not self._apt_label:
            return

        if not apt_status or not apt_status.checked:
            self._apt_label.update("Updates: [yellow]checking...[/yellow]")
            return

        # Format cache age
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
