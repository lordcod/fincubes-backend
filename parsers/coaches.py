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
    "дискв.",
    "дискв:"
]
ERROR_VALUES.sort(key=len, reverse=True)

#  30 49 3 Бердников Доминик 2015 Барнаул 01.12,00 01:18.31 Гудз О.В.
#  9 94 3 Коробейников Савелий 2011 III Бийск МБУ ДО "СШ "Дельфин" 03.55,00 04:12.15 I юн Рылова Н.А.,Черепанова О.В.
# 3 96 2 Кожевникова Вероника 2009 II Бийск МБУ ДО "СШ "Дельфин" 03.50,00 04:14.69 III Рылова Н.А.,Черепанова О.В.
pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+|в/?к\s+)?(\d+\s+\d+\s+)?
    (?P<last_name>[А-ЯЁа-яё\-]+)\s+
    (?P<first_name>[А-ЯЁа-яё\-]+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<coach>[А-ЯЁа-яё\-\s\.,:]+)?
    \s*
    ((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?
    (?P<team>[А-ЯЁа-яё0-9\s\"\/\-\']+?)\s*
    ((?P<prelim>\d{1,2}[:\.,]\d{1,2}(?:[:\.,]\d{1,2})?к?\s+))?
    ((?P<result>\d{1,2}[:\.,]\d{1,2}(?:[:\.,]\d{1,2})?к?\s+))?
    (?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС))?
    \s*$
""", re.VERBOSE)
pattern3 = re.compile(r"""
    ^\s*(?P<place>(?:\d+\s+){0,3})?(?P<last_name>[А-ЯЁа-яё\-]+)\s+(?P<first_name>[А-ЯЁа-яё\-]+)\s+(?P<birth_year>\d{4})\s+((?P<rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?(?P<team>[А-ЯЁа-яё0-9\s\"\/\-\']+?)\s+(?P<prelim>\d{1,2}(?:[:\.,]\d{1,2}){1,2})?\s*(?P<result>\d{1,2}(?:[:\.,]\d{1,2}){1,2})?\s*(?P<final_rank>(?:[123](\s*юн?\.?)?|I{1,3}(\s*юн?)?|б\/?р|КМС|МСМК|МС|ЗМС))?\s*(?P<coach>[А-ЯЁа-яё\-\s\.,]+)?\s*$
""", re.VERBOSE | re.IGNORECASE)


class CoachesIndividualModel(IndividualModelBase, name='coaches'):
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        super().__init__(
            name='coaches',
            state=state,
            regexes=[pattern, pattern3],
            error_values=ERROR_VALUES
        )

    def prerender(self, data):
        data['status'] = 'COMPLETED'

        place = data['place']
        if place:
            args = place.split()
            if len(args) == 2:
                data['place'] = None
            if len(args) in {3, 1}:
                data['place'] = args[0]

        data['place'] = data.get('place') and data['place'].lower()
        if data['place'] == 'в/к' or data['place'] == 'вк':
            data['status'] = 'EXH'
            data['place'] = None
        if data['place'] == 'д/к':
            data['status'] = 'DSQ'
            data['place'] = None

        coaches = data.get('coach', '')
        for error in ERROR_VALUES:
            if error in coaches:
                logging.debug('Found dsq in coaches %s: %s', coaches, error)

                data['status'] = 'DSQ'
                data['result'] = None
                coaches = coaches.replace(error, '').replace('.', '').strip()

                # if data['place'] and not data["rank"]:
                #     logging.debug(
                #         'Transfer place to rank in dsq %s %s', data['place'], data["rank"])
                #     data["rank"] = data['place']
                #     data['place'] = ''
        data['coach'] = coaches.strip()
        # data['team'] = data['coach']

        return data
