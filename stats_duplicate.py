import json
import re


with open("output/2_itogi.json", "rb") as file:
    athletes = json.load(file)
with open('output/2_distances.json', 'rb') as file:
    distances = json.load(file)


def parse_time(time_str):
    """Parse time strings like '1:23.45' or '12,34'."""
    if not time_str:
        return None
    match = re.fullmatch(
        r'\s*((\d{1,2})[:\.,])?(\d{1,2})[:\.,](\d{1,2})к?\s*', time_str
    )
    if not match:
        return None
    _, minutes, seconds, millis = match.groups()
    minutes = int(minutes) if minutes else 0
    seconds = int(seconds)
    millis = int(millis)
    return minutes * 60 + seconds + millis / 100


count = 0
for athl in athletes:
    results = athl['results']
    reserved = set()
    for res in results:
        key = (res['stroke'], res['distance'], athl['gender'])
        if key in reserved:
            print(
                f"Дубликат: {athl['first_name']} {athl['last_name']} {athl['birth_year']} - {res['stroke']} {res['distance']} {athl['gender']}")
            count += 1
        else:
            reserved.add(key)
        if parse_time(res['result']) and (parse_time(res['result']) < 10 or parse_time(res['result']) > 300):
            print('Result error', res)

if count == 0:
    print("Дубликатов не найдено")
else:
    print(f"Всего дубликатов: {count}")
