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
        self.requests = {}

    async def get_athlete(self, session, last, first, year) -> dict | None:
        params = {"last_name": last, "first_name": first, "birth_year": year}
        async with session.get(f"{self.BASE_URL}/athlete/", params=params, headers=headers) as r:
            # Если сервер вернул не-json — безопасно прочитаем текст
            try:
                data = await r.json()
            except Exception:
                data = None
            if r.status not in (200,):
                print(f"GET athlete error ({r.status}):", data)
                return None
            return data[0] if data else None

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
        async with session.post(f"{self.BASE_URL}/athlete/", json=payload, headers=headers) as r:
            try:
                res = await r.json()
            except Exception:
                res = None
            if r.status not in (200, 201):
                print(f"CREATE athlete error ({r.status}):", res)
                return None
            return res

    async def update_athlete(self, session, athlete_id, data: dict):
        """
        Делает PUT /athlete/{id}/ с переданными полями (updates).
        Возвращает обновлённый объект спортсмена или None.
        """
        clean_data = {k: v for k, v in data.items(
        ) if k in allowed_athlete_fields and v is not None}

        async with session.put(f"{self.BASE_URL}/athlete/{athlete_id}/", json=clean_data, headers=headers) as r:
            try:
                res = await r.json()
            except Exception:
                res = None
            if r.status not in (200, 201):
                print(f"UPDATE athlete {athlete_id} error ({r.status}):", res)
                return None
            return res

    def check_updates(self, athlete, data):
        """
        Возвращает словарь отличий между athlete (из API) и data (вход).
        Формат: { 'club': {'old': ..., 'new': ...}, ... }
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

    def prepare_patch_payload_for_missing(self, athlete, data):
        """
        Если у athlete пустые club/city, а в data они есть — соберём payload для PUT.
        Только те поля, которые заполнены в data и пусты у athlete.
        """
        payload = {}
        if not (athlete.get("club")) and data.get("team"):
            payload["club"] = data["team"]
        if not (athlete.get("city")) and data.get("city"):
            payload["city"] = data["city"]
        return payload

    async def process_athlete(self, session, data):
        athlete = await self.get_athlete(session, data["last_name"], data["first_name"], data["birth_year"])

        if not athlete:
            athlete = await self.create_athlete(session, data)
            if not athlete:
                print("❌ Failed to create athlete:", data.get(
                    "last_name"), data.get("first_name"))
                return None
        else:
            patch_payload = self.prepare_patch_payload_for_missing(
                athlete, data)
            if patch_payload:
                new_athlete = {**athlete, **patch_payload}
                updated = await self.update_athlete(session, athlete["id"], new_athlete)
                if updated:
                    athlete = updated
                else:
                    print(
                        f"⚠️ Failed to patch athlete {athlete['id']} with {patch_payload}")

            updates = self.check_updates(athlete, data)
            if updates:
                self.requests[athlete["id"]] = {
                    "athlete": f"{athlete.get('last_name', '')} {athlete.get('first_name', '')}".strip(),
                    "changes": updates,
                }

        return {
            "competition_id": self.competition_id,
            "athlete_id": athlete["id"],
            "results": data["results"],
        }

    async def send_all_results(self, session, results):
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
                print(f"BULK create error ({r.status}):", res)
            return res

    async def run(self):
        with open(self.input_file, "r", encoding="utf-8") as f:
            athletes = json.load(f)

        async with aiohttp.ClientSession() as session:
            tasks = [self.process_athlete(session, a) for a in athletes]
            processed = [r for r in await asyncio.gather(*tasks) if r]

            print(f"✅ Parsed {len(processed)} athletes, sending results...")
            response = await self.send_all_results(session, processed)

        # сохраняем итоги
        with open(self.final_file, "w", encoding="utf-8") as f:
            json.dump(response, f, ensure_ascii=False, indent=2)

        with open(self.requests_file, "w", encoding="utf-8") as f:
            json.dump(self.requests, f, ensure_ascii=False, indent=2)

        print(f"💾 Results saved to {self.final_file}")
        print(f"📝 Update requests saved to {self.requests_file}")


if __name__ == "__main__":
    comp_id = int(input("Competition ID: "))
    asyncio.run(AthleteProcessor(comp_id).run())
