import re
import logging
from models.state import State
from models.swim_types import SwimResult


regex_normal = re.compile(r"""
    ^\s*
    (?P<place>\d+\.|DSQ|DNS|EXH)?\s*                                       # Место
    (?P<last_name>[А-Яа-яЁё\-]+)\s+                                        # Фамилия
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+                                     # Имя
    ((?P<patronymic>[А-Яа-яЁё\-]+)\s+)?                                      # Отчество (опционально)
    (?P<birth_year>\d{2,4})\s+                                             # Год рождения
    (?P<team>.+?)\s+                                                       # Команда (жадный захват, но остановка перед временем или разрядом)
    (?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)?                      # Результат (MM:SS, M:SS, MM.SS, и т.п.)
    \s*
    (?P<final_rank>(?:[123]|I{1,3}|МС|КМС|МСМК|ЗМС|[IVX]+(?:\s+юн?)?)\.?)?  # Разряд (опционально)
    \s*$
""", re.VERBOSE | re.IGNORECASE)


# BeSwimmerBot
# DNS Терехов Борис 2019 СК "Легенда" г. Домодедово
regex_normal = re.compile(r"""
    (?P<place>(\d+\s*|DSQ|DNS|EXH)\s*)?                 
    (?P<last_name>[А-Яа-яЁё\-]+)\s+                  
    (?P<first_name>[А-Яа-яЁё\-\.]+)\s+                    
    (?P<birth_year>\d{2,4})\s+                            
    (?P<team>.+?)                                          
    (?:\s+(?P<result>(\d{1,2}[:.,])?\d{1,2}[:.,]\d{2}))?
    (?:\s+(?P<final_rank>(I{1,3}(?:\(ю\))?|б\/?р|КМС|МСМК|МС|ЗМС)))?
    (?:\s+(?P<points>(?:лично|\d+)))?
    \s*$
""", re.VERBOSE | re.IGNORECASE)

# WITH PRERANK
# regex_normal = re.compile(r"""
#     ^\s*
#     (?P<place>\d+\.|DSQ|DNS|EXH)?\s*
#     (?P<last_name>[А-Яа-яЁё\-]+),?\s+
#     (?P<first_name>[А-Яа-яЁё\-\.]+)\s+
#     (?P<patronymic>[А-Яа-яЁё\-]+)?\s*
#     (?P<birth_year>\d{2,4})\s+
#     (?P<rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?)?))?\s*
#     (?P<team>.+?)
#     (?=\s*\d{1,2}[:\.,]\d{2})
#     \s*
#     (?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)\s*
#     (?P<final_rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?)?))?
#     \s*
#     (((\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)\s*){2,})?
#     $
# """, re.VERBOSE | re.IGNORECASE)

# regex_normal = re.compile(r"""
#     ^\s*
#     (?P<place>\d+\.|DSQ|DNS|EXH)?\s*                                  # Место
#     (?P<rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?)?))?\s*        # Разряд: Iю, I юн, 1ю и т.д.
#     (?P<last_name>[А-Яа-яЁё\-]+),?\s+                                 # Фамилия
#     (?P<first_name>[А-Яа-яЁё\-\.]+)\s+                                # Имя
#     (?P<birth_year>\d{2,4})\s+                                          # Год рождения
#     (?P<team>.+?)                                                     # Команда
#     (?=\s*\d{1,2}[:\.,]\d{2})                                         # Lookahead — перед результатом
#     \s*
#     (?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?)\s*               # Результат
#     (?P<final_rank>(?:МСМК|ЗМС|КМС|МС|[123I]{1,3}(?:\s*ю[н]?)?))?     # Итог. разряд
#     \s*$
# """, re.VERBOSE | re.IGNORECASE)


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
        data = match.groupdict()
        dsq = data.get("place").strip() in ('DSQ', 'DNS')
        print(data.get("place"), dsq)
        swr = SwimResult(
            distance=self.state.current_distance,
            place=not dsq and data.get(
                "place") and data.get("place").strip('. '),
            last_name=data.get("last_name"),
            first_name=data.get("first_name"),
            birth_year=data.get("birth_year"),
            team=data.get("team").strip(),
            result=data.get("result"),
            final_rank=data.get('final_rank'),
            dsq=dsq,
            rank=data.get("rank")
        )
        self.state.individual_rows.append(swr)
        self.state.current_athlete = swr
