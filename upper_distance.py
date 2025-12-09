import re

# Список всех твоих regex-шаблонов
REGEX_LIST = [
    r"(?P<style>.+) - (?P<distance>\d+) метров\s*(?P<gender>[а-я]+)",
    r"(?P<style>.+) - (?P<distance>\d+) метров\s*(?P<gender>[а-я]+)(\s*\(.+\))?",
    r"(?P<style>.+) – (?P<distance>\d+) м,?\s*(?P<gender>[а-я]+)\s*(\(.+\))?",
    r"(?P<style>.+) – (?P<distance>\d+) м,?\s*(?P<gender>[а-я]+),?\s*.+",
    r"(?P<style>.+) - (?P<distance>\d+) (метров|м)\s+(?P<gender>[а-яА-Я]+)\s*(\(.+\))?\s*",
    r"(?P<style>.+) - (?P<distance>\d+)\s*м,\s*(?P<gender>[а-я]+)",
    r"(?P<style>.+) - (?P<distance>\d+)\s*м\s*(?P<gender>[а-я]+)\s+.+",
    r"(?P<style>.+)\s+(?P<distance>\d+)\s*(метров|м),\s+(?P<gender>[а-яА-Я]+)\s+.+\s*",

    r"\s*(?P<style>.+)\s*(?P<distance>\d+)\s*М\s*(?P<gender>[а-я]+)\s*",
    r"^[^;]+;\d+;(?P<style>[^-]+)-\s*(?P<distance>\d+)м;(?P<gender>[MF])$",
    r"^\s*.+(?P<gender>Women|Men)'s\s+(?P<distance>\d+)\s*m\s+(?P<style>[A-Z]{2,})\s*$",
    r"^(FSW)(?P<gender>[MW])(?P<distance>\d+)M(?P<style>[A-Z]+)-+(FNL-\d+-+)$",
    r'^\s*Event\s*\d+\s+(?P<gender>Men|Women)\s+[\d\s&\-Over]+(?P<distance>\d+)\s+(?:LC|SC)\s*Meter\s+(?P<stroke>[A-Z]{2,3})\s*$',
    r'(?i)^\s*Event\s*\d+\s+(?P<gender>Men|Women)\s+[\d\s&\-\w]*?(?P<distance>\d+)\s+(?:LC|SC)\s*Meter(?:\s+[A-Za-z]+)*\s+(?P<style>[A-Za-z]{2,20})\s*$',

    r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<style>.+) - (?P<distance>\d+) метров\s*.*",
    r"Дистанция\s+(?P<distance>\d+)м\s+(?P<style>.+),\s*(?P<gender>[а-я]+)\s*",
    r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<style>.+) - (?P<distance>\d+)м.*",
    r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<distance>\d+)m\s(?P<style>[a-zа-я]+).*",
    r"\s*(?P<style>.+) - (?P<distance>\d+) м,\s*(?P<gender>[а-я]+)\s*.+",
    r"(?P<style>.+)\s*- (?P<distance>\d+)\s*м,\s*(?P<gender>[а-я]+)\s*(?P<min_age>\d{4})(-(?P<max_age>\d{4}))?.*",
    r"(9\s)?(?P<distance>\d+)(\s*м)?\s+(?P<style>.+?)\s+(?P<gender>[а-яё]+)\s+(?P<min_age>\d{4})(\-(?P<max_age>\d{4}))?.*",
    r"(?P<style>.+);(?P<distance>.+);(?P<gender>.+)",
    r"Дистанция\s+\d+\s+(?P<gender>[А-Яа-я]+),\s+(?P<distance>\d+)[мm]?\s6+(?P<style>[а-яё\s]+?)(год|\d{4}).*$",
    r"Дистанция\s+(?P<distance>\d+)м\s+(?P<style>[а-яА-ЯёЁ\s]+),\s*(?P<gender>[а-яА-ЯёЁ]+)",
    r"Дистанция\s+\d+,?\s*(?P<gender>[А-Яа-яё]+),?\s*(?P<distance>\d+)\s*м?\s*(?P<style>[А-Яа-яё\s]+?)(?:,?\s*(?:год\s+рождения\s+)?(?P<ages>\d{4}\s*-\s*\d{4}|\d{4}\s*и\s*моложе|\d{4}))?$",
    r"Дистанция\s+\d+,?\s+(?P<gender>[а-я]+),\s+(?P<style>.+)\s*-\s*(?P<distance>\d+)м.*",

    r"(?P<style>.+?)\s*[-–]\s*(?P<distance>\d+)\s*(?:м|метров)\s*(?:\((?P<special_code>[^)]+)\))?\s*(?P<gender>[а-яА-ЯёЁ]+)(?:\s*(?P<min_age>\d{4})(?:-(?P<max_age>\d{4})|\s*и\s*старше)?)?\s*г?\.?р?\.?.+",
    'Дистанция\\s+\\d+,?\\s+(?P<gender>[а-я]+),\\s+(?P<distance>\\d+)m\\s(?P<style>[a-zа-я\\s]+)\\s.*',
    r"(?P<style>.+)\s*-\s*(?P<distance>\d+)\s*м\s*(?P<gender>[а-я]+),?\s*.+",
    r"(?P<style>.+)\s*-\s*(?P<distance>\d+)\s*м\s*\(.+\),\s*(?P<gender>[а-я]+)\s*.+",

    r"(?P<style>.+)\s*-\s*(?P<distance>\d+)\s*м\s*-\s*(?P<gender>[а-я]+)\s*.+",

    r"(?P<distance>\d+)\s+(?P<style>.+)\s*+(?P<gender>девочки|мальчики)",
    r"(?P<distance>\d+)\s*м\s*(?P<style>.+)\s*(?P<gender>[а-я]+)",
    r'(?:9\s)?(?P<distance>\d+)\s*м?\s+(?P<style>.+?)\s+(?P<gender>[а-яё]+)\s+(?P<min_ages>\d{4})(?:-(?P<max_ages>\d{4})|\s*и\s*старше)?\s*г\.р\.?.*',
    r"(?P<style>.+?)-\s*(?P<distance>\d+)\s*м\s*(?P<special_code>\(\d+\w?\))\s*(?P<gender>[а-яА-ЯёЁ]+)\s*(?P<min_age>\d{4})(-(?P<max_age>\d{4})|(\s*и\s*старше))?\s*г\.р\.",
    'Дистанция\\s+\\d+,?\\s*(?P<style>.+)\\s*(-|–)\\s*(?P<distance>\\d+)\\s*м,?\\s*(?P<gender>[а-я]+),?\\s*.+',
]


def parse_distance_input():
    text = input("Enter distance description: ").strip()
    matches = []

    for idx, pattern in enumerate(REGEX_LIST):
        regex = re.compile(pattern, re.IGNORECASE)
        match = regex.fullmatch(text)
        if match:
            matches.append((idx, pattern, match.groupdict()))

    if not matches:
        print("❌ No regex matched this input.")
        return None

    # сортируем по приоритету (индекс)
    matches.sort(key=lambda x: x[0])

    print(f"\n✅ Found {len(matches)} matches, sorted by priority:")
    for idx, pattern, groups in matches:
        print(f"\nPriority {idx}: {pattern!r}")
        for k, v in groups.items():
            print(f"  {k}: {v}")
    return [g for _, _, g in matches]


if __name__ == "__main__":
    parse_distance_input()
