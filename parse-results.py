import logging
from pathlib import Path
from models.swim import SwimResultsParser


# Дистанции
# r"^.*?метров.*?(Женщины|Мужчины)$"
# r"^.*?метров.*?$"
#  r"^.+\s-\s.*?метров.*?$"
#  r"^.+-\s?\d+\s?м.*?$"
# r"(\d\s)?\d{2,}(\sм)?.+\d{4}.+г\.р\..*"
# r"Дистанция\s\d+.+"


def main():
    input_file = Path("output/cleaned_results.txt")
    output_file = Path("output/output_results.json")

    parser = SwimResultsParser(
        get_parser('lenex'),
        distance_header_re=r"Дистанция\s\d+.+",
        input_file=input_file,
        output_file=output_file,
    )
    parser.parse()


def get_parser(type: str):
    match type.lower():
        case 'lenex':
            from models_lenex.individual import IndividualParser
        case 'final':
            from models_wfwp.individual import IndividualParser
        case 'points':
            from models_wpnf.individual import IndividualParser
        case _:
            from models_custom.individual import IndividualParser
    return IndividualParser


def load_logging():
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


if __name__ == "__main__":
    load_logging()
    main()
