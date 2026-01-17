"""Unit tests for formatting utilities."""

import pytest

from monitor_dashboard.utils.formatting import format_bytes, format_percent


def test_format_bytes_bytes():
    """Test formatting values less than 1 KB."""
    assert format_bytes(0) == "0 B"
    assert format_bytes(100) == "100 B"
    assert format_bytes(1023) == "1023 B"


def test_format_bytes_kb():
    """Test formatting kilobyte values."""
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1536) == "1.5 KB"
    assert format_bytes(10240) == "10.0 KB"


def test_format_bytes_mb():
    """Test formatting megabyte values."""
    assert format_bytes(1024**2) == "1.0 MB"
    assert format_bytes(500_000_000) == "476.8 MB"
    assert format_bytes(1024**2 * 500) == "500.0 MB"


def test_format_bytes_gb():
    """Test formatting gigabyte values."""
    assert format_bytes(1024**3) == "1.0 GB"
    assert format_bytes(4_200_000_000) == "3.9 GB"
    assert format_bytes(16 * 1024**3) == "16.0 GB"


def test_format_bytes_tb():
    """Test formatting terabyte values."""
    assert format_bytes(1024**4) == "1.0 TB"
    assert format_bytes(5 * 1024**4) == "5.0 TB"


def test_format_percent_integer():
    """Test formatting integer percentages."""
    assert format_percent(0.0) == "0%"
    assert format_percent(50.0) == "50%"
    assert format_percent(100.0) == "100%"


def test_format_percent_decimal():
    """Test formatting decimal percentages (rounded to integer)."""
    assert format_percent(26.7) == "26%"
    assert format_percent(99.9) == "99%"
    assert format_percent(0.1) == "0%"
