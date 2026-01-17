# Epic 3: Logs, Info & Alerts

## Epic Overview

| Field | Value |
|-------|-------|
| Epic ID | 3 |
| Title | Logs, Info & Alerts |
| Status | Ready |
| Stories | 8 (3.1 - 3.8) |
| Priority | MVP - Must Have |

## Goal

Complete the MVP dashboard with system logs (dmesg output with severity highlighting and clipboard support), an info bar (date/time, uptime, kernel, distro), and a visual alert system that flashes and persists until acknowledged. After this epic, the dashboard is fully functional for passive monitoring with proactive alerting.

## Dependencies

- Epic 1 (Foundation & System Health) - app infrastructure
- Epic 2 (Storage & Devices) - for alert threshold integration

## Technical Context

**Key Technologies:**
- subprocess (dmesg command)
- platform module (system info)
- pyperclip 1.8.2 (clipboard)
- Python logging module

**Key Data Models:**
```python
class LogSeverity(Enum):
    EMERGENCY = "emerg"
    ALERT = "alert"
    CRITICAL = "crit"
    ERROR = "err"
    WARNING = "warn"
    NOTICE = "notice"
    INFO = "info"
    DEBUG = "debug"

@dataclass
class LogEntry:
    timestamp: datetime
    severity: LogSeverity
    message: str
    raw: str

class AlertType(Enum):
    LOW_BATTERY = "low_battery"
    HIGH_CPU = "high_cpu"
    LOW_MEMORY = "low_memory"
    LOW_DISK = "low_disk"
    DEVICE_DISCONNECT = "device_disconnect"

@dataclass
class Alert:
    alert_type: AlertType
    message: str
    triggered_at: datetime
    acknowledged: bool = False
    source_panel: str = ""
```

**Hardcoded Alert Thresholds (MVP):**
- Battery < 20%
- CPU > 80%
- Memory < 10% free
- Disk < 10% free

**Alert State Machine:**
- Inactive → Triggered (threshold exceeded)
- Triggered → Acknowledged (user presses 'a')
- Acknowledged → Inactive (cooldown + threshold OK)

## Stories in This Epic

| Story | Title | Status |
|-------|-------|--------|
| 3.1 | System Logs Data Collection | Draft |
| 3.2 | Logs Panel Display | Draft |
| 3.3 | Clipboard Copy for Logs | Draft |
| 3.4 | System Info Data Collection | Draft |
| 3.5 | Info Bar Display | Draft |
| 3.6 | Alert Threshold Engine | Draft |
| 3.7 | Visual Alert Display | Draft |
| 3.8 | Bluetooth Disconnect Notification | Draft |

## Acceptance Criteria (Epic Level)

- [ ] Logs panel displays last 30 dmesg entries, scrollable to 100
- [ ] Log entries color-coded by severity (red=error, yellow=warning, white=info)
- [ ] 'c' copies visible logs, 'C' copies all logs to clipboard
- [ ] Info bar shows date/time, uptime, kernel version, distro
- [ ] Alerts flash LED indicators when thresholds exceeded
- [ ] 'a' acknowledges all alerts, 'A' acknowledges one at a time
- [ ] Bluetooth disconnect triggers notification
- [ ] All data refreshes at 1 Hz

## Definition of Done

- [ ] All 8 stories completed with acceptance criteria met
- [ ] Unit tests for alert engine with edge cases
- [ ] dmesg permission handling documented and graceful
- [ ] Clipboard error handling is robust
- [ ] Integration tests verify alert display and acknowledgment
- [ ] Code passes black, ruff, and mypy checks
- [ ] Full MVP functionality verified end-to-end
