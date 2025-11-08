import asyncio
import aiohttp
import json
import random
from pathlib import Path

ROOT_PATH = Path("lsport")
ROOT_PATH.mkdir(exist_ok=True)

INPUT_FILE = ROOT_PATH / "results.json"
OUTPUT_FILE = ROOT_PATH / "output.json"

BASE_URL = "https://lsport.net/data/"
MAX_RETRIES = 3


async def fetch(session, url):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = {
                "sub": random.randint(0, 5000),
                "subDsc": None,
                "flow": None
            }
            async with session.post(url, json=data, timeout=60) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            print(f"Ошибка при POST {url} (попытка {attempt}): {e}")
            if attempt == MAX_RETRIES:
                return None
            await asyncio.sleep(1)


async def main():
    data_list = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, BASE_URL + item["url"]) for item in data_list]
        results = await asyncio.gather(*tasks)

    results = [r for r in results if r is not None]

    OUTPUT_FILE.write_text(json.dumps(
        results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Сохранено {len(results)} результатов в {OUTPUT_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
