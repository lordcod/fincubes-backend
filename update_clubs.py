import asyncio
import json
import aiohttp
from __config__ import headers

BASE_URL = "https://api.fincubes.ru/admin"
allowed_fields = {
    "last_name",
    "first_name",
    "birth_year",
    "club",
    "city",
    "license",
    "gender",
    "avatar_url",
    "is_top",
}


async def get_athlete(session, last, first, year):
    params = {"last_name": last, "first_name": first, "birth_year": year}
    async with session.get(f"{BASE_URL}/athlete/", params=params, headers=headers) as r:
        try:
            data = await r.json()
        except Exception:
            data = None
        if r.status != 200:
            print(f"❌ GET athlete error ({r.status}): {data}")
            return None
        return data[0] if data else None


async def update_athlete(session, athlete_id, data):
    clean_data = {k: v for k, v in data.items() if k in allowed_fields}
    async with session.put(f"{BASE_URL}/athlete/{athlete_id}/", json=clean_data, headers=headers) as r:
        try:
            res = await r.json()
        except Exception:
            res = None
        if r.status not in (200, 201):
            print(f"❌ UPDATE athlete {athlete_id} error ({r.status}): {res}")
            return None
        print(f"✅ Updated athlete {athlete_id}: {clean_data}")
        return res


def prepare_patch_payload(athlete, data):
    """
    Если у athlete пустые club/city, а в data они есть — собрать payload для обновления.
    """
    payload = {}
    if not athlete.get("club") and data.get("team"):
        payload["club"] = data["team"]
    if not athlete.get("city") and data.get("city"):
        payload["city"] = data["city"]
    return payload


async def process_athlete(session, data):
    athlete = await get_athlete(session, data["last_name"], data["first_name"], data["birth_year"])
    if not athlete:
        print(
            f"⚠️ Athlete not found: {data['last_name']} {data['first_name']} ({data['birth_year']})")
        return None

    patch_payload = prepare_patch_payload(athlete, data)
    if not patch_payload:
        return None

    print(
        f"🔧 Need to update {athlete['last_name']} {athlete['first_name']} ({athlete['id']}): {patch_payload}")
    updated = await update_athlete(session, athlete["id"], {**athlete, **patch_payload})

    if updated:
        print(
            f"✅ Successfully updated {updated['last_name']} {updated['first_name']}")
    else:
        print(
            f"⚠️ Failed to update {athlete['last_name']} {athlete['first_name']}")


async def run(input_file="output/2_itogi.json"):
    with open(input_file, "r", encoding="utf-8") as f:
        athletes = json.load(f)

    async with aiohttp.ClientSession() as session:
        tasks = [process_athlete(session, a) for a in athletes]
        await asyncio.gather(*tasks)

    print("🏁 Done checking and updating missing clubs/cities.")


if __name__ == "__main__":
    asyncio.run(run())
