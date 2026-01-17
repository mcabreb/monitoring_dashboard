"""Entry point for monitor_dashboard package."""

from monitor_dashboard.app import MonitorDashboardApp


def main() -> None:
    """Launch the Monitor Dashboard application."""
    app = MonitorDashboardApp()
    app.run()


if __name__ == "__main__":
    main()
