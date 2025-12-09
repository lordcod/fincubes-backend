import os
import json
from bs4 import BeautifulSoup


def split_name(full_name: str):
    """
    Разделяет строку имени на фамилию (все CAPS) и имя (нормальное написание).
    Пример:
        "SZABO GYOERGYEI Szebasztian" -> {'surname': 'SZABO GYOERGYEI', 'firstname': 'Szebasztian'}
    """
    if not full_name or not isinstance(full_name, str):
        return {"surname": None, "firstname": None}

    # Разбиваем по пробелам
    parts = full_name.strip().split()

    # Если всё в верхнем регистре — фамилия неизвестна, имя неизвестно
    if all(p.isupper() for p in parts):
        return {"surname": " ".join(parts), "firstname": None}

    # Находим индекс, где начинается первая часть, не полностью в CAPS
    index = next((i for i, p in enumerate(parts)
                 if not p.isupper()), len(parts))

    surname = " ".join(parts[:index]).strip()
    firstname = " ".join(parts[index:]).strip()

    return {
        "last_name": surname or None,
        "first_name": firstname or None
    }


def parse_event_results(html_path):
    """Парсит таблицу результатов из локального HTML-файла и возвращает list[dict]."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        table = soup.select_one("span.ResultList_FSW table.sortable")
        if not table:
            print(
                f"⚠️ Таблица не найдена в файле: {os.path.basename(html_path)}")
            return []

        results = []
        for row in table.select("tbody tr"):
            rank_el = row.select_one("td.rankColumn span")
            name_el = row.select_one("td.athleteName a span.sortValue")
            noc_el = row.select_one("td.noc a")
            time_el = row.select_one("td.All_result span.sortValue")
            place = rank_el.get_text(strip=True) if rank_el else None
            data = {
                "place": place and place[:len(place)//2],
                "name": name_el.get_text(strip=True) if name_el else None,
                "team": noc_el.get_text(strip=True) if noc_el else None,
                "result": time_el.get_text(strip=True) if time_el else None,
                "status": "COMPLETED"
            }
            data.update(split_name(data['name']))

            if any(data.values()):
                results.append(data)

        return results

    except Exception as e:
        print(f"❌ Ошибка при обработке {html_path}: {e}")
        return []


def process_results_folder(folder_path, output_file="output/1_output_results.json"):
    """Обходит все HTML-файлы с -FNL- и собирает результаты в один JSON."""
    all_results = []
    distances = []

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".html"):
            continue
        if "-FNL-" not in file_name:
            continue
        if "X" in file_name:
            print("❌ Пропустил:", file_name)
            continue

        full_path = os.path.join(folder_path, file_name)
        distance_name = os.path.splitext(file_name)[0]  # убираем .html
        distances.append(distance_name)

        print(f"📄 Обрабатываем: {file_name}")

        results = parse_event_results(full_path)
        if results:
            for res in results:
                if res['team'] == 'AIN':
                    res['distance'] = distance_name
                    all_results.append(res)

    # Сохраняем всё в общий JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"individual_results": all_results,
                  "distances": distances}, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Все результаты сохранены в {output_file}")
    print(f"Всего файлов обработано: {len(all_results)}")


# 🚀 Пример использования
if __name__ == "__main__":
    folder = "twg2025_results"  # <-- путь к папке с HTML-файлами
    process_results_folder(folder)
