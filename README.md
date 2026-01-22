# Monitor Dashboard

A Linux system monitoring dashboard built with Textual, providing real-time insights into system health, processes, storage, devices, and logs.

## Features

### Panels

- **System Health** - CPU, memory, and load average with real-time history graphs
- **Processes** - Sortable process list with CPU/memory usage, kill functionality
- **Devices** - Battery status, Bluetooth devices, and storage/disk information
- **Logs** - System logs from journalctl with severity highlighting
- **Info Bar** - System info, uptime, and apt upgrade status with cache age

### Key Features

- Real-time monitoring with configurable refresh intervals
- Expandable panels for detailed views
- Element selection with sticky multi-select
- Process management (sort, view details, kill)
- Log export functionality
- Automatic terminal resize on startup (Wayland compatible)
- Keyboard-driven interface with mouse support

## Installation

### Option 1: Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that handles virtual environments automatically.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/mcabreb/monitoring_dashboard.git
cd monitoring_dashboard
uv sync
```

### Option 2: Using pip

```bash
# Clone the repository
git clone https://github.com/mcabreb/monitoring_dashboard.git
cd monitoring_dashboard

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Usage

```bash
# With uv (no need to activate venv)
uv run monitor-dashboard

# With pip (after activating venv)
source .venv/bin/activate
monitor-dashboard
```

### Global Command Setup (Optional)

To run `monitor-dashboard` from anywhere without `uv run` or activating a virtual environment:

```bash
# Create ~/.local/bin if it doesn't exist
mkdir -p ~/.local/bin

# Create the launcher script (adjust the path to where you cloned the repo)
cat > ~/.local/bin/monitor-dashboard << 'EOF'
#!/bin/bash
cd ~/workspace/local/monitoring_dashboard && uv run monitor-dashboard "$@"
EOF

# Make it executable
chmod +x ~/.local/bin/monitor-dashboard
```

Make sure `~/.local/bin` is in your PATH. Add this to your `~/.bashrc` or `~/.zshrc` if needed:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Now you can run `monitor-dashboard` from any directory.

## Keyboard Shortcuts

### Navigation

| Key | Action |
|-----|--------|
| `Tab` | Next panel |
| `Shift+Tab` | Previous panel |
| `Enter` | Expand/collapse panel |
| `Escape` | Return to dashboard |

### Selection

| Key | Action |
|-----|--------|
| `Up/Down` | Select element |
| `Home/End` | First/last element |
| `Space` | Toggle sticky selection |
| `c` | Clear sticky selections |
| `i` | Show info for selection |

### Actions

| Key | Action |
|-----|--------|
| `p` | Cycle process sort column (CPU, MEM, TIME, COMMAND, PID, USER) |
| `k` | Kill selected process (Processes panel only) |
| `l` | Export logs to file (Logs panel only) |
| `w` | Resize window to preferred size |
| `?` | Show help overlay |
| `q` | Quit application |

## Requirements

- Linux (tested on Ubuntu)
- Python 3.10+
- systemd (for journalctl logs)
- apt (for package upgrade status)

## Dependencies

- textual - Terminal UI framework
- psutil - System monitoring
- pydbus - D-Bus integration (Bluetooth)
- pyperclip - Clipboard support
- pyyaml - Configuration
- ddgs - Web search integration

## Development

### Setup

```bash
# Install development dependencies
uv sync --all-extras

# Or with pip
pip install -e ".[dev]"
```

### Linting and Type Checking

```bash
black --check src/
ruff check src/
mypy src/
```

### Run Tests

```bash
pytest tests/unit/
```

## Architecture

The application follows a modular architecture:

- `app.py` - Main application with data collectors and refresh timers
- `panels/` - Individual panel widgets (system_health, processes, devices, logs)
- `screens/` - Screen components (main dashboard, expanded view, popups, help)
- `data_sources/` - Data collectors for system metrics
- `models/` - Data models for type safety
- `utils/` - Utility functions and helpers

## License

MIT
