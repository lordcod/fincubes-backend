from datetime import date
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
    \*?(?P<place>\d+)\s+                                 # место
    (?P<first_name>[A-Za-z'`\-]+)\s+                 # имя
    (?P<last_name>[A-Za-z'`\-]+)\s+                  # фамилия
    (?P<age>\d{1,3})\s+                              # возраст / год
    (?P<team>[A-Za-z0-9\s]+)\s+                        # команда
    (?P<prelim>[0-9:.,]+|NT)\s+                     # любое время (заявочное)
    (?P<result>[0-9:.,]+)\s*                         # любое время (результат)
    \s*$                                             # конец строки
    """,
    re.VERBOSE | re.IGNORECASE
)


class InternationalMicroplusModel(IndividualModelBase, name='international_hytek'):

    def __init__(self, state: State):
        super().__init__(
            name='international_hytek',
            state=state,
            regexes=[pattern_international],
            error_values=[],
        )

    def prerender(self, data: dict) -> dict:
        """Обработка и нормализация данных после regex-сопоставления."""
        team = data.get("team", "").strip()
        age = data.pop("age")
        result = data.get("result")

        if age:
            data["birth_year"] = date.today().year - int(age)
        else:
            data["birth_year"] = None

        if result in ("DNS", "DSQ", "DNF"):
            data["status"] = result
            data["result"] = None
        else:
            data["status"] = "COMPLETED"

        return data
