# models/swim.py

import re
import json
import logging
from pathlib import Path
from .swim_types import *
from .state import State
from .relay import RelayParser
from .score import ScoreParser


class SwimResultsParser:
    def __init__(self, individual_parser, *, distance_header_re: str, input_file: Path, output_file: Path):
        self.input_file = input_file
        self.output_file = output_file

        self.state = State()

        # Инициализация парсеров
        self.relay_parser = RelayParser(self.state)
        self.individual_parser = individual_parser(self.state)
        self.score_parser = ScoreParser(self.state)

        self.lines = self.read_input_file()
        self.record_re = re.compile(
            r"рекорд (Мира|Европы|России)", re.IGNORECASE)
        self.distance_header_re = re.compile(
            distance_header_re, re.IGNORECASE)

    def read_input_file(self):
        with self.input_file.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def save_results(self):
        with open(self.output_file, "w", encoding="utf-8") as json_file:
            json.dump({
                "individual_results": [result.__dict__ for result in self.state.individual_rows],
                "relay_results": [result.__dict__ for result in self.state.relay_rows],
                "team_score": [result.__dict__ for result in self.state.team_score_rows],
                "distances": self.state.distances
            }, json_file, ensure_ascii=False, indent=4)

    def parse(self):
        for line in self.lines:
            if self.record_re.search(line):
                print(line)
                self.state.current_athlete.record = line
                logging.info(
                    f"[RECORD_GIVEN] {self.state.current_athlete}")
                continue

            if re.match(r"^КОМАНДНЫЙ ЗАЧЕТ$", line):
                self.state.in_team_score_block = True
                continue

            if self.state.in_team_score_block:
                self.score_parser.parse_team_score(line)
                continue

            if self.relay_parser.get_relay_start(line):
                self.state.in_relay_block = True
                continue
            elif self.distance_header_re.match(line):
                self.state.distances.append(line.strip())
                self.state.current_distance = line.strip()
                self.state.in_relay_block = False
                continue

            if self.state.in_relay_block:
                self.relay_parser.parse(line)
                self.relay_parser.save_relay()
                continue

            # if re.match(r"^\d+[^)]", line):
            self.individual_parser.parse_individual_result(line)

        self.save_results()
