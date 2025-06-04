import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

# 6. ДАРЧИЕВА Моника Алана 12 Бодуроv_Team "СШ ВВС" 27.99 III
pattern = re.compile(r"""
    (?P<place>(\d+.?|DSQ|DNS|EXH)\s*)?
    (?P<last_name>[А-Яа-яЁё\-]+)\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    (?P<birth_year>\d{2,4})\s+
    (?P<team>.+?)
    (?:\s+(?P<result>(\d{1,2}[:.,])?\d{1,2}[:.,]\d{2}))?
    (?:\s+(?P<final_rank>(I{1,3}(?:\(ю\))?|I{1,3}(?:\s*юн)?|б\/?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<points>(?:лично|\d+)))?
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
        dsq = data.get("place") and data.get("place").strip() in ('DSQ', 'DNS')
        if not dsq:
            data['place'] = data.get(
                "place") and data.get("place").strip('. ')
        else:
            data['place'] = None
        return data
