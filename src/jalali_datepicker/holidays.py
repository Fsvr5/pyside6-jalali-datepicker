from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from PySide6.QtCore import QCalendar, QDate

_JALALI = QCalendar(QCalendar.System.Jalali)


@dataclass(frozen=True, slots=True)
class Holiday:
    """One holiday or occasion attached to a concrete QDate."""

    date: QDate
    title: str
    official: bool = True


# Fixed Solar-Hijri official holidays. Lunar/religious holidays intentionally
# belong to a provider because their Gregorian/Jalali dates vary by year and
# should come from an authoritative source chosen by the application.
_FIXED_IRAN_HOLIDAYS: tuple[tuple[int, int, str], ...] = (
    (1, 1, "نوروز"),
    (1, 2, "عید نوروز"),
    (1, 3, "عید نوروز"),
    (1, 4, "عید نوروز"),
    (1, 12, "روز جمهوری اسلامی ایران"),
    (1, 13, "روز طبیعت"),
    (3, 14, "رحلت امام خمینی"),
    (3, 15, "قیام ۱۵ خرداد"),
    (11, 22, "پیروزی انقلاب اسلامی ایران"),
    (12, 29, "روز ملی شدن صنعت نفت ایران"),
)

HolidayProvider = Callable[[int], Iterable[Holiday]]


def fixed_iran_holidays(jalali_year: int) -> list[Holiday]:
    """Return only fixed-date Iranian official holidays for a Jalali year.

    This function deliberately does not guess lunar/religious holiday dates.
    Applications can merge an authoritative provider via ``merge_holidays``.
    """
    result: list[Holiday] = []
    for month, day, title in _FIXED_IRAN_HOLIDAYS:
        if _JALALI.isDateValid(jalali_year, month, day):
            result.append(Holiday(_JALALI.dateFromParts(jalali_year, month, day), title))
    return result


def merge_holidays(*groups: Iterable[Holiday]) -> list[Holiday]:
    """Merge holiday groups by date while preserving all distinct titles."""
    merged: dict[QDate, Holiday] = {}
    for group in groups:
        for item in group:
            if not item.date.isValid():
                raise ValueError("holiday date must be a valid QDate")
            previous = merged.get(item.date)
            if previous is None:
                merged[item.date] = item
                continue
            titles = [part.strip() for part in previous.title.split(" • ") if part.strip()]
            if item.title and item.title not in titles:
                titles.append(item.title)
            merged[item.date] = Holiday(
                item.date,
                " • ".join(titles),
                previous.official or item.official,
            )
    return sorted(merged.values(), key=lambda item: item.date.toJulianDay())
