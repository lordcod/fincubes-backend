#!/usr/bin/env python3
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

ROOT_PATH = Path("lsport")
ROOT_PATH.mkdir(exist_ok=True)

input_file = ROOT_PATH / "output.json"
output_file = Path("output/1_output_results.json")

RANKS = {
    0: "Б/Р", 5: "3 юн", 6: "2 юн", 7: "1 юн",
    15: "3", 16: "2", 17: "1",
    25: "КМС", 26: "МС", 27: "МСМК", 28: "ЗМС", 29: "ГМ",
    50: "ЗРФК РФ", 51: "ЗТ РФ", 52: "ЗТ СССР",
    53: "МПЛ", 54: "МНР", 55: "ОФКС", 56: "ЗРФК",
    57: "ОНП", 58: "ПРО", 59: "ПС",
    1000000: "Другое"
}


def get_rank(rank_id: Any) -> str:
    try:
        return RANKS.get(int(rank_id), "")
    except (ValueError, TypeError):
        return ""


@dataclass
class SwimResult:
    distance: str
    last_name: str
    first_name: str
    birth_year: str
    team: str
    status: str
    city: str = ""
    coach: str = ""
    place: str = ""
    result: str = ""
    rank: str = ""
    final: str = ""
    final_rank: str = ""
    points: str = ""
    record: str = ""
    patronymic: str = ""


def process_item(item: Dict[str, Any], event: Dict[str, Any]) -> SwimResult:
    person = item.get("Person", {})
    results = item.get("Results", {}).get("Final", {}) or {}
    td = item.get("TournamentDiscipline", {})
    res = item.get("FinalResult", 0)
    is_dsq = res < 0

    return SwimResult(
        distance=td.get("Name") or event.get("Discipline", {}).get("Name", ""),
        last_name=person.get("LastName", ""),
        first_name=person.get("FirstName", ""),
        patronymic=person.get("MiddleName", ""),
        birth_year=str(person.get("BirthYear", "")),
        team=item.get("Organization", ""),
        status="DSQ" if is_dsq else "COMPLETED",
        city=person.get("City", {}).get("Name", ""),
        coach=item.get("Trainer", ""),
        place=str(results.get("Place") or item.get("Place") or ""),
        result=(
            results.get("FormattedResult")
            or item.get("FinalFormattedResult", "")
            or item.get("FormattedAppliedResult", "")
        ),
        rank=get_rank(person.get("RankID", "")),
        final_rank=get_rank(item.get("NewRankID", "")),
        points=str(results.get("Points") or ""),
        record=""
    )


def extract_results_from_json(all_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Возвращает список всех результатов участников как словари"""
    all_results: List[Dict[str, Any]] = []
    for data in all_data:
        for event in data:
            for item in event.get("Data", {}).get("Items", []):
                all_results.append(asdict(process_item(item, event)))
    return all_results


def extract_unique_distances(all_results: List[Dict[str, Any]]) -> List[str]:
    """Возвращает список уникальных дистанций, сохраняя порядок"""
    seen = set()
    distances = []
    for result in all_results:
        distance = result.get("distance", "")
        if distance and distance not in seen:
            seen.add(distance)
            distances.append(distance)
    return distances


if __name__ == "__main__":
    with open(input_file, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    all_results = extract_results_from_json(all_data)
    distances = extract_unique_distances(all_results)

    output_data = {
        'individual_results': all_results,
        'distances': distances
    }
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(
        f"[✓] Готово! Сохранено {len(all_results)} результатов → {output_file}")
    print(f"[✓] Список дистанций сохранен → {output_file}")
