import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+\.?|DSQ|DNS|EXH|DNF)?\s*
    (?P<last_name>[А-Яа-яЁё\-]+),?\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s*)?
    (?P<birth_year>\d{2,4})\s+
    (?P<team>.+?)?
    (?:\s+(?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?))?
    \s*
    (?:\s+(?P<final_rank>(?:МСМК|ЗМС|КМС|МС|I{1,3}|1|2|3)(?:\s*(?:\(?юн\)?|юн|ю)\.?)?)?)?
    (?P<points>(?:\s*\d+)\,?\d+)?
    \s*-?
    (((\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)\s*){2,})?
    $
""", re.VERBOSE | re.IGNORECASE)


class ExpandedSplitIndividualModel(IndividualModelBase, name='expanded_split'):
    def __init__(self, state: State):
        super().__init__(
            name='expanded_split',
            state=state,
            regexes=[pattern],
            error_values=[]
        )

    def prerender(self, data: dict) -> dict:
        place = (data.get("place", '') or '').strip()
        points = data.get('points') or None
        data['points'] = points and int(float(points.replace(',', '.')))
        if place in ('DSQ', 'DNS', 'DNF'):
            data['place'] = None
            data['status'] = 'DSQ'
        elif place == 'EXH':
            data['place'] = None
            data['status'] = 'EXH'
        else:
            data['place'] = place.strip('. ')
            data['status'] = 'COMPLETED'
        return data
