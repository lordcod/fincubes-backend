import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

ERROR_VALUES = [
    "за нарушение ПС",
    "a за нарушение ПС"
    "снята нар.пр.сор.",
    "снят нар.пр.сор.",
    "снята за нар.пр.сор.",
    "снят за нар.пр.сор.",
    "а нар.пр. сор.",
    "за нар.пр.сор",
    "за нар.пр.сор.",
    "а за нар.пр.сор.",
    "нар. Пр.сор",
    "нар.пр.сор.",
    "DSQ",
    "Фальстарт",
    "не допущен",
    "не явился",
    "Сошёл",
    "сошѐл",
    "Нар. пр. сор",
    "Переныр 15м",
    "Мед отвод",
    "Переныр",
    "н/я",
    "снята за нар пр. сор.",
    "снят за нар пр. сор.",
    "снят",
    "DSQ", "Фальстарт", "не допущен", "не явился", "Сошёл",
    "Нар. пр. сор", "Переныр 15м", "Переныр 15м.", "Мед отвод", "Переныр",
    "Фальстарт лично", "Сошёл лично", "Нар. пр. сор лично",
    "сошла",
    "сошел"
]


regex_normal = re.compile(r"""
    ^(?P<place>\d+)\s*
    (?P<rank>(?:[123]\s*юн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<result>\d{2}:\d{2}[,.]\d{2})\s*
    (?P<final_time>\d{2}:\d{2}[,.]\d{2})?\s*
    (?P<final_rank>(?:[123]\s*юн|[123]|КМС|МС|МСМК|ЗМС)?)?\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


regex_dq = re.compile(r"""
    ^(?P<rank>(?:[123]\s*юн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<dsq>
        Фальстарт|
        не\sдопущен|
        не\sявился|
        Сошёл|
        Сошел|
        нар\.?\s*пр\.?\s*сор\.?\s*|
        Переныр\s?15м\.?|
        переныр 15 м.|
        Нар\.\spr\.\sсор|
        [Мм]ед.?\s*отвод\s*|W
        Переныр|
        снят\sза\sнар.пр.сор.|
        снята\sза\sнар.пр.сор.|
        снят\sнар.пр.сор.|
        снята\sнар.пр.сор.|
        нар.пр.сор.|
        переныр 15 м.|
        сошла|
        мед.отвод|
        снят[а-яА-Я0-9\s\.]+
    )\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


regex_dq_final = re.compile(r"""
    ^(?P<place>\d+)\s*
    (?P<rank>(?:[123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<result>\d{2}:\d{2},\d{2})\s+
    (?P<dsq_final>
        Фальстарт|
        не\sдопущен|
        нар\.?\s*пр\.?\s*сор\.?\s*|
        не\sявился|
        Сошёл|
        Переныр\s?15м\.?|
        Нар\.\spr\.\sсор|
        Мед\sотвод|
        Переныр
    )\s*
    (?P<final_rank>(?:МС|МСМК|КМС|[123]))?\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


class FinalIndividualModel(IndividualModelBase, name='final'):
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        super().__init__(
            name='final',
            state=state,
            regexes=[regex_normal, regex_dq, regex_dq_final],
            error_values=ERROR_VALUES
        )
