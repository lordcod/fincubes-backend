# models/swim.py

from math import dist
import re
import json
import logging
from pathlib import Path
from .swim_types import *
from .state import State
from .relay import RelayParser
from parsers.base import IndividualModelBase


class SwimResultsParser:
    def __init__(
        self,
        individual_parser: type[IndividualModelBase],
        *,
        distance_header_re: str,
        input_file: Path,
        output_file: Path
    ):
        self.input_file = input_file
        self.output_file = output_file

        self.state = State()

        # Инициализация парсеров
        self.relay_parser = RelayParser(self.state)
        self.individual_parser = individual_parser(self.state)

        self.lines = self._read_input_file()

        # Регулярные выражения
        self.record_re = re.compile(
            r"рекорд (Мира|Европы|России)", re.IGNORECASE)
        self.distance_header_re = re.compile(distance_header_re, re.IGNORECASE)

    def _read_input_file(self) -> list[str]:
        """Чтение входного файла построчно, пропуск пустых строк."""
        with self.input_file.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def _save_results(self):
        """Сохранение результатов в JSON."""
        def serialize_row(row):
            return row.__dict__ if row is not None else None

        data = {
            "individual_results": [serialize_row(r) for r in self.state.individual_rows if r is not None],
            "relay_results": [serialize_row(r) for r in self.state.relay_rows],
            "team_score": [serialize_row(r) for r in self.state.team_score_rows],
            "distances": self.state.distances
        }

        with self.output_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def parse(self):
        """Главный метод парсинга файла."""
        for line in self.lines:
            # Обработка рекорда
            if self.record_re.search(line) and not self.state.in_relay_block:
                if self.state.current_athlete:
                    self.state.current_athlete.record = line
                    logging.info(
                        f"[RECORD_GIVEN] {self.state.current_athlete}")
                continue

            accept = re.fullmatch(
                r'(Мужчины|Женщины|Юниорки|Юниоры|Девушки|Юноши|девочки|мальчики)\s*\d{2}.+', line, re.IGNORECASE)
            if accept and not self.state.in_relay_block:
                distance = self.state.distances[-1]
                if self.state.current_category:
                    distance = distance.replace(
                        self.state.current_category, '').replace(',', '').strip()

                self.state.current_category = line
                self.state.current_distance = distance + ', ' + line
                self.state.distances.append(self.state.current_distance)
                continue

            if self.relay_parser.get_relay_start(line):
                self.state.in_relay_block = True
                continue

            if self.distance_header_re.match(line):
                self.state.distances.append(line.strip())
                self.state.current_distance = line.strip()
                self.state.in_relay_block = False
                continue

            if self.state.in_relay_block:
                self.relay_parser.parse(line)
                self.relay_parser.save_relay()
                continue

            swr = self.individual_parser.parse(line)
            if swr:
                self.state.current_athlete = swr
                self.state.individual_rows.append(swr)

        self._save_results()
