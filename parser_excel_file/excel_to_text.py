import logging
from pathlib import Path
from datetime import datetime, date, time
import openpyxl

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class ExcelToTextConverter:
    def __init__(self, input_file, output_file, config):
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        # {'convert_fields': {index: 'type'}} - индекс колонки и тип преобразования
        self.config = config

    def convert_cell(self, cell, conv_type=None):
        if cell is None:
            return ''

        if conv_type == 'year':
            if isinstance(cell, (datetime, date)):
                logging.info(
                    f"Converting datetime/date {cell} to year {cell.year}")
                return str(cell.year)
            else:
                return str(cell)

        elif conv_type == 'time_str':
            if isinstance(cell, time):
                if cell.hour:
                    val = f"{cell.hour}:{cell.minute:02}:{cell.second:02}.{int(cell.microsecond / 10000):02}"
                else:
                    val = f"{cell.minute:02}:{cell.second:02}.{int(cell.microsecond / 10000):02}"
                logging.info(
                    f"Converting numeric {cell} to formatted time string {val}")
                return val
            elif isinstance(cell, (int, float)):
                val = float(cell)
                if 0 < val < 1:
                    total_seconds = val * 24 * 3600
                else:
                    total_seconds = val

                if total_seconds > 36000:
                    return str(cell)

                minutes = int(total_seconds // 60)
                seconds = int(total_seconds % 60)
                hundredths = int(
                    round((total_seconds - int(total_seconds)) * 100))
                return f"{minutes}:{seconds:02}.{hundredths:02}"
            else:
                return str(cell)

        else:
            return str(cell)

    def process_row(self, row):
        result_cells = []
        for idx, cell in enumerate(row):
            conv_type = self.config.get('convert_fields', {}).get(idx)
            val = self.convert_cell(cell, conv_type)
            if val.strip():
                result_cells.append(val.strip())
        return ' '.join(result_cells)

    def convert(self):
        wb = openpyxl.load_workbook(self.input_file, data_only=True)
        sheet = wb.active

        with open(self.output_file, 'w', encoding='utf-8') as f:
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=1):
                row_str = self.process_row(row)
                if row_str:
                    f.write(row_str + '\n')


if __name__ == '__main__':
    input_path = Path(
        r"C:\Users\2008d\Downloads\Telegram Desktop\ИТОГОВЫЙ_Новогодние_старты_2025_—_копия.xlsx")
    output_path = "output/0_cleaned_results.txt"
    config = {
        'convert_fields': {
            # 3: 'year',
            4: 'year',
            # 5: 'time_str',
            8: 'time_str',
        }
    }

    converter = ExcelToTextConverter(input_path, output_path, config)
    converter.convert()
