from _reserved_team import locations
import json


with open("output/1_output_results.json", 'rb') as file:
    output = json.load(file)

stats = set()

for result in output['individual_results']:
    team = result['team']
    if team not in locations and team not in stats:
        print('Not found team:', team)
        stats.add(team)

print(stats)
