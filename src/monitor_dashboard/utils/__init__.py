"""Utility modules for monitor dashboard."""

from monitor_dashboard.utils.formatting import format_bytes, format_percent
from monitor_dashboard.utils.history_buffer import HistoryBuffer
from monitor_dashboard.utils.web_search import SearchResult, search_for_error

__all__ = [
    "HistoryBuffer",
    "SearchResult",
    "format_bytes",
    "format_percent",
    "search_for_error",
]
