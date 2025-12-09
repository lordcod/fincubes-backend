from _reserved_team import locations
import json

# Загрузка данных
with open("output/1_output_results.json", 'rb') as file:
    output = json.load(file)

data = {
    "СЕНИЧКИНА": "Александра",
    "ГОЛОВКИНА": "Александра",
}

stats = set()
not_found_teams = set()
not_found_names = []

for result in output['individual_results']:
    if result.get('prelim') and not result['result'] and result['status'] == 'COMPLETED':
        result['result'] = result['prelim']
    team = result['team']
    stats.add(team)
    if team not in locations:
        not_found_teams.add(team)
    if '.' not in result['first_name'] or '.' not in result['last_name']:
        data[result['last_name']] = result['first_name']

replacement_count = 0
for result in output['individual_results']:
    if '.' in result['first_name']:
        value = data.get(result['last_name'])
        if value is not None:
            result['first_name'] = value
            replacement_count += 1
        else:
            not_found_names.append(
                f"{result['last_name']} {result['first_name']}")
    if '.' in result['last_name']:
        value = data.get(result['first_name'])
        if value is not None:
            result['last_name'] = value
            replacement_count += 1
        else:
            not_found_names.append(
                f"{result['last_name']} {result['first_name']}")

records = sum(1 for result in output['individual_results'] if result['record'])

# Компактный лог
print(f"Не найденных команд: {not_found_teams}")
print(f"Имен заменено: {replacement_count}")
print(f"Не найдено имён для замены: {not_found_names}")
print(f"Записей с рекордом: {records}")
print(f"Всего результатов: {len(output['individual_results'])}")


with open('output/2_stats.json', 'wb+') as file:
    file.write(json.dumps(sorted(list(stats)),
               indent=4, ensure_ascii=False).encode())


if replacement_count != 0:
    with open("output/1_output_results.json", 'wb+') as file:
        file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())
