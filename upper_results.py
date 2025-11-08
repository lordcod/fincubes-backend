import contextlib
from pathlib import Path
import re

from parsers import load_dir

# ---------------------------------------------
# State для хранения текущей дистанции (можно расширять)


class State:
    current_distance: str = 'none'


state = State()
current_dir = Path('./parsers')


def parse_results_input():
    text = input("Enter distance description: ").strip()
    matchers = load_dir(current_dir)

    results = []

    for key, matcher_cls in matchers.items():
        try:
            matcher = matcher_cls(state)
            parsed = matcher.parse(text)
            if parsed:
                results.append((key, parsed))
        except Exception as exc:
            print(f'❌ Error regex ({key}): [{type(exc).__name__}] {exc}')

    if not results:
        print("❌ No matcher found a match.")
        return

    print(f"\n✅ Found {len(results)} matches:")
    for key, groups in results:
        print(f"\nMatcher key: {key}")
        print(groups)


if __name__ == "__main__":
    parse_results_input()
