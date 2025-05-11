from collections import defaultdict
import contextlib
import json
import re
import aiohttp
import logging
import asyncio
lock = asyncio.Lock()


class Stats:
    teams = set()
    clubs_wa = defaultdict(list)

    athletes = list()
    no_register = list()
    with_register = list()

    results = list()
    dsq_items = list()

    @staticmethod
    def to_dict():
        return {
            'teams': list(Stats.teams),
            'athletes': Stats.athletes,
            'no_register': Stats.no_register,
            'with_register': Stats.with_register,
            'results': Stats.results,
            'clubs_wa': dict(Stats.clubs_wa),
            'dsq_items': Stats.dsq_items
        }


logger = logging.getLogger('athlete_processing')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


file_handler = logging.FileHandler('athlete_processing.log', mode='w')
file_handler.setLevel(logging.WARN)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

COMP_ID = int(input('Compt id: '))
ATHLETE_API_URL = 'http://localhost:8000/athletes/'
RESULTS_API_URL = f'http://localhost:8000/results/{COMP_ID}'
time_regex = re.compile(r'(\d{2}):(\d{2}),(\d{1,2})')


def parse_time(time_str):
    if not time_str:
        return
    try:
        match = time_regex.fullmatch(time_str)
        if not match:
            logger.warning('Excepted time, received %s', time_str)
            return
        min, sec, mili = match.groups()
        return f'{min:02}:{sec:02}.{mili:02}'
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


async def add_result(session, athlete_id, stroke, distance, result, final_rank, record, dsq):
    if dsq:
        result = ''

    result_data = {
        'stroke': stroke,
        'distance': distance,
        'result': parse_time(result),
        'final_rank': final_rank,
        'record': record,
        'dsq': dsq
    }

    if result and not time_regex.fullmatch(result):
        logger.error('no catch error result %s %s %s',
                     athlete_id, result, result_data)

    try:
        d = None
        async with session.post(f'{RESULTS_API_URL}/{athlete_id}', json=result_data) as response:
            with contextlib.suppress(Exception):
                d = await response.json()
            response.raise_for_status()
            logger.info(f"Result added successfully for athlete {athlete_id}")
            return True
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error while adding result: {e} {d}")
        raise
    return False


async def process_athlete_data(data, session):
    athlete = await get_athlete_by_name_and_birth_year(session, data['last_name'], data['first_name'], data['birth_year'])
    athlete_data = (data['last_name'], data['first_name'],
                    data['birth_year'], data['team'], data['rank'], data['sex'])
    Stats.athletes.append(data)
    Stats.teams.add(data['team'])
    Stats.clubs_wa[data['team']].append(data)

    if not athlete:
        logger.info(
            f"Athlete {data['first_name']} {data['last_name']} not found. Creating new athlete.")
        athlete = await create_athlete(session, *athlete_data)
        if not athlete:
            logger.error("Failed to create athlete.")
            return
        Stats.no_register.append((athlete['id'],)+athlete_data)
    else:
        Stats.with_register.append((athlete['id'],)+athlete_data)

    athlete_id = athlete['id']

    for result in data['results']:
        data = (
            athlete_id,
            result['stroke'],
            result['distance'],
            result['result'],
            result['final_rank'],
            result['record'],
            result['dsq']
        )
        Stats.results.append(data)
        if result['dsq']:
            Stats.dsq_items.append(data)
        async with lock:
            await add_result(
                session,
                *data
            )


async def main():
    with open('itogi.json', 'rb') as file:
        athlete_data = json.load(file)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for data in athlete_data:
            tasks.append(process_athlete_data(data, session))
        await asyncio.gather(*tasks)

    with open('stats.json', 'wb+') as file:
        file.write(json.dumps(Stats.to_dict(), ensure_ascii=False).encode())


asyncio.run(main())
