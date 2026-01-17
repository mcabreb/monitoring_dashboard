# monitor_dashboard Product Requirements Document (PRD)

## Goals and Background Context

### Goals

- Provide real-time visibility into system health (CPU, memory, disk, load average) through an intuitive TUI interface
- Monitor laptop and Bluetooth device battery states with drain curves and time-remaining estimates
- Offer a unified view of connected devices, mounted volumes, and network status
- Enable quick access to system logs (dmesg) with severity highlighting and scrolling
- Support passive monitoring with visual alerts for critical thresholds (low battery, high CPU, low memory/disk)
- Deliver a distinctive retro GEM desktop aesthetic that is both functional and visually appealing
- Provide a foundation for future expansion (process management, utilities, screensaver mode)

### Background Context

Developers and system administrators often need quick visibility into system health without leaving the terminal. While tools like htop and btop exist, they lack unified battery monitoring for Bluetooth devices and don't offer the aesthetic customization some users desire. **monitor_dashboard** addresses this gap by combining hardware monitoring, device battery tracking, and system logs into a single TUI application with a distinctive GEM desktop retro aesthetic.

The project is a spare-time, free tool designed for personal use on Ubuntu/GNOME systems. It prioritizes ease of maintenance and incremental upgrades, using Python with the textual TUI library. The MVP focuses on core monitoring (System Health, Storage, Devices panels), with subsequent waves adding process management, alerts, utilities, and optional GNOME screensaver integration.

### Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-01-16 | 0.1 | Initial PRD draft based on brainstorming session | John (PM) |
| 2026-01-16 | 1.0 | Complete PRD with all epics, stories, and checklist validation | John (PM) |

---

## Requirements

### Functional

- **FR1:** The application shall display CPU usage as a bar chart with historical data (scrollable timeline)
- **FR2:** The application shall display memory usage as a percentage bar with historical data
- **FR3:** The application shall display system load average (1, 5, 15 minute)
- **FR4:** The application shall display disk usage as percentage bars for all mounted partitions
- **FR5:** The application shall list all mounted volumes with mount points and available space
- **FR6:** The application shall display laptop battery status including percentage, charging state, and time remaining estimate
- **FR7:** The application shall display connected Bluetooth devices with battery percentage where available
- **FR8:** The application shall show a battery drain curve visualization for laptop battery
- **FR9:** The application shall highlight/notify when a Bluetooth device disconnects
- **FR10:** The application shall display the latest 30 lines of dmesg output, scrollable to 100 lines
- **FR11:** The application shall color-code log entries by severity level (error, warning, info)
- **FR12:** The application shall support copying log content to clipboard
- **FR13:** The application shall use a fixed tmux-style pane layout with bordered windows
- **FR14:** The application shall support Tab key to cycle between panels
- **FR15:** The application shall support Enter key to expand a panel to full-screen and return
- **FR16:** The application shall display a help popup when ? key is pressed
- **FR17:** The application shall refresh all data at 1 Hz (1 update per second)
- **FR18:** The application shall display visual alerts (flashing, color change) when thresholds are exceeded
- **FR19:** The application shall persist alerts until user acknowledges them via keypress
- **FR20:** The application shall display system info: date/time, uptime, kernel version, distro

### Non-Functional

- **NFR1:** The application shall be implemented in Python using the textual TUI library
- **NFR2:** The application shall use psutil for system metrics collection
- **NFR3:** The application shall use UPower/D-Bus for battery and Bluetooth device information
- **NFR4:** The application shall store user configuration in `~/.config/monitor_dashboard/config.yaml`
- **NFR5:** The application shall maintain responsive UI with <100ms input latency
- **NFR6:** The application shall consume minimal system resources (<2% CPU, <50MB RAM during normal operation)
- **NFR7:** The application shall gracefully handle missing Bluetooth hardware (show empty devices panel)
- **NFR8:** The application shall be designed for easy maintenance and incremental upgrades
- **NFR9:** The application shall follow a GEM desktop retro aesthetic with server rack LED indicators
- **NFR10:** The application shall support arrow key navigation in modeless interaction style
- **NFR11:** The application shall target Ubuntu/GNOME as the primary platform
- **NFR12:** The application shall be free and open source

---

## User Interface Design Goals

### Overall UX Vision

A clean, information-dense TUI dashboard that evokes the elegance of the 1980s GEM desktop environment while providing modern system monitoring capabilities. The interface prioritizes **glanceability** - users should be able to assess system health in under 2 seconds. The aesthetic combines GEM's bordered windows and clean typography with server rack-style LED status indicators for instant visual feedback.

The experience should feel like a well-organized control panel: calm during normal operation, but immediately attention-grabbing when something requires action.

### Key Interaction Paradigms

- **Modeless navigation:** No vim-style modes; all keys work the same regardless of context
- **Panel-centric layout:** Fixed tmux-style panes, each dedicated to a monitoring domain
- **Focus cycling:** Tab moves focus between panels; visual indicator shows active panel
- **Drill-down on demand:** Enter expands focused panel to full-screen; Enter/Escape returns
- **Contextual help:** ? key triggers help overlay showing all available keys
- **Alert acknowledgment:** Keypress dismisses persistent alerts
- **Passive-first:** Dashboard is primarily for observation; actions are secondary

### Core Screens and Views

1. **Main Dashboard** (default view)
   - System Health panel (CPU chart, memory bar, load average)
   - Storage panel (disk bars, mounted volumes)
   - Devices panel (Bluetooth devices, laptop battery with drain curve)
   - Logs panel (dmesg with severity colors)
   - Info bar (date/time, uptime, kernel, distro)

2. **Expanded Panel View** (Enter on any panel)
   - Full-screen view of single panel with additional detail
   - More historical data visible for charts
   - More log lines visible for Logs panel

3. **Help Overlay** (? key)
   - Translucent overlay showing all keyboard shortcuts
   - Dismisses on any keypress

### Accessibility: None

No specific accessibility requirements for MVP. This is a personal tool with known user (the developer). Future consideration: high-contrast theme option.

### Branding

**GEM Desktop + Server Rack hybrid aesthetic:**

- **Reference:** See `images/gem/` for visual examples
- **Window style:** Clean bordered windows with title bars, drop shadows
- **Color palette:** Monochrome base (black, white, grays) with limited accent colors (green for OK, yellow for warning, red for critical)
- **Typography:** Clean monospace font, sharp pixel appearance
- **Status indicators:** Server rack-style LED dots (● green, ● yellow, ● red) for at-a-glance health
- **Animations:** Flashing effect for active alerts (1-2 Hz blink)
- **Overall feel:** Professional, retro, functional - like a well-maintained server room

### Target Devices and Platforms: Desktop Only

- **Primary:** Linux terminal (Ubuntu/GNOME)
- **Terminal requirements:** 256-color support, Unicode box-drawing characters
- **Minimum size:** 80x24 characters (standard terminal)
- **Recommended:** 120x40+ for optimal data density
- **No responsive layout:** Fixed panel positions regardless of terminal size

---

## Technical Assumptions

### Repository Structure: Monorepo

Single repository containing all project code. This is a simple, single-application project with no need for polyrepo complexity.

```
monitor_dashboard/
├── src/
│   └── monitor_dashboard/
│       ├── __init__.py
│       ├── app.py              # Main textual application
│       ├── panels/             # Panel widgets
│       ├── data_sources/       # System data collectors
│       └── config.py           # Configuration handling
├── tests/
├── images/gem/                 # Visual reference images
├── docs/
├── pyproject.toml
└── README.md
```

### Service Architecture: Monolith

Single Python application with no microservices or serverless components. The application runs as a standalone TUI process.

**Components (internal modules, not separate services):**
- **App Layer:** Textual application, screen management, key handling
- **Panel Widgets:** Reusable UI components for each monitoring domain
- **Data Sources:** Collectors for system metrics (psutil, UPower D-Bus)
- **Config Manager:** YAML config loading and validation

### Testing Requirements: Unit + Integration

| Type | Scope | Tools |
|------|-------|-------|
| **Unit** | Data source collectors, config parsing, utility functions | pytest |
| **Integration** | Panel rendering, data flow from collectors to UI | pytest + textual testing utilities |
| **Manual** | Visual appearance, keyboard navigation, alert behavior | Human verification against GEM reference |

**Notes:**
- No E2E browser testing needed (TUI application)
- Visual/aesthetic testing requires human judgment against `images/gem/` reference
- Consider snapshot testing for panel layouts if textual supports it

### Additional Technical Assumptions and Requests

- **Python version:** 3.10+ (for modern typing and match statements)
- **Package manager:** pip with pyproject.toml (PEP 517/518 compliant)
- **Key dependencies:**
  - `textual` - TUI framework
  - `psutil` - System metrics (CPU, memory, disk, processes)
  - `pydbus` or `dbus-python` - D-Bus access for UPower
  - `pyyaml` - Configuration file parsing
  - `pyperclip` - Clipboard integration for log copying
- **Development dependencies:**
  - `pytest` - Testing
  - `black` - Code formatting
  - `ruff` - Linting
  - `mypy` - Type checking
- **No external services:** All data sourced locally from system APIs
- **No database:** State is ephemeral; config is file-based YAML
- **Graceful degradation:** If Bluetooth/UPower unavailable, show informative message in Devices panel rather than crashing
- **Logging:** Use Python's logging module for debug output; do not display app logs in the dashboard itself

---

## Epic List

| Epic | Title | Goal |
|------|-------|------|
| **Epic 1** | Foundation & System Health | Establish project infrastructure (textual app, layout, navigation) and deliver core system health monitoring (CPU, memory, load average) |
| **Epic 2** | Storage & Devices | Add storage monitoring (disk usage, mounted volumes) and device tracking (Bluetooth devices, laptop battery with drain curve) |
| **Epic 3** | Logs, Info & Alerts | Complete the dashboard with system logs (dmesg), info bar, and visual alert system for critical thresholds |

**Future Epics (Post-MVP):**

| Epic | Title | Goal |
|------|-------|------|
| **Epic 4** | Process Management | Add process list panel with sorting and kill capability |
| **Epic 5** | Network & Services | Add network monitoring panel and user-configurable services watchlist |
| **Epic 6** | Utilities & Screensaver | Add system utilities (toggles, IP info) and GNOME screensaver integration |

---

## Epic 1: Foundation & System Health

**Goal:** Establish the project infrastructure with a working textual TUI application, implement the fixed panel layout with keyboard navigation, and deliver the first functional panel displaying real-time CPU usage, memory usage, and load average. After this epic, the user can launch the app, see live system health data, navigate between panels, and access help.

---

### Story 1.1: Project Setup & Minimal App

**As a** developer,
**I want** a properly structured Python project with all dependencies configured,
**so that** I can start building the monitoring dashboard with a solid foundation.

**Acceptance Criteria:**

1. Project has `pyproject.toml` with metadata, dependencies (textual, psutil, pyyaml), and dev dependencies (pytest, black, ruff, mypy)
2. Source code is organized under `src/monitor_dashboard/` with `__init__.py` and `app.py`
3. Running `python -m monitor_dashboard` launches a minimal textual app displaying "monitor_dashboard" in a bordered container
4. Project includes `.gitignore` appropriate for Python projects
5. Basic `README.md` exists with project name and run instructions

---

### Story 1.2: Panel Layout Structure

**As a** user,
**I want** to see a fixed multi-panel layout when I launch the app,
**so that** I have dedicated areas for different monitoring categories.

**Acceptance Criteria:**

1. App displays a fixed layout with 5 panel areas: System Health, Storage, Devices, Logs, and Info bar
2. Each panel has a visible border with a title label (GEM-style bordered windows)
3. Panels contain placeholder text indicating their purpose (e.g., "System Health - Coming Soon")
4. Layout is fixed and does not reflow when terminal is resized
5. Panels are visually distinct with the GEM aesthetic (clean borders, monochrome base)

---

### Story 1.3: Keyboard Navigation

**As a** user,
**I want** to navigate between panels using keyboard shortcuts,
**so that** I can focus on different monitoring areas without using a mouse.

**Acceptance Criteria:**

1. Tab key cycles focus forward through panels (System Health → Storage → Devices → Logs → back to System Health)
2. Shift+Tab cycles focus backward through panels
3. Currently focused panel has a visual indicator (highlighted border or different color)
4. Arrow keys work within focused panel (preparation for scrollable content)
5. Navigation is modeless - keys work the same regardless of current state

---

### Story 1.4: Help Overlay

**As a** user,
**I want** to press ? to see all available keyboard shortcuts,
**so that** I can learn how to use the dashboard effectively.

**Acceptance Criteria:**

1. Pressing ? displays a centered overlay/modal showing all keyboard shortcuts
2. Overlay lists: Tab (next panel), Shift+Tab (prev panel), Enter (expand), Escape (back), ? (help), q (quit)
3. Overlay has GEM-style bordered appearance
4. Pressing any key dismisses the overlay and returns to dashboard
5. Overlay is semi-transparent or clearly overlaid on the dashboard content

---

### Story 1.5: System Health Data Collection

**As a** developer,
**I want** a data collection module that gathers CPU, memory, and load average metrics,
**so that** the System Health panel can display real system data.

**Acceptance Criteria:**

1. `data_sources/system_health.py` module exists with functions to collect metrics
2. CPU percentage is collected using `psutil.cpu_percent()` with per-CPU breakdown available
3. Memory usage is collected using `psutil.virtual_memory()` returning used/total/percent
4. Load average is collected using `psutil.getloadavg()` returning 1/5/15 minute values
5. Module includes unit tests verifying data collection returns expected types
6. Collection is designed to be called at 1Hz without blocking the UI

---

### Story 1.6: System Health Panel Display

**As a** user,
**I want** to see real-time CPU usage, memory usage, and load average in the System Health panel,
**so that** I can monitor my system's performance at a glance.

**Acceptance Criteria:**

1. System Health panel displays CPU usage as a horizontal bar chart (percentage filled)
2. CPU history is shown as a simple rolling chart (last 60 seconds of data points)
3. Memory usage is displayed as a percentage bar with used/total values (e.g., "4.2 GB / 16 GB (26%)")
4. Load average displays 1, 5, and 15 minute values with labels
5. All values update at 1 Hz (1 refresh per second)
6. Panel includes LED-style status indicator (green if healthy, yellow/red if thresholds exceeded for future alerts)

---

### Story 1.7: Panel Expansion

**As a** user,
**I want** to expand a panel to full-screen for more detail,
**so that** I can see more information when needed.

**Acceptance Criteria:**

1. Pressing Enter on a focused panel expands it to fill the entire screen
2. Expanded view shows the same content but with more space (longer history charts, more detail)
3. Pressing Escape or Enter again returns to the normal multi-panel view
4. Focus remains on the same panel after returning from expanded view
5. Other panels are hidden during expansion, not just overlaid

---

## Epic 2: Storage & Devices

**Goal:** Extend the dashboard with storage monitoring (disk usage for all partitions, mounted volumes list) and device tracking (connected Bluetooth devices with battery status, laptop battery with drain curve and time remaining). After this epic, users can monitor all their storage and connected devices alongside system health.

---

### Story 2.1: Storage Data Collection

**As a** developer,
**I want** a data collection module that gathers disk and mount point information,
**so that** the Storage panel can display real storage data.

**Acceptance Criteria:**

1. `data_sources/storage.py` module exists with functions to collect storage metrics
2. Disk partitions are enumerated using `psutil.disk_partitions()` filtering relevant mount points
3. Disk usage (total, used, free, percent) is collected for each partition using `psutil.disk_usage()`
4. Module returns a list of disk objects with mount point, device, filesystem type, and usage stats
5. Module includes unit tests verifying data collection returns expected structure
6. Collection handles unmounted/inaccessible partitions gracefully (skip with warning, don't crash)

---

### Story 2.2: Storage Panel Display

**As a** user,
**I want** to see disk usage for all partitions and mounted volumes in the Storage panel,
**so that** I can monitor available space across my system.

**Acceptance Criteria:**

1. Storage panel displays a percentage bar for each mounted partition
2. Each bar shows: mount point, used/total space, percentage (e.g., "/home - 120 GB / 500 GB (24%)")
3. Bars use color coding: green (<70%), yellow (70-90%), red (>90%)
4. Partitions are sorted by mount point (/ first, then alphabetically)
5. Panel scrolls if there are more partitions than fit in the panel height
6. LED status indicator shows worst-case status (red if any disk >90%)

---

### Story 2.3: Laptop Battery Data Collection

**As a** developer,
**I want** a data collection module that retrieves laptop battery status via UPower,
**so that** the Devices panel can display battery information.

**Acceptance Criteria:**

1. `data_sources/devices.py` module exists with functions to collect battery/device metrics
2. Laptop battery status is retrieved via UPower D-Bus interface (or psutil.sensors_battery() as fallback)
3. Collected data includes: percentage, charging state (charging/discharging/full), time remaining estimate
4. Module maintains a history buffer of battery percentages for drain curve (last 60 data points)
5. Module handles systems without battery gracefully (returns None, doesn't crash)
6. Module includes unit tests with mocked D-Bus responses

---

### Story 2.4: Bluetooth Device Data Collection

**As a** developer,
**I want** to retrieve connected Bluetooth devices and their battery levels,
**so that** the Devices panel can display Bluetooth device status.

**Acceptance Criteria:**

1. Connected Bluetooth devices are enumerated via UPower D-Bus interface
2. For each device: name, type (headphones, mouse, keyboard, etc.), battery percentage if available
3. Module detects device connection/disconnection events (for notification in Epic 3)
4. Module handles systems without Bluetooth gracefully (returns empty list, doesn't crash)
5. Module handles devices without battery reporting (show device, indicate "N/A" for battery)
6. Collection refreshes at 1Hz without blocking the UI

---

### Story 2.5: Devices Panel Display

**As a** user,
**I want** to see laptop battery status and connected Bluetooth devices in the Devices panel,
**so that** I can monitor battery levels across all my devices.

**Acceptance Criteria:**

1. Laptop battery section shows: percentage bar, charging state icon, time remaining estimate
2. Laptop battery includes a drain curve visualization (simple line chart of last 60 readings)
3. Bluetooth devices section lists each device with: name, type icon, battery percentage bar
4. Devices without battery show "Battery: N/A" instead of a bar
5. Panel shows "No Bluetooth devices connected" when list is empty
6. Panel shows "No battery detected" if running on desktop without battery
7. LED status indicator reflects worst battery status (laptop or any BT device <20%)

---

### Story 2.6: Memory History Graph

**As a** user,
**I want** to see memory usage history similar to CPU history,
**so that** I can track memory trends over time (useful for detecting leaks).

**Acceptance Criteria:**

1. System Health panel includes memory history graph alongside CPU history
2. Memory history shows last 60 seconds of data points as a rolling line chart
3. Graph uses same visual style as CPU history for consistency
4. History data is maintained in memory buffer, collected at 1Hz
5. Expanded view shows longer history (more data points visible)

---

## Epic 3: Logs, Info & Alerts

**Goal:** Complete the MVP dashboard with system logs (dmesg output with severity highlighting and clipboard support), an info bar (date/time, uptime, kernel, distro), and a visual alert system that flashes and persists until acknowledged. After this epic, the dashboard is fully functional for passive monitoring with proactive alerting.

---

### Story 3.1: System Logs Data Collection

**As a** developer,
**I want** a data collection module that retrieves dmesg output,
**so that** the Logs panel can display system log entries.

**Acceptance Criteria:**

1. `data_sources/logs.py` module exists with functions to collect log data
2. Module retrieves dmesg output via subprocess call (`dmesg --time-format iso`)
3. Each log entry is parsed into: timestamp, severity level, message
4. Severity detection identifies: emergency, alert, critical, error, warning, notice, info, debug
5. Module returns the last 100 entries (configurable buffer size)
6. Module handles dmesg permission issues gracefully (may require running with appropriate permissions)
7. Module includes unit tests with sample dmesg output

---

### Story 3.2: Logs Panel Display

**As a** user,
**I want** to see recent system logs with severity highlighting in the Logs panel,
**so that** I can quickly spot errors and warnings.

**Acceptance Criteria:**

1. Logs panel displays the 30 most recent dmesg entries
2. Each entry shows: timestamp (HH:MM:SS), severity indicator, message (truncated if needed)
3. Entries are color-coded by severity: red (error/critical), yellow (warning), white (info/notice), gray (debug)
4. Panel supports scrolling with arrow keys to view up to 100 entries
5. New entries appear at the bottom, auto-scrolling if at the end of the list
6. Expanded view shows full messages without truncation
7. LED status indicator turns red if any error-level entries appear in visible range

---

### Story 3.3: Clipboard Copy for Logs

**As a** user,
**I want** to copy log entries to the clipboard,
**so that** I can paste them elsewhere for sharing or further analysis.

**Acceptance Criteria:**

1. Pressing 'c' when Logs panel is focused copies visible log entries to clipboard
2. Pressing 'C' (shift+c) copies all buffered entries (up to 100) to clipboard
3. Copied text includes timestamps and full messages (not truncated)
4. Visual feedback confirms copy action (brief flash or status message)
5. Clipboard integration uses pyperclip library
6. Graceful handling if clipboard is unavailable (show error message, don't crash)

---

### Story 3.4: System Info Data Collection

**As a** developer,
**I want** a data collection module that retrieves system information,
**so that** the Info bar can display system details.

**Acceptance Criteria:**

1. `data_sources/system_info.py` module exists with functions to collect system info
2. Current date/time is retrieved using Python datetime
3. System uptime is retrieved via `psutil.boot_time()` and calculated
4. Kernel version is retrieved from `platform.release()`
5. Distribution info is retrieved from `platform.freedesktop_os_release()` or `/etc/os-release`
6. Module includes unit tests verifying data collection returns expected types

---

### Story 3.5: Info Bar Display

**As a** user,
**I want** to see date/time, uptime, kernel version, and distro in an info bar,
**so that** I have essential system context always visible.

**Acceptance Criteria:**

1. Info bar is displayed at the bottom or top of the dashboard (always visible, not a panel)
2. Shows current date and time, updating every second (e.g., "2026-01-16 14:32:15")
3. Shows uptime in human-readable format (e.g., "Up: 3d 14h 22m")
4. Shows kernel version (e.g., "Kernel: 6.14.0-37-generic")
5. Shows distribution name and version (e.g., "Ubuntu 24.04")
6. Info bar uses subtle styling to not distract from main panels

---

### Story 3.6: Alert Threshold Engine

**As a** developer,
**I want** an alert engine that monitors metrics and triggers alerts when thresholds are exceeded,
**so that** the UI can display visual warnings.

**Acceptance Criteria:**

1. `alerts/engine.py` module exists with threshold monitoring logic
2. Hardcoded thresholds: battery <20%, CPU >80%, memory <10% free, disk <10% free
3. Engine checks all metrics on each refresh cycle (1Hz)
4. Engine maintains alert state: active alerts list with type, message, timestamp
5. Alerts are added when threshold crossed, remain until acknowledged
6. Engine provides API for UI to query active alerts and acknowledge them
7. Module includes unit tests with edge cases (exactly at threshold, recovery, etc.)

---

### Story 3.7: Visual Alert Display

**As a** user,
**I want** flashing visual alerts when critical thresholds are exceeded,
**so that** problems catch my attention even during passive monitoring.

**Acceptance Criteria:**

1. Active alerts trigger flashing effect on affected panel's LED indicator (1-2 Hz blink)
2. Alert notification appears in a dedicated area or overlay showing alert message
3. Multiple simultaneous alerts are all displayed (not just the first one)
4. Flashing continues until alert is acknowledged
5. Pressing 'a' acknowledges and dismisses all active alerts
6. Pressing 'A' acknowledges alerts one by one (cycles through)
7. Acknowledged alerts don't re-trigger immediately (cooldown period or hysteresis)

---

### Story 3.8: Bluetooth Disconnect Notification

**As a** user,
**I want** to be notified when a Bluetooth device disconnects,
**so that** I'm aware if my headphones or other devices lose connection.

**Acceptance Criteria:**

1. When a previously connected Bluetooth device disconnects, an alert is triggered
2. Alert message identifies the device (e.g., "Disconnected: Sony WH-1000XM4")
3. Devices panel shows disconnected device with "Disconnected" status briefly before removal
4. Alert follows same acknowledgment pattern as threshold alerts
5. Reconnection clears the disconnect alert automatically

---

## Out of Scope (MVP)

The following features are explicitly excluded from MVP and planned for future epics:

- Process list panel with kill functionality (Epic 4)
- Network monitoring panel (Epic 5)
- User-configurable services watchlist (Epic 5)
- System utilities - WiFi/Bluetooth toggles, IP info display (Epic 6)
- GNOME screensaver integration (Epic 6)
- Configurable alert thresholds (thresholds are hardcoded in MVP)
- Responsive/adaptive layout for different terminal sizes
- Remote machine monitoring
- Configuration UI (config is file-based only)

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard launch time | < 1 second |
| Panel refresh latency | < 100ms |
| Glanceability | User can assess system health in < 2 seconds |
| Memory footprint | < 50 MB RAM |
| CPU overhead | < 2% during normal operation |
| Alert visibility | Critical alerts noticed within 2 seconds |

---

## Checklist Results Report

**Validation Date:** 2026-01-16
**Overall Completeness:** 88%
**MVP Scope:** Just Right
**Architecture Readiness:** READY

### Category Statuses

| Category | Status | Notes |
|----------|--------|-------|
| Problem Definition & Context | PARTIAL | Clear problem; no formal KPIs |
| MVP Scope Definition | PASS | Well-defined boundaries |
| User Experience Requirements | PASS | Complete UI vision |
| Functional Requirements | PASS | 20 testable FRs |
| Non-Functional Requirements | PARTIAL | Minimal security (appropriate) |
| Epic & Story Structure | PASS | 21 well-sequenced stories |
| Technical Guidance | PASS | Clear stack and direction |
| Cross-Functional Requirements | PARTIAL | No external integrations |
| Clarity & Communication | PASS | Well-organized document |

### Identified Risks

1. **D-Bus/UPower integration** - May have edge cases on different Linux distributions
2. **dmesg permissions** - May require running with elevated permissions or adding user to appropriate group
3. **Clipboard in terminal** - pyperclip may have limitations in some terminal emulators

### Final Decision

**READY FOR ARCHITECT** - PRD is comprehensive and ready for architectural design.

---

## Next Steps

### UX Expert Prompt

> Review the PRD at `docs/prd.md` for monitor_dashboard. Focus on the User Interface Design Goals section and the GEM desktop aesthetic references in `images/gem/`. Create detailed wireframes or mockups for the main dashboard layout showing all 5 panels (System Health, Storage, Devices, Logs, Info bar) with the GEM retro aesthetic. Consider the panel expansion view and help overlay.

### Architect Prompt

> Review the PRD at `docs/prd.md` for monitor_dashboard. Create the technical architecture document covering: (1) Module structure for the textual application, (2) Data flow from psutil/UPower collectors to UI panels, (3) Alert engine design, (4) Configuration system design, and (5) Testing strategy. Reference the Technical Assumptions section for stack decisions.
