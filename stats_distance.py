from _reserved_team import locations
import json

with open("output/1_output_results.json", 'rb') as file:
    output = json.load(file)

distances = []

for result in output['individual_results']:
    distances.append(result['distance'])


output['distances'] = list(dict.fromkeys(distances).keys())
with open("output/1_output_results.json", 'wb+') as file:
    file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())
