from __future__ import annotations

from enum import Enum


class Theme(str, Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


def stylesheet(theme: Theme | str = Theme.SYSTEM) -> str:
    """Return a compact stylesheet for the Jalali date picker widgets."""
    value = Theme(theme)
    if value is Theme.SYSTEM:
        return ""

    if value is Theme.DARK:
        return """
QWidget[jalaliPicker="true"] {
    color: #F3F4F6;
}
QDateEdit[jalaliDateEdit="true"] {
    background: #1F2937;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 24px;
}
QDateEdit[jalaliDateEdit="true"]:focus {
    border: 1px solid #60A5FA;
}
QToolButton[jalaliAction="true"] {
    background: #374151;
    color: #F9FAFB;
    border: 1px solid #4B5563;
    border-radius: 8px;
    padding: 5px 9px;
}
QToolButton[jalaliAction="true"]:hover {
    background: #4B5563;
}
QCalendarWidget QWidget {
    background: #111827;
    color: #F9FAFB;
}
QCalendarWidget QAbstractItemView:enabled {
    background: #111827;
    color: #F9FAFB;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}
"""

    return """
QWidget[jalaliPicker="true"] {
    color: #111827;
}
QDateEdit[jalaliDateEdit="true"] {
    background: #FFFFFF;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 24px;
}
QDateEdit[jalaliDateEdit="true"]:focus {
    border: 1px solid #2563EB;
}
QToolButton[jalaliAction="true"] {
    background: #F9FAFB;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 5px 9px;
}
QToolButton[jalaliAction="true"]:hover {
    background: #F3F4F6;
}
QCalendarWidget QAbstractItemView:enabled {
    background: #FFFFFF;
    color: #111827;
    selection-background-color: #2563EB;
    selection-color: #FFFFFF;
}
"""
