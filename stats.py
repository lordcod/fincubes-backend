from collections import defaultdict
import json
import logging
import re
import uuid


with open("output/output_results.json", 'rb') as file:
    output = json.load(file)

stats = set()

for result in output['individual_results']:
    stats.add(result['team'])


with open('stats.json', 'wb+') as file:
    file.write(json.dumps(list(stats), ensure_ascii=False).encode())
