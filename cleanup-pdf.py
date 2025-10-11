import re
import pdfplumber
import pytesseract
from pathlib import Path


# Путь к PDF6
pdf_path = Path(
    r"C:\Users\2008d\TEMP\ВС\ЛЕНЕКС 🤿Итоговый_🇷🇺ВС_протокол_результатов_ВРВС_черновик.pdf"
)

# Мусорные ключевые фразы
trash = """
Главный судья соревнований, судья ССВК Е.В. Кулик
Главный секретарь соревнований, судья ССВК А.И. Подгорный
Норматив А
04.2023 Результаты

№ Фамилия имя
Место Фамилия Имя
Место Год рождения
Splash Meet Manager
Главный судья
Главный секретарь
"""
trash_keywords = [t.strip().lower()
                  for t in trash.strip().split('\n') if t.strip()]

# Результаты
cleaned_lines = []
seen_logs = set()  # Для уникальных логов


def fix_ocr_errors(text: str) -> str:
    return (
        text.replace("|", "I")
            .replace("]", "I")
    )


def clean_line(line: str):
    stripped = line.strip()
    lowered = stripped.lower()

    if not stripped:
        log_msg = "[EMPTY]"
    elif any(k in lowered for k in trash_keywords):
        log_msg = stripped
    else:
        cleaned_lines.append(stripped)
        return

    if log_msg not in seen_logs:
        print(f"REMOVED: {log_msg}")
        seen_logs.add(log_msg)


def parse_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                for line in text.split('\n'):
                    clean_line(line)
            else:
                print(f"OCR: page {i+1}")
                continue
                image = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(image, lang="rus+eng")
                for line in ocr_text.split('\n'):
                    clean_line(fix_ocr_errors(line))


def extract_number(filename):
    """Извлекает первое число из имени файла, если есть, иначе возвращает None."""
    match = re.search(r'\d+', filename)
    if match:
        return int(match.group())
    return None


if pdf_path.is_dir():
    files = sorted(
        (f for f in pdf_path.iterdir() if f.suffix == '.pdf'),
        key=lambda f: (extract_number(f.stem) is None,
                       extract_number(f.stem) or 0, f.name)
    )

    for file in files:
        if file.suffix != '.pdf':
            continue
        parse_pdf(file)
else:
    parse_pdf(pdf_path)

output_text_path = Path(
    "output/0_cleaned_results.txt")
output_text_path.write_text("\n".join(cleaned_lines), encoding="utf-8")
