import re
import pandas as pd
import json
import logging
from pathlib import Path
from .swim_types import *
from .state import State
from .individual import IndividualParser
from .relay import RelayParser
from .score import ScoreParser


class SwimResultsParser:
    def __init__(self, input_file: Path, output_file: Path, error_log_path: Path, file_format='excel'):
        self.input_file = input_file
        self.output_file = output_file
        self.error_log_path = error_log_path
        self.file_format = file_format  # Можно передавать 'excel' или 'json'

        self.state = State()

        # Инициализация парсеров
        self.relay_parser = RelayParser(self.state)
        self.individual_parser = IndividualParser(self.state)
        self.score_parser = ScoreParser(self.state)

        self.lines = self.read_input_file()

        self.record_re = re.compile(
            r"(рекорд Мира|Европы|России)", re.IGNORECASE)
        self.distance_header_re = re.compile(
            r".+ - \d+ метров.+", re.IGNORECASE)
        # Настройка логирования
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.error_log_path,
                                    mode="w", encoding='utf-8'),
                logging.StreamHandler()  # Вывод в консоль
            ]
        )

    def read_input_file(self):
        with self.input_file.open(encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def save_results(self):
        # Сохраняем результаты в excel или json
        if self.file_format == "excel":
            with pd.ExcelWriter(self.output_file) as writer:
                pd.DataFrame([result.__dict__ for result in self.state.individual_rows]).to_excel(
                    writer, sheet_name="individual_results", index=False)
                pd.DataFrame([result.__dict__ for result in self.state.relay_rows]).to_excel(
                    writer, sheet_name="relay_results", index=False)
                pd.DataFrame([result.__dict__ for result in self.state.team_score_rows]).to_excel(
                    writer, sheet_name="team_score", index=False)
        else:
            with open(self.output_file, "w", encoding="utf-8") as json_file:
                json.dump({
                    "individual_results": [result.__dict__ for result in self.state.individual_rows],
                    "relay_results": [result.__dict__ for result in self.state.relay_rows],
                    "team_score": [result.__dict__ for result in self.state.team_score_rows]
                }, json_file, ensure_ascii=False, indent=4)

    def parse(self):
        for line in self.lines:
            if self.record_re.search(line):
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
