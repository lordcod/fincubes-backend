import re


def time_to_seconds(time_str: str) -> float:
    match = re.match(r'(\d+):(\d+)[,\.](\d+)', time_str)
    if not match:
        raise ValueError("Неверный формат времени. Ожидается MM:SS,FF")

    minutes, seconds, fractions = map(int, match.groups())
    total_seconds = minutes * 60 + seconds + fractions / 100
    return total_seconds


if __name__ == '__main__':
    examples = ["00:14,70", "01:00,70", "02:35,50"]
    for t in examples:
        print(f"{t} -> {time_to_seconds(t)}")
