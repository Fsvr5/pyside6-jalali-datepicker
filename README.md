# PySide6 Jalali DatePicker

Native Jalali (Solar Hijri / Persian) date widgets for PySide6, built on Qt's own `QCalendar.System.Jalali` support.

No third-party Jalali conversion package is required.

## Features

- Jalali `QDateEdit` with popup calendar
- Persian locale and Saturday-first calendar
- `yyyy/MM/dd` display format
- Jalali ↔ `QDate` conversion helpers
- `JalaliDateRangeEdit` with linked start/end dates
- Validation for invalid Jalali dates and reversed ranges
- Installable `src/` package layout
- Pytest coverage and GitHub Actions CI

## Install for development

```bash
python -m pip install -e ".[test]"
```

## Basic usage

```python
from jalali_datepicker import JalaliDateEdit

picker = JalaliDateEdit()
picker.set_jalali_date(1405, 6, 7)

year, month, day = picker.jalali_date()
qdate = picker.date()
```

## Date range

```python
from jalali_datepicker import JalaliDateRangeEdit

range_picker = JalaliDateRangeEdit()
start_qdate, end_qdate = range_picker.date_range()
```

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
