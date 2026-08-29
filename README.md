# PySide6 Jalali DatePicker

Native Jalali (Solar Hijri / Persian) date widgets for PySide6, built on Qt's own `QCalendar.System.Jalali` support.

No third-party Jalali conversion package is required.

## Features

- Native Jalali `QDateEdit` with Persian popup calendar
- Professional `JalaliDatePicker` composite widget
- Persian locale, RTL layout, and Saturday-first calendar
- `yyyy/MM/dd` display format
- Built-in Today and optional Clear actions
- Light, dark, and system themes
- Minimum/maximum date range support
- Jalali ↔ `QDate` conversion helpers
- Linked `JalaliDateRangeEdit`
- Backward-compatible low-level `JalaliDateEdit`
- Pytest coverage and GitHub Actions CI

## Install for development

```bash
python -m pip install -e ".[test]"
```

## Professional picker

```python
from jalali_datepicker import JalaliDatePicker, Theme

picker = JalaliDatePicker(
    theme=Theme.DARK,
    show_today_button=True,
    clearable=True,
)

picker.set_jalali_date(1405, 6, 7)
print(picker.jalali_text())
```

Switch theme at runtime:

```python
picker.apply_theme(Theme.LIGHT)
```

Limit the selectable range:

```python
from PySide6.QtCore import QDate

picker.set_date_range(
    QDate(2026, 1, 1),
    QDate(2026, 12, 31),
)
```

## Low-level date edit

```python
from jalali_datepicker import JalaliDateEdit

editor = JalaliDateEdit()
editor.set_jalali_date(1405, 6, 7)

year, month, day = editor.jalali_date()
qdate = editor.date()
```

## Date range

```python
from jalali_datepicker import JalaliDateRangeEdit, Theme

range_picker = JalaliDateRangeEdit(theme=Theme.LIGHT)
start_qdate, end_qdate = range_picker.date_range()
start_jalali, end_jalali = range_picker.jalali_range()
```

## Signals

`JalaliDatePicker` exposes:

- `dateChanged(QDate)`
- `jalaliDateChanged(year, month, day)`
- `cleared()`

## Run the example

```bash
python examples/basic.py
```

## Run tests

```bash
pytest
```

For headless Linux environments:

```bash
QT_QPA_PLATFORM=offscreen pytest
```

## Design note

Qt stores the selected day as a `QDate`; `QCalendar.System.Jalali` controls how that day is interpreted and presented as Solar Hijri. This keeps the component close to Qt and avoids maintaining a separate date-conversion algorithm.
