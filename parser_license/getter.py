import json
import os
import sys
import aiohttp
import asyncio


sys.path.append(os.getcwd())

if True:
    from parser_license.time_convert import time_to_seconds
    from __config__ import headers


async def get_standards(session: aiohttp.ClientSession):
    url = 'https://api.fincubes.ru/public/server/standard/'
    async with session.get(url, headers=headers) as response:
        data = await response.json()
        if not response.ok:
            print("Ошибка обновления:", data)
        response.raise_for_status()
        return data


async def process_standards():
    async with aiohttp.ClientSession() as session:
        standards = await get_standards(session)
    results: dict[str, list] = {}
    for st in standards:
        key = f"{st['type']}:{st['gender']}:{st['stroke']}:{st['distance']}"
        l = results.setdefault(key, [])
        l.append([time_to_seconds(st['result']), st['code']])
    for l in results.values():
        l.sort(key=lambda item: item[0])
    return results


if __name__ == '__main__':
    print('Start get standards')
    res = asyncio.run(process_standards())
    print('Response:', res)
    with open("lsport/standards.json", 'wb+') as file:
        file.write(json.dumps(res, indent=4, ensure_ascii=False).encode())
