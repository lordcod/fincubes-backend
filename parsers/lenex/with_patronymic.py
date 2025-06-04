import re
import logging
from models.state import State
from models.swim_types import *
from parsers.base import IndividualModelBase

pattern = re.compile(r"""
    ^\s*
    (?P<place>\d+\.|DSQ|DNS|EXH)?\s*
    (?P<last_name>[А-Яа-яЁё\-]+)\s+
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s+)?
    (?P<birth_year>\d{2,4})\s+
    (?P<team>.+?)\s+
    (?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)?
    \s*
    (?P<final_rank>(?:[123]|I{1,3}|МС|КМС|МСМК|ЗМС|[I]+(?:\s+юн?)?)\.?)?
    \s*$
""", re.VERBOSE | re.IGNORECASE)


class WithPatronymicIndividualModel(IndividualModelBase, name='with_patronymic'):
    def __init__(self, state: State):
        super().__init__(
            name='with_patronymic',
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
