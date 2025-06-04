from collections import defaultdict
import json
from pathlib import Path
from lenexpy import fromfile


class SwimResultsParser:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.lenex = fromfile(input_file)

    def parse(self):
        individual = []
        events = {}
        rankings = {}
        standards = defaultdict(lambda: defaultdict(dict))
        for session in self.lenex.meet.sessions:
            for event in session.events:
                events[event.eventid] = (
                    event.swimstyle.stroke, event.swimstyle.distance, event.gender)
                for agegroup in event.agegroups:
                    for rank in agegroup.rankings:
                        if rank.place <= 0:
                            continue
                        rankings[rank.result_id] = rank.place

        for standardList in self.lenex.timeStandardLists:
            for standard in standardList.timeStandards:
                standards[(standardList.gender,
                           standard.swimstyle.stroke,
                           standard.swimstyle.distance)][standardList.code] = standard.swimtime.as_duration()

        for club in self.lenex.meet.clubs:
            for athl in club.athletes:
                if not athl.results:
                    continue
                for res in athl.results:
                    if res.status == 'DNS':
                        print('Skip DNS', res.resultid)
                        continue
                    if len(athl.firstname.split()) >= 2:
                        new = athl.firstname.split()[0]
                        # print(athl.firstname, '=>', new)
                        athl.firstname = new

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
                        'dsq': False,
                        'dsq_final': False
                    }
                    if res.status in ('DSQ', 'DNF'):
                        data['dsq'] = True
                    if res.swimTime.as_duration() == 0:
                        print('Skip DNS', res.resultid)
                        continue
                    data['result'] = str(res.swimTime)
                    data['final_rank'] = self.get_license(
                        res.swimTime.as_duration(),
                        standards[(athl.gender,
                                   event.swimstyle.stroke,
                                   event.swimstyle.distance)]
                    )
                    place = rankings.get(res.resultid)
                    if place is None:
                        if data['dsq']:
                            print('DSQ PLACE', res.resultid)
                            place = ''
                        else:
                            print('EXH PLACE', res.resultid)
                            place = 'EXH'
                    data['place'] = str(place)
                    individual.append(data)

        with open(self.output_file, 'wb') as file:
            file.write(json.dumps({
                'individual_results': individual,
                'distances': [';'.join(map(str, ev)) for ev in events.values()]
            },
                indent=4,
                ensure_ascii=False,
            ).encode())

    def get_license(self, result: float, standards: dict):
        for code, standard_result in standards.items():
            if result < standard_result:
                return code


if __name__ == '__main__':
    input_file = r"C:\Users\2008d\Downloads\20250531_PL2.lxf"
    output_file = Path("output/output_results.json")
    SwimResultsParser(input_file, output_file).parse()
