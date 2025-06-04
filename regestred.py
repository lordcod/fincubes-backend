from collections import defaultdict
import json
import logging
import re


styles = {
    'ныряние': 'APNEA',
    'ныряние в ластах в длину': 'APNEA',
    'плавание в ластах': 'SURFACE',
    'плавание в классических ластах': 'BIFINS',
    'классические ласты': 'BIFINS',
    'подводное плавание': 'IMMERSION',
    'bifins': 'BIFINS',
    'плавание в ластах(моноласта)': 'SURFACE',
    'в классических ластах': 'BIFINS'
}
sexs = {
    'женщины': 'F',
    'девочки': 'F',
    'девушки': 'F',
    'юниорки': 'F',
    'женщин':  'F',
    'f':  'F',


    'мужчины': 'M',
    'мальчики': 'M',
    'юноши': 'M',
    'юниоры': 'M',
    'мужчин': 'M',
    'юниорыи': 'M',
    'm': 'M',
}


#  ============== REGEX ==============
# r"(?P<style>.+) - (?P<distance>\d+) метров\s*(?P<gender>[а-я]+)"
# r"(?P<style>.+) - (?P<distance>\d+) метров\s*(?P<gender>[а-я]+)(\s*\(.+\))?"
# r"(?P<style>.+) – (?P<distance>\d+) м,\s*(?P<gender>[а-я]+)\s*(\(.+\))?"
# r"(?P<style>.+)- (?P<distance>\d+) м \([0-9а-я]+\)\s*(?P<gender>[а-я]+)\s*.+"
# r"(?P<style>.+) - (?P<distance>\d+) (метров|м)\s+(?P<gender>[а-яА-Я]+)\s*(\(.+\))?\s*"
# r"(?P<style>.+) - (?P<distance>\d+)\s*м,\s*(?P<gender>[а-я]+)"
# r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<style>.+) - (?P<distance>\d+) метров\s*.*"
#  r"Дистанция\s+(?P<distance>\d+)м\s+(?P<style>.+),\s*(?P<gender>[а-я]+)\s*"
# r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<style>.+) - (?P<distance>\d+)м.*"

# WA
# r"(?P<style>.+)\s*- (?P<distance>\d+)\s*м,\s*(?P<gender>[а-я]+)\s*(?P<min_age>\d{4})(-(?P<max_age>\d{4}))?.*"
# r"(9\s)?(?P<distance>\d+)(\s*м)?\s+(?P<style>.+?)\s+(?P<gender>[а-яё]+)\s+(?P<min_age>\d{4})(\-(?P<max_age>\d{4}))?.*"
#
# r"(?P<style>.+);(?P<distance>.+);(?P<gender>.+)"

invalid = {}


def invalid_distance(distance):
    if distance not in invalid:
        print(distance)
        invalid[distance] = input("> ").split(';')
    return invalid[distance]


class RegisterParser:
    def __init__(
        self,
        results: str = "output/1_output_results.json",
        itogi: str = 'output/2_itogi.json',
        distances: str = 'output/2_distances.json',
    ):
        with open(results, 'rb') as file:
            self.output = json.load(file)
        self.itogi_file = itogi
        self.distances_file = distances
        self.results = defaultdict(list)
        self.athletes = defaultdict(list)

        self.distance_re = re.compile(
            r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<distance>\d+)m\s(?P<style>[a-zа-я]+).*",
            re.IGNORECASE,
        )

        self.time_regex = re.compile(
            r'((\d{1,2})[:\.,])?(\d{1,2})[:\.,](\d{1,2})к?')

    def normalize_rank(self, text):
        if not text:
            return ''
        text = re.sub(r"(взрослый|разряд|взр|вз|спортивный|юношеский)",
                      "", text, flags=re.IGNORECASE)
        text = text.replace('(', '').replace(')', '')
        text = re.sub(r"[.\s\-]", "", text)
        text = re.sub(r"ю", "юн", text, flags=re.IGNORECASE)
        text = re.sub(r"юнн", "юн", text, flags=re.IGNORECASE)
        text = re.sub(r"1", "I", text)
        text = re.sub(r"2", "II", text)
        text = re.sub(r"3", "III", text)
        text = re.sub(r"кмс", "КМС", text)
        text = re.sub(r"мс", "МС", text)
        text = text.replace("|", "I")
        return text

    def parse_time(self, time_str):
        if not time_str:
            return
        try:
            match = self.time_regex.fullmatch(time_str)
            if not match:
                logging.warning(
                    'Expected time format, received: %s', time_str)
                return
            _, minutes, seconds, millis = match.groups()
            if not minutes:
                return f'00:{int(seconds):02}.{int(millis):02}'
            return f'{int(minutes):02}:{int(seconds):02}.{int(millis):02}'
        except Exception as e:
            logging.error("Failed to parse time: %s", e)
            raise

    def parse_integer(self, points: str):
        if points == 'EXH':
            return points
        if isinstance(points, int):
            return points
        if not points:
            return
        if not points.isdigit():
            return
        return int(points)

    def parse_point(self, points: str):
        if points and points.lower() == 'лично':
            return points.lower()
        points = self.parse_integer(points)
        return str(points) if points else None

    def parse_distance(self, distance):
        res = self.distance_re.fullmatch(distance)
        if not res:
            style, distance, sex = invalid_distance(distance)
            mna, mxa, age = None, None, None
        else:
            data = res.groupdict()
            style, distance, sex, mna, mxa, age = data['style'], data['distance'], data['gender'], data.get(
                'min_age'), data.get('max_age'), data.get('age')
        stroke, distance, sex, mna, mxa, age = styles[style.lower().strip()], int(
            distance), sexs[sex.lower().strip()], int(mna) if mna else None, int(mxa) if mxa else None, int(age) if age else None
        if age:
            if mna or mxa:
                logging.warning(
                    'Found mna and mxa in age %s %s %s', age, mna, mxa)
            mna = mxa = age
        else:
            if mna and not mxa:
                pass
                # mxa = mna
                # mna = None
        return stroke, distance, sex, mna, mxa

    def parse_athlete(self, result, gender):
        result['birth_year'] = str(result['birth_year'])
        if not result['birth_year'].isdigit():
            raise TypeError('birth_year is not int')
        if len(result['birth_year']) == 2:
            result['birth_year'] = '20'+result['birth_year']
        key = (
            result['last_name'],
            result['first_name'],
            result['birth_year'],
        )
        self.athletes[key] = {
            "first_name": result['first_name'].title(),
            "last_name": result['last_name'].title(),
            'birth_year': str(result['birth_year']),
            'team': result['team'],
            'rank': self.normalize_rank(result['rank']),
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
            final_rank=self.normalize_rank(result.get('final_rank')),
            record=result.get('record'),
            dsq=result.get('dsq', False),
            dsq_final=result.get('dsq_final', False),
            place=self.parse_integer(result.get(
                'place') and result.get(
                'place').replace('.', '').strip()),
            points=self.parse_point(result.get('points')),
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
                indent=4,
                ensure_ascii=False
            ).encode())

    def save_distances(self, distances):
        with open(self.distances_file, 'wb+') as file:
            file.write(json.dumps(
                distances,
                indent=4,
                ensure_ascii=False
            ).encode())

    def run(self):
        for result in self.output['individual_results']:
            style, distance, gender, am, ax = self.parse_distance(
                result['distance'])
            data = self.parse_athlete(result, gender)
            self.parse_result(data, style, distance, result)

        self.save_itogi()

        distances = []
        for dist in self.output['distances']:
            key = self.parse_distance(dist)
            if key not in distances:
                distances.append(key)

        self.save_distances(distances)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    reg = RegisterParser()
    reg.run()
