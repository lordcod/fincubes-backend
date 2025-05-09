import re
import logging
from .state import State
from .swim_types import *

ERROR_VALUES = [
    "DSQ", "Фальстарт", "не допущен", "не явился", "Сошёл",
    "Нар. пр. сор", "Переныр 15м", "Мед отвод", "Переныр"
]


class IndividualParser:
    ERROR_VALUES = ERROR_VALUES

    def __init__(self, state: State):
        self.state = state

    def parse_individual_result(self, line):
        """Парсит строку с результатами индивидуального участника."""
        try:
            tokens = line.split()

            # Проверяем на наличие "Фальстарт" или других ошибок
            points, result, final = self.check_for_errors(tokens)

            # Если нет ошибок, продолжаем обычное извлечение данных
            if not result:
                place, rank, last_name, first_name, birth_year, result, final, final_rank, team, points = self.extract_tokens(
                    tokens)
            else:
                # В случае ошибки (например, фальстарт), извлекаем только ошибки
                place, rank, last_name, first_name, birth_year, result, final, final_rank, team, points = self.extract_error_tokens(
                    tokens)

            swr = SwimResult(
                distance=self.state.current_distance,
                place=place,
                rank=rank,
                last_name=last_name,
                first_name=first_name,
                birth_year=birth_year,
                team=team,
                result=result,
                final=final,
                final_rank=final_rank,
                points=points
            )
            self.state.current_athlete = swr
            self.state.individual_rows.append(swr)
        except Exception as e:
            logging.error(f"[INDIVIDUAL_PARSE_ERROR] {line} - {e}")

    def check_for_errors(self, tokens):
        """Проверяет строку на наличие ошибок, таких как 'Фальстарт'."""
        points = ""
        result = ""
        final = ""

        # Если строка содержит ошибку (например, Фальстарт)
        if any(error in tokens for error in self.ERROR_VALUES):
            result = "Фальстарт"  # Или другая ошибка
            final = result
            points = ""  # Очков не будет
        return points, result, final

    def extract_tokens(self, tokens):
        """Экстрагирует необходимые данные из токенов (нормальный случай)."""
        rank = self.extract_razryad(tokens[-2])
        points = tokens[-1] if tokens[-1].isdigit() or tokens[-1].lower() == "лично" else ""

        result, final = self.extract_time_and_result(tokens)
        result_index = tokens.index(result)

        # Находим индекс года рождения
        birth_year_index = next(i for i in range(
            result_index - 1, -1, -1) if re.match(r"\d{4}", tokens[i]))
        birth_year = tokens[birth_year_index]
        first_name = tokens[birth_year_index - 1]
        last_name = tokens[birth_year_index - 2]

        # Место — если первое значение — это число
        place = tokens[0] if tokens[0].isdigit() else ''

        # Команду берём между годом рождения и результатом
        if final:
            result_index -= 1
        team_tokens = tokens[birth_year_index + 1:result_index]
        team = " ".join(team_tokens).strip()

        return place, rank, last_name, first_name, birth_year, result, final, rank, team, points

    def extract_error_tokens(self, tokens):
        """Экстрагирует данные в случае ошибок (например, Фальстарт)."""
        place = tokens.pop(0) if tokens[0].isdigit(
        ) and tokens[0] not in ('1', '2', '3') else ''
        rank = tokens[0]
        last_name = tokens[1]
        first_name = tokens[2]
        birth_year = tokens[3]
        points = tokens[-1]

        # Ищем индекс ошибки
        error_index = next((i for i, t in enumerate(
            tokens) if t in self.ERROR_VALUES), None)

        # Сохраняем команду (до ошибки)
        team_tokens = tokens[4:error_index -
                             1 if place else error_index] if error_index else tokens[4:]
        team = " ".join(team_tokens).strip()

        # Определяем, была ли попытка (по наличию времени до ошибки)
        result = ""
        final = tokens[error_index] if error_index else ""

        # Попытка засчитана — значит до ошибки было время
        for i in range(error_index - 1, 3, -1):
            if re.match(r"\d{1,2}:\d{2},\d{2}", tokens[i]):
                result = tokens[i]
                break

        # Ищем разряд в конце строки
        final_rank = ""
        for token in reversed(tokens):
            if self.extract_razryad(token):
                final_rank = self.extract_razryad(token)
                break

        if not result and final:
            result = final
            final = ""
        if not (result and final):
            final_rank = ""
        return place, rank, last_name, first_name, birth_year, result, final, final_rank, team, points

    def extract_razryad(self, token):
        """Извлекает разряд из строки."""
        valid_ranks = ["МСМК", "КМС", "МС", "Разряд"]  # Разряды
        if token in valid_ranks:
            return token
        return ""  # Если не найден разряд, возвращаем пустую строку

    def extract_time_and_result(self, tokens):
        """Извлекает время и результат из токенов."""
        result = ""
        final = ""
        time_pattern = r"\d{1,2}:\d{2},\d{2}"

        # Ищем время и ошибки
        for i in range(len(tokens) - 1, 0, -1):
            if re.match(time_pattern, tokens[i]):
                if not result:
                    result = tokens[i]
                elif not final:
                    final = tokens[i]
                    break
            elif tokens[i] in self.ERROR_VALUES:
                if not result:
                    result = tokens[i]
                elif not final:
                    final = tokens[i]
                    break
        return result, final

    def extract_name_and_birth_year(self, tokens, result_index):
        """Извлекает фамилию, имя и год рождения."""
        birth_year_index = next(i for i in range(
            result_index - 1, -1, -1) if re.match(r"\d{4}", tokens[i]))
        birth_year = tokens[birth_year_index]
        first_name = tokens[birth_year_index - 1]
        last_name = tokens[birth_year_index - 2]
        return last_name, first_name, birth_year
