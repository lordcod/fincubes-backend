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
    "снят за нар.прав.сор.": "DSQ",
    "Д\\к": "DSQ",
    "Д\\К": "DSQ",
    "Н\\Я": "DSQ",
    "Д/К": "DSQ",
    "нар.пр.сор": "DSQ",
    "н.кас. поворота": "DSQ",
    "н/кас. пов.": "DSQ",

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
    "не явка": "DNS",

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
    "мед отвод": "WDR",

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
print(ERROR_MAP)
# 1	KMC	ЗАХАРОВА Елизавета	2012	Ярославская область	04:06,86	KMC	50
# 1 КМС ДВОЙНИШНИКОВА Мария 2012 Ярославская область 00:23,35 КМС 50
# (\d{2}\.?\s*\d{2}\.?\s*)? с датой
# 15 1 ГРЯКАЛOВА Елизавета 2005 Москва 00:25,73 1
# 11 1 ГРЯКАЛOВА Елизавета 2005 Москва 04:36,89 2
pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+.?|в/?к|д/к\s+)?
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?.?)?|б\\?\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?
    (?P<last_name>[А-Яа-яЁёëO\-]+),?\s*
    (?P<first_name>[А-Яа-яЁёë\-]+)\s*
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s*)?
    (\d{2}\.\d{2}\.)?(?P<birth_year>\d{4})\s+
    (?P<team>.+?)
    (?:\s+(?P<result>\d{1,2}[:\.,]\d{1,2}(?:[:\.,]\d{1,2})?))?
    (?:\s*(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?\\?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s*(?P<points>(?:лично|\d+|в/?к|д/?к)))?
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
        for error, status in ERROR_MAP.items():
            if not points:
                break
            if error in points:
                logging.debug('Found dsq (%s) in points %s: %s',
                              status, points, error)
                data['status'] = status
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
