import json

with open("output/2_itogi.json", "rb") as file:
    athletes = json.load(file)

warnings_count = 0

for athl in athletes:
    results = athl.get('results', [])
    for res in results:
        has_result = res.get('result') not in (None, '', 0)
        status_completed = res.get('status') == 'COMPLETED'
        no_place = res.get('place') in (None, '', 0)

        if has_result and status_completed and no_place:
            print(
                f"Warning: {athl['first_name']} {athl['last_name']} ({athl['birth_year']}), "
                f"{res['stroke']} {res['distance']}м — результат есть, статус COMPLETED, но place отсутствует."
            )
            warnings_count += 1

if warnings_count == 0:
    print("Нарушений не найдено")
else:
    print(f"Всего предупреждений: {warnings_count}")
