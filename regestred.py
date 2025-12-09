
from datetime import datetime
import json
import logging
import re
from collections import defaultdict
from typing import Any, Optional, Tuple

from _reserved_team import locations

# ================== CONSTANTS ==================

STROKES = {
    'ныряние': 'APNEA',
    'ныряние в ластах в длину': 'APNEA',
    'плавание в ластах': 'SURFACE',
    'плавание в классических ластах': 'BIFINS',
    'классические ласты': 'BIFINS',
    'подводное плавание': 'IMMERSION',
    'bifins': 'BIFINS',
    'плавание в ластах(моноласта)': 'SURFACE',
    'в классических ластах': 'BIFINS',
    'моноласта': 'SURFACE',
    'плавание в  ластах': 'SURFACE',
    'плавание в класичесских ластах': 'BIFINS',
    'плавание в классических':  'BIFINS',
    'плавяние в ластах': 'SURFACE',
    'плавание в  классических ластах': 'BIFINS',
    'пл\\л': 'SURFACE',
    'пл/л': 'SURFACE',
    'кл\\л': 'BIFINS',
    'кл/л': 'BIFINS',
    'ap': 'APNEA',
    'sf': 'SURFACE',
    'bf': 'BIFINS',
    'im': 'IMMERSION',
}

SEXES = {
    'женщины': 'F', 'девочки': 'F', 'девушки': 'F', 'юниорки': 'F', 'женщин': 'F', 'f': 'F', 'жещины': 'F', 'women':  'F', 'w':  'F',
    'мужчины': 'M', 'мальчики': 'M', 'юноши': 'M', 'юниоры': 'M', 'мужчин': 'M', 'm': 'M', 'men':  'M', 'мужчинны':  'M',
}

INVALID_DISTANCES = {}
PLACES = {}

# ================== HELPERS ==================


def normalize_rank(text: Optional[str]) -> Optional[str]:
    """Normalize a rank string to standard format."""
    if not text:
        return None

    text = text.lower().replace('i', 'I')
    text = re.sub(r"(взрослый|разряд|взр|вз|спортивный|юношеский)", "", text)
    text = text.replace('(', '').replace(')', '').replace("|", "I")
    text = re.sub(r"[.\s\-]", "", text)
    text = re.sub(r"ю", "юн", text)
    text = re.sub(r"юнн", "юн", text)
    text = text.replace('1', 'I').replace('2', 'II').replace('3', 'III')
    text = text.upper().replace('ЮН', 'юн')

    ranks = ["III", "МС", "I", "МСМК", "Iюн",
             "II", "IIIюн", "IIюн", "ЗМС", "КМС"]
    return text if text in ranks else None


def parse_time(time_str: Optional[str]) -> Optional[str]:
    """Parse time strings like '1:23.45' or '12,34,56'."""
    if not time_str:
        return None
    match = re.fullmatch(
        r'\s*((\d{1,2})[:\.,])?(\d{1,2})[:\.,](\d{1,2})к?\s*', time_str)
    if not match:
        logging.warning('Unexpected time format: %s', time_str)
        return None
    _, minutes, seconds, millis = match.groups()
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds)
    millis = int(millis)
    return f"{minutes:02}:{seconds:02}.{millis:02}"


def parse_time_offer_figna(time_str: Optional[str]) -> Optional[str]:
    if time_str.isdigit():
        if int(time_str) < 10:
            return f"{int(time_str):02}:00.00"
        return f"00:{int(time_str):02}.00"
    match = re.fullmatch(
        r'\s*((?P<minutes>\d{1,2}):)?((?P<seconds>\d{1,2}),)?((?P<mili>\d{1,2}))?\s*', time_str)
    if not match:
        return None
    minutes = match.group('minutes')
    seconds = match.group('seconds')
    mili = match.group('mili')
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds)
    mili = int(mili) if mili else 0
    if minutes == 0 and seconds < 10:
        print('request error', time_str, f"{seconds:02}:{mili:02}.00")
        return f"{seconds:02}:{mili:02}.00"
    return f"{minutes:02}:{seconds:02}.{mili:02}"


def parse_integer(value: Optional[str]) -> Optional[int]:
    if value == 'EXH':
        return value
    if isinstance(value, int):
        return value
    if value and value.isdigit():
        return int(value)
    return None


def parse_point(points: Optional[str]) -> str:
    if points and str(points).lower() == 'лично':
        return 'лично'
    val = parse_integer(points)
    return str(val) if val else ''


def handle_invalid_distance(distance: str) -> Tuple[str, int, str]:
    if distance not in INVALID_DISTANCES:
        print(f"Invalid distance format detected: {distance}")
        INVALID_DISTANCES[distance] = input("> ").split(';')
    return tuple(INVALID_DISTANCES[distance])


# ================== PARSER CLASS ==================


class RegisterParser:
    def __init__(
        self,
        results_file: str = "output/1_output_results.json",
        itogi_file: str = "output/2_itogi.json",
        distances_file: str = "output/2_distances.json",
    ):
        with open(results_file, 'r', encoding='utf-8') as f:
            self.output = json.load(f)

        self.itogi_file = itogi_file
        self.distances_file = distances_file

        self.results: defaultdict[Tuple[str,
                                        str, str], list] = defaultdict(list)
        self.athletes: dict = {}

        self.distance_regex = re.compile(
            '(?P<style>.+)\\s*-\\s*(?P<distance>\\d+)\\s*м(\\s*\\(.+\\))?,\\s*(?P<gender>[а-я]+)\\s*.+',
            re.IGNORECASE
        )

    def parse_distance(self, distance: str) -> Tuple[str, int, str, Optional[int], Optional[int]]:
        match = self.distance_regex.fullmatch(distance)
        if match:
            data = match.groupdict()
            style, dist, gender = data['style'], int(
                data['distance']), data['gender']
            min_age = max_age = None
        else:
            style, dist, gender = handle_invalid_distance(distance)
            min_age = max_age = None

        stroke = STROKES[style.lower().strip()]
        sex = SEXES[gender.lower().strip()]
        return stroke, int(dist), sex, min_age, max_age

    def parse_athlete(self, result: dict, gender: str) -> list:
        birth_year = str(result['birth_year'])
        if len(birth_year) == 2:
            if int(birth_year) >= datetime.now().year:
                birth_year = '19' + birth_year
            else:
                birth_year = '20' + birth_year
        result['birth_year'] = birth_year

        loc = locations.get(
            result.get('team', None), {'city': None, 'club': result.get('team')})
        if not result.get('city'):
            loc = locations[result['team']]
            result['city'], result['team'] = loc['city'], loc['club']
        # # !!! FATAL !!!
        # result['city'] = result['team'].strip()
        # result['team'] = None

        key = (result['last_name'], result['first_name'], result['birth_year'])
        self.athletes[key] = {
            "first_name": result['first_name'].title(),
            "last_name": result['last_name'].title(),
            'birth_year': birth_year,
            'team': result.get('team'),
            'city': result['city'],
            'rank': normalize_rank(result.get('rank')),
            'gender': gender,
            'athlete_id': result.get('athlete_id')
        }
        return self.results[key]

    def parse_result(self, data: list, stroke: str, distance: int, result: dict):
        if result.get('status') == 'DSQ':
            result['result'] = ''
        if result.get('status') == 'DSQ_FINAL':
            result['final'] = ''
        if result.get('status') == 'COMPLETED' and not result['result']:
            print('Not found result in:', result)

        time_key = parse_time(result.get('result'))
        key = (stroke, distance, time_key)
        if not result.get('place') and result.get('status') == 'COMPLETED':
            place = PLACES.get(key)
            if place:
                result['place'] = place
        elif result.get('place'):
            PLACES[key] = result.get('place')

        place = parse_integer(result.get('place') and result.get(
            'place').replace('.', '').strip())
        metadata = {}
        if attempts := result.get('attempts'):
            metadata['attempts'] = attempts

        data.append({
            'stroke': stroke,
            'distance': distance,
            'result': parse_time(result.get('result')),
            'final': parse_time(result.get('final')),
            'final_rank': normalize_rank(result.get('final_rank')),
            'record': result.get('record'),
            'status': result['status'],
            'place': place and str(place),
            'points': parse_point(result.get('points')),
            'metadata': metadata if metadata else None
        })

    def save_itogi(self):
        itogi = []
        for key, results in self.results.items():
            athlete_data = self.athletes[key]
            athlete_data['results'] = results
            itogi.append(athlete_data)
        with open(self.itogi_file, 'w', encoding='utf-8') as f:
            json.dump(itogi, f, indent=4, ensure_ascii=False)

    def save_distances(self, distances: list):
        with open(self.distances_file, 'w', encoding='utf-8') as f:
            json.dump(distances, f, indent=4, ensure_ascii=False)

    def run(self):
        logging.info("Processing %d individual results...",
                     len(self.output.get('individual_results', [])))
        for result in self.output.get('individual_results', []):
            stroke, distance, gender, _, _ = self.parse_distance(
                result['distance'])
            data = self.parse_athlete(result, gender)
            self.parse_result(data, stroke, distance, result)

        self.save_itogi()

        distances = []
        for dist in self.output.get('distances', []):
            key = self.parse_distance(dist)
            if key not in distances:
                distances.append(key)
        self.save_distances(distances)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    parser = RegisterParser()
    parser.run()
