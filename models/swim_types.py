from dataclasses import dataclass, field


@dataclass
class SwimResult:
    distance: str
    place: str
    rank: str
    last_name: str
    first_name: str
    birth_year: str
    team: str
    result: str
    final: str = ""
    final_rank: str = ""
    points: str = ""
    record: str = ""


@dataclass
class RelayResult:
    distance: str
    team_name: str
    place: str
    team_result: str
    points: str
    swimmers: list = field(default_factory=list)


@dataclass
class TeamScore:
    place: str
    team_name: str
    points: str
