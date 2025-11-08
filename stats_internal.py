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

    # Кеш для уже найденных спортсменов
    athlete_cache = {}  # ключ = "last_first_year", значение = athlete_id

    async with aiohttp.ClientSession() as session:
        for result in output["individual_results"]:
            last_name_orig = result["last_name"]
            first_name_orig = result["first_name"]
            birth_year = result.get("birth_year")

            # Создаём ключ для кеша
            cache_key = f"{last_name_orig.lower().strip()}_{first_name_orig.lower().strip()}_{birth_year}"

            if cache_key in athlete_cache:
                result["athlete_id"] = athlete_cache[cache_key]
                print(
                    f"[CACHE] {first_name_orig} {last_name_orig} -> ID {result['athlete_id']}")
                continue

            last_name = translit(last_name_orig.lower().strip(), "ru")
            first_name = translit(first_name_orig.lower().strip(), "ru")
            print(first_name, last_name)

            athlete = await get_athlete(session, last_name, first_name, birth_year)

            if athlete:
                print(
                    f"\n[{first_name_orig} {last_name_orig}] Найден атлет: {athlete['first_name']} {athlete['last_name']}")
                print(f"  ID: {athlete.get('id')}")
                print(f"  Город: {athlete.get('city') or '-'}")
                print(f"  Клуб: {athlete.get('club') or '-'}")
                print(f"  Пол: {athlete.get('gender') or '-'}")
                print(f"  Разряд: {athlete.get('license') or '-'}")
                print(f"  Год рождения: {athlete.get('birth_year') or '-'}")

                confirm = input(
                    "Это правильный атлет? (y/n): ").strip().lower()
                if confirm == "y":
                    athlete_id = athlete.get("id")
                else:
                    athlete_id = input(
                        f"Введите ID для {first_name} {last_name}: ").strip()

            else:
                print(
                    f"\nАтлет не найден: {first_name_orig} {last_name_orig} ({birth_year})")
                athlete_id = input(
                    f"Введите ID для {first_name} {last_name}: ").strip()

            # Сохраняем в результат и кеш
            result["athlete_id"] = athlete_id
            athlete_cache[cache_key] = athlete_id

    # Сохраняем JSON обратно
    with open("output/1_output_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
