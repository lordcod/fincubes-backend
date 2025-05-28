import asyncio
import contextlib
import json
import logging
from typing import Optional
import aiohttp
from __config__ import headers


class AthleteProcessor:
    def __init__(
        self,
        competition_id: int,
        json_file: str = 'output/itogi.json',
        log_file: str = 'output/athlete_processing.log',
        requests_file: str = 'output/requests.json',
        final_file: str = 'output/final.json',
        team_qt_city: bool = False,
        locked_request: bool = True,
    ):
        self.lock = (asyncio.Lock()
                     if locked_request
                     else contextlib.nullcontext())
        self.competition_id = competition_id
        self.json_file = json_file
        self.requests_file = requests_file
        self.final_file = final_file
        self.team_qt_city = team_qt_city
        self.athlete_api_url = 'https://localhost:8000/athletes/'
        self.results_api_url = f'https://localhost:8000/results/{self.competition_id}'
        self.results_bulk_api_url = 'https://localhost:8000/results/bulk-create'
        self.logger = self.setup_logger(log_file)
        self.requests = {}

    @staticmethod
    def setup_logger(log_file):
        logger = logging.getLogger('athlete_processing')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(log_file, mode='w')
        file_handler.setLevel(logging.WARN)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    async def get_athlete(
        self,
        session: aiohttp.ClientSession,
        last_name: str,
        first_name: str,
        birth_year: str
    ):
        params = {
            'last_name': last_name,
            'first_name': first_name,
            'birth_year': birth_year
        }
        async with session.get(self.athlete_api_url, params=params) as response:
            athletes = await response.json()
            response.raise_for_status()
            if len(athletes) > 1:
                self.logger.warning(
                    'Found 2, more athletes %s %s %s', last_name, first_name, birth_year)
            return athletes[0] if athletes else None

    async def create_athlete(
        self,
        session: aiohttp.ClientSession,
        last_name: str,
        first_name: str,
        birth_year: str,
        team: str,
        rank: str,
        gender: str
    ):
        athlete_data = {
            'last_name': last_name,
            'first_name': first_name,
            'birth_year': birth_year,
            'club': team,
            'license': rank,
            'gender': gender
        }

        async with session.post(self.athlete_api_url, json=athlete_data, headers=headers) as response:
            data = await response.json()
            if not response.ok:
                print(data)
            response.raise_for_status()
            return data

    async def add_result(
        self,
        session: aiohttp.ClientSession,
        athlete_id: int,
        stroke: str,
        distance: int,
        place: Optional[str] = None,
        points: Optional[str] = None,
        result: Optional[str] = None,
        final: Optional[str] = None,
        final_rank: Optional[str] = None,
        record: Optional[str] = None,
        dsq: Optional[bool] = None,
        dsq_final: Optional[bool] = None,
    ):
        result_data = {
            'stroke': stroke,
            'distance': distance,
            'result': result,
            'final': final,
            'final_rank': final_rank,
            'record': record,
            'dsq': dsq,
            'dsq_final': dsq_final,
            'place': place,
            'points': points
        }

        async with session.post(f'{self.results_api_url}/{athlete_id}', json=result_data, headers=headers) as response:
            data = await response.json()
            if not response.ok:
                print(data)
            response.raise_for_status()
            self.logger.info(f"Result added for athlete {athlete_id}")
            return True

    async def send_all_results(
        self,
        session: aiohttp.ClientSession,
        requests: list
    ):
        async with session.post(self.results_bulk_api_url, json=requests, headers=headers, timeout=3600) as response:
            data = await response.json()
            if not response.ok:
                print(data)
            response.raise_for_status()
            return data

    async def check_updated(self, request, data, athlete, key, key2):
        if athlete[key] != data[key2]:
            request[key] = [athlete[key], data[key2]]
            self.logger.debug(
                'Send request %s change %s %s %s: %s %s',
                key,
                athlete['id'],
                athlete['first_name'],
                athlete['last_name'],
                *request[key]
            )

    async def process_athlete(self, session, data):
        athlete = await self.get_athlete(session, data['last_name'], data['first_name'], data['birth_year'])
        if not athlete:
            athlete = await self.create_athlete(session,
                                                data['last_name'],
                                                data['first_name'],
                                                data['birth_year'],
                                                data['team'],
                                                data['rank'],
                                                data['gender'])
            if not athlete:
                self.logger.error("Failed to create athlete.")
                return

        else:
            request = {}
            sender = [
                ('club', 'team'),
                ('license', 'rank'),
                ('gender', 'gender')
            ]
            for key, key2 in sender:
                await self.check_updated(request, data, athlete,
                                         key, key2)

            if request:
                request['athlete'] = athlete
                self.requests[athlete['id']] = request

        athlete_id = athlete['id']
        results = []
        for result in data['results']:
            result = dict(
                stroke=result['stroke'],
                distance=result['distance'],
                result=result.get('result'),
                final=result.get('final'),
                final_rank=result.get('final_rank'),
                record=result.get('record'),
                dsq=result.get('dsq'),
                dsq_final=result.get('dsq_final'),
                place=str(result.get('place')),
                points=result.get('points'),
            )
            results.append(result)

        return {
            'competition_id': self.competition_id,
            'athlete_id': athlete_id,
            'results': results
        }

    async def run(self):
        with open(self.json_file, 'rb') as f:
            athlete_data_list = json.load(f)

        async with aiohttp.ClientSession() as session:
            tasks = [self.process_athlete(session, data)
                     for data in athlete_data_list]
            requests = await asyncio.gather(*tasks)
            print('Parse', len(requests), 'athletes results')
            responses = await self.send_all_results(session, requests)

        with open(self.final_file, 'wb+') as file:
            file.write(json.dumps(responses,
                       ensure_ascii=False).encode())
        with open(self.requests_file, 'wb+') as file:
            file.write(json.dumps(self.requests,
                       ensure_ascii=False).encode())


if __name__ == '__main__':
    comp_id = int(input("Competition ID: "))
    processor = AthleteProcessor(comp_id, locked_request=False)
    asyncio.run(processor.run())
