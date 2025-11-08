import re
import logging
from .state import State
from .swim_types import *

# r".+ - \d+ х \d+ .+"
# r".+Эстафета.+"
# r".*Эстафетное плавание.*"
# r"Дистанция\s+\d+,?.+4 х.+"


class RelayParser:
    def __init__(self, state: State):
        self.state = state
        self.relay_start_re = re.compile(
            r".*4 Х \d+.+", re.IGNORECASE)
        self.relay_swimmer_re = re.compile(r"^\d\)", re.IGNORECASE)

    def parse(self, line):
        match = re.match(
            r"^(\d+)\s+(.*?)\s+(\d{2}:\d{2},\d{2})\s+(лично|\d+)$", line)
        if match:
            self.parse_relay_info(match)
        elif re.match(r"^\d\)", line):
            self.parse_relay_swimmer(line)
        else:
            logging.error(f"[RELAY_HEADER_ERROR] {line}")

    def get_relay_start(self, line):
        match = self.relay_start_re.search(line)
        if match:
            self.state.current_distance = line
            return True
        return False

    def parse_relay_info(self, match):
        place, team_name, team_result, points = match.groups()
        self.state.current_relay_info = RelayResult(
            self.state.current_distance,
            team_name,
            place,
            team_result,
            points
        )
        self.state.relay_swimmers = []

    def parse_relay_swimmer(self, line):
        try:
            parts = line.split()
            idx = int(parts[0][0])
            last_name = parts[1]
            first_name = parts[2]
            birth_year = parts[3]
            rank = parts[4]
            time = parts[5] if len(parts) > 5 else ""

            self.state.relay_swimmers.append({
                "order": idx,
                "lastname": last_name,
                "firstname": first_name,
                "birth_year": birth_year,
                "rank": rank,
                "result": time
            })
        except Exception:
            logging.error(f"[RELAY_SWIMMER_ERROR] {line}")

    def save_relay(self):
        if len(self.state.relay_swimmers) == 4 and self.state.current_relay_info:
            relay_info = self.state.current_relay_info
            relay_info.swimmers = self.state.relay_swimmers
            self.state.relay_rows.append(relay_info)
            self.state.relay_team_rows.append(self.state.current_relay_info)
            self.state.relay_swimmers = []
