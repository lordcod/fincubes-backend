from parsers.base import IndividualModelBase
import re
import logging
from models.state import State
from models.swim_types import *

ERROR_VALUES = [
    'нар. пр. сор.',
    'не стартовала',
    'сошёл',
    'мед.отвод',
    'переныр 15 м',
    "не старт",
    "не старт.",
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
    "DNS",
    "Фальстарт",
    "не допущен",
    "не явился",
    "Сошёл",
    "Нар. пр. сор",
    "Переныр 15м",
    "Мед отвод",
    "Переныр",
    "н/я",
    "DSQ",
    "ня",
    "снята за нар пр. сор.",
    "снят за нар пр. сор.",
    "снят",
    "DSQ", "Фальстарт", "не допущен", "не явился", "Сошёл",
    "Нар. пр. сор", "Переныр 15м", "Переныр 15м.", "Мед отвод", "Переныр",
    "Фальстарт лично", "Сошёл лично", "Нар. пр. сор лично",
    "сошла",
    "сошел",
    "ф/с",
    'DNF',
    "переныр 15м",
    "фальстарт",
    "DQ",
    "неявка",
    "д/к",
    "н\\я",
    "переныр",
    "н/кас поворота",
    "ст за нар пр сор",
    "ста за нар пр сор",
    "фальстар",
    "мед. отвод",
    "фальсатрт",
    "н/я",
    "снят"
]
ERROR_VALUES.sort(key=len, reverse=True)

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+.?|в/к|д/к)?\s*
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?
    (?P<last_name>[А-Яа-яЁёë\-]+),?\s+
    (?P<first_name>[А-Яа-яЁёë\-]+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?\s*)
    (?:\s+(?P<result>\d{1,2}[:\.,]\d{1,2}(?:[:\.,]\d{1,2})?к?))?
    (?:\s+(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<points>(?:лично|\d+)))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class PointsIndividualModel(IndividualModelBase, name='points'):
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        super().__init__(
            name='points',
            state=state,
            regexes=[pattern],
            error_values=ERROR_VALUES
        )

    def prerender(self, data):
        team = data['team']
        data['status'] = 'COMPLETED'
        for error in ERROR_VALUES:
            if error in team:
                logging.debug('Found dsq in team %s: %s', team, error)

                data['status'] = 'DSQ'
                data['result'] = None
                team = team.replace(error, '').replace('.', '').strip()

                if data['place'] and not data["rank"]:
                    logging.debug(
                        'Transfer place to rank in dsq %s %s', data['place'], data["rank"])
                    data["rank"] = data['place']
                    data['place'] = ''
        data['team'] = team

        if data['place'] == 'в/к':
            data['status'] = 'EXH'
            data['place'] = None
        if data['place'] == 'д/к':
            data['status'] = 'DSQ'
            data['place'] = None

        return data
