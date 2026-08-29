from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QDate
from PySide6.QtGui import QColor, QTextCharFormat


@dataclass(frozen=True, slots=True)
class DayMarker:
    """Visual metadata for one calendar date.

    Markers are intentionally data-only so applications can provide deadlines,
    production days, holidays, maintenance dates, or any other domain event.
    """

    label: str = ""
    foreground: str | None = None
    background: str | None = None
    bold: bool = False

    def text_format(self) -> QTextCharFormat:
        fmt = QTextCharFormat()
        if self.foreground:
            fmt.setForeground(QColor(self.foreground))
        if self.background:
            fmt.setBackground(QColor(self.background))
        if self.bold:
            fmt.setFontWeight(700)
        if self.label:
            fmt.setToolTip(self.label)
        return fmt


class MarkerStore:
    """Small in-memory marker registry keyed by QDate."""

    def __init__(self) -> None:
        self._markers: dict[QDate, DayMarker] = {}

    def set(self, date: QDate, marker: DayMarker) -> None:
        if not date.isValid():
            raise ValueError("marker date must be a valid QDate")
        self._markers[date] = marker

    def remove(self, date: QDate) -> None:
        self._markers.pop(date, None)

    def get(self, date: QDate) -> DayMarker | None:
        return self._markers.get(date)

    def clear(self) -> None:
        self._markers.clear()

    def items(self):
        return self._markers.items()
