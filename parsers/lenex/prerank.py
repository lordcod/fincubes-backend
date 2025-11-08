import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+\.|DSQ|DNS|EXH|DNF)?\s*
    (?P<last_name>[А-Яа-яЁё\-\.]+),?\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    (?P<birth_year>\d{2,4})\s*
    (?P<rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?|ю[н]?|юн)?\.?))?\s*
    (?P<team>.+?)\s*
    (?:(?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?))?\s*
    (?:(?P<final_rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?|ю[н]?|юн)?.?)))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class PrerankIndividualModel(IndividualModelBase, name='prerank'):
    def __init__(self, state: State):
        super().__init__(
            name='prerank',
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
            data['place'] = place and place.strip('. ')
            data['status'] = 'COMPLETED'

        return data
