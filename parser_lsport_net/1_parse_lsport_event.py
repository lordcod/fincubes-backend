import json
from pathlib import Path

ROOT_PATH = Path("lsport")
ROOT_PATH.mkdir(exist_ok=True)

INPUT_FILE = ROOT_PATH / "event.json"
OUTPUT_FILE = ROOT_PATH / "results.json"


def collect_items(parent_title, items, results):
    if not items:
        return

    for item in items:
        title = item.get("Title")
        url = item.get("Url")
        full_title = f"{parent_title} {title}".strip()

        if url:
            results.append({
                "name": full_title,
                "url": url.replace('Results', 'Participants')
            })

        # рекурсивно идём глубже
        collect_items(full_title, item.get("Items"), results)

        # inline = item.get("InlineItems")
        # if inline:
        #     for sub in inline:
        #         sub_title = sub.get("Title")
        #         sub_url = sub.get("Url")
        #         if sub_url:
        #             results.append({
        #                 "name": f"{full_title} {sub_title}".strip(),
        #                 "url": sub_url
        #             })


def main():
    data = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    menu = data.get("menuItems", {})

    # ищем главную группу results
    results_menu = next(
        (v for v in menu.values() if v.get("Alias") == "results"), None)
    if not results_menu:
        print("Не найден menu Alias=results")
        return

    # ищем resultsDsc
    results_dsc = next((i for i in results_menu.get(
        "Items", []) if i.get("Alias") == "resultsDsc"), None)
    if not results_dsc:
        print("Не найден Alias=resultsDsc")
        return

    results = []
    collect_items("", results_dsc.get("Items"), results)

    OUTPUT_FILE.write_text(json.dumps(
        results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Готово! Сохранено {len(results)} элементов в {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
