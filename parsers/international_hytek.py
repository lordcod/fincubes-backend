from datetime import date
import re
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase


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
