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
    "дк": "DSQ",

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
pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+.?|в/?к|д/к\s+)?
    (?P<last_name>[А-Яа-яЁёë\-]+),?\s*
    (?P<first_name>[А-Яа-яЁёë\-]+)\s*
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)
    (?:\s+(?P<result>\d{1,2}(?:[:,\.]\d{1,2})?(?:[:,\.]\d{1,2})?))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


def find_coach_in_team(text: str):
    match = re.fullmatch(
        r'(?P<coach>([А-ЯЁ][а-яё]+(\s*|\.)[А-ЯЁ]\.[А-ЯЁ]\.?(?:\s*[,/]\s*[А-ЯЁ][а-яё]+ [А-ЯЁ]\.[А-ЯЁ]\.?)*))(?P<team>([а-яА-Я\d\s\."-A-Za-zVolkovSharksинностар дайвинг]+))', text)
    if match:
        return match.group('coach').strip(), match.group('team').strip()
    return None


class PointsIndividualModel(IndividualModelBase, name='bred'):
    def __init__(self, state: State):
        super().__init__(
            name='bred',
            state=state,
            regexes=[pattern],
            error_values=[]
        )

    def prerender(self, data):
        data['status'] = 'COMPLETED'
        team = find_coach_in_team(data['team'].strip())
        data['team'] = team[1] if team else input(f'{data['team']} >>> ')

        team = data['team']
        for error, status in ERROR_MAP.items():
            if error in team:
                logging.debug('Found dsq (%s) in team %s: %s',
                              status, team, error)

                data['status'] = status
                data['result'] = None
                team = team.replace(error, '').replace('.', '').strip()
        data['team'] = team
        return data
