from __future__ import annotations

from PySide6.QtCore import QDate, QPoint, Qt
from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout, QWidget

from .calendar import JalaliCalendarWidget
from .themes import Theme, stylesheet
from .widgets import JalaliDatePicker


class JalaliPopupDatePicker(JalaliDatePicker):
    """Jalali date picker using the package's fully custom calendar popup."""

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
        super().__init__(
            parent,
            date=date,
            theme=theme,
            show_today_button=show_today_button,
            clearable=clearable,
            today_text=today_text,
            clear_text=clear_text,
        )
        self.date_edit.setCalendarPopup(False)

        self.calendar_button = QToolButton(self)
        self.calendar_button.setText("▾")
        self.calendar_button.setToolTip("باز کردن تقویم شمسی")
        self.calendar_button.setProperty("jalaliAction", True)
        self.layout().insertWidget(1, self.calendar_button)

        self._popup = QFrame(None, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self._popup.setProperty("jalaliPicker", True)
        popup_layout = QVBoxLayout(self._popup)
        popup_layout.setContentsMargins(0, 0, 0, 0)

        self.calendar = JalaliCalendarWidget(
            self._popup,
            date=self.date_edit.date(),
            theme=theme,
        )
        popup_layout.addWidget(self.calendar)

        self.calendar_button.clicked.connect(self.show_popup)
        self.calendar.dateSelected.connect(self._calendar_selected)
        self.date_edit.dateChanged.connect(self._sync_calendar)
        self.apply_theme(theme)

    def show_popup(self) -> None:
        current = self.date()
        if current.isValid():
            self.calendar.set_date(current)

        minimum = self.date_edit.minimumDate()
        maximum = self.date_edit.maximumDate()
        self.calendar.set_date_range(minimum, maximum)

        self._popup.adjustSize()
        global_pos = self.mapToGlobal(QPoint(0, self.height() + 4))
        self._popup.move(global_pos)
        self._popup.show()
        self._popup.raise_()

    def hide_popup(self) -> None:
        self._popup.hide()

    def set_date_range(self, minimum: QDate, maximum: QDate) -> None:
        super().set_date_range(minimum, maximum)
        self.calendar.set_date_range(minimum, maximum)

    def apply_theme(self, theme: Theme | str) -> None:
        super().apply_theme(theme)
        if hasattr(self, "calendar"):
            self.calendar.apply_theme(theme)
        if hasattr(self, "_popup"):
            self._popup.setStyleSheet(stylesheet(theme))

    def _calendar_selected(self, date: QDate) -> None:
        self.set_date(date)
        self.hide_popup()

    def _sync_calendar(self, date: QDate) -> None:
        if date.isValid():
            self.calendar.set_date(date)
