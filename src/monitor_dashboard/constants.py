"""Refresh rate constants for the monitoring dashboard.

All refresh rates are prime numbers in seconds for optimal timer distribution.
Edit these values to adjust how frequently each data type is refreshed.
"""

# =============================================================================
# SYSTEM HEALTH PANEL REFRESH RATES (seconds)
# =============================================================================
REFRESH_CPU = 1  # CPU percent and graph
REFRESH_MEMORY = 7  # Memory percent and graph
REFRESH_LOAD = 13  # Load averages and graph

# =============================================================================
# PROCESSES PANEL REFRESH RATES (seconds)
# =============================================================================
REFRESH_PROCESSES = 5  # Process list

# =============================================================================
# DEVICES PANEL REFRESH RATES (seconds)
# =============================================================================
REFRESH_BATTERY = 67  # Battery status
REFRESH_STORAGE = 71  # Disk/storage usage

# =============================================================================
# LOGS PANEL REFRESH RATES (seconds)
# =============================================================================
REFRESH_LOGS = 59  # System logs

# =============================================================================
# INFO PANEL REFRESH RATES (seconds)
# =============================================================================
REFRESH_SYSTEM_INFO = 13 * 3600  # Hostname, distro, kernel (13 hours)
REFRESH_UPTIME = 61  # Uptime display
REFRESH_APT_PACKAGES = 61 * 60  # Apt upgradable packages (61 minutes)
REFRESH_APT_CACHE_AGE = 73  # Apt cache age check

# =============================================================================
# WINDOW SIZE CONSTANTS (pixels)
# =============================================================================
WINDOW_NORMAL_WIDTH = 3200
WINDOW_NORMAL_HEIGHT = 370
WINDOW_COMPACT_WIDTH = 1200
WINDOW_COMPACT_HEIGHT = 220
