#!/usr/bin/env python3
import sys
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT_PATH = Path("lsport")
ROOT_PATH.mkdir(exist_ok=True)

OUTPUT_FILE = ROOT_PATH / "event.json"


def extract_ls_event_object(path_or_url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, devtools=True)
        page = browser.new_page()

        # Определяем, локальный файл или URL
        if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
            page.goto(path_or_url)
        else:
            html_file = Path(path_or_url).resolve()
            page.goto(f"file:///{html_file}")

        # Можно добавить небольшую паузу для полной загрузки JS
        page.wait_for_timeout(2000)  # 2 секунды

        # Получаем объект lsport.event из окна браузера
        try:
            event_obj = page.evaluate("() => lsport.event")
        except Exception as e:
            print(f"[!] Не удалось получить lsport.event: {e}")
            browser.close()
            return None

        browser.close()
        print("[✓] Объект lsport.event успешно извлечён через Playwright.")
        return event_obj


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python extract_ls_event_playwright.py <html-файл или URL>")
        path_or_url = input('html-файл или URL>>> ')
    else:
        path_or_url = sys.argv[1]

    event_obj = extract_ls_event_object(path_or_url)
    if not event_obj:
        sys.exit(1)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(event_obj, f, ensure_ascii=False, indent=2)
    print(f"[+] Сохранен event.json ({len(event_obj)} ключей)")
