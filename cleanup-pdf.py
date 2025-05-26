import os
from pathlib import Path
import pdfplumber


pdf_path = Path(
    r"C:\Users\2008d\TEMP\Ленекс\itogovyj-protokol-kubok-06.10.pdf")
output_text_path = Path("output/cleaned_results.txt")
log_path = Path("output/log_removed_lines.txt")
trash = """
ЦСП "Северный" Электронная система регистрации времени SEIKO 06 октября 2024 г.
Бассейн 50 метров г. Москва
Splash Meet Manager, 
11.78560 Registered to RSF/Moscow City Swimming Federation
"""

trash_keywords = list(filter(bool, trash.split('\n')))

cleaned_lines = []
log_lines = []


def parse_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                if 'дайвинг' in line:
                    print('Found diving style')
                stripped = line.strip()
                if not stripped:
                    log_lines.append("[EMPTY]")
                elif any(keyword.lower() in stripped.lower() for keyword in trash_keywords):
                    log_lines.append(stripped)
                else:
                    cleaned_lines.append(stripped)


if pdf_path.is_dir():
    for file in pdf_path.iterdir():
        if file.suffix != '.pdf':
            continue
        parse_pdf(file)
else:
    parse_pdf(pdf_path)


output_text_path.write_text("\n".join(cleaned_lines), encoding="utf-8")
log_path.write_text("\n".join(log_lines), encoding="utf-8")
