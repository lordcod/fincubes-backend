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
    r"\s*переныр 15\s*м\s*",
    "снят",
    "дискв."
]
ERROR_VALUES.sort(key=len, reverse=True)
# 1 КМС КАЛАБИНА София Олеговна 2009 ГАУ ДО НСО "СШОР ВВС" 00:19,28 КМС Степаненко Н.А.
# 24 3 ГРУШЕЦКИЙ Руслан Гасанович 2013 МАУДО СШОР "ЦЕНТР ВВС" 00:28,95 Патрушевы
# 6 1 ГОЛОВАНОВА Юлия Алексеевна 2009 ILIN TEAM 00:53,40 1 Ilin Team
# (?P<team>(.+?)?\s+)?

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+|в/к)?\s*
    (?P<last_name>[А-ЯЁа-яё\-]+)\s+
    (?P<first_name>[А-ЯЁа-яё\-]+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+
    ((?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?к?)\s+)?
    ((?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС))\s+)?
    (?P<coach>[a-zA-ZА-ЯЁа-яё\-\s\.]+)?
    \s*$
""", re.VERBOSE)
pattern2 = re.compile(r"""
    ^\s*
    (?P<place>\d+|в/?к)?\s*
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s*)?
    (?P<last_name>[А-Яа-яЁёë\-]+)\s+
    (?P<first_name>[А-Яа-яЁёë\-]+)\s*
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s+)?
    (?P<birth_year>\d{4})\s*
    (?P<team>("""+'|'.join(ERROR_VALUES)+r""")?\s*)?
    (?:\s+(?P<result>\d{1,2}[:]\d{2}(?:[.,]\d{1,2})?))?
    (?:\s+(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<coach>([а-яё\-\s\_\.]+))?)
    \s*$
""", re.VERBOSE | re.IGNORECASE)
pattern3 = re.compile(r"""
    ^м?\s*
    (?P<place>\d+|в/?к)?\s*
    (?P<last_name>[А-Яа-яЁёë\-]+)\s+
    (?P<first_name>[А-Яа-яЁёë\-]+)\s*
    (?P<birth_year>\d{4})\s*
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s*)?
    (?P<team>("""+'|'.join(ERROR_VALUES)+r""")?\s*)?
    (?:\s+(?P<result>\d{1,2}[:]\d{2}(?:[.,]\d{1,2})?))?
    (?:\s+(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<coach>([а-яё\-\s\_\.]+))?)
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class CoachesIndividualModel(IndividualModelBase, name='coaches_copy'):
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        super().__init__(
            name='coaches_copy',
            state=state,
            regexes=[pattern, pattern3],
            error_values=ERROR_VALUES
        )

    def prerender(self, data):
        data['status'] = 'COMPLETED'

        data['place'] = data['place'] and data['place'].lower()
        if data['place'] == 'в/к' or data['place'] == 'вк':
            data['status'] = 'EXH'
            data['place'] = None
        if data['place'] == 'д/к':
            data['status'] = 'DSQ'
            data['place'] = None

        team = data.get('team', '')
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
        data['team'] = team.strip()
        # data['team'] = data['coach']

        return data
