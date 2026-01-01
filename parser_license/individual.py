import json
import os
import sys


sys.path.append(os.getcwd())

if True:
    from parser_license.time_convert import time_to_seconds

SYSTEM = 'AUTO'  # MANUAL / AUTO
MODE = 'CHECK'  # CHECK / AUTO

SKIPPED = []
WARNINGS = ['МСМК']

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
                if code in WARNINGS:
                    print(
                        f"⚠ | {res['stroke']} {res['distance']}м | {res['result']} → предупреждение (код {code})")
                if code in SKIPPED:
                    print(
                        f"⏭ | {res['stroke']} {res['distance']}м | {res['result']} → пропущено (код {code})")
                    continue

                if MODE == 'AUTO':
                    res['final_rank'] = code
                elif MODE == 'CHECK':
                    final_rank = res.get('final_rank')
                    if final_rank != code:
                        print(
                            f"⚠ | {res['stroke']} {res['distance']}м | {res['result']} → должен быть код {code}, стоит {final_rank}")
                break

with open("output/2_itogi.json", 'wb+') as file:
    file.write(json.dumps(output, indent=4, ensure_ascii=False).encode())
