# Epic 2: Storage & Devices

## Epic Overview

| Field | Value |
|-------|-------|
| Epic ID | 2 |
| Title | Storage & Devices |
| Status | Ready |
| Stories | 6 (2.1 - 2.6) |
| Priority | MVP - Must Have |

## Goal

Extend the dashboard with storage monitoring (disk usage for all partitions, mounted volumes list) and device tracking (connected Bluetooth devices with battery status, laptop battery with drain curve and time remaining). After this epic, users can monitor all their storage and connected devices alongside system health.

## Dependencies

- Epic 1 (Foundation & System Health) - panel layout, navigation, and app infrastructure must be complete

## Technical Context

**Key Technologies:**
- psutil 5.9.8 (disk partitions, disk usage)
- pydbus 0.6.0 (UPower D-Bus for battery/Bluetooth)
- textual widgets (ProgressBar, ListView)

**Key Data Models:**
```python
@dataclass
class DiskInfo:
    mount_point: str
    device: str
    fs_type: str
    total: int
    used: int
    free: int
    percent: float

@dataclass
class BatteryStatus:
    percent: float
    state: BatteryState  # CHARGING, DISCHARGING, FULL, UNKNOWN
    time_remaining: int | None
    is_present: bool

@dataclass
class BluetoothDevice:
    name: str
    address: str
    device_type: DeviceType
    battery_percent: int | None
    is_connected: bool
```

**D-Bus Retry Policy:**
- Max retries: 2
- Initial delay: 100ms
- Backoff factor: 2.0
- Timeout: 1 second per call

## Stories in This Epic

| Story | Title | Status |
|-------|-------|--------|
| 2.1 | Storage Data Collection | Draft |
| 2.2 | Storage Panel Display | Draft |
| 2.3 | Laptop Battery Data Collection | Draft |
| 2.4 | Bluetooth Device Data Collection | Draft |
| 2.5 | Devices Panel Display | Draft |
| 2.6 | Memory History Graph | Draft |

## Acceptance Criteria (Epic Level)

- [ ] Storage panel displays all mounted partitions with usage bars
- [ ] Disk usage color-coded: green (<70%), yellow (70-90%), red (>90%)
- [ ] Laptop battery shows percentage, state, time remaining, and drain curve
- [ ] Bluetooth devices listed with name, type icon, and battery percentage
- [ ] Graceful handling when no battery or Bluetooth is available
- [ ] LED status indicators reflect worst-case status per panel
- [ ] Memory history graph added to System Health panel
- [ ] All data refreshes at 1 Hz

## Definition of Done

- [ ] All 6 stories completed with acceptance criteria met
- [ ] Unit tests with mocked D-Bus responses
- [ ] Storage collector handles inaccessible partitions gracefully
- [ ] Devices collector handles missing hardware gracefully
- [ ] Integration tests verify panel rendering
- [ ] Code passes black, ruff, and mypy checks
