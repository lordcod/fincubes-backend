from collections import defaultdict
import json
import re


with open("output_results.json", 'rb') as file:
    output = json.load(file)


data = defaultdict(list)

distance_header_re = re.compile(
    r"(.+) - (\d+) метров (.+)", re.IGNORECASE)

styles = {
    'Ныряние в ластах в длину': 'APNEA',
    'Плавание в ластах': 'SURFACE',
    'Плавание в классических ластах': 'BIFINS',
    'Подводное плавание': 'IMMERSION',
}
sexs = {
    'Женщины': 'F',
    'Мужчины': 'M',
}

for result in output['individual_results']:
    res = distance_header_re.fullmatch(result['distance'])
    style, distance, sex = res.groups()

    stroke, distance, sex = styles[style], int(distance), sexs[sex]
    data[(sex, stroke, distance)].append(result)

print(data)
