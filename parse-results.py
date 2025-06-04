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
    input_file = Path("output/0_cleaned_results.txt")
    output_file = Path("output/1_output_results.json")

    type = 'beswimmer'
    parser = SwimResultsParser(
        get_parser(type),
        distance_header_re=r"Дистанция\s\d+\s+.+",
        input_file=input_file,
        output_file=output_file,
    )
    parser.parse()


def get_parser(type: str):
    from parsers import load_dir
    dir = Path('./parsers')
    data = load_dir(dir)
    return data[type.lower()]


def load_logging():
    error_log_path = Path("output/1_errors.log")

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
