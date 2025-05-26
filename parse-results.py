import logging
from pathlib import Path
from models.swim import SwimResultsParser
from models_lenex.individual import IndividualParser

# Константы для ошибок


def main():
    input_file = Path("output/cleaned_results.txt")
    output_file = Path("output/output_results.json")  # Можно менять на .xlsx
    error_log_path = Path("output/errors.log")

    file_handler = logging.FileHandler(error_log_path,
                                       mode="w",
                                       encoding='utf-8')
    file_handler.setLevel(logging.WARN)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            file_handler,
            logging.StreamHandler()  # Вывод в консоль
        ]
    )

    parser = SwimResultsParser(IndividualParser,
                               input_file, output_file, error_log_path, file_format='json')
    parser.parse()


if __name__ == "__main__":
    main()
