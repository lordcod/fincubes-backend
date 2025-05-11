import re
import logging
from .state import State
from .swim_types import *

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


INPUT_TOKENS = {}
OUTPUT_TOKENS = {}

# Регулярные выражения

regex_normal = re.compile(r"""
    ^(?P<place>\d+)\s*
    (?P<rank>(?:[123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<result>\d{2}:\d{2},\d{2})\s*
    (?P<final_time>\d{2}:\d{2},\d{2})?\s*
    (?P<final_rank>(?:[123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)?\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


regex_dq = re.compile(r"""
    ^(?P<rank>(?:[123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<result>
        Фальстарт|
        не\sдопущен|
        не\sявился|
        Сошёл|
        Переныр\s?15м\.?|
        Нар\.\spr\.\sсор|
        Мед\sотвод|
        Переныр|
        снят\sза\sнар.пр.сор.|
        снята\sза\sнар.пр.сор.|
        снят\sнар.пр.сор.|
        снята\sнар.пр.сор.|
        снят[а-яА-Я0-9\s\.]+
    )\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


regex_dq_final_result = re.compile(r"""
    ^(?P<place>\d+)\s*
    (?P<rank>(?:[123]\sюн|[123]|КМС|МС|МСМК|ЗМС)?)\s+
    (?P<last_name>\S+)\s+
    (?P<first_name>\S+)\s+
    (?P<birth_year>\d{4})\s+
    (?P<team>.+?)\s+
    (?P<result>\d{2}:\d{2},\d{2})\s+
    (?P<disqualification_status>
        Фальстарт|
        не\sдопущен|
        не\sявился|
        Сошёл|
        Переныр\s?15м\.?|
        Нар\.\spr\.\sсор|
        Мед\sотвод|
        Переныр
    )\s*
    (?P<final_rank>(?:МС|МСМК|КМС|[123]))?\s*
    (?P<points>(?:лично|\d+))?$
""", re.VERBOSE | re.IGNORECASE)


class IndividualParser:
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        self.state = state

    def parse_individual_result(self, line):
        """Парсит строку с результатами индивидуального участника."""
        try:
            match = regex_normal.match(line)
            if match:
                self._process_normal_result(match, line)
                return

            match = regex_dq.match(line)
            if match:
                self._process_disqualified_no_result(match, line)
                return

            match = regex_dq_final_result.match(line)
            if match:
                self._process_disqualified_with_result(match, line)
                return

            logging.error(
                f"[INDIVIDUAL_PARSE_ERROR] Не удалось распарсить строку: {line}")
        except Exception as e:
            logging.error(f"[INDIVIDUAL_PARSE_ERROR] {line} - {e}")

    def _process_normal_result(self, match, line):
        """Обработка обычной строки с результатом."""
        place = match.group("place")
        rank = match.group("rank")
        last_name = match.group("last_name")
        first_name = match.group("first_name")
        birth_year = match.group("birth_year")
        team = match.group("team").strip()
        result = match.group("result")
        final_time = match.group("final_time") or ''
        final_rank = match.group("final_rank")
        points = match.group("points")

        if result in self.ERROR_VALUES:
            final_rank = result
            result = ""
            points = ""

        swr = SwimResult(
            distance=self.state.current_distance,
            place=place,
            rank=rank,
            last_name=last_name,
            first_name=first_name,
            birth_year=birth_year,
            team=team,
            result=result,
            final=final_time,
            final_rank=final_rank,
            points=points
        )

        self.state.current_athlete = swr
        self.state.individual_rows.append(swr)

    def _process_disqualified_no_result(self, match, line):
        """Обработка дисквалификации без результата."""
        rank = match.group("rank")
        last_name = match.group("last_name")
        first_name = match.group("first_name")
        birth_year = match.group("birth_year")
        team = match.group("team").strip()
        disqualification_status = match.group("result")
        points = match.group("points")

        swr = SwimResult(
            distance=self.state.current_distance,
            place="",
            rank=rank,
            last_name=last_name,
            first_name=first_name,
            birth_year=birth_year,
            team=team,
            result=disqualification_status,
            final="",
            final_rank="",
            points=points,
            dsq=True
        )

        self.state.current_athlete = swr
        self.state.individual_rows.append(swr)

    def _process_disqualified_with_result(self, match, line):
        """Обработка дисквалификации с результатом в финале."""
        place = match.group("place")
        rank = match.group("rank")
        last_name = match.group("last_name")
        first_name = match.group("first_name")
        birth_year = match.group("birth_year")
        team = match.group("team").strip()
        result = match.group("result")
        disqualification_status = match.group("disqualification_status")
        final_rank = match.group("final_rank")
        points = match.group("points")

        swr = SwimResult(
            distance=self.state.current_distance,
            place=place,
            rank=rank,
            last_name=last_name,
            first_name=first_name,
            birth_year=birth_year,
            team=team,
            result=result,
            final=disqualification_status,
            final_rank=final_rank,
            points=points,
            dsq_final=True
        )

        self.state.current_athlete = swr
        self.state.individual_rows.append(swr)
