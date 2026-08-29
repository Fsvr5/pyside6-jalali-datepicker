from PySide6.QtCore import QDate, Qt

from jalali_datepicker import (
    DayMarker, Holiday, JalaliCalendarWidget, JalaliDateEdit, JalaliDatePicker,
    JalaliDateRangeEdit, JalaliPopupDatePicker, Theme, fixed_iran_holidays,
    merge_holidays,
)


def test_known_nowruz_conversion(qtbot):
    widget=JalaliDateEdit(); qtbot.addWidget(widget); widget.set_jalali_date(1403,1,1)
    assert widget.date()==QDate(2024,3,20); assert widget.jalali_date()==(1403,1,1); assert widget.jalali_text()=="1403/01/01"

def test_invalid_jalali_date_raises(qtbot):
    widget=JalaliDateEdit(); qtbot.addWidget(widget)
    try: widget.set_jalali_date(1403,13,1)
    except ValueError: pass
    else: raise AssertionError("Expected ValueError for invalid Jalali date")

def test_qdate_roundtrip(qtbot):
    widget=JalaliDateEdit(); qtbot.addWidget(widget); source=QDate(2026,8,29); assert widget.qdate_from_jalali(*widget.jalali_from_qdate(source))==source

def test_picker_clear_and_restore(qtbot):
    picker=JalaliDatePicker(date=QDate(2026,8,29),clearable=True); qtbot.addWidget(picker); picker.clear(); assert not picker.date().isValid() and picker.jalali_date() is None and picker.jalali_text()==""; picker.set_jalali_date(1405,6,7); assert picker.date().isValid() and picker.jalali_date()==(1405,6,7)

def test_picker_applies_theme(qtbot):
    picker=JalaliDatePicker(theme=Theme.DARK); qtbot.addWidget(picker); assert picker.styleSheet(); picker.apply_theme(Theme.LIGHT); assert picker.styleSheet()

def test_picker_date_range_validation(qtbot):
    picker=JalaliDatePicker(); qtbot.addWidget(picker); minimum,maximum=QDate(2026,1,1),QDate(2026,12,31); picker.set_date_range(minimum,maximum); assert picker.date_edit.minimumDate()==minimum and picker.date_edit.maximumDate()==maximum

def test_custom_calendar_jalali_navigation(qtbot):
    calendar=JalaliCalendarWidget(date=QDate(2024,3,20)); qtbot.addWidget(calendar); assert calendar.jalali_date()==(1403,1,1); calendar.next_month(); assert calendar.month_combo.currentIndex()==1; calendar.previous_month(); assert calendar.month_combo.currentIndex()==0

def test_custom_calendar_set_jalali_date(qtbot):
    calendar=JalaliCalendarWidget(); qtbot.addWidget(calendar); calendar.set_jalali_date(1404,12,29); assert calendar.jalali_date()==(1404,12,29)

def test_calendar_custom_marker(qtbot):
    calendar=JalaliCalendarWidget(); qtbot.addWidget(calendar); date=QDate(2026,8,29); calendar.set_marker(date,DayMarker("موعد تولید",foreground="#2563EB",bold=True)); fmt=calendar.calendar.dateTextFormat(date); assert fmt.toolTip()=="موعد تولید" and fmt.fontWeight()==700

def test_calendar_holiday(qtbot):
    calendar=JalaliCalendarWidget(); qtbot.addWidget(calendar); date=QDate(2026,3,21); calendar.set_holidays([(date,"تعطیل رسمی")]); assert calendar.calendar.dateTextFormat(date).toolTip()=="تعطیل رسمی"

def test_fixed_iran_holidays_include_nowruz():
    holidays=fixed_iran_holidays(1405); nowruz=JalaliDateEdit.qdate_from_jalali(1405,1,1); assert any(item.date==nowruz and item.title=="نوروز" for item in holidays)

def test_merge_holidays_preserves_multiple_titles():
    date=JalaliDateEdit.qdate_from_jalali(1405,1,1); merged=merge_holidays([Holiday(date,"نوروز")],[Holiday(date,"شروع برنامه تولید",official=False)]); assert len(merged)==1 and "نوروز" in merged[0].title and "شروع برنامه تولید" in merged[0].title and merged[0].official

def test_calendar_loads_provider_holidays(qtbot):
    calendar=JalaliCalendarWidget(); qtbot.addWidget(calendar); extra=JalaliDateEdit.qdate_from_jalali(1405,2,5); calendar.load_iran_holidays(1405,lambda year:[Holiday(extra,"مناسبت متغیر")]); assert calendar.calendar.dateTextFormat(extra).toolTip()=="مناسبت متغیر"

def test_calendar_friday_highlight_toggle(qtbot):
    calendar=JalaliCalendarWidget(); qtbot.addWidget(calendar); calendar.set_friday_highlight(False); fmt=calendar.calendar.weekdayTextFormat(Qt.DayOfWeek.Friday); assert fmt.foreground().style()==Qt.BrushStyle.NoBrush

def test_popup_picker_syncs_selected_date(qtbot):
    picker=JalaliPopupDatePicker(date=QDate(2024,3,20)); qtbot.addWidget(picker); selected=QDate(2024,4,1); picker._calendar_selected(selected); assert picker.date()==selected and picker.calendar.date()==selected

def test_popup_picker_range_propagates(qtbot):
    picker=JalaliPopupDatePicker(); qtbot.addWidget(picker); minimum,maximum=QDate(2026,1,1),QDate(2026,12,31); picker.set_date_range(minimum,maximum); assert picker.calendar.calendar.minimumDate()==minimum and picker.calendar.calendar.maximumDate()==maximum

def test_range_rejects_reverse_dates(qtbot):
    try: widget=JalaliDateRangeEdit(start_date=QDate(2026,8,30),end_date=QDate(2026,8,29)); qtbot.addWidget(widget)
    except ValueError: pass
    else: raise AssertionError("Expected ValueError for reversed date range")

def test_range_keeps_end_on_or_after_start(qtbot):
    widget=JalaliDateRangeEdit(start_date=QDate(2026,8,1),end_date=QDate(2026,8,10)); qtbot.addWidget(widget); widget.start.setDate(QDate(2026,8,8)); start,end=widget.date_range(); assert start==QDate(2026,8,8) and end>=start
