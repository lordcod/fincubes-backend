import re
import logging
from models.state import State
from models.swim_types import *

ERROR_VALUES = [
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
    "фальстар"
]


class IndividualParser:
    def __init__(self, state: State):
        self.state = state

    def parse_individual_result(self, line):
        try:

            pattern = re.compile(r"""
                ^\s*
                (?P<place>\d+|в/к)?\s*
                ((?P<rank>(?:[123]\s*юн\.?|[123]|I\s*юн|II\s*юн|III\s*юн|I|II|III|б\/?р|КМС|МСМК|МС|ЗМС)?)\s+)?
                (?P<last_name>[А-Яа-яЁёë\-]+)\s+
                (?P<first_name>[А-Яа-яЁёë\-]+)\s+
                (?P<birth_year>\d{4})\s+
                (?P<team>.+?\s*)
                (?:\s+(?P<result>\d{1,2}[:\.,]\d{2}(?:[:\.,]\d{1,2})?к?))?
                (?:\s+(?P<final_rank>(?:[123]\s*юн\.?|[123]|I\s*юн|II\s*юн|III\s*юн|I|II|III|б\/?р|КМС|МСМК|МС|ЗМС)))?
                (?:\s+(?P<points>(?:лично|\d+)))?
                \s*$
            """, re.VERBOSE | re.IGNORECASE)
            match = re.match(pattern, line)

            if match:
                data = match.groupdict()

                team = data['team']
                result = data["result"]
                dsq = False

                for error in ERROR_VALUES:
                    if error in team:
                        logging.debug('Found dsq in team %s: %s', team, error)

                        dsq = True
                        result = error
                        team = team.replace(error, '').replace('.', '').strip()

                        if data['place'] and not data["rank"]:
                            logging.debug(
                                'Transfer place to rank in dsq %s %s', data['place'], data["rank"])
                            data["rank"] = data['place']
                            data['place'] = ''

                swr = SwimResult(
                    distance=self.state.current_distance,
                    place=data["place"],
                    rank=data["rank"] if data.get("rank") else "",
                    last_name=data["last_name"],
                    first_name=data["first_name"],
                    birth_year=data["birth_year"],
                    team=team,
                    result=result if result else "",
                    final="",
                    final_rank=data["final_rank"] if data.get(
                        "final_rank") else "",
                    record="",
                    dsq=dsq,
                    points=data.get('points')
                )
                self.state.current_athlete = swr
                self.state.individual_rows.append(swr)

            else:
                logging.error(
                    f"[INDIVIDUAL_PARSE_ERROR] Line does not match expected format: {line}")

        except Exception as e:
            logging.error(
                f"[INDIVIDUAL_PARSE_ERROR] {line} - [{type(e).__name__}] {e}")
