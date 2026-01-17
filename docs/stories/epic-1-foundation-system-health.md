# Epic 1: Foundation & System Health

## Epic Overview

| Field | Value |
|-------|-------|
| Epic ID | 1 |
| Title | Foundation & System Health |
| Status | Ready |
| Stories | 7 (1.1 - 1.7) |
| Priority | MVP - Must Have |

## Goal

Establish the project infrastructure with a working textual TUI application, implement the fixed panel layout with keyboard navigation, and deliver the first functional panel displaying real-time CPU usage, memory usage, and load average. After this epic, the user can launch the app, see live system health data, navigate between panels, and access help.

## Dependencies

- None (this is the foundation epic)

## Technical Context

**Key Technologies:**
- Python 3.10+
- textual 0.47.1 (TUI framework)
- psutil 5.9.8 (system metrics)
- PyYAML 6.0.1 (configuration)

**Key Architecture Patterns:**
- Layered Architecture (presentation, business logic, data collection)
- Collector Pattern for data sources
- Circular Buffer for history data

**Project Structure:**
```
src/monitor_dashboard/
├── __init__.py
├── __main__.py
├── app.py
├── config.py
├── models/
├── data_sources/
├── panels/
├── widgets/
├── screens/
├── utils/
└── styles/
```

## Stories in This Epic

| Story | Title | Status |
|-------|-------|--------|
| 1.1 | Project Setup & Minimal App | Draft |
| 1.2 | Panel Layout Structure | Draft |
| 1.3 | Keyboard Navigation | Draft |
| 1.4 | Help Overlay | Draft |
| 1.5 | System Health Data Collection | Draft |
| 1.6 | System Health Panel Display | Draft |
| 1.7 | Panel Expansion | Draft |

## Acceptance Criteria (Epic Level)

- [ ] Application launches with `python -m monitor_dashboard`
- [ ] Fixed 5-panel layout is visible (System Health, Storage, Devices, Logs, Info bar)
- [ ] Tab/Shift+Tab navigates between panels with visual indicator
- [ ] ? key shows help overlay with all keyboard shortcuts
- [ ] System Health panel displays live CPU, memory, and load average
- [ ] Enter key expands focused panel to full-screen
- [ ] Data refreshes at 1 Hz
- [ ] GEM desktop aesthetic is evident in borders and styling

## Definition of Done

- [ ] All 7 stories completed with acceptance criteria met
- [ ] Unit tests pass with >80% coverage on data sources
- [ ] Integration tests verify panel rendering
- [ ] Code passes black, ruff, and mypy checks
- [ ] Manual visual verification against GEM reference images
