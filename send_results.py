import asyncio
import json
import aiohttp
from __config__ import headers

allowed_athlete_fields = {
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


class AthleteProcessor:
    BASE_URL = "https://api.fincubes.ru/admin"

    def __init__(
        self,
        competition_id: int,
        input_file: str = "output/2_itogi.json",
        requests_file: str = "output/3_requests.json",
        final_file: str = "output/3_final.json",
    ):
        self.competition_id = competition_id
        self.input_file = input_file
        self.requests_file = requests_file
        self.final_file = final_file
        self.requests = []

    async def get_athlete(self, session, last, first, year) -> dict | None:
        params = {"last_name": last, "first_name": first, "birth_year": year}
        async with session.get(f"{self.BASE_URL}/athlete/", params=params, headers=headers) as r:
            try:
                data = await r.json()
            except Exception:
                data = None

            if r.status != 200:
                print(f"GET athlete error ({r.status}):", data)
                return None

            if not data:
                return None

            if len(data) > 2:
                print(
                    f"⚠️ Found {len(data)} athletes with same name/year: {last} {first} ({year})")
                for a in data:
                    print((
                        f"   • ID {a.get('id')}: "
                        f"city='{a.get('city') or '-'}', "
                        f"club='{a.get('club') or '-'}', "
                        f"license='{a.get('license') or '-'}', "
                        f"gender='{a.get('gender') or '-'}'"
                    ))

            return data[0]

    async def create_athlete(self, session, data) -> None | dict:
        payload = {
            "last_name": data["last_name"],
            "first_name": data["first_name"],
            "birth_year": data["birth_year"],
            "license": data.get("rank") or "",
            "gender": data.get("gender") or "",
            "club": data.get("team") or "",
            "city": data.get("city") or "",
        }

        print(
            f"🟢 Creating new athlete: {payload['last_name']} {payload['first_name']} ({payload['birth_year']})")

        async with session.post(f"{self.BASE_URL}/athlete/", json=payload, headers=headers) as r:
            try:
                res = await r.json()
            except Exception:
                res = None

            if r.status not in (200, 201):
                print(f"❌ CREATE athlete error ({r.status}):", res)
                return None

            print(
                f"✅ Athlete created: ID {res.get('id')} - {payload['last_name']} {payload['first_name']}")
            return res

    def check_updates(self, athlete, data):
        """
        Возвращает словарь отличий между athlete (из API) и data (вход).
        Формат: { 'license': {'old': ..., 'new': ...}, ... }
        """
        mapping = {
            "license": "rank",
            "gender": "gender",
        }
        changes = {}
        for field, src in mapping.items():
            old = (athlete.get(field) or "").strip()
            new = (data.get(src) or "").strip()
            if old != new:
                changes[field] = {"old": old, "new": new}
        return changes

    async def process_athlete(self, session, data):
        athlete = await self.get_athlete(session, data["last_name"], data["first_name"], data["birth_year"])

        if not athlete:
            athlete = await self.create_athlete(session, data)
            if not athlete:
                print(
                    f"❌ Failed to create athlete: {data['last_name']} {data['first_name']}")
                return None
        else:
            updates = self.check_updates(athlete, data)
            if updates:
                self.requests.append({
                    "id": athlete["id"],
                    "data": athlete,
                    "athlete": f"{athlete.get('last_name', '')} {athlete.get('first_name', '')}".strip(),
                    "changes": updates,
                })

        return {
            "competition_id": self.competition_id,
            "athlete_id": athlete["id"],
            "results": data["results"],
        }

    async def send_all_results(self, session, results):
        print(f"🔵 Starting bulk results upload ({len(results)} entries)...")

        async with session.post(
            f"{self.BASE_URL}/result/bulk-create/",
            json=results,
            headers=headers,
            timeout=3600,
        ) as r:
            try:
                res = await r.json()
            except Exception:
                res = None

            if r.status not in (200, 201):
                print(f"❌ BULK create error ({r.status}):", res)
            else:
                print(f"✅ Bulk upload completed successfully ({r.status})")

            return res

    async def run(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            athletes = json.load(f)

        async with aiohttp.ClientSession() as session:
            tasks = [self.process_athlete(session, a) for a in athletes]
            processed = [r for r in await asyncio.gather(*tasks) if r]

            print(
                f"✅ Parsed {len(processed)} athletes, preparing to send results...")
            response = await self.send_all_results(session, processed)

        with open(self.final_file, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)

        with open(self.requests_file, "w", encoding="utf-8") as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

        print(f"💾 Results saved to {self.final_file}")
        print(f"📝 Update requests saved to {self.requests_file}")


if __name__ == "__main__":
    comp_id = int(input("Competition ID: "))
    asyncio.run(AthleteProcessor(comp_id).run())
