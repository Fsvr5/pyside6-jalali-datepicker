# PySide6 Jalali DatePicker

Native Jalali (Solar Hijri / Persian) date widgets for PySide6, built on Qt's own `QCalendar.System.Jalali` support.

No third-party Jalali conversion package is required.

## Features

- Native Jalali `QDateEdit`
- Professional `JalaliDatePicker` composite widget
- Fully custom `JalaliCalendarWidget`
- `JalaliPopupDatePicker` with a real custom popup calendar
- Persian month names and explicit month/year controls
- Previous/next month navigation
- Persian locale, RTL layout, and Saturday-first calendar
- Built-in Today and optional Clear actions
- Light, dark, and system themes
- Minimum/maximum date range support
- Friday highlighting
- Extensible holidays and occasions with tooltips
- Built-in fixed-date Iranian official holidays
- Custom day markers for deadlines, production, maintenance, etc.
- Jalali ↔ `QDate` conversion helpers
- Linked `JalaliDateRangeEdit`
- Pytest coverage and GitHub Actions CI

## Install for development

```bash
python -m pip install -e ".[test]"
```

## Custom popup picker

```python
from jalali_datepicker import JalaliPopupDatePicker, Theme

picker = JalaliPopupDatePicker(
    theme=Theme.DARK,
    show_today_button=True,
    clearable=True,
)
picker.set_jalali_date(1405, 6, 7)
```

## Holidays and occasions

The package ships only Iranian official holidays whose dates are fixed in the Solar Hijri calendar. Moving lunar/religious holidays are deliberately not guessed; applications should provide those from an authoritative source for the requested year.

```python
from jalali_datepicker import JalaliCalendarWidget, fixed_iran_holidays

calendar = JalaliCalendarWidget()
holidays = fixed_iran_holidays(1405)
calendar.set_holidays((item.date, item.title) for item in holidays)
```

You can merge moving holidays or application occasions without changing the widget:

```python
from jalali_datepicker import Holiday, merge_holidays

all_holidays = merge_holidays(
    fixed_iran_holidays(1405),
    [Holiday(some_qdate, "مناسبت سازمانی", official=False)],
)
calendar.set_holidays((item.date, item.title) for item in all_holidays)
```

## Highlight deadlines and production dates

```python
from jalali_datepicker import DayMarker

calendar.set_marker(
    deadline_qdate,
    DayMarker("موعد تولید", foreground="#2563EB", bold=True),
)
calendar.set_marker(
    maintenance_qdate,
    DayMarker("تعمیرات ماشین", background="#FEF3C7", bold=True),
)
```

Application markers take precedence over holiday styling for the same date, so domain-specific states remain visible.

## Friday highlighting

Friday highlighting is enabled by default and can be disabled:

```python
calendar.set_friday_highlight(False)
```

## Limit the selectable range

```python
from PySide6.QtCore import QDate

picker.set_date_range(QDate(2026, 1, 1), QDate(2026, 12, 31))
```

## Date range

```python
from jalali_datepicker import JalaliDateRangeEdit, Theme

range_picker = JalaliDateRangeEdit(theme=Theme.LIGHT)
start_qdate, end_qdate = range_picker.date_range()
start_jalali, end_jalali = range_picker.jalali_range()
```

## Signals

`JalaliDatePicker` and `JalaliPopupDatePicker` expose `dateChanged(QDate)`, `jalaliDateChanged(year, month, day)`, and `cleared()`.

`JalaliCalendarWidget` exposes `dateSelected(QDate)` and `jalaliDateSelected(year, month, day)`.

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

Qt stores the selected day as a `QDate`; `QCalendar.System.Jalali` controls how that day is interpreted and presented as Solar Hijri. Holiday data is kept behind a small data/provider seam so moving dates can come from a trusted source chosen by the application instead of becoming stale package constants.
