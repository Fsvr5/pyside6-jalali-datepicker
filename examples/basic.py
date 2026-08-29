import sys

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QApplication, QFormLayout, QLabel, QVBoxLayout, QWidget

from jalali_datepicker import JalaliDateEdit, JalaliDateRangeEdit


app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("PySide6 Jalali DatePicker")

single = JalaliDateEdit()
single.set_jalali_date(1405, 6, 7)

range_edit = JalaliDateRangeEdit(
    start_date=QDate.currentDate(),
    end_date=QDate.currentDate().addDays(7),
)

single_value = QLabel()
range_value = QLabel()


def refresh_single() -> None:
    y, m, d = single.jalali_date()
    single_value.setText(f"{y:04d}/{m:02d}/{d:02d}")


def refresh_range(start: QDate, end: QDate) -> None:
    sy, sm, sd = JalaliDateEdit.jalali_from_qdate(start)
    ey, em, ed = JalaliDateEdit.jalali_from_qdate(end)
    range_value.setText(
        f"{sy:04d}/{sm:02d}/{sd:02d}  تا  {ey:04d}/{em:02d}/{ed:02d}"
    )


single.jalaliDateChanged.connect(lambda *_: refresh_single())
range_edit.rangeChanged.connect(refresh_range)

form = QFormLayout()
form.addRow("تاریخ:", single)
form.addRow("مقدار:", single_value)
form.addRow("بازه:", range_edit)
form.addRow("مقدار بازه:", range_value)

layout = QVBoxLayout(window)
layout.addLayout(form)

refresh_single()
start, end = range_edit.date_range()
refresh_range(start, end)

window.resize(520, 220)
window.show()
sys.exit(app.exec())
