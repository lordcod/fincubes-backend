from collections import defaultdict
import json
import logging
import re


styles = {
    'ныряние в ластах в длину': 'APNEA',
    'плавание в ластах': 'SURFACE',
    'плавание в классических ластах': 'BIFINS',
    'подводное плавание': 'IMMERSION',
}
sexs = {
    'женщины': 'F',
    'мужчины': 'M',
    'девочки': 'F',
    'девушки': 'F',
    'мальчики': 'M',
    'юноши': 'M',
    'юниорки': 'F',
    'юниоры': 'M',
}
#  ============== REGEX ==============
#
#  r"(.+) - (\d+) (метров|м)?(.+)\(.+\)"

invalid = {}


def invalid_distance(distance):
    if distance not in invalid:
        print(distance)
        invalid[distance] = input("> ").split(';')
    return invalid[distance]


class RegisterParser:
    def __init__(
        self,
        results: str = "output/output_results.json",
        itogi: str = 'output/itogi.json'
    ):
        with open(results, 'rb') as file:
            self.output = json.load(file)
        self.itogi_file = itogi
        self.results = defaultdict(list)
        self.athletes = defaultdict(list)

        self.distance_re = re.compile(
            r"(.+) - (\d+) (метров|м)\s([А-Яа-я]+)\s+.+", re.IGNORECASE)
        self.time_regex = re.compile(r'(\d{2})[:\.,](\d{2})[:\.,](\d{1,2})')

    def parse_time(self, time_str):
        if not time_str:
            return
        try:
            match = self.time_regex.fullmatch(time_str)
            if not match:
                logging.warning(
                    'Expected time format, received: %s', time_str)
                return
            minutes, seconds, millis = match.groups()
            return f'{int(minutes):02}:{int(seconds):02}.{int(millis):02}'
        except Exception as e:
            logging.error("Failed to parse time: %s", e)
            raise

    def parse_integer(self, points: str):
        if isinstance(points, int):
            return points
        if not points:
            return
        assert points.isdigit(), 'Not is integer'
        return int(points)

    def parse_point(self, points: str):
        if points == 'лично':
            return points
        return self.parse_integer(points)

    def parse_distance(self, result):
        res = self.distance_re.fullmatch(result['distance'])
        if not res:
            style, distance, sex = invalid_distance(result['distance'])
        else:
            style, distance, _, sex, *_ = res.groups()
        stroke, distance, sex = styles[style.lower().strip()], int(
            distance), sexs[sex.lower().strip()]
        return stroke, distance, sex

    def parse_athlete(self, result, gender):
        if not isinstance(result['birth_year'], int) and not result['birth_year'].isdigit():
            raise TypeError('birth_year is not int')
        key = (
            result['last_name'],
            result['first_name'],
            result['birth_year'],
        )
        self.athletes[key] = {
            "first_name": result['first_name'].title(),
            "last_name": result['last_name'],
            'birth_year': str(result['birth_year']),
            'team': result['team'],
            'rank': result['rank'],
            'gender': gender
        }
        return self.results[key]

    def parse_result(self, data, stroke, distance, result):
        if result.get('dsq'):
            result['result'] = ''
        if result.get('dsq_final'):
            result['final'] = ''

        if not result['dsq'] and not result['result']:
            logging.warning('Found not dsq and not rsl: %s', result)

        data.append(dict(
            stroke=stroke,
            distance=distance,
            result=self.parse_time(result.get('result')),
            final=self.parse_time(result.get('final')),
            final_rank=result.get('final_rank'),
            record=result.get('record'),
            dsq=result.get('dsq', False),
            dsq_final=result.get('dsq_final', False),
            place=self.parse_integer(result.get('place')),
            points=self.parse_point(result.get('point')),
        ))

    def save_itogi(self):
        itogi = []
        for sm, results in self.results.items():
            res = self.athletes[sm]
            res['results'] = results
            itogi.append(res)

        with open(self.itogi_file, 'wb+') as file:
            file.write(json.dumps(
                itogi,
                ensure_ascii=False
            ).encode())

    def run(self):
        for result in self.output['individual_results']:
            style, distance, gender = self.parse_distance(result)
            data = self.parse_athlete(result, gender)
            self.parse_result(data, style, distance, result)
        self.save_itogi()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    reg = RegisterParser()
    reg.run()
