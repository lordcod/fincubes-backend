import contextlib
import json
from xml.sax import default_parser_list
import aiohttp
import asyncio

# Упорядоченный список разрядов от высшего к младшему

athlete_api_url = 'http://localhost:8000/athletes'
RANK_ORDER = {
    'МС': 0,
    'КМС': 1,
    '1': 2,
    '2': 3,
    '3': 4,
    '1 юн': 5,
    '2 юн': 6,
    '3 юн': 7,
    'I': 2,
    'II': 3,
    'III': 4,
    'I юн': 5,
    'II юн': 6,
    'III юн': 7
}


def is_rank_higher(new_rank: str, old_rank: str) -> bool:
    try:
        return RANK_ORDER[new_rank] < RANK_ORDER[old_rank]
    except (ValueError, KeyError):
        return False


async def update_athlete_if_needed(session: aiohttp.ClientSession, athlete_data: dict, headers: dict):
    athlete = athlete_data["athlete"]
    current_rank = athlete["license"]
    new_ranks = athlete_data["license"]

    # Находим самый высокий из новых разрядов
    new_rank = sorted(new_ranks, key=lambda r: RANK_ORDER.index(r))[0]

    if is_rank_higher(new_rank, current_rank):
        updated_data = {
            "last_name": athlete["last_name"],
            "first_name": athlete["first_name"],
            "birth_year": athlete["birth_year"],
            "club": athlete["club"],
            "license": new_rank,
            "gender": athlete["gender"]
        }
        url = f"{athlete_api_url}/{athlete['id']}"
        async with session.put(url, json=updated_data, headers=headers) as response:
            data = await response.json()
            if not response.ok:
                print("Ошибка обновления:", data)
            response.raise_for_status()
            return data
    else:
        print(
            f"{athlete['last_name']} {athlete['first_name']}: разряд не обновляется ({current_rank} >= {new_rank})")
        return None


async def process_athletes(data_list: list, headers: dict):
    async with aiohttp.ClientSession() as session:
        tasks = [
            update_athlete_if_needed(session, item, headers)
            for item in data_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5OTk5MjY5MDEwZGRkZEBnbWFpbC5jb20iLCJleHAiOjE3NDgyODcyNDR9.a2ZkP16ehtKJJdY9dyNnRewIoxyvqD7HdKs_UwbnBQY"
    headers = {
        'Authorization': 'Bearer '+token
    }

    with open('output/requests.json', 'rb') as file:
        data = json.load(file)
    data_list = []
    for req in data.values():
        if 'license' in req:
            data_list.append(req)
    print('Start refresh', len(data_list), 'athletes')
    asyncio.run(process_athletes(data_list, headers))
