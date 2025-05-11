import re
import logging
from .state import State
from .swim_types import *

# Список флагов ошибок
ERROR_VALUES = [
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
    "Фальстарт",
    "не допущен",
    "не явился",
    "Сошёл",
    "Нар. пр. сор",
    "Переныр 15м",
    "Мед отвод",
    "Переныр",
    "н/я",
    "снята за нар пр. сор.",
    "снят за нар пр. сор.",
    "снят",
    "DSQ", "Фальстарт", "не допущен", "не явился", "Сошёл",
    "Нар. пр. сор", "Переныр 15м", "Переныр 15м.", "Мед отвод", "Переныр",
    "Фальстарт лично", "Сошёл лично", "Нар. пр. сор лично",
    "сошла",
    "сошел"
]


class IndividualParser:
    def __init__(self, state: State):
        self.state = state

    def parse_individual_result(self, line):
        try:

            # Новое регулярное выражение для проверки строки
            pattern = r"^(?P<place>\d+)?\s*(?P<rank>([123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)\s*(?P<last_name>\S+)\s*(?P<first_name>\S+)\s*(?P<birth_year>\d{4})\s*(?P<team>.*?)\s*(?P<result>(\d{2}:\d{2},\d{1,2})?)\s*(?P<final_rank>([123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)?$"
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
                        team = team.replace(error, '').strip()

                        if data['place'] and not data["rank"]:
                            data["rank"] = data['place']
                            data['place'] = ''

                swr = SwimResult(
                    distance=self.state.current_distance,
                    place=data["place"],
                    rank=data["rank"] if data["rank"] else "",
                    last_name=data["last_name"],
                    first_name=data["first_name"],
                    birth_year=data["birth_year"],
                    team=team,
                    result=result if result else "",
                    final="",
                    final_rank=data["final_rank"] if data["final_rank"] else "",
                    record="",
                    dsq=dsq
                )
                self.state.current_athlete = swr
                self.state.individual_rows.append(swr)

            else:
                logging.error(
                    f"[INDIVIDUAL_PARSE_ERROR] Line does not match expected format: {line}")

        except Exception as e:
            logging.error(f"[INDIVIDUAL_PARSE_ERROR] {line} - {e}")
