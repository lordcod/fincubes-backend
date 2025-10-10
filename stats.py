from collections import defaultdict
import json
import logging
import re
from sys import orig_argv
import uuid


with open("output/1_output_results.json", 'rb') as file:
    output = json.load(file)

stats = set()
data = {
    "СЕНИЧКИНА": "Александра",
    "ГОЛОВКИНА": "Александра",
}

for result in output['individual_results']:
    if '.' not in result['first_name']:
        data[result['last_name']] = result['first_name']
    stats.add(result['team'])

for result in output['individual_results']:
    if '.' in result['first_name']:
        value = data.get(
            result['last_name'])
        if value is not None:
            print('Found', result['last_name'],
                  result['first_name'], ':', value)
            result['first_name'] = value
        else:
            print('NOT FOUND', result['last_name'], result['first_name'])

records = 0
for result in output['individual_results']:
    if result['record']:
        records += 1
print('Records count:', records)

with open("output/1_output_results.json", 'wb+') as file:
    file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())

with open('output/2_stats.json', 'wb+') as file:
    file.write(json.dumps(list(stats), indent=4, ensure_ascii=False).encode())
