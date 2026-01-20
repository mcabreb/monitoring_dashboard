"""Selection mixin for panels with element selection support."""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SelectionState:
    """Stores selection state for a panel."""

    cursor_index: int | None = None
    sticky_ids: set[str] | None = None

    def __post_init__(self):
        if self.sticky_ids is None:
            self.sticky_ids = set()


class SelectableMixin:
    """Mixin providing element selection capabilities to panels.

    Panels using this mixin must implement:
    - get_selectable_ids(): Returns list of element IDs in display order
    - get_element_data(element_id): Returns data for an element
    - refresh_selection_display(): Re-renders the panel with selection styling
    """

    def init_selection(self) -> None:
        """Initialize selection state. Call from __init__."""
        self._cursor_index: int | None = None
        self._sticky_ids: set[str] = set()

    @abstractmethod
    def get_selectable_ids(self) -> list[str]:
        """Return list of selectable element IDs in display order.

        Returns:
            List of unique element identifiers.
        """
        ...

    @abstractmethod
    def get_element_data(self, element_id: str) -> Any:
        """Get the data associated with an element ID.

        Args:
            element_id: The element's unique identifier.

        Returns:
            The element's data (type varies by panel).
        """
        ...

    @abstractmethod
    def refresh_selection_display(self) -> None:
        """Re-render the panel with current selection styling."""
        ...

    def get_selection_state(self) -> SelectionState:
        """Get current selection state for persistence.

        Returns:
            SelectionState with cursor and sticky selections.
        """
        return SelectionState(
            cursor_index=self._cursor_index,
            sticky_ids=self._sticky_ids.copy(),
        )

    def set_selection_state(self, state: SelectionState) -> None:
        """Restore selection state.

        Args:
            state: Previously saved selection state.
        """
        self._cursor_index = state.cursor_index
        self._sticky_ids = state.sticky_ids.copy() if state.sticky_ids else set()
        # Validate that sticky IDs still exist
        valid_ids = set(self.get_selectable_ids())
        self._sticky_ids = self._sticky_ids & valid_ids
        # Validate cursor index
        if self._cursor_index is not None:
            max_idx = len(valid_ids) - 1
            if max_idx < 0:
                self._cursor_index = None
            elif self._cursor_index > max_idx:
                self._cursor_index = max_idx

    def clear_selections(self) -> None:
        """Clear all selections (cursor and sticky)."""
        self._cursor_index = None
        self._sticky_ids.clear()
        self.refresh_selection_display()

    def select_next(self) -> None:
        """Move cursor to next element, stopping at end."""
        ids = self.get_selectable_ids()
        if not ids:
            return

        if self._cursor_index is None:
            self._cursor_index = 0
        elif self._cursor_index < len(ids) - 1:
            self._cursor_index += 1
        # else: at end, do nothing

        self.refresh_selection_display()

    def select_previous(self) -> None:
        """Move cursor to previous element, stopping at start."""
        ids = self.get_selectable_ids()
        if not ids:
            return

        if self._cursor_index is None:
            self._cursor_index = 0
        elif self._cursor_index > 0:
            self._cursor_index -= 1
        # else: at start, do nothing

        self.refresh_selection_display()

    def select_first(self) -> None:
        """Move cursor to first element."""
        ids = self.get_selectable_ids()
        if not ids:
            return

        self._cursor_index = 0
        self.refresh_selection_display()

    def select_last(self) -> None:
        """Move cursor to last element."""
        ids = self.get_selectable_ids()
        if not ids:
            return

        self._cursor_index = len(ids) - 1
        self.refresh_selection_display()

    def clear_sticky_selections(self) -> None:
        """Clear only sticky selections, keep cursor."""
        self._sticky_ids.clear()
        self.refresh_selection_display()

    def toggle_sticky(self) -> None:
        """Toggle sticky selection on current cursor element."""
        if self._cursor_index is None:
            return

        ids = self.get_selectable_ids()
        if not ids or self._cursor_index >= len(ids):
            return

        element_id = ids[self._cursor_index]
        if element_id in self._sticky_ids:
            self._sticky_ids.discard(element_id)
        else:
            self._sticky_ids.add(element_id)

        self.refresh_selection_display()

    def get_cursor_id(self) -> str | None:
        """Get the ID of the element under cursor.

        Returns:
            Element ID or None if no cursor.
        """
        if self._cursor_index is None:
            return None
        ids = self.get_selectable_ids()
        if not ids or self._cursor_index >= len(ids):
            return None
        return ids[self._cursor_index]

    def get_sticky_ids(self) -> set[str]:
        """Get set of sticky-selected element IDs.

        Returns:
            Set of element IDs that are sticky-selected.
        """
        return self._sticky_ids.copy()

    def is_cursor(self, element_id: str) -> bool:
        """Check if element is under cursor.

        Args:
            element_id: Element to check.

        Returns:
            True if element is under cursor.
        """
        cursor_id = self.get_cursor_id()
        return cursor_id is not None and cursor_id == element_id

    def is_sticky(self, element_id: str) -> bool:
        """Check if element is sticky-selected.

        Args:
            element_id: Element to check.

        Returns:
            True if element is sticky-selected.
        """
        return element_id in self._sticky_ids

    def get_selection_class(self, element_id: str) -> str | None:
        """Get CSS class for element's selection state.

        Args:
            element_id: Element to check.

        Returns:
            CSS class name or None if not selected.
        """
        if self.is_cursor(element_id):
            return "selected-cursor"
        elif self.is_sticky(element_id):
            return "selected-sticky"
        return None

    def adjust_cursor_for_id(self, target_id: str) -> None:
        """Move cursor to element with given ID.

        Used to follow elements when list order changes.

        Args:
            target_id: Element ID to move cursor to.
        """
        ids = self.get_selectable_ids()
        try:
            self._cursor_index = ids.index(target_id)
        except ValueError:
            # Element no longer exists, keep cursor at same position
            # but clamp to valid range
            if self._cursor_index is not None and ids:
                self._cursor_index = min(self._cursor_index, len(ids) - 1)
            elif not ids:
                self._cursor_index = None

    def prune_invalid_sticky(self) -> None:
        """Remove sticky selections for elements that no longer exist."""
        valid_ids = set(self.get_selectable_ids())
        self._sticky_ids = self._sticky_ids & valid_ids
