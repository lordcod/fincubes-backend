from parsers.base import IndividualModelBase
import re
import logging
from models.state import State
from models.swim_types import *

ERROR_MAP = {
    # ==========================
    # 🟥 DSQ — Disqualified (дисквалификация)
    # ==========================
    "нар. пр. сор.": "DSQ",
    "нар. пр. сор": "DSQ",
    "нар. Пр.сор": "DSQ",
    "нар.пр.сор.": "DSQ",
    "а нар.пр. сор.": "DSQ",
    "за нар.пр.сор": "DSQ",
    "за нар.пр.сор.": "DSQ",
    "а за нар.пр.сор.": "DSQ",
    "снята нар.пр.сор.": "DSQ",
    "снят нар.пр.сор.": "DSQ",
    "снята за нар.пр.сор.": "DSQ",
    "снят за нар.пр.сор.": "DSQ",
    "снята за нар пр. сор.": "DSQ",
    "снят за нар пр. сор.": "DSQ",
    "снят": "DSQ",
    "снята": "DSQ",
    "ст за нар пр сор": "DSQ",
    "ста за нар пр сор": "DSQ",
    "н/кас поворота": "DSQ",
    "фальстарт": "DSQ",
    "Фальстарт": "DSQ",
    "фальстар": "DSQ",
    "фальсатрт": "DSQ",
    "ф/с": "DSQ",
    "DQ": "DSQ",
    "DSQ": "DSQ",
    "д/к": "DSQ",
    "д\\к": "DSQ",
    "переныр": "DSQ",
    "переныр 15 м": "DSQ",
    "переныр 15м": "DSQ",
    "Переныр": "DSQ",
    "Переныр 15м": "DSQ",
    "Переныр 15м.": "DSQ",
    "Фальстарт лично": "DSQ",
    "Нар. пр. сор лично": "DSQ",
    "Фальстарт лично": "DSQ",  # продублировано, чтобы не потерять
    "Нар. пр. сор": "DSQ",
    "Снят": "DSQ",

    # ==========================
    # 🟦 DNS — Did Not Start (не стартовал)
    # ==========================
    "не стартовала": "DNS",
    "не стартовал": "DNS",
    "не старт": "DNS",
    "не старт.": "DNS",
    "не явился": "DNS",
    "неявка": "DNS",
    "DNS": "DNS",
    "н/я": "DNS",
    "н\\я": "DNS",
    "ня": "DNS",
    "Н/я": "DNS",

    # ==========================
    # 🟧 DNF — Did Not Finish (не финишировал / сошёл)
    # ==========================
    "сошёл": "DNF",
    "Сошёл": "DNF",
    "сошел": "DNF",
    "сошла": "DNF",
    "Сошёл лично": "DNF",
    "DNF": "DNF",

    # ==========================
    # 🟩 WDR — Withdrawn (мед. отвод / отказ)
    # ==========================
    "мед.отвод": "WDR",
    "мед. отвод": "WDR",
    "Мед отвод": "WDR",
    "медотвод": "WDR",
    "WDR": "WDR",

    # ==========================
    # 🟨 EXH — Exhibition / вне конкурса
    # ==========================
    "в/к": "EXH",
    "вк": "EXH",
    "в\\к": "EXH",
    "EXH": "EXH",

    # ==========================
    # 🟪 RJC — Rejected / не допущен
    # ==========================
    "не допущен": "RJC",
    "REJ": "RJC",
    "REJECTED": "RJC",
}
ERROR_MAP = dict(
    sorted(ERROR_MAP.items(), key=lambda item: len(item[0]), reverse=True)
)

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+.?|в/?к|д/к)?\s*
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?
    (?P<last_name>[А-Яа-яЁёë\-]+),?\s*
    (?P<first_name>[А-Яа-яЁёë\-]+)\s*
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s*)?
    (\d{2}\.?\s*\d{2}\.?\s*)?(?P<birth_year>\d{4})\s+
    (?P<team>.+?\s*)[1234]?
    (?:\s+(?P<result>\d{1,2}[:\.,]\d{1,2}(?:[:\.,]\d{1,2})?к?))?
    (?:\s+(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?\\?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<points>(?:лично|\d+|в\/к|д\\к|д\к|Д\\\\К)))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class PointsIndividualModel(IndividualModelBase, name='points'):
    def __init__(self, state: State):
        super().__init__(
            name='points',
            state=state,
            regexes=[pattern],
            error_values=[]
        )

    def prerender(self, data):
        data['status'] = 'COMPLETED'
        points = data['place'] and data['place'].lower()
        if points == 'в/к' or points == 'вк':
            data['status'] = 'EXH'
            data['place'] = None
            data['points'] = None
        if points == 'д/к' or points == 'д\\к':
            data['status'] = 'DSQ'
            data['place'] = None
            data['points'] = None

        team = data['team']
        for error, status in ERROR_MAP.items():
            if error in team:
                logging.debug('Found dsq (%s) in team %s: %s',
                              status, team, error)

                data['status'] = status
                data['result'] = None
                team = team.replace(error, '').replace('.', '').strip()

                if data['place'] and not data["rank"]:
                    logging.debug(
                        'Transfer place to rank in dsq %s %s', data['place'], data["rank"])
                    data["rank"] = data['place']
                    data['place'] = ''
        data['team'] = team

        return data
