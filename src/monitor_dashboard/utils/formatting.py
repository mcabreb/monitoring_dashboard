"""Formatting utilities for displaying metrics."""


def format_bytes(bytes_value: int) -> str:
    """Format byte values as human-readable sizes.

    Args:
        bytes_value: Number of bytes to format.

    Returns:
        Formatted string (e.g., "4.2 GB", "500.0 MB", "1.5 KB").
    """
    units = [
        ("TB", 1024**4),
        ("GB", 1024**3),
        ("MB", 1024**2),
        ("KB", 1024),
        ("B", 1),
    ]

    for unit_name, unit_size in units:
        if bytes_value >= unit_size:
            value = bytes_value / unit_size
            # Use integer formatting for bytes, decimal for larger units
            if unit_name == "B":
                return f"{int(value)} {unit_name}"
            return f"{value:.1f} {unit_name}"

    return f"{bytes_value} B"


def format_percent(value: float) -> str:
    """Format a percentage value.

    Args:
        value: Percentage value (0-100).

    Returns:
        Formatted string (e.g., "26%", "100%").
    """
    return f"{int(value)}%"
