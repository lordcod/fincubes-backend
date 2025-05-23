import re
import logging
from .state import State
from .swim_types import *


class ScoreParser:
    def __init__(self, state: State):
        self.state = state

    def parse_team_score(self, line):
        match = re.match(r"^(\d+)\s+(.*?)\s+(\d+)$", line)
        if match:
            place, team_name, points = match.groups()
            self.state.team_score_rows.append(TeamScore(
                place=place, team_name=team_name, points=points))
        else:
            logging.error(f"[TEAM_SCORE_ERROR] {line}")
