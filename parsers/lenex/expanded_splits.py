import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+\.|DSQ|DNS|EXH)?\s*
    (?P<last_name>[А-Яа-яЁё\-]+),?\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    (?P<birth_year>\d{2,4})\s+
    (?P<team>.+?)
    (?=\s*\d{1,2}[:\.,]\d{2})
    \s*
    (?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)\s*
    (?P<final_rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?)?))?
    \s*
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
        dsq = data.get("place", '').strip() in ('DSQ', 'DNS')
        if not dsq:
            data['place'] = data.get(
                "place") and data.get("place").strip('. ')
        else:
            data['place'] = None
        return data
