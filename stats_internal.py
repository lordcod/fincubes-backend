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
    athlete_cache = {'alena_zubareva_2009': 275, 'daniil_gaidai_2009': 8, 'timchenko_ekaterina_2008': 29, 'saprykina_kseniia_2008': 18, 'peshkov_iaroslav_2008': 138, 'gaidai_daniil_2008': '8', 'ivanushkina_polina_2008': 1314, 'dorogavtseva_sofia_2008': 105, 'shtark_matvey_2008': 199, 'kovalenok_maksim_2008': 202, 'novikova_elizaveta_2010': 1118, 'pavlova_daria_2009': 1116, 'gilmutdinov_ainur_2008': 90, 'maksimov_vladimir_2008': 92, 'zubareva_alena_2009': '275', 'akentev_david_2008': 287, 'shilina_daria_2008': 98, 'bainov_iaroslav_2008': 213, 'gaivak_nikita_2008': 133, 'nasyrov_victor_2008': 987, 'achatkina_angelina_2009': 170, 'romashov_denis_2008': 145, 'tarasov_vladimir_2009': 71, 'kozyrina_daria_2010': 75, 'bachurin_aleksey_2009': 209,
                     'nekrasova_polina_2008': 86, 'тимченко_екатерина_2008': 29, 'ачаткина_ангелина_2009': 170, 'петракова_анастасия_2010': 2325, 'пешков_ярослав_2008': 138, 'арсентьев_александр_2008': 28, 'брытков_никита_2010': 146, 'понкратов_кирилл_2008': 857, 'формова_вероника_2010': 912, 'желнина_ксения_2010': 99, 'сырямина_софья_2009': 19, 'штарк_матвей_2008': 199, 'бачурин_алексей_2009': 209, 'коваленок_максим_2008': 202, 'купрессова_елизавета_2008': 273, 'зубарева_алёна_2009': '275', 'акентьев_давид_2008': 287, 'гильмутдинов_айнур_2008': 90, 'дорогавцева_софья_2008': 105, 'ушакова_софья_2009': 159, 'чичендаева_ольга_2008': 158, 'шевяков_владимир_2008': 986, 'суслопаров_константин_2008': '216', 'ковалев_денис_2010': 1036}

    async with aiohttp.ClientSession() as session:
        for result in output["individual_results"]:
            place = result.get("place") and result.get("place").strip()
            if not (place and place.isdigit() and int(place) in [1, 2, 3]):
                continue
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

    print(athlete_cache)
    # Сохраняем JSON обратно
    with open("output/1_output_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
