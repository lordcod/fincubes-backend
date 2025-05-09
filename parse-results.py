from pathlib import Path
from models_no_final.swim import SwimResultsParser

# Константы для ошибок


def main():
    input_file = Path("cleaned_results.txt")
    output_file = Path("output_results.json")  # Можно менять на .xlsx
    error_log_path = Path("errors.log")

    parser = SwimResultsParser(
        input_file, output_file, error_log_path, file_format='json')
    parser.parse()


if __name__ == "__main__":
    main()
