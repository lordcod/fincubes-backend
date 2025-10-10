from datetime import datetime
import json
from pathlib import Path
import re
import openpyxl

distance_re = re.compile(
    r"(?P<style>.+)\s*-\s*(?P<distance>\d+) м.+",
    re.IGNORECASE,
)
gender_re = re.compile(
    r"(?P<gender>[а-я]+)\s*\(.+\).*",
    re.IGNORECASE,
)
place_re = re.compile(
    r"(\d+|в/к)",
    re.IGNORECASE,
)
time_re = re.compile(
    r"(\d{1,2}[:,.])?\d{2}[:,.]\d{1,2}",
    re.IGNORECASE,
)


class SwimResultsParser:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.workbook = openpyxl.load_workbook(input_file)
        self.sheet = self.workbook.active

    def parse(self):
        individual = []
        events = []
        is_combin = False
        for index, row in enumerate(self.sheet.iter_rows(values_only=True)):
            if not row[2] and not row[1]:
                continue

            if (row[2] and 'эстафета' in row[2].lower()) or (row[1] and 'эстафета' in row[1].lower()):
                is_combin = True
                print('эстафета', index)
                continue
            if distance_re.fullmatch(row[2]):
                is_combin = False
                events.append(row[2])
                continue
            if is_combin:
                continue
            # if row[0] and row[6] and distance_re.fullmatch(row[0]) and gender_re.fullmatch(row[6]):
            #     events.append(f'{row[0]} {row[6]}')
            #     continue

            if (row[0] and (not isinstance(row[0], int) or (isinstance(row[0], str) and not place_re.fullmatch(row[0])))):
                print('SKIP', row)
                continue
            lastname, firstname = row[2].split()

            result = row[8]
            dsq = False
            if isinstance(result, int):
                result = f'{result}.00'
            if isinstance(result, float):
                result = f'{result}'
            if not time_re.fullmatch(result):
                print('Give dsq', result)
                dsq = True
                result = None

            data = {
                'distance': events[-1],
                'place': str(row[0]),
                'last_name': lastname,
                'first_name': firstname,
                'birth_year': row[4].year if isinstance(row[4], datetime) else int(row[4]),
                'team': row[5],
                'rank': row[1],
                'final': None,
                'result': result,
                'final_rank': row[9],
                'points': '',
                'record': '',
                'dsq': dsq,
                'dsq_final': False
            }
            individual.append(data)

        with open(self.output_file, 'wb') as file:
            file.write(json.dumps({
                'individual_results': individual,
                'distances': events
            },
                indent=4,
                ensure_ascii=False,
            ).encode())


if __name__ == '__main__':
    input_file = Path(
        r"C:\Users\2008d\Downloads\ITOGOVYI_774_g.xlsx")
    output_file = Path("output/1_output_results.json")
    SwimResultsParser(input_file, output_file).parse()
