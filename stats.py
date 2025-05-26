from collections import defaultdict
import json
import logging
import re
import uuid


with open("output/output_results.json", 'rb') as file:
    output = json.load(file)

stats = set()
data = {}

for result in output['individual_results']:
    if '.' not in result['first_name']:
        data[result['last_name']] = result['first_name']
    stats.add(result['team'])

for result in output['individual_results']:
    if '.' in result['first_name']:
        result['first_name'] = data.get(result['last_name'])


with open("output/output_results.json", 'wb+') as file:
    file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())

with open('stats.json', 'wb+') as file:
    file.write(json.dumps(list(stats), indent=4, ensure_ascii=False).encode())
