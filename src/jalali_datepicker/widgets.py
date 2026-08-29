from __future__ import annotations

from PySide6.QtCore import QCalendar, QDate, QLocale, Qt, Signal
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QLabel, QWidget


_JALALI = QCalendar(QCalendar.System.Jalali)
_PERSIAN_LOCALE = QLocale(QLocale.Language.Persian, QLocale.Territory.Iran)


class JalaliDateEdit(QDateEdit):
    """A QDateEdit that displays and edits Solar Hijri (Jalali) dates.

    Internally, Qt still stores the selected day as a QDate. The Jalali calendar
    controls how that day is displayed, edited, and shown in the popup calendar.
    """

    jalaliDateChanged = Signal(int, int, int)

    def __init__(self, parent: QWidget | None = None, *, date: QDate | None = None) -> None:
        super().__init__(parent)
        self.setCalendarPopup(True)
        self.setCalendar(_JALALI)
        self.setLocale(_PERSIAN_LOCALE)
        self.setDisplayFormat("yyyy/MM/dd")
        self.setKeyboardTracking(False)

        popup = self.calendarWidget()
        popup.setCalendar(_JALALI)
        popup.setLocale(_PERSIAN_LOCALE)
        popup.setFirstDayOfWeek(Qt.DayOfWeek.Saturday)
        popup.setGridVisible(True)

        self.setDate(date if date is not None else QDate.currentDate())
        self.dateChanged.connect(self._emit_jalali_date)

    def jalali_date(self) -> tuple[int, int, int]:
        """Return the current date as ``(year, month, day)`` in Jalali."""
        parts = _JALALI.partsFromDate(self.date())
        return parts.year, parts.month, parts.day

    def set_jalali_date(self, year: int, month: int, day: int) -> None:
        """Set the current date from Jalali date parts.

        Raises:
            ValueError: if the supplied Jalali date is invalid.
        """
        if not _JALALI.isDateValid(year, month, day):
            raise ValueError(f"Invalid Jalali date: {year:04d}/{month:02d}/{day:02d}")

        value = _JALALI.dateFromParts(year, month, day)
        if not value.isValid():
            raise ValueError(f"Invalid Jalali date: {year:04d}/{month:02d}/{day:02d}")
        self.setDate(value)

    @staticmethod
    def qdate_from_jalali(year: int, month: int, day: int) -> QDate:
        """Convert Jalali parts to the corresponding Qt ``QDate``."""
        if not _JALALI.isDateValid(year, month, day):
            return QDate()
        return _JALALI.dateFromParts(year, month, day)

    @staticmethod
    def jalali_from_qdate(date: QDate) -> tuple[int, int, int]:
        """Convert a valid Qt ``QDate`` to Jalali date parts."""
        if not date.isValid():
            raise ValueError("QDate must be valid")
        parts = _JALALI.partsFromDate(date)
        return parts.year, parts.month, parts.day

    def _emit_jalali_date(self, date: QDate) -> None:
        year, month, day = self.jalali_from_qdate(date)
        self.jalaliDateChanged.emit(year, month, day)


class JalaliDateRangeEdit(QWidget):
    """Two linked Jalali date editors for choosing an inclusive date range."""

    rangeChanged = Signal(QDate, QDate)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        start_date: QDate | None = None,
        end_date: QDate | None = None,
        separator: str = "تا",
    ) -> None:
        super().__init__(parent)

        today = QDate.currentDate()
        start = start_date if start_date is not None else today
        end = end_date if end_date is not None else start
        if start > end:
            raise ValueError("start_date cannot be after end_date")

        self.start = JalaliDateEdit(self, date=start)
        self.end = JalaliDateEdit(self, date=end)
        self.separator_label = QLabel(separator, self)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.start)
        layout.addWidget(self.separator_label)
        layout.addWidget(self.end)

        self.start.dateChanged.connect(self._start_changed)
        self.end.dateChanged.connect(self._end_changed)
        self._sync_limits()

    def date_range(self) -> tuple[QDate, QDate]:
        return self.start.date(), self.end.date()

    def set_date_range(self, start: QDate, end: QDate) -> None:
        if not start.isValid() or not end.isValid():
            raise ValueError("start and end must be valid QDate values")
        if start > end:
            raise ValueError("start cannot be after end")

        self.start.blockSignals(True)
        self.end.blockSignals(True)
        self.start.setDate(start)
        self.end.setDate(end)
        self.start.blockSignals(False)
        self.end.blockSignals(False)
        self._sync_limits()
        self.rangeChanged.emit(start, end)

    def _sync_limits(self) -> None:
        self.end.setMinimumDate(self.start.date())
        self.start.setMaximumDate(self.end.date())

    def _start_changed(self, start: QDate) -> None:
        if self.end.date() < start:
            self.end.setDate(start)
        self._sync_limits()
        self.rangeChanged.emit(self.start.date(), self.end.date())

    def _end_changed(self, end: QDate) -> None:
        if self.start.date() > end:
            self.start.setDate(end)
        self._sync_limits()
        self.rangeChanged.emit(self.start.date(), self.end.date())
