from collections import defaultdict
import json
import re
import uuid


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


sportsmans = {}

for result in output['individual_results']:
    res = distance_header_re.fullmatch(result['distance'])
    style, distance, sex = res.groups()

    stroke, distance, sex = styles[style], int(distance), sexs[sex]

    key = (
        result['last_name'],
        result['first_name'],
        result['birth_year'],
        result['team'],
        result['rank'],
        sex
    )
    data = sportsmans.setdefault(key, [])

    points = result['points']
    if points is not None and points.isdigit():
        points = int(points)

    place = result['place']
    if place.isdigit():
        place = int(place)

    data.append({
        'stroke': stroke,
        'distance': distance,
        'result': result['result'],
        'final': result['final'],
        'place': place,
        'final_rank': result['final_rank'],
        'points': points,
        'record': result['record'],
        'dsq_final': result['dsq_final'],
        'dsq': result['dsq'],
    })


itogi = []
for sm, results in sportsmans.items():
    id = str(uuid.uuid4().int)
    res = {
        'parse_id': id,
        'last_name': sm[0],
        'first_name': sm[1],
        'birth_year': sm[2],
        'team': sm[3],
        'rank': sm[4],
        'sex': sm[5],
        'results': results
    }
    itogi.append(res)

with open('itogi.json', 'wb+') as file:
    file.write(json.dumps(itogi, ensure_ascii=False).encode())
