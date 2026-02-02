"""Web search utility using DuckDuckGo."""

import logging
import re
from dataclasses import dataclass

from ddgs import DDGS

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    snippet: str
    url: str


def _extract_error_terms(message: str) -> str:
    """Extract key error terms from a log message.

    Tries to find the most relevant searchable part of an error message,
    removing timestamps, hostnames, PIDs, and non-ASCII text.

    Args:
        message: The full log message.

    Returns:
        Cleaned search query with key error terms.
    """
    # Remove common log prefixes (timestamps, hostnames, service names with PIDs)
    # Pattern: service[PID]: or hostname service[PID]:
    cleaned = re.sub(r"^\S+\[\d+\]:\s*", "", message)
    cleaned = re.sub(r"^\S+\s+\S+\[\d+\]:\s*", "", cleaned)

    # Try to extract text before "Error:" or similar markers (often the key message)
    error_match = re.search(r"^(.+?)(?:\.\s*Error:|:\s*Error:|\s+Error:)", cleaned)
    if error_match:
        cleaned = error_match.group(1).strip()

    # Remove non-ASCII characters (localized error messages)
    cleaned = re.sub(r"[^\x00-\x7F]+", " ", cleaned)

    # Remove URLs and file paths but keep the key part
    cleaned = re.sub(r"[a-z]+://[^\s]+", "", cleaned)

    # Clean up extra whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Truncate to reasonable length (first ~80 chars of meaningful content)
    if len(cleaned) > 80:
        # Try to cut at a word boundary
        cleaned = cleaned[:80].rsplit(" ", 1)[0]

    return cleaned


def search_for_error(query: str, max_results: int = 1) -> list[SearchResult]:
    """Search DuckDuckGo for information about an error or log message.

    Args:
        query: The search query (typically a log message or error).
        max_results: Maximum number of results to return.

    Returns:
        List of SearchResult objects with title, snippet, and URL.
    """
    results = []

    # Extract key error terms from the message
    search_query = _extract_error_terms(query)

    if not search_query or len(search_query) < 10:
        # Query too short, use original but truncated
        search_query = query[:100]

    # Add context to improve search relevance
    search_query = f"linux {search_query}"

    try:
        with DDGS() as ddgs:
            # Search with worldwide region for English results
            search_results = ddgs.text(search_query, region="wt-wt", max_results=max_results)

            for r in search_results:
                results.append(
                    SearchResult(
                        title=r.get("title", ""),
                        snippet=r.get("body", ""),
                        url=r.get("href", ""),
                    )
                )
    except Exception as e:
        logger.debug(f"Web search failed: {e}")

    return results
