import sys

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from jalali_datepicker import JalaliDatePicker, JalaliDateRangeEdit, Theme


class Demo(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PySide6 Jalali DatePicker")
        self.resize(520, 220)

        self.single = JalaliDatePicker(
            date=QDate.currentDate(),
            theme=Theme.LIGHT,
            show_today_button=True,
            clearable=True,
        )
        self.single.set_jalali_minimum = self.single.date_edit.set_jalali_minimum
        self.single.set_jalali_maximum = self.single.date_edit.set_jalali_maximum

        self.range = JalaliDateRangeEdit(theme=Theme.LIGHT)
        self.output = QLabel(self)
        self.output.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("تاریخ:", self))
        layout.addWidget(self.single)
        layout.addWidget(QLabel("بازه تاریخ:", self))
        layout.addWidget(self.range)
        layout.addWidget(self.output)

        self.single.dateChanged.connect(self.refresh)
        self.single.cleared.connect(self.refresh)
        self.range.rangeChanged.connect(self.refresh)
        self.refresh()

    def refresh(self, *args) -> None:
        single = self.single.jalali_text() or "—"
        start, end = self.range.jalali_range()
        start_text = f"{start[0]:04d}/{start[1]:02d}/{start[2]:02d}"
        end_text = f"{end[0]:04d}/{end[1]:02d}/{end[2]:02d}"
        self.output.setText(f"تاریخ انتخابی: {single}\nبازه: {start_text} تا {end_text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec())
