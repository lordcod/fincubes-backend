import re
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase


# Пример строки:
# 4 4 TIMCHENKO Ekaterina CM1 09 JAN 2008 0.90 17.18 0.56 q
# 5 5 SAPRYKINA Kseniia CM1 16 JUN 2008 0.98 17.44 0.47
# 1 4 4 SHTARK Matvey CM1 18 JUL 2008 0.83 20.87 43.39 q
# 6 4 4 TIMCHENKO Ekaterina CM1 09 JAN 2008 0.90 17.18 0.56 q
# 9 4 5 DOROGAVTSEVA Sofia CM1 07 JUL 2008 0.87 24.27 50.25 1.90 R1
# 1 4 4 IVANUSHKINA Polina CM1 05 MAR 2008 0.95 23.94 50.82 1:19.41 1:48.71 q
pattern_international = re.compile(
    r"""
    ^\s*
    (?P<rank>\d+)?\s+                          # место
    (\d+)\s+                                  # заплыв
    (\d+)\s+                                  # дорожка
    (?P<last_name>[A-Za-z\'\-]+)\s+
    (?P<first_name>[A-Za-z\'\-]+)\s+
    (?P<team>[A-Z0-9]+)\s+
    (?P<birth_date>\d{2}\s+[A-Z]{3}\s+\d{4})\s+
    ((?:\d{1,2}(?::|,|\.)\d{1,2}\s+)+)?
    (?P<result>\d{1,2}(?:[:.,]\d{1,2}){1,2})   # результат (время)
    (?:\s+\d{1,2}(?:[:.,]\d{1,2}){1,2})?                           # реакция или доп. время
    (?:\s+(q|R1|R2|Bronze|Silver|Gold))?             # q, R1 и т.п.
    \s*$
    """,
    re.VERBOSE | re.IGNORECASE
)


class InternationalMicroplusModel(IndividualModelBase, name='international_microplus'):
    """
    Парсер международных PDF-протоколов (Microplus / CMAS).
    Извлекает фамилию, имя, команду, дату рождения, год и результат старта.
    """

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
        result = data.get("result")

        # год рождения
        if birth_date:
            year_match = re.search(r"\d{4}", birth_date)
            data["birth_year"] = int(
                year_match.group()) if year_match else None
        else:
            data["birth_year"] = None

        # статус
        if result in ("DNS", "DSQ", "DNF"):
            data["status"] = result
            data["result"] = None
        else:
            data["status"] = "COMPLETED"

        if team != "CM1":
            return None

        return data
