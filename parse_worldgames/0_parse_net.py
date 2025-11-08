#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from pathlib import Path
import json
import re
import time

OUTPUT_DIR = Path("twg2025_results")
OUTPUT_DIR.mkdir(exist_ok=True)

BASE_URL = "https://www.theworldgames.org/editions/Chengdu-CHN-2025-14/infosystem"


def setup_browser():
    """Настраивает и возвращает браузер и контекст"""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    return playwright, browser, context


def setup_response_interceptor(page):
    """Настраивает перехватчик HTTP-ответов"""
    captured_responses = []

    def on_response(response):
        url = response.url
        if ("twg2025.swisstiming.com" in url and
                ("ListPartial" in url or "ResultList" in url or "rsc=" in url or "Result" in url)):
            print(f"Intercepted: {url}")
            captured_responses.append({
                'url': url,
                'status': response.status
            })

            try:
                event_match = re.search(r"rsc=([A-Z0-9\-]+)", url)
                if event_match:
                    name = event_match.group(1)
                else:
                    name = re.sub(r"[^a-zA-Z0-9]", "_", url.split("/")[-1])

                out_file = OUTPUT_DIR / f"{name}.html"
                body = response.text()
                out_file.write_text(body, encoding="utf-8")
                print(f"[✓] Saved {out_file.name}")
            except Exception as e:
                print(f"[!] Error saving response: {e}")

    page.on("response", on_response)
    return captured_responses


def navigate_to_finswimming(page):
    """Переходит на главную страницу и выбирает Finswimming"""
    print("Navigating to main page...")
    page.goto(BASE_URL, wait_until="networkidle")
    time.sleep(3)

    # Сохраняем отладочную информацию
    page.screenshot(path=OUTPUT_DIR / "debug_main_page.png")
    (OUTPUT_DIR / "debug_main_page.html").write_text(page.content(), encoding="utf-8")
    print("✓ Saved debug files")

    # Ищем iframe
    print("Looking for iframe...")
    iframe = page.frame_locator("#infosystemiframe")
    print("✓ Found iframe")

    # Кликаем Finswimming
    print("Clicking Finswimming...")
    iframe.locator("text=Finswimming").first.click()
    time.sleep(3)

    return iframe


def switch_to_event_view(iframe, page):
    """Переключается на вид 'by Event'"""
    print("Switching to 'by Event' view...")
    iframe.locator("text=by Event").first.click()
    time.sleep(5)

    # Сохраняем скриншот для отладки
    page.screenshot(path=OUTPUT_DIR / "after_by_event.png")
    (OUTPUT_DIR / "after_by_event.html").write_text(page.content(), encoding="utf-8")
    print("✓ Switched to event view")


def find_events(iframe):
    """Находит все события на странице"""
    print("Looking for events...")

    events = iframe.locator(
        "[class*='RelatedInfoItemScheduleDescriptionEvent']")
    event_count = events.count()
    print(f"Found {event_count} events by class")

    if event_count == 0:
        events = iframe.locator("div > div").filter(
            has_text=re.compile(r"Women|Men", re.IGNORECASE))
        event_count = events.count()
        print(f"Found {event_count} events by text pattern")

    return events, event_count


def get_event_name(iframe, event, event_index):
    """Получает название ивента"""
    event_name = f"Event_{event_index + 1}"

    # Пытаемся найти название разными способами
    try:
        # Способ 1: Ищем в родительских элементах
        parent_container = event.locator(
            "xpath=./ancestor::*[contains(@class, 'RelatedInfoItem') or contains(@class, 'ScheduleItem')][1]")
        name_element = parent_container.locator(
            ":text-matches('.*'):not(:has-text('Event Summary'))").first
        if name_element.count() > 0:
            event_name = name_element.inner_text().strip()
            return event_name
    except:
        pass

    # Способ 2: Ищем в соседних элементах
    try:
        name_element = event.locator(
            "xpath=preceding-sibling::*[1] | following-sibling::*[1]")
        if name_element.count() > 0:
            event_name = name_element.inner_text().strip()
    except:
        pass

    return event_name


def process_event_summary(page, iframe, event, event_index, event_count):
    """Обрабатывает Event Summary для конкретного ивента"""
    print(f"\n--- Processing event {event_index + 1}/{event_count} ---")

    # Получаем название ивента
    event_name = get_event_name(iframe, event, event_index)
    print(f"  Event: {event_name}")

    try:
        print("  Navigating DOM structure...")

        # Прокручиваем до видимости event
        event.scroll_into_view_if_needed()
        page.wait_for_timeout(500)

        # Поднимаемся на 6 родителей
        parent = event
        for _ in range(6):
            parent = parent.locator("xpath=..")

        print("  Click parent")
        parent.evaluate("(el) => el.click()")
        # Берем еще одного родителя (7-й уровень)
        outer_parent = parent.locator("xpath=..")

        # Находим div с классом content
        content_div = outer_parent.locator("div.content")

        # Находим div, чей класс начинается с 'FNL-'
        final_div = content_div.locator(":scope div[key^='FNL-']").first

        header_div = final_div.locator("div.header")
        header_div.click()
        print("  Clicked header_div")

        page.wait_for_timeout(1500)

        # Внутри final_div находим div.content
        final_content = final_div.locator("div.content")

        # Находим ссылку с классом resultLink (в любом потомке)
        result_link = final_content.locator("a.resultLink", has_text="")
        result_link.click()
        print("  Clicked resultLink")

        page.wait_for_timeout(3000)

        # Сохраняем страницу Event Summary
        save_event_summary_page(iframe, event_name, event_index)

        # Возвращаемся назад
        page.evaluate("window.history.back()")
        page.wait_for_timeout(3000)

        return True

    except Exception as e:
        print(f"  Error processing Event Summary: {e}")
        return False


def save_event_summary_page(iframe, event_name, event_index):
    """Сохраняет страницу Event Summary"""
    try:
        # Сохраняем HTML содержимое
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', event_name)
        filename = f"event_summary_{event_index + 1}_{safe_name}.html"

        # Получаем содержимое iframe
        html_content = iframe.locator("body").inner_html()
        (OUTPUT_DIR / filename).write_text(html_content, encoding="utf-8")
        print(f"  ✓ Saved Event Summary: {filename}")

    except Exception as e:
        print(f"  Error saving Event Summary: {e}")


def save_final_results(page, captured_responses):
    """Сохраняет финальные результаты и статистику"""
    # Сохраняем финальное состояние
    page.screenshot(path=OUTPUT_DIR / "final_state.png")
    print("✓ Saved final screenshot")

    # Сохраняем информацию о запросах
    requests_file = OUTPUT_DIR / "captured_requests.json"
    requests_file.write_text(json.dumps(
        captured_responses, indent=2), encoding="utf-8")
    print(f"[✓] Saved {len(captured_responses)} captured requests")


def run_scraper():
    """Основная функция запуска скрапера"""
    playwright, browser, context = setup_browser()
    page = context.new_page()
    page.go_back()

    try:
        captured_responses = setup_response_interceptor(page)

        iframe = navigate_to_finswimming(page)

        switch_to_event_view(iframe, page)

        events, event_count = find_events(iframe)
        print(f"Found {event_count} events")

        # Обрабатываем события через Event Summary
        processed_events = 0

        for i in range(event_count):
            try:
                success = process_event_summary(page,
                                                iframe, events.nth(i), i, event_count)
                if success:
                    processed_events += 1
            except Exception as e:
                print(f"Error processing event {i + 1}: {e}")

        print(
            f"\nSuccessfully processed {processed_events}/{event_count} events")

        # Сохраняем финальные результаты
        save_final_results(page, captured_responses)

        print("[✓] Script completed successfully")

    except Exception as e:
        print(f"[!] Critical error: {e}")
        # Сохраняем скриншот при ошибке
        page.screenshot(path=OUTPUT_DIR / "error_state.png")
        raise

    finally:
        # Всегда закрываем браузер
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    run_scraper()
