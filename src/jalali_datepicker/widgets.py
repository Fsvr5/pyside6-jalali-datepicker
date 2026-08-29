from __future__ import annotations

from PySide6.QtCore import QCalendar, QDate, QLocale, Qt, Signal
from PySide6.QtWidgets import QDateEdit, QHBoxLayout, QLabel, QToolButton, QWidget

from .themes import Theme, stylesheet


_JALALI = QCalendar(QCalendar.System.Jalali)
_PERSIAN_LOCALE = QLocale(QLocale.Language.Persian, QLocale.Territory.Iran)


class JalaliDateEdit(QDateEdit):
    """A QDateEdit that displays and edits Solar Hijri (Jalali) dates."""

    jalaliDateChanged = Signal(int, int, int)

    def __init__(self, parent: QWidget | None = None, *, date: QDate | None = None) -> None:
        super().__init__(parent)
        self.setProperty("jalaliDateEdit", True)
        self.setCalendarPopup(True)
        self.setCalendar(_JALALI)
        self.setLocale(_PERSIAN_LOCALE)
        self.setDisplayFormat("yyyy/MM/dd")
        self.setKeyboardTracking(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        popup = self.calendarWidget()
        popup.setCalendar(_JALALI)
        popup.setLocale(_PERSIAN_LOCALE)
        popup.setFirstDayOfWeek(Qt.DayOfWeek.Saturday)
        popup.setGridVisible(True)
        popup.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.setDate(date if date is not None else QDate.currentDate())
        self.dateChanged.connect(self._emit_jalali_date)

    def jalali_date(self) -> tuple[int, int, int]:
        parts = _JALALI.partsFromDate(self.date())
        return parts.year, parts.month, parts.day

    def jalali_text(self) -> str:
        year, month, day = self.jalali_date()
        return f"{year:04d}/{month:02d}/{day:02d}"

    def set_jalali_date(self, year: int, month: int, day: int) -> None:
        if not _JALALI.isDateValid(year, month, day):
            raise ValueError(f"Invalid Jalali date: {year:04d}/{month:02d}/{day:02d}")
        value = _JALALI.dateFromParts(year, month, day)
        if not value.isValid():
            raise ValueError(f"Invalid Jalali date: {year:04d}/{month:02d}/{day:02d}")
        self.setDate(value)

    def set_jalali_minimum(self, year: int, month: int, day: int) -> None:
        value = self.qdate_from_jalali(year, month, day)
        if not value.isValid():
            raise ValueError("Invalid Jalali minimum date")
        self.setMinimumDate(value)

    def set_jalali_maximum(self, year: int, month: int, day: int) -> None:
        value = self.qdate_from_jalali(year, month, day)
        if not value.isValid():
            raise ValueError("Invalid Jalali maximum date")
        self.setMaximumDate(value)

    @staticmethod
    def qdate_from_jalali(year: int, month: int, day: int) -> QDate:
        if not _JALALI.isDateValid(year, month, day):
            return QDate()
        return _JALALI.dateFromParts(year, month, day)

    @staticmethod
    def jalali_from_qdate(date: QDate) -> tuple[int, int, int]:
        if not date.isValid():
            raise ValueError("QDate must be valid")
        parts = _JALALI.partsFromDate(date)
        return parts.year, parts.month, parts.day

    def _emit_jalali_date(self, date: QDate) -> None:
        year, month, day = self.jalali_from_qdate(date)
        self.jalaliDateChanged.emit(year, month, day)


class JalaliDatePicker(QWidget):
    """Professional composite Jalali picker with optional Today/Clear actions.

    ``dateChanged`` emits a valid QDate when selected and an invalid QDate after
    ``clear()``. The underlying ``date_edit`` remains directly accessible for
    advanced QDateEdit configuration.
    """

    dateChanged = Signal(QDate)
    jalaliDateChanged = Signal(int, int, int)
    cleared = Signal()

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        date: QDate | None = None,
        theme: Theme | str = Theme.SYSTEM,
        show_today_button: bool = True,
        clearable: bool = False,
        today_text: str = "امروز",
        clear_text: str = "پاک",
    ) -> None:
        super().__init__(parent)
        self.setProperty("jalaliPicker", True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._is_cleared = False
        self._theme = Theme(theme)

        self.date_edit = JalaliDateEdit(self, date=date)
        self.today_button = QToolButton(self)
        self.today_button.setText(today_text)
        self.today_button.setToolTip("انتخاب تاریخ امروز")
        self.today_button.setProperty("jalaliAction", True)
        self.today_button.setVisible(show_today_button)

        self.clear_button = QToolButton(self)
        self.clear_button.setText(clear_text)
        self.clear_button.setToolTip("پاک کردن تاریخ")
        self.clear_button.setProperty("jalaliAction", True)
        self.clear_button.setVisible(clearable)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.date_edit, 1)
        layout.addWidget(self.today_button)
        layout.addWidget(self.clear_button)

        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.today_button.clicked.connect(self.set_today)
        self.clear_button.clicked.connect(self.clear)
        self.apply_theme(self._theme)

    def date(self) -> QDate:
        return QDate() if self._is_cleared else self.date_edit.date()

    def jalali_date(self) -> tuple[int, int, int] | None:
        return None if self._is_cleared else self.date_edit.jalali_date()

    def jalali_text(self) -> str:
        return "" if self._is_cleared else self.date_edit.jalali_text()

    def set_date(self, date: QDate) -> None:
        if not date.isValid():
            raise ValueError("date must be a valid QDate")
        self._is_cleared = False
        self.date_edit.setDate(date)
        self.date_edit.setEnabled(True)

    def set_jalali_date(self, year: int, month: int, day: int) -> None:
        self._is_cleared = False
        self.date_edit.set_jalali_date(year, month, day)
        self.date_edit.setEnabled(True)

    def set_today(self) -> None:
        self.set_date(QDate.currentDate())

    def clear(self) -> None:
        self._is_cleared = True
        self.date_edit.setEnabled(False)
        self.cleared.emit()
        self.dateChanged.emit(QDate())

    def set_clearable(self, enabled: bool) -> None:
        self.clear_button.setVisible(enabled)

    def set_today_button_visible(self, visible: bool) -> None:
        self.today_button.setVisible(visible)

    def set_date_range(self, minimum: QDate, maximum: QDate) -> None:
        if not minimum.isValid() or not maximum.isValid():
            raise ValueError("minimum and maximum must be valid QDate values")
        if minimum > maximum:
            raise ValueError("minimum cannot be after maximum")
        self.date_edit.setDateRange(minimum, maximum)

    def apply_theme(self, theme: Theme | str) -> None:
        self._theme = Theme(theme)
        self.setStyleSheet(stylesheet(self._theme))

    def _on_date_changed(self, date: QDate) -> None:
        self._is_cleared = False
        self.date_edit.setEnabled(True)
        self.dateChanged.emit(date)
        year, month, day = self.date_edit.jalali_date()
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
        theme: Theme | str = Theme.SYSTEM,
    ) -> None:
        super().__init__(parent)
        self.setProperty("jalaliPicker", True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

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
        layout.setSpacing(8)
        layout.addWidget(self.start)
        layout.addWidget(self.separator_label)
        layout.addWidget(self.end)

        self.start.dateChanged.connect(self._start_changed)
        self.end.dateChanged.connect(self._end_changed)
        self._sync_limits()
        self.apply_theme(theme)

    def date_range(self) -> tuple[QDate, QDate]:
        return self.start.date(), self.end.date()

    def jalali_range(self) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        return self.start.jalali_date(), self.end.jalali_date()

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

    def apply_theme(self, theme: Theme | str) -> None:
        self.setStyleSheet(stylesheet(theme))

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
