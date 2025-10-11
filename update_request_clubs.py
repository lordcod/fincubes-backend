from collections import defaultdict
import json
import aiohttp
import asyncio
from __config__ import headers

athlete_api_url = 'https://api.fincubes.ru/admin/athlete'


async def update_athlete_if_needed(session: aiohttp.ClientSession, athlete_data: dict, headers: dict):
    athlete = athlete_data["athlete"]
    update_fields = {}

    # Проверка и обновление клуба
    if "club" in athlete_data:
        old_club, new_club = athlete_data["club"]
        if (athlete["club"] in [None, "", "null"]) and new_club not in [None, "", "null"]:
            update_fields["club"] = new_club

    # Проверка и обновление города
    if "city" in athlete_data:
        old_city, new_city = athlete_data["city"]
        if (athlete["city"] in [None, "", "null"]) and new_city not in [None, "", "null"]:
            update_fields["city"] = new_city

    if not update_fields:
        print(
            f"{athlete['last_name']} {athlete['first_name']}: нет данных для обновления.")
        return None

    # Если есть, что обновлять
    updated_data = {
        "last_name": athlete["last_name"],
        "first_name": athlete["first_name"],
        "birth_year": athlete["birth_year"],
        "license": athlete["license"],
        "gender": athlete["gender"],
        "club": update_fields.get("club", athlete["club"]),
        "city": update_fields.get("city", athlete["city"]),
    }

    print(
        f"{athlete['last_name']} {athlete['first_name']}: обновление {', '.join(update_fields.keys())} → {update_fields}"
    )

    url = f"{athlete_api_url}/{athlete['id']}"
    async with session.put(url, json=updated_data, headers=headers) as response:
        data = await response.json()
        if not response.ok:
            print("Ошибка обновления:", data)
        response.raise_for_status()
        return data


async def process_athletes(data_list: list, headers: dict):
    async with aiohttp.ClientSession() as session:
        tasks = [
            update_athlete_if_needed(session, item, headers)
            for item in data_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        responses = list(
            filter(bool, filter(lambda item: not isinstance(
                item, Exception), results))
        )
        print('Responses', responses)
        print(f'Обновилось {len(responses)} записей')


if __name__ == '__main__':
    with open('output/3_requests.json', 'rb') as file:
        data = json.load(file)

    data_list = []
    for req in data.values():
        if 'athlete' in req:
            data_list.append(req)

    print('Start refresh', len(data_list), 'athletes')
    asyncio.run(process_athletes(data_list, headers))
