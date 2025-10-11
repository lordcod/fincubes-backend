import json
import aiohttp
import asyncio
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
}


def is_rank_higher(new_rank: str, old_rank: str) -> bool:
    try:
        return RANK_ORDER[new_rank] < RANK_ORDER[old_rank]
    except KeyError:
        return False


async def update_athlete(session: aiohttp.ClientSession, athlete_id: int, data: dict):
    """Update athlete via PUT with logging."""
    clean_data = {k: v for k, v in data.items() if k in allowed_fields}
    async with session.put(f"{BASE_URL}/athlete/{athlete_id}/", json=clean_data, headers=headers) as r:
        try:
            res = await r.json()
        except Exception:
            res = None
        if r.status not in (200, 201):
            print(
                f"❌ [ERROR] Athlete {athlete_id} update failed (HTTP {r.status})")
            print("   Payload:", clean_data)
            print("   Server response:", res)
            return None
        print(f"✅ [SUCCESS] Athlete {athlete_id} updated")
        return res


async def update_athlete_if_needed(session: aiohttp.ClientSession, item: dict):
    """
    item = {
        "id": 3484,
        "athlete": { full athlete object },
        "changes": { "license": { "old": "...", "new": "..." } }
    }
    """
    athlete = item["data"]
    athlete_id = athlete["id"]
    athlete_name = f"{athlete['last_name']} {athlete['first_name']}"

    if "license" in item.get("changes", {}):
        old_rank = item["changes"]["license"]["old"].strip()
        new_rank = item["changes"]["license"]["new"].strip()

        if (not old_rank and new_rank) or is_rank_higher(new_rank, old_rank):
            print(
                f"⬆️ [UPDATE] {athlete_name}: {old_rank or '-'} → {new_rank}")
            athlete["license"] = new_rank
            return await update_athlete(session, athlete_id, athlete)
        else:
            print(
                f"⏭ [SKIP] {athlete_name}: current rank ({old_rank}) >= new rank ({new_rank}), skipped")
            return None
    else:
        print(f"ℹ️ [NO CHANGE] {athlete_name}: no rank changes detected")
    return None


async def process_athletes(data_list: list):
    print(f"\n🚀 Starting rank updates for {len(data_list)} athletes...\n")
    async with aiohttp.ClientSession() as session:
        tasks = [update_athlete_if_needed(session, item) for item in data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    responses = [r for r in results if isinstance(r, dict)]
    print(f"\n💾 Updated {len(responses)} athletes successfully")
    return responses


if __name__ == "__main__":
    with open("output/3_requests.json", "r", encoding="utf-8") as file:
        requests_data = json.load(file)

    data_list = [
        item
        for item in requests_data
        if "license" in item.get("changes", {})
    ]
    asyncio.run(process_athletes(data_list))
