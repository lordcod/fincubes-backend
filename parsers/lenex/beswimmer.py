import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase
#
# 1. ЕДАЛОВА Евгения 08 КМС МБУ ДО СШ 2 Таганрог 20.31 I
pattern = re.compile(r"""
    (?P<place>(\d+.?|DSQ|DNS|EXH|DNF)\s*)?
    (?P<last_name>[А-Яа-яЁё\-]+),?\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    (?P<birth_year>\d{2,4})\s+
    (?P<rank>(?:МСМК|ЗМС|КМС|МС|I{1,3}|1|2|3)(?:\s*(?:\(?юн\)?|юн|ю))?\.?\s+)?
    (?P<team>.+?)
    (?:\s+(?P<result>(\d{1,2}[:\.,])?\d{1,2}[:.,]\d{2}))?
    (?:\s+(?P<final_rank>(?:МСМК|ЗМС|КМС|МС|I{1,3}|1|2|3)(?:\s*(?:\(?юн?\)?|юн|ю))?)?)?
    (?:\s+(лично|\d+))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class BeswimmerIndividualModel(IndividualModelBase, name='beswimmer'):
    def __init__(self, state: State):
        super().__init__(
            name='beswimmer',
            state=state,
            regexes=[pattern],
            error_values=[]
        )

    def prerender(self, data: dict) -> dict:
        place = data.get("place") and data.get(
            "place").strip()
        if place in ('DSQ', 'DNS', 'DNF'):
            data['place'] = None
            data['status'] = 'DSQ'
        elif place == 'EXH':
            data['place'] = None
            data['status'] = 'EXH'
        else:
            data['place'] = place
            data['status'] = 'COMPLETED'
        return data
