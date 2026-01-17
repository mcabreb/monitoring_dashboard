# Monitor Dashboard

A Linux system monitoring dashboard built with Textual, providing real-time insights into system health, storage, devices, and logs.

## Installation

```bash
# Install in development mode
pip install -e ".[dev]"
```

## Usage

Run the monitoring dashboard:

```bash
python -m monitor_dashboard
```

Or use the installed command:

```bash
monitor-dashboard
```

## Development

Run linting and type checking:

```bash
black --check src/
ruff check src/
mypy src/
```

Run tests:

```bash
pytest tests/unit/
```
