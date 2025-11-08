import re
import logging
from typing import List, Optional
from models.state import State
from models.swim_types import SwimResult


class IndividualModelBase:
    __model_name__ = None

    def __init__(
        self,
        name: str,
        state: State,
        regexes: List[re.Pattern],
        error_values: List[str],
    ):
        if self.__model_name__ is None:
            type(self).__model_name__ = name
        self.name = name
        self.state = state
        self.regexes = regexes
        self.error_values = error_values

    def parse(self, line: str) -> Optional[SwimResult]:
        for regex in self.regexes:
            match = regex.match(line)
            if match:
                data = self.prerender(self.extract_result(match))
                if data is None:
                    return None
                return SwimResult(distance=self.state.current_distance,
                                  **self.prerender(self.extract_result(match)))

        logging.warning(f"Не удалось распарсить строку: {line}")
        return None

    def prerender(self, data: dict) -> dict:
        return data

    def extract_result(self, match: re.Match) -> dict:
        return match.groupdict()

    def __init_subclass__(cls, name: Optional[str] = None):
        cls.__model_name__ = name
