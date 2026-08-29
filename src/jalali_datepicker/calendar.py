from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QCalendar, QDate, QLocale, Qt, Signal
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from .markers import DayMarker, MarkerStore
from .themes import Theme, stylesheet

_JALALI = QCalendar(QCalendar.System.Jalali)
_PERSIAN_LOCALE = QLocale(QLocale.Language.Persian, QLocale.Territory.Iran)
_MONTHS = (
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند",
)


class JalaliCalendarWidget(QWidget):
    """Custom Jalali calendar with navigation and extensible day highlighting."""

    dateSelected = Signal(QDate)
    jalaliDateSelected = Signal(int, int, int)

    def __init__(self, parent: QWidget | None = None, *, date: QDate | None = None,
                 theme: Theme | str = Theme.SYSTEM) -> None:
        super().__init__(parent)
        self.setProperty("jalaliPicker", True)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._theme = Theme(theme)
        self._syncing = False
        self._markers = MarkerStore()
        self._holidays: dict[QDate, str] = {}
        self._highlight_fridays = True

        self.previous_button = QToolButton(self)
        self.previous_button.setText("‹")
        self.previous_button.setToolTip("ماه قبل")
        self.previous_button.setProperty("jalaliAction", True)
        self.next_button = QToolButton(self)
        self.next_button.setText("›")
        self.next_button.setToolTip("ماه بعد")
        self.next_button.setProperty("jalaliAction", True)

        self.month_combo = QComboBox(self)
        self.month_combo.addItems(_MONTHS)
        self.month_combo.setMinimumWidth(120)
        self.year_spin = QSpinBox(self)
        self.year_spin.setRange(1, 9999)
        self.year_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.year_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.year_spin.setMinimumWidth(72)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(6)
        header.addWidget(self.previous_button)
        header.addStretch(1)
        header.addWidget(self.month_combo)
        header.addWidget(self.year_spin)
        header.addStretch(1)
        header.addWidget(self.next_button)

        self.calendar = QCalendarWidget(self)
        self.calendar.setCalendar(_JALALI)
        self.calendar.setLocale(_PERSIAN_LOCALE)
        self.calendar.setFirstDayOfWeek(Qt.DayOfWeek.Saturday)
        self.calendar.setGridVisible(True)
        self.calendar.setNavigationBarVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.today_label = QLabel(self)
        self.today_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.today_button = QPushButton("امروز", self)
        self.today_button.setProperty("jalaliAction", True)
        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.addWidget(self.today_label, 1)
        footer.addWidget(self.today_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        layout.addLayout(header)
        layout.addWidget(self.calendar)
        layout.addLayout(footer)

        self.previous_button.clicked.connect(self.previous_month)
        self.next_button.clicked.connect(self.next_month)
        self.month_combo.currentIndexChanged.connect(self._header_changed)
        self.year_spin.valueChanged.connect(self._header_changed)
        self.today_button.clicked.connect(self.set_today)
        self.calendar.currentPageChanged.connect(self._page_changed)
        self.calendar.clicked.connect(self._selected)
        self.calendar.activated.connect(self._selected)

        self.set_date(date if date is not None else QDate.currentDate())
        self._update_today_label()
        self.apply_theme(self._theme)
        self.refresh_day_formats()

    def date(self) -> QDate:
        return self.calendar.selectedDate()

    def jalali_date(self) -> tuple[int, int, int]:
        parts = _JALALI.partsFromDate(self.date())
        return parts.year, parts.month, parts.day

    def set_date(self, date: QDate) -> None:
        if not date.isValid():
            raise ValueError("date must be a valid QDate")
        self.calendar.setSelectedDate(date)
        self._sync_header_from_date(date)

    def set_jalali_date(self, year: int, month: int, day: int) -> None:
        if not _JALALI.isDateValid(year, month, day):
            raise ValueError(f"Invalid Jalali date: {year:04d}/{month:02d}/{day:02d}")
        self.set_date(_JALALI.dateFromParts(year, month, day))

    def set_date_range(self, minimum: QDate, maximum: QDate) -> None:
        if not minimum.isValid() or not maximum.isValid():
            raise ValueError("minimum and maximum must be valid QDate values")
        if minimum > maximum:
            raise ValueError("minimum cannot be after maximum")
        self.calendar.setMinimumDate(minimum)
        self.calendar.setMaximumDate(maximum)

    def set_marker(self, date: QDate, marker: DayMarker) -> None:
        self._markers.set(date, marker)
        self.refresh_day_formats()

    def remove_marker(self, date: QDate) -> None:
        self._markers.remove(date)
        self.refresh_day_formats()

    def clear_markers(self) -> None:
        self._markers.clear()
        self.refresh_day_formats()

    def set_holidays(self, holidays: Iterable[tuple[QDate, str]]) -> None:
        values: dict[QDate, str] = {}
        for date, title in holidays:
            if not date.isValid():
                raise ValueError("holiday date must be a valid QDate")
            values[date] = title
        self._holidays = values
        self.refresh_day_formats()

    def clear_holidays(self) -> None:
        self._holidays.clear()
        self.refresh_day_formats()

    def set_friday_highlight(self, enabled: bool) -> None:
        self._highlight_fridays = enabled
        self.refresh_day_formats()

    def refresh_day_formats(self) -> None:
        """Rebuild special date formats without coupling the widget to a holiday API."""
        minimum = self.calendar.minimumDate()
        maximum = self.calendar.maximumDate()
        for date in list(self._holidays) + [d for d, _ in self._markers.items()]:
            self.calendar.setDateTextFormat(date, QTextCharFormat())

        # Fridays use the weekday format, so the rule works for every visible month.
        friday = QTextCharFormat()
        if self._highlight_fridays:
            friday.setForeground(QColor("#DC2626"))
            friday.setFontWeight(700)
        self.calendar.setWeekdayTextFormat(Qt.DayOfWeek.Friday, friday)

        for date, title in self._holidays.items():
            if minimum <= date <= maximum:
                fmt = QTextCharFormat()
                fmt.setForeground(QColor("#DC2626"))
                fmt.setFontWeight(700)
                if title:
                    fmt.setToolTip(title)
                self.calendar.setDateTextFormat(date, fmt)

        # Custom application markers intentionally win over holiday styling.
        for date, marker in self._markers.items():
            if minimum <= date <= maximum:
                self.calendar.setDateTextFormat(date, marker.text_format())

    def previous_month(self) -> None:
        self.calendar.showPreviousMonth()

    def next_month(self) -> None:
        self.calendar.showNextMonth()

    def set_today(self) -> None:
        today = QDate.currentDate()
        if today < self.calendar.minimumDate():
            today = self.calendar.minimumDate()
        elif today > self.calendar.maximumDate():
            today = self.calendar.maximumDate()
        self.set_date(today)
        self._selected(today)

    def apply_theme(self, theme: Theme | str) -> None:
        self._theme = Theme(theme)
        self.setStyleSheet(stylesheet(self._theme))
        self.refresh_day_formats()

    def _header_changed(self) -> None:
        if self._syncing:
            return
        self.calendar.setCurrentPage(self.year_spin.value(), self.month_combo.currentIndex() + 1)

    def _page_changed(self, year: int, month: int) -> None:
        self._syncing = True
        self.year_spin.setValue(year)
        self.month_combo.setCurrentIndex(month - 1)
        self._syncing = False

    def _sync_header_from_date(self, date: QDate) -> None:
        parts = _JALALI.partsFromDate(date)
        self._syncing = True
        self.year_spin.setValue(parts.year)
        self.month_combo.setCurrentIndex(parts.month - 1)
        self.calendar.setCurrentPage(parts.year, parts.month)
        self._syncing = False

    def _selected(self, date: QDate) -> None:
        self._sync_header_from_date(date)
        parts = _JALALI.partsFromDate(date)
        self.dateSelected.emit(date)
        self.jalaliDateSelected.emit(parts.year, parts.month, parts.day)

    def _update_today_label(self) -> None:
        parts = _JALALI.partsFromDate(QDate.currentDate())
        self.today_label.setText(f"امروز: {parts.year:04d}/{parts.month:02d}/{parts.day:02d}")
