import json
import aiohttp
import asyncio
from transliterate import translit
from __config__ import headers

BASE_URL = "https://api.fincubes.ru/public/client"


async def get_athlete(session, last, first, year) -> dict | None:
    params = {"query": f'{last} {first}'}
    async with session.get(f"{BASE_URL}/athlete/", params=params, headers=headers) as r:
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


async def main():
    # Загружаем JSON
    with open("output/1_output_results.json", "r", encoding="utf-8") as f:
        output = json.load(f)

    clubs_cache = {}
    athlete_cache = {}
    async with aiohttp.ClientSession() as session:
        lenght = len(output["individual_results"])
        for result in output["individual_results"]:
            last_name_orig = result["last_name"]
            first_name_orig = result["first_name"]
            birth_year = result.get("birth_year")
            key = f"{last_name_orig.lower().strip()}_{first_name_orig.lower().strip()}_{birth_year}"
            if key in athlete_cache:
                continue
            else:
                athlete_cache[key] = True

            print(
                f"Processing {len(athlete_cache)}/{lenght}: {first_name_orig} {last_name_orig} ({birth_year})")
            athlete = await get_athlete(session, last_name_orig, first_name_orig, birth_year)
            if not athlete:
                continue

            if athlete['last_name'].lower() == last_name_orig.lower() and athlete['first_name'].lower() == first_name_orig.lower() and int(athlete['birth_year']) == int(birth_year):
                athlete_id = athlete.get("id")
                result["athlete_id"] = athlete_id
                ret = clubs_cache.setdefault(result['team'], [])
                ret.append((athlete_id, athlete['club'], athlete['city']))
                print(
                    f"Found athlete: {first_name_orig} {last_name_orig} -> team: {result['team']}, club: {athlete['club']}")

    with open("output/1_clubs_cache.json", "w", encoding="utf-8") as f:
        json.dump(clubs_cache, f, ensure_ascii=False, indent=4)
    with open("output/1_output_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
