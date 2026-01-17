# Brainstorming Session Results

**Session Date:** 2026-01-16
**Facilitator:** Business Analyst Mary
**Project:** monitor_dashboard

---

## Executive Summary

**Topic:** TUI-based Global System Monitoring Dashboard

**Session Goals:** Broad exploration of features for a terminal-based system monitoring tool with retro GEM-style visuals, covering hardware stats, connected devices, logs, utilities, and actionable commands.

**Techniques Used:**
- Mind Mapping (feature discovery and organization)
- Role Playing (developer, sysadmin, casual user perspectives)
- What If Scenarios (edge cases and alerts)
- Analogical Thinking (inspiration from tmux, server racks)
- SCAMPER (refinement and consolidation)

**Total Ideas Generated:** 50+

**Key Themes Identified:**
- Hardware and system health monitoring as core priority
- Visual feedback through retro GEM aesthetic + server rack LEDs
- Actionable utilities beyond passive monitoring
- Alert system for critical thresholds
- Clean, fixed-layout tmux-style panes

---

## Technique Sessions

### Mind Mapping

**Description:** Started with central concept and built out main branches to organize the feature space.

**Ideas Generated:**
1. Hardware Stats panel (CPU, Memory, Disk, Bluetooth devices)
2. System Logs panel (dmesg, scrollable, color-coded)
3. Network panel (usage, WiFi status, sparklines)
4. Help/Keys system (? popup, arrow navigation, modeless)
5. Utilities/Commands (kill process, restart service, toggles)
6. UI/Visuals (GEM retro style, bar charts, percentage bars, drain curves)
7. Info/Status panel (date/time, uptime, kernel, distro)

**Insights Discovered:**
- Seven main feature branches emerged naturally
- User wants both passive monitoring AND active utilities
- Visual style (GEM retro) is important to the experience

**Notable Connections:**
- Battery monitoring spans both laptop AND Bluetooth devices
- TUI graphics serve both function (data viz) and aesthetics (retro style)

---

### Role Playing

**Description:** Explored features from different user perspectives - developer debugging, sysadmin post-reboot, casual daily use.

**Ideas Generated:**
1. Process list panel (top 20 processes, sortable by CPU/MEM/PID/Name)
2. Memory history graph (like CPU, to trace leaks over time)
3. Services watchlist (user-configurable in config file)
4. Network connectivity check (verify connection works)
5. Mounted disks display (see all volumes)
6. Load average display (quick health pulse)
7. Visual alerts with color highlighting (low battery, high CPU, low mem/disk)

**Insights Discovered:**
- Developer scenario revealed need for process management and memory history
- Sysadmin scenario revealed need for service monitoring and connectivity checks
- Casual use scenario revealed need for passive alerts that catch attention

**Notable Connections:**
- Memory history graph parallels CPU history - consistent pattern
- Alerts are essential for passive monitoring use case

---

### What If Scenarios

**Description:** Explored edge cases and unexpected situations to uncover additional features.

**Ideas Generated:**
1. Battery time remaining estimate (critical when low)
2. Bluetooth device disconnect notification (highlight when lost)
3. Sticky alerts that persist until acknowledged (don't miss warnings)

**Insights Discovered:**
- User prefers manual control (no auto-start, no responsive layout)
- Alerts need to persist - can't rely on user watching constantly
- Remote access and sharing features not important for this use case

**Notable Connections:**
- Acknowledgment pattern for alerts prevents alert fatigue while ensuring nothing is missed

---

### Analogical Thinking

**Description:** Drew inspiration from other TUI tools and interfaces.

**Ideas Generated:**
1. Tmux-style window panes for layout
2. Rich color palette throughout
3. Fixed layout (predictable, consistent)
4. Tab to cycle between panels
5. Enter to expand panel full-screen, back to return
6. 1 Hz refresh rate (1 update per second)

**Insights Discovered:**
- Tmux mental model is familiar and works well for multi-panel TUI
- Fixed layout preferred over flexibility - reduces cognitive load
- 1 Hz refresh balances responsiveness with resource usage

**Notable Connections:**
- GEM aesthetic + tmux panes = bordered windows naturally

---

### SCAMPER Refinement

**Description:** Systematically refined the feature set through Substitute, Combine, Adapt, Modify, Put to other uses, Eliminate, Reverse.

**Ideas Generated:**
1. Combined panels into focused groups (System Health, Network, Storage, Devices)
2. Server rack aesthetic (LED status indicators: green/yellow/red)
3. Flashing animation for active alerts
4. GNOME screensaver mode (retro TUI as idle screen)

**Insights Discovered:**
- Combining related metrics reduces panel count and improves focus
- Server rack + GEM aesthetics complement each other
- No features eliminated - all earned their place

**Notable Connections:**
- Server rack LEDs provide at-a-glance health alongside detailed metrics

---

## Idea Categorization

### Immediate Opportunities
*Ideas ready to implement now - MVP Wave 1*

1. **System Health Panel**
   - Description: CPU bar chart with history, Memory percentage bar with history, Load average
   - Why immediate: Core monitoring functionality, foundation of the tool
   - Resources needed: System APIs for CPU/mem/load stats, TUI charting library

2. **Storage Panel**
   - Description: Disk usage percentage bars, Mounted volumes list
   - Why immediate: Essential system info, straightforward to implement
   - Resources needed: Filesystem APIs, mount point enumeration

3. **Devices Panel**
   - Description: Bluetooth connected devices, Battery states with drain curve, Time remaining estimate
   - Why immediate: Key differentiator (BT battery monitoring), user priority
   - Resources needed: Bluetooth APIs, battery/power management APIs

### Future Innovations
*Ideas requiring development/research - Wave 2 & 3*

1. **Processes Panel**
   - Description: Top 20 processes, sortable by CPU/MEM/PID/Name, kill action
   - Development needed: Process enumeration, sorting logic, signal handling
   - Timeline: Wave 2

2. **Logs Panel**
   - Description: dmesg output, 30 lines visible (scroll to 100), color by severity, copy to clipboard
   - Development needed: dmesg parsing, severity detection, clipboard integration
   - Timeline: Wave 2

3. **Network Panel**
   - Description: Usage sparklines, WiFi status, connectivity check
   - Development needed: Network stats APIs, WiFi status detection, ping/connectivity test
   - Timeline: Wave 2

4. **Alerts System**
   - Description: Thresholds (battery <20%, CPU >80%, mem <10%, disk <10%), flashing, sticky until ack
   - Development needed: Threshold monitoring, alert state management, flash animation
   - Timeline: Wave 3

5. **Info Panel**
   - Description: Date/time, uptime, kernel version, distro info
   - Development needed: System info APIs, formatting
   - Timeline: Wave 3

6. **Services Watchlist**
   - Description: User-configurable service list, status indicators (running/stopped/failed)
   - Development needed: Config file parsing, systemd integration
   - Timeline: Wave 3

### Moonshots
*Ambitious, transformative concepts - Wave 4*

1. **Utilities/Actions**
   - Description: Kill process, restart service, show IP/hostname, WiFi toggle, Bluetooth toggle
   - Transformative potential: Turns passive monitor into active system control center
   - Challenges to overcome: Permissions, safe execution, confirmation dialogs

2. **UI Polish (GEM + Server Rack)**
   - Description: Full GEM retro aesthetic, bordered windows, dithered patterns, LED status lights
   - Transformative potential: Unique visual identity, delightful user experience
   - Challenges to overcome: TUI rendering complexity, consistent style across panels

3. **GNOME Screensaver Mode**
   - Description: Run as GNOME screensaver showing system stats on idle/lock screen
   - Transformative potential: Always-visible system status, retro aesthetic showcase
   - Challenges to overcome: GNOME screensaver integration, security considerations

### Insights & Learnings
*Key realizations from the session*

- **Passive + Active balance**: Dashboard should support both watching (monitoring) and doing (utilities)
- **Alert persistence matters**: Sticky alerts until acknowledged prevents missing critical warnings
- **Visual style is functional**: GEM aesthetic + server rack LEDs serve UX purpose, not just decoration
- **Fixed layout wins**: Predictable panel positions reduce cognitive load for quick glances
- **User-configurable services**: Avoid guessing what matters - let user define their watchlist

---

## Action Planning

### Top 3 Priority Ideas

**#1 Priority: System Health Panel**
- Rationale: Core functionality that defines the tool's purpose
- Next steps: Set up textual app skeleton, implement CPU/mem/load data collection with psutil
- Resources needed: Python textual, psutil, plotext (for TUI charts)
- Timeline: Wave 1 MVP

**#2 Priority: Storage Panel**
- Rationale: Essential system info, complements System Health
- Next steps: Use psutil.disk_partitions() and disk_usage() for enumeration
- Resources needed: psutil (already needed for #1)
- Timeline: Wave 1 MVP

**#3 Priority: Devices Panel**
- Rationale: Unique feature (BT battery monitoring), high user interest
- Next steps: Research UPower D-Bus API for battery info, use pydbus for integration
- Resources needed: pydbus or dbus-python, UPower
- Timeline: Wave 1 MVP

---

## Technical Specifications

### Language & Framework
- **Language:** Python
- **TUI Library:** textual (recommended) or rich/urwid
- **Config:** YAML config file at `~/.config/monitor_dashboard/config.yaml`

### UI/Layout
- Tmux-style fixed panes
- GEM retro aesthetic with bordered windows (see `images/gem/` for reference)
  - Clean bordered windows with title bars
  - Monochrome base with limited color accents (black, white, green)
  - Sharp pixel graphics, clean lines
  - Drop shadows on window borders
  - Simple geometric icons
- Server rack LED indicators (green/yellow/red)
- 1 Hz refresh rate

### Navigation
- Arrow keys for navigation
- Tab to cycle between panels
- Enter to expand panel full-screen
- ? to show help popup
- Modeless interaction (no vim modes)

### Alerts
- Hardcoded thresholds: Battery <20%, CPU >80%, Memory <10%, Disk <10%
- Flashing animation when triggered
- Persist until user acknowledges

### Data Display
- CPU: Bar chart with history
- Memory: Percentage bar with history
- Disk: Percentage bars
- Battery: Drain curve with time remaining
- Network: Sparklines
- Logs: 30 lines visible, scroll to 100, color by severity

### Configuration
- **Config file:** `~/.config/monitor_dashboard/config.yaml`
- **Configurable settings:**
  - Services watchlist (list of services to monitor)
  - Future: panel layout customization
  - Future: color theme adjustments
  - Future: alert thresholds

---

## Implementation Roadmap

| Wave | Panels/Features | Focus |
|------|-----------------|-------|
| **Wave 1 (MVP)** | System Health, Storage, Devices | Core monitoring |
| **Wave 2** | Processes, Logs, Network | Extended monitoring |
| **Wave 3** | Alerts, Info, Services | Awareness & status |
| **Wave 4** | Utilities, UI polish, Screensaver | Actions & delight |

---

## Reflection & Follow-up

### What Worked Well
- Mind mapping established clear feature categories quickly
- Role playing uncovered practical features (process list, memory history) that weren't initially considered
- SCAMPER consolidation reduced complexity by combining related panels
- User had clear vision which made prioritization straightforward

### Areas for Further Exploration
- **TUI library:** textual (Python) - modern, async, CSS-like styling
- **System stats:** psutil library for CPU, memory, disk, processes
- **Bluetooth battery:** UPower/D-Bus integration via pydbus or dbus-python
- **GEM aesthetic:** Reference images in `images/gem/` for visual implementation

### Recommended Follow-up Techniques
- Prototyping: Create a minimal visual mockup of the layout before coding
- Technical spike: Test TUI library capabilities for charts and styling

### Questions That Emerged
- ~~What programming language will this be built in?~~ **DECIDED: Python**
- ~~Should there be a config file for layout customization in the future?~~ **DECIDED: Yes, config file for future customization**
- How to handle systems without Bluetooth (graceful degradation)?

### Next Session Planning
- **Suggested topics:** Project brief creation, architecture design, UI mockups
- **Recommended timeframe:** Before starting implementation
- **Preparation needed:** Review GEM reference images in `images/gem/`, explore textual library examples

---

*Session facilitated using the BMAD-METHOD brainstorming framework*
