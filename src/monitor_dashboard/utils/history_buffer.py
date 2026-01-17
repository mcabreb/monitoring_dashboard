"""Fixed-size circular buffer for time-series data."""

from collections import deque


class HistoryBuffer:
    """Fixed-size circular buffer for storing historical metric values.

    Uses collections.deque for efficient O(1) append and automatic eviction
    of old values when buffer is full.

    Attributes:
        maxlen: Maximum number of values to store.
    """

    def __init__(self, maxlen: int = 60) -> None:
        """Initialize history buffer with fixed size.

        Args:
            maxlen: Maximum number of values to store (default: 60).
        """
        self._buffer: deque[float] = deque(maxlen=maxlen)

    def append(self, value: float) -> None:
        """Append a value to the buffer.

        If buffer is at maxlen, oldest value is automatically removed.

        Args:
            value: The metric value to append.
        """
        self._buffer.append(value)

    def get_values(self) -> list[float]:
        """Get all values in buffer as a list.

        Returns:
            List of values in chronological order (oldest first).
        """
        return list(self._buffer)

    def clear(self) -> None:
        """Remove all values from the buffer."""
        self._buffer.clear()
