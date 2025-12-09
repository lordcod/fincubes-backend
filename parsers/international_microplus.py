import logging
import re
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase


# Более простая, но железобетонная регулярка:
# — матчит ВСЕ строки
# — собирает ВСЕ времена в одну группу times
pattern_international = re.compile(
    r"""
    ^\s*
    (?P<place>\d+)?\s+                     # место
    (\d+)\s+                      # заплыв
    (\d+)\s+                      # дорожка
    (?P<last_name>[A-Za-z\'\-]+)\s+
    (?P<first_name>[A-Za-z\'\-]+)\s+
    (?P<team>[A-Z0-9]+)\s+
    (?P<birth_date>\d{2}\s+[A-Z]{3}\s+\d{4})\s+
    (?P<times>(?:\d{1,2}(?:[:.,]\d{1,2}){1,2}\s*)+)   # ВСЕ времена подряд
    (q|R1|R2|Bronze|Silver|Gold)?\s*(=?WJ)?         # пометка
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE
)


def parse_time(time_str):
    """Parse time strings like '1:23.45' or '12,34'."""
    if not time_str:
        return None
    match = re.fullmatch(
        r'\s*((\d{1,2})[:\.,])?(\d{1,2})[:\.,](\d{1,2})к?\s*', time_str
    )
    if not match:
        return None
    _, minutes, seconds, millis = match.groups()
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds)
    millis = int(millis)
    return minutes * 60 + seconds + millis / 100


class InternationalMicroplusModel(IndividualModelBase, name='international_microplus'):
    """Парсер международных PDF-протоколов (Microplus / CMAS)."""

    def __init__(self, state: State):
        super().__init__(
            name='international_microplus',
            state=state,
            regexes=[pattern_international],
            error_values=[],
        )

    def prerender(self, data: dict) -> dict:
        """Обработка и нормализация данных после regex-сопоставления."""

        team = data.get("team", "").strip()
        birth_date = data.pop("birth_date")

        # год рождения
        if birth_date:
            year_match = re.search(r"\d{4}", birth_date)
            data["birth_year"] = int(
                year_match.group()) if year_match else None
        else:
            data["birth_year"] = None

        # DNS/DSQ/etc
        result = data.get("result")
        if result in ("DNS", "DSQ", "DNF"):
            data["status"] = result
            data["result"] = None
        else:
            data["status"] = "COMPLETED"

        # Фильтрация по команде
        if team != "CM1":
            return None

        # Собираем ВСЕ времена
        times_raw = data.pop("times", "")
        times = re.findall(r"\d{1,2}(?:[:.,]\d{1,2}){1,2}", times_raw)

        # Применяем твою логику: берём максимальное время
        result_value = None
        parsed = []
        for t in times:
            p = parse_time(t)
            if p is not None:
                parsed.append((t, p))

        if parsed:
            best, _ = max(parsed, key=lambda x: x[1])
            result_value = best

        data["result"] = result_value

        if times and not result_value:
            logging.error("CRITICAL ERRRRR %s", data)

        return data
