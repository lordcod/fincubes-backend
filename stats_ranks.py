import asyncio
from collections import defaultdict
import json

import aiohttp

from __config__ import headers


BASE_URL = "https://api.fincubes.ru"


async def get_athlete(session, last, first, year) -> dict | None:
    params = {"query": f'{last} {first}'}
    async with session.get(f"{BASE_URL}/public/client/athlete/", params=params, headers=headers) as r:
        try:
            data = await r.json()
        except Exception:
            data = None

        if r.status != 200:
            print(f"GET athlete error ({r.status}):", data)
            return None

        if not data:
            return None
        for a in data:
            if str(a.get("birth_year")) == str(year) or not year:
                return a

        return None


async def get_last_rank_sprint(session, id: int) -> str:
    async with session.get(f"{BASE_URL}/public/server/athlete/{id}/performances/", headers=headers) as r:
        try:
            data = await r.json()
        except Exception:
            data = ""
        if not data:
            return ""

        max_rank = ""
        for comp in data["results"]:
            for perf in comp["performances"]:
                final_rank = perf.get("final_rank", "")
                print('Final rank:', final_rank, 'max rank:', max_rank)
                max_rank = final_rank if is_rank_higher(
                    final_rank, max_rank) else max_rank
        return max_rank


RANK_ORDER = {
    # Top ranks
    "МСМК": 0,
    "ЗМС":  1,
    "МС":   2,
    "КМС":  3,

    # Adult ranks (alternative notations)
    "1":    6,   "I":    6,
    "2":    7,   "II":   7,
    "3":    8,   "III":  8,

    # Junior ranks (alternative notations)
    "1юн":  9,   "Iюн":  9,
    "2юн": 10,   "IIюн": 10,
    "3юн": 11,   "IIIюн": 11,

    "": 100,
}


def is_rank_higher(new_rank: str, old_rank: str) -> bool:

    try:
        return RANK_ORDER[new_rank] < RANK_ORDER[old_rank]
    except KeyError:
        return False


with open("output/2_itogi.json", "rb") as file:
    athletes = json.load(file)

stats_ranks = defaultdict(int)


async def main():
    async with aiohttp.ClientSession() as session:
        for athl in athletes:
            athlete = await get_athlete(
                session, athl['last_name'], athl['first_name'], athl['birth_year'])
            if not athlete:
                max_rank = ""
            else:
                max_rank = await get_last_rank_sprint(session, athlete['id'])
                print(max_rank)

            results = athl['results']
            for res in results:
                if res['status'] != 'COMPLETED':
                    continue

                final_rank = res.get('final_rank')
                if not final_rank:
                    continue

                if not max_rank and final_rank:
                    print('Not rank')
                    stats_ranks[final_rank] += 1

                if is_rank_higher(final_rank, max_rank):
                    stats_ranks[final_rank] += 1

asyncio.run(main())

print(stats_ranks)
print(sum(stats_ranks.values()))
