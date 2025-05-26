import re
import logging
from models.state import State
from models.swim_types import SwimResult

regex_normal = re.compile(r"""
    (?P<place>(\d+\.\s*|DSQ|DNS|EXH)\s*)?                
    (?P<last_name>[А-Яа-яЁё\-]+)\s+                 
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+                 
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s*)?                  
    (?P<birth_year>\d{2,4})\s+                           
    (?P<team>[\w\s\."\'\(\)]+?)\s+           
    (?P<result>(\d{1,2}[:.,])?\d{1,2}[:.,]\d{2})
    (\s+(?P<final_rank>(?:[123]|МС|КМС|МСМК|ЗМС|[IVX]+(?:\s+юн)?)?))?\s* 
""", re.VERBOSE | re.IGNORECASE)


class IndividualParser:
    def __init__(self, state: State):
        self.state = state

    def parse_individual_result(self, line: str):
        try:
            match = regex_normal.match(line)
            if match:
                self._process_normal_result(match)
                return

            logging.error(
                f"[INDIVIDUAL_PARSE_ERROR] Не удалось распарсить строку: {line}")
        except Exception as e:
            logging.exception(f"[INDIVIDUAL_PARSE_ERROR] {line} - {e}")

    def _process_normal_result(self, match,):
        dsq = match.group("place") in ('DSQ', 'DNS')
        swr = SwimResult(
            distance=self.state.current_distance,
            place=not dsq and match and match.group("place").strip('.\s'),
            last_name=match.group("last_name"),
            first_name=match.group("first_name"),
            birth_year=match.group("birth_year"),
            team=match.group("team").strip(),
            result=match.group("result"),
            final_rank=match.group('final_rank'),
            dsq=dsq
        )
        self.state.individual_rows.append(swr)
        self.state.current_athlete = swr

    def _process_disqualified_no_result(self, match):
        swr = SwimResult(
            distance=self.state.current_distance,
            place="",
            rank=match.group("rank"),
            last_name=match.group("last_name"),
            first_name=match.group("first_name"),
            birth_year=match.group("birth_year"),
            team=match.group("team").strip(),
            result=match.group("result"),
            final="",
            final_rank="",
            points=match.group("points"),
            dsq=True,
        )
        self.state.individual_rows.append(swr)
        self.state.current_athlete = swr
