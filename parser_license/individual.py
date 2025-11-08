import json
import os
import sys


sys.path.append(os.getcwd())

if True:
    from parser_license.time_convert import time_to_seconds

SYSTEM = 'AUTO'  # MANUAL/AUTO
SKIPPED = []

with open("lsport/standards.json", 'rb') as file:
    standards = json.load(file)
with open("output/2_itogi.json", 'rb') as file:
    output = json.load(file)

for athlete in output:
    results = athlete['results']
    for res in results:
        if not res['result']:
            continue

        key = f"{SYSTEM}:{athlete['gender']}:{res['stroke']}:{res['distance']}"
        st = standards.get(key)
        if not st:
            continue

        result_time = time_to_seconds(res['result'])
        for time, code in st:
            if time >= result_time:
                if code in SKIPPED:
                    print('Skip', res, 'iso', code, 'in skipped')
                    continue
                res['final_rank'] = code
                # if code != res['final_rank']:
                #     print('Result error',  code, res['final_rank'], res)
                break

with open("output/2_itogi.json", 'wb+') as file:
    file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())
