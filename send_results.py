import json
import re
import aiohttp
import logging
import asyncio
import datetime
from typing import List, Optional


logger = logging.getLogger('athlete_processing')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


file_handler = logging.FileHandler('athlete_processing.log')
file_handler.setLevel(logging.WARN)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

ATHLETE_API_URL = 'http://localhost:8000/athletes/'
RESULTS_API_URL = 'http://localhost:8000/results/8'


def parse_time(time_str):
    if not time_str:
        return
    try:
        match = re.fullmatch(r'(\d{2})[:\.,](\d{2})[\.,](\d{1,2})', time_str)
        min, sec, mili = match.groups()
        return f'{min:02}:{sec:02},{mili:02}'
    except:
        raise


async def get_athlete_by_name_and_birth_year(session, last_name, first_name, birth_year):
    try:
        async with session.get(f'{ATHLETE_API_URL}?last_name={last_name}&first_name={first_name}&birth_year={birth_year}') as response:
            response.raise_for_status()
            athletes = await response.json()
            if athletes:
                return athletes[0]
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while fetching athlete: {e}")
        raise
    return None


async def create_athlete(session, last_name, first_name, birth_year, team, rank, sex):
    athlete_data = {
        'last_name': last_name,
        'first_name': first_name,
        'birth_year': birth_year,
        'club': team,
        'license': rank,
        'gender': sex
    }
    try:
        async with session.post(ATHLETE_API_URL, json=athlete_data) as response:
            d = await response.json()
            response.raise_for_status()
            return d
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while creating athlete: {e} {d}")
        raise
    return None


async def add_result(session, athlete_id, stroke, distance, result, final, place, final_rank, points, record, dsq, dsq_final):
    if dsq:
        result = ''
    if dsq_final:
        final = ''

    result_data = {
        'stroke': stroke,
        'distance': distance,
        'result': parse_time(result),
        'final': parse_time(final),
        'place': int(place) if place or place == 0 else place,
        'final_rank': final_rank,
        'points': str(points),
        'record': record,
        'dsq': dsq,
        'dsq_final': dsq_final
    }
    try:
        async with session.post(f'{RESULTS_API_URL}/{athlete_id}', json=result_data) as response:
            d = await response.json()
            response.raise_for_status()
            logger.info(f"Result added successfully for athlete {athlete_id}")
            return True
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while adding result: {e} {d}")
        raise
    return False


async def process_athlete_data(data, session):
    data['last_name'] = data['last_name'].title()
    athlete = await get_athlete_by_name_and_birth_year(session, data['last_name'], data['first_name'], data['birth_year'])

    if not athlete:
        logger.info(
            f"Athlete {data['first_name']} {data['last_name']} not found. Creating new athlete.")
        athlete = await create_athlete(session, data['last_name'], data['first_name'], data['birth_year'], data['team'], data['rank'], data['sex'])
        if not athlete:
            logger.error("Failed to create athlete.")
            return

    athlete_id = athlete['id']

    for result in data['results']:
        logger.info(
            f"Adding result for athlete {athlete_id}: {result['stroke']} {result['distance']}m")
        await add_result(
            session,
            athlete_id,
            result['stroke'],
            result['distance'],
            result['result'],
            result['final'],
            result['place'],
            result['final_rank'],
            result['points'],
            result['record'],
            result['dsq'],
            result['dsq_final']
        )


async def main():
    with open('itogi.json', 'rb') as file:
        athlete_data = json.load(file)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for data in athlete_data:
            tasks.append(process_athlete_data(data, session))
        await asyncio.gather(*tasks)


asyncio.run(main())
