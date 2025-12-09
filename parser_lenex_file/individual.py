from collections import defaultdict
import json
from pathlib import Path
from lenexpy import fromfile
from typing import List, Dict, Tuple, Optional


class SwimResultsParser:
    def __init__(self, input_file: str, output_file: Path):
        self.input_file = input_file
        self.output_file = output_file
        self.lenex = fromfile(input_file)

    def parse(self):
        events = self._collect_events()
        rankings = self._collect_rankings(events)
        standards = self._collect_standards()

        individual_results = self._process_athletes(
            events, rankings, standards)

        self._save_results(individual_results, events)

    def _collect_events(self) -> Dict[str, Tuple[str, int, str, str]]:
        events = {}
        for session in self.lenex.meet.sessions:
            for event in session.events:
                events[event.eventid] = (
                    event.swimstyle.stroke,
                    event.swimstyle.distance,
                    event.swimstyle.name,
                    event.gender
                )
        return events

    def _collect_rankings(self, events: Dict[str, Tuple[str, int, str, str]]) -> Dict[str, int]:
        rankings = {}
        for session in self.lenex.meet.sessions:
            for event in session.events:
                for agegroup in event.agegroups:
                    for rank in agegroup.rankings or []:
                        if rank.place > 0:
                            rankings[rank.result_id] = rank.place
        return rankings

    def _collect_standards(self) -> Dict[Tuple[str, str, int], Dict[str, float]]:
        standards = defaultdict(lambda: defaultdict(dict))
        for standard_list in self.lenex.timeStandardLists:
            for standard in standard_list.timeStandards:
                key = (standard_list.gender, standard.swimstyle.name,
                       standard.swimstyle.distance)
                standards[key][standard_list.code] = standard.swimtime.as_duration()

        for key, stl in standards.items():
            standards[key] = dict(
                sorted(stl.items(), key=lambda item: item[1]))
        return standards

    def _process_athletes(
        self,
        events: Dict[str, Tuple[str, int, str, str]],
        rankings: Dict[str, int],
        standards: Dict[Tuple[str, str, int], Dict[str, float]]
    ) -> List[Dict]:
        individual = []

        for club in self.lenex.meet.clubs:
            for athl in club.athletes or []:
                if not athl.results:
                    continue

                for res in athl.results:
                    if res.eventid not in events:
                        print('Skip event', res.eventid)
                        continue

                    athl.firstname = athl.firstname.split()[0] if len(
                        athl.firstname.split()) >= 2 else athl.firstname

                    data = self._build_result_data(
                        res, athl, club, events, rankings, standards)
                    individual.append(data)

        return individual

    def _build_result_data(
        self,
        res,
        athl,
        club,
        events,
        rankings,
        standards
    ) -> Dict:
        stroke, distance, name, gender = events[res.eventid]
        standard_key = (athl.gender, name, distance)
        data = {
            'distance': ';'.join(map(str, events[res.eventid])),
            'last_name': athl.lastname,
            'first_name': athl.firstname,
            'birth_year': athl.birthdate.year,
            'team': club.name,
            'rank': athl.license,
            'final': None,
            'points': '',
            'record': '',
            'status': res.status or 'COMPLETED',
            'result': res.swimTime and str(res.swimTime),
            'final_rank': res.swimTime and self.get_license(res.swimTime.as_duration(), standards.get(standard_key, {}))
        }

        if not res.swimTime.as_duration():
            data['result'] = None
        place = rankings.get(res.resultid)
        if not place and data['status'] == 'COMPLETED':
            if not data['result']:
                print('No swim time for result with no place:', data)
            else:
                data['status'] = 'EXH'
                print('No place found, marking as EXH for result:', data)
        if data['status'] != 'COMPLETED':
            print('Status is not completed for result', data['status'])
        if place:
            data['place'] = str(place)

        return data

    def get_license(self, result: float, standards: Dict[str, float]) -> Optional[str]:
        if not result:
            return None
        for code, standard_result in standards.items():
            if result < standard_result:
                return code
        return None

    def _save_results(self, individual_results: List[Dict], events: Dict[str, Tuple[str, int, str, str]]):
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        output_data = {
            'individual_results': individual_results,
            'distances': [';'.join(map(str, ev)) for ev in events.values()]
        }

        with self.output_file.open('w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
        print(f'Results saved to {self.output_file}')


if __name__ == '__main__':
    input_file = r"C:\Users\2008d\Downloads\results.lxf"
    output_file = Path("output/1_output_results.json")
    SwimResultsParser(input_file, output_file).parse()
