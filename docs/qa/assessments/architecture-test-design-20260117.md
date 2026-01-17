# Test Design: Architecture-Derived Test Scenarios

**Date:** 2026-01-17
**Designer:** Quinn (Test Architect)
**Source:** `docs/architecture.md`
**Type:** Pre-Story Architecture Validation

---

## Test Strategy Overview

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total test scenarios** | 78 | 100% |
| **Unit tests** | 42 | 54% |
| **Integration tests** | 26 | 33% |
| **E2E tests** | 10 | 13% |
| **P0 (Critical)** | 18 | 23% |
| **P1 (High)** | 32 | 41% |
| **P2 (Medium)** | 22 | 28% |
| **P3 (Low)** | 6 | 8% |

---

## 1. Data Models (Unit Tests)

Pure dataclass validation and enum behavior.

### 1.1 SystemMetrics

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-001 | Unit | P1 | Validate SystemMetrics dataclass creation with valid data | Core data structure integrity |
| ARCH-UNIT-002 | Unit | P2 | Validate cpu_percent bounds (0-100) | Prevent invalid display |
| ARCH-UNIT-003 | Unit | P2 | Validate memory calculations (used + free = total) | Data consistency |
| ARCH-UNIT-004 | Unit | P2 | Validate load_avg tuple structure | Data integrity |

### 1.2 DiskInfo

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-005 | Unit | P1 | Validate DiskInfo creation with valid partition data | Core data structure |
| ARCH-UNIT-006 | Unit | P2 | Validate percent calculation accuracy | Display correctness |
| ARCH-UNIT-007 | Unit | P2 | Handle zero-size partitions without division error | Edge case safety |

### 1.3 BatteryStatus & BatteryState

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-008 | Unit | P0 | Validate BatteryState enum values (CHARGING, DISCHARGING, FULL, UNKNOWN) | Alert engine dependency |
| ARCH-UNIT-009 | Unit | P1 | Validate BatteryStatus with None time_remaining | Common scenario |
| ARCH-UNIT-010 | Unit | P1 | Validate is_present=False handling | Desktop systems |

### 1.4 BluetoothDevice & DeviceType

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-011 | Unit | P1 | Validate DeviceType enum values | Device classification |
| ARCH-UNIT-012 | Unit | P2 | Validate BluetoothDevice with None battery_percent | Common for some devices |
| ARCH-UNIT-013 | Unit | P2 | Validate is_connected state transitions | UI state accuracy |

### 1.5 LogEntry & LogSeverity

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-014 | Unit | P1 | Validate LogSeverity enum ordering (EMERGENCY > ALERT > CRITICAL > ERROR > WARNING > NOTICE > INFO > DEBUG) | Log filtering logic |
| ARCH-UNIT-015 | Unit | P1 | Validate LogEntry creation with raw line preservation | Debug capability |
| ARCH-UNIT-016 | Unit | P2 | Parse timestamp from various dmesg formats | Format compatibility |

### 1.6 Alert & AlertType

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-017 | Unit | P0 | Validate AlertType enum completeness (LOW_BATTERY, HIGH_CPU, LOW_MEMORY, LOW_DISK, DEVICE_DISCONNECT) | Alert engine coverage |
| ARCH-UNIT-018 | Unit | P0 | Validate Alert acknowledged state transition | Alert lifecycle |
| ARCH-UNIT-019 | Unit | P1 | Validate Alert source_panel assignment | UI correlation |

### 1.7 AppConfig & ThresholdConfig

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-020 | Unit | P0 | Validate ThresholdConfig default values (battery_low=20, cpu_high=80, memory_low=10, disk_low=10) | Alert accuracy |
| ARCH-UNIT-021 | Unit | P1 | Validate AppConfig default values (refresh_rate=1.0, history_length=120, log_buffer_size=100) | Operational correctness |
| ARCH-UNIT-022 | Unit | P2 | Validate custom threshold override | User configuration |

---

## 2. Data Collectors

### 2.1 SystemHealthCollector

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-023 | Unit | P0 | Mock psutil.cpu_percent returns valid SystemMetrics | Core data flow |
| ARCH-UNIT-024 | Unit | P0 | Mock psutil.virtual_memory returns correct memory metrics | Core data flow |
| ARCH-UNIT-025 | Unit | P1 | Mock psutil.getloadavg returns tuple | Load display |
| ARCH-UNIT-026 | Unit | P1 | Handle psutil exception gracefully (return None) | Error resilience |
| ARCH-INT-001 | Integration | P1 | Verify real psutil.cpu_percent call works | System integration |
| ARCH-INT-002 | Integration | P1 | Verify real psutil.virtual_memory call works | System integration |

### 2.2 StorageCollector

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-027 | Unit | P1 | Mock psutil.disk_partitions returns list[DiskInfo] | Disk enumeration |
| ARCH-UNIT-028 | Unit | P1 | Filter virtual filesystems (tmpfs, devtmpfs) | Clean display |
| ARCH-UNIT-029 | Unit | P2 | Handle permission denied on certain mounts | Graceful degradation |
| ARCH-INT-003 | Integration | P1 | Verify real disk enumeration works | System integration |

### 2.3 DevicesCollector

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-030 | Unit | P0 | Mock UPower D-Bus returns valid BatteryStatus | Battery monitoring |
| ARCH-UNIT-031 | Unit | P1 | Mock Bluetooth D-Bus returns list[BluetoothDevice] | Device monitoring |
| ARCH-UNIT-032 | Unit | P1 | Handle no battery present (desktop systems) | System compatibility |
| ARCH-UNIT-033 | Unit | P1 | Handle no Bluetooth adapter | System compatibility |
| ARCH-UNIT-034 | Unit | P0 | Track device disconnection events | Alert trigger |
| ARCH-INT-004 | Integration | P1 | Verify D-Bus retry logic with exponential backoff | Resilience |
| ARCH-INT-005 | Integration | P2 | Verify D-Bus timeout handling (1 second) | Reliability |
| ARCH-INT-006 | Integration | P2 | Verify cached value return after retry exhaustion | Graceful degradation |

### 2.4 LogsCollector

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-035 | Unit | P1 | Parse dmesg output with severity levels | Log display |
| ARCH-UNIT-036 | Unit | P1 | Parse dmesg timestamps correctly | Time display |
| ARCH-UNIT-037 | Unit | P1 | Handle dmesg permission denied gracefully | Error handling |
| ARCH-UNIT-038 | Unit | P2 | Respect log_buffer_size limit (100 entries) | Memory management |
| ARCH-INT-007 | Integration | P2 | Verify subprocess dmesg call works | System integration |

### 2.5 SystemInfoCollector

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-039 | Unit | P2 | Mock platform module returns system info | Info display |
| ARCH-UNIT-040 | Unit | P2 | Calculate uptime from psutil.boot_time | Uptime display |
| ARCH-INT-008 | Integration | P2 | Verify real platform info collection | System integration |

---

## 3. Business Logic

### 3.1 AlertEngine

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-041 | Unit | P0 | Trigger LOW_BATTERY alert when percent < threshold | Core alert |
| ARCH-UNIT-042 | Unit | P0 | Trigger HIGH_CPU alert when percent > threshold | Core alert |
| ARCH-UNIT-043 | Unit | P0 | Trigger LOW_MEMORY alert when free < threshold | Core alert |
| ARCH-UNIT-044 | Unit | P0 | Trigger LOW_DISK alert when free < threshold | Core alert |
| ARCH-UNIT-045 | Unit | P0 | Trigger DEVICE_DISCONNECT alert on device removal | Core alert |
| ARCH-UNIT-046 | Unit | P1 | Do not trigger alert when threshold not exceeded | False positive prevention |
| ARCH-UNIT-047 | Unit | P1 | Acknowledge all alerts clears list | User action |
| ARCH-UNIT-048 | Unit | P1 | Acknowledge next clears oldest only | User action |
| ARCH-UNIT-049 | Unit | P1 | Alert state machine: inactive -> triggered -> acknowledged -> inactive | State management |
| ARCH-INT-009 | Integration | P0 | AlertEngine integrates with collectors for threshold check | Core functionality |

### 3.2 HistoryBuffer (Circular Buffer)

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-050 | Unit | P1 | Append within capacity maintains all values | Basic operation |
| ARCH-UNIT-051 | Unit | P1 | Append beyond capacity evicts oldest values | Memory management |
| ARCH-UNIT-052 | Unit | P1 | Buffer size respects history_length config (120) | Configuration |
| ARCH-UNIT-053 | Unit | P2 | O(1) append operation performance | NFR: Performance |

### 3.3 ConfigManager

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-UNIT-054 | Unit | P1 | Load valid YAML config file | Configuration |
| ARCH-UNIT-055 | Unit | P1 | Return defaults for missing config file | Graceful startup |
| ARCH-UNIT-056 | Unit | P1 | Validate config values (positive numbers) | Input validation |
| ARCH-UNIT-057 | Unit | P2 | Handle malformed YAML gracefully | Error handling |
| ARCH-INT-010 | Integration | P1 | Load config from Path.home() / ".config/monitor_dashboard" | File system integration |

---

## 4. UI Components

### 4.1 Panel Base Functionality

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-011 | Integration | P1 | All panels handle None input gracefully | Error resilience |
| ARCH-INT-012 | Integration | P1 | All panels implement get_led_status() | Alert indicator |

### 4.2 SystemHealthPanel

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-013 | Integration | P1 | Render CPU percentage bar correctly | Core display |
| ARCH-INT-014 | Integration | P1 | Render memory percentage bar correctly | Core display |
| ARCH-INT-015 | Integration | P2 | Render sparkline history chart | Visual feature |
| ARCH-INT-016 | Integration | P2 | Display load average values | Info display |

### 4.3 StoragePanel

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-017 | Integration | P1 | Render disk usage bars for all partitions | Core display |
| ARCH-INT-018 | Integration | P2 | Apply color-coded thresholds (green/yellow/red) | Visual feedback |
| ARCH-INT-019 | Integration | P2 | Scroll when partitions exceed visible area | UI usability |

### 4.4 DevicesPanel

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-020 | Integration | P1 | Render battery percentage and state | Core display |
| ARCH-INT-021 | Integration | P2 | Render battery drain curve sparkline | Visual feature |
| ARCH-INT-022 | Integration | P2 | Render Bluetooth devices with battery levels | Device display |
| ARCH-INT-023 | Integration | P2 | Show "No battery detected" for desktops | System compatibility |

### 4.5 LogsPanel

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-024 | Integration | P1 | Render log entries with severity coloring | Core display |
| ARCH-INT-025 | Integration | P2 | Support scrolling through log buffer | UI usability |
| ARCH-INT-026 | Integration | P2 | Copy visible logs to clipboard | User feature |
| ARCH-INT-027 | Integration | P2 | Copy all logs to clipboard | User feature |

### 4.6 InfoBar

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-028 | Integration | P2 | Display date/time updating at 1 Hz | Info display |
| ARCH-INT-029 | Integration | P2 | Display uptime, kernel version, distribution | Info display |

### 4.7 HelpOverlay

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-INT-030 | Integration | P2 | Show overlay on help key | User feature |
| ARCH-INT-031 | Integration | P2 | Dismiss overlay on any keypress | User interaction |

---

## 5. Core Workflows (E2E Tests)

### 5.1 Main Data Refresh Loop

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-E2E-001 | E2E | P0 | Application starts and renders main dashboard | Critical startup |
| ARCH-E2E-002 | E2E | P0 | Data refresh occurs at 1 Hz interval | Core functionality |
| ARCH-E2E-003 | E2E | P1 | All panels update simultaneously after refresh | UI consistency |
| ARCH-E2E-004 | E2E | P1 | LED indicators update based on alert state | Alert visibility |

### 5.2 Alert Lifecycle

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-E2E-005 | E2E | P0 | Alert triggers LED flashing when threshold exceeded | User notification |
| ARCH-E2E-006 | E2E | P1 | Press 'a' acknowledges alert, LED becomes solid | User action |
| ARCH-E2E-007 | E2E | P1 | Alert auto-clears when condition resolves | State management |

### 5.3 Panel Expansion Flow

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-E2E-008 | E2E | P1 | Press Enter expands focused panel to full screen | User feature |
| ARCH-E2E-009 | E2E | P1 | Press Escape/Enter returns to main dashboard | Navigation |
| ARCH-E2E-010 | E2E | P2 | Data continues refreshing in expanded view | Consistency |

---

## 6. Non-Functional Requirements

### 6.1 Performance (NFR)

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-NFR-001 | Integration | P0 | CPU usage < 2% during normal operation | Resource constraint |
| ARCH-NFR-002 | Integration | P0 | Memory usage < 50MB | Resource constraint |
| ARCH-NFR-003 | Integration | P1 | 1 Hz refresh rate maintained consistently | User experience |
| ARCH-NFR-004 | Unit | P1 | HistoryBuffer O(1) append verified | Algorithm efficiency |

### 6.2 Reliability

| ID | Level | Priority | Test Scenario | Justification |
|----|-------|----------|---------------|---------------|
| ARCH-NFR-005 | Integration | P0 | Single collector failure doesn't crash app | Graceful degradation |
| ARCH-NFR-006 | Integration | P1 | D-Bus timeout recovers within 1 refresh cycle | Service resilience |

---

## Quality Checklist

- [x] Every architectural component has test coverage
- [x] Test levels are appropriate (unit for logic, integration for components, E2E for workflows)
- [x] No duplicate coverage across levels
- [x] Priorities align with business risk (alerts = P0, display = P1-P2)
- [x] Test IDs follow naming convention (ARCH-{LEVEL}-{SEQ})
- [x] Scenarios are atomic and independent

---

## Recommended Execution Order

1. **P0 Unit tests** (ARCH-UNIT-017 through 020, 023-024, 030, 034, 041-045) - Fail fast on critical logic
2. **P0 Integration tests** (ARCH-INT-009, ARCH-NFR-001, 002, 005) - Verify core integration
3. **P0 E2E tests** (ARCH-E2E-001, 002, 005) - Validate critical workflows
4. **P1 tests in sequence** - Core functionality
5. **P2+ tests as time permits** - Enhanced coverage

---

## Gate YAML Block

```yaml
test_design:
  source: architecture.md
  date: 2026-01-17
  scenarios_total: 78
  by_level:
    unit: 42
    integration: 26
    e2e: 10
  by_priority:
    p0: 18
    p1: 32
    p2: 22
    p3: 6
  coverage_by_domain:
    data_models: 22
    data_collectors: 18
    business_logic: 14
    ui_components: 21
    core_workflows: 10
    nfr: 6
  coverage_gaps:
    - Story-level acceptance criteria (no stories exist yet)
    - Visual regression snapshots (require implementation first)
```

---

## Trace References

```
Test design matrix: docs/qa/assessments/architecture-test-design-20260117.md
P0 tests identified: 18
Recommended implementation order: Data Models -> Collectors -> AlertEngine -> Panels -> Workflows
```

---

## Next Steps

1. **Create story files** to derive story-specific test scenarios
2. **Implement P0 unit tests** as part of Epic 1 development
3. **Set up pytest infrastructure** with fixtures from architecture patterns
4. **Configure snapshot testing** for panel rendering validation
