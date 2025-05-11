from collections import defaultdict
import json
import logging
import re
import uuid


with open("output_results.json", 'rb') as file:
    output = json.load(file)


data = defaultdict(list)
"Плавание в ластах - 100 метров Девушки 2011 -2012 г.р."
distance_header_re = re.compile(
    r"(.+) - (\d+) (метров|м)\s([А-Яа-я]+)\s+.+", re.IGNORECASE)

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
    'юниорки': 'F',
    'юниоры': 'M',
    'мальчики': 'M',
    'юноши': 'M',
}


sportsmans = {}
storage_dist = {}

for result in output['individual_results']:
    res = distance_header_re.fullmatch(result['distance'])
    if not res:
        if res not in storage_dist:
            print(result['distance'])
            storage_dist[res] = input('> ').split(';')
        style, distance, sex = storage_dist[res]
    else:
        style, distance, _, sex, *_ = res.groups()

    stroke, distance, sex = styles[style.lower().strip()], int(
        distance), sexs[sex.lower().strip()]

    key = (
        result['last_name'],
        result['first_name'],
        result['birth_year'],
        result['team'],
        result['rank'],
        sex
    )
    data = sportsmans.setdefault(key, [])

    if not result['dsq'] and not result['result']:
        print('Found not dsq and not rsl: %s', result)

    data.append({
        'stroke': stroke,
        'distance': distance,
        'result': result['result'],
        'final_rank': result['final_rank'],
        'record': result['record'],
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
