import json
import aiohttp
import asyncio
from __config__ import headers


async def create_distances(session: aiohttp.ClientSession, competition_id, distance_data, headers):
    url = f'https://localhost:8000/competitions/{competition_id}/distances'
    async with session.post(url, json=distance_data, headers=headers) as response:
        data = await response.json()
        if not response.ok:
            print("Ошибка обновления:", data)
        response.raise_for_status()
        return data


async def process_distances(data_list: list, comp_id, headers: dict):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for order, item in enumerate(data_list):
            data = {
                "stroke": item[0],
                "distance": item[1],
                "gender": item[2],
                "order": order,
                "category": "",
                "min_year": item[3],
                "max_year": item[4]
            }
            task = create_distances(session, comp_id, data, headers)
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

if __name__ == '__main__':
    comp_id = int(input("Competition id: "))

    with open('output/distances.json', 'rb') as file:
        data = json.load(file)

    print('Start create', len(data), 'distances')
    asyncio.run(process_distances(data, comp_id, headers))
