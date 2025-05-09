from pathlib import Path
import pdfplumber

pdf_path = Path("Итоговый.pdf")
output_text_path = Path("cleaned_results.txt")
log_path = Path("log_removed_lines.txt")

trash_keywords = [
    "ИТОГОВЫЙ ПРОТОКОЛ",
    "Плавательный бассейн",
    "Первенство Томской области",
    "Swiss timing", "г. Новосибирск", "Апреля", "Мая", "стр.",
    "страница", "ЦВВС \"Звездный\"-50м", "дисциплин",
    "Место Разряд ФИ г/р Команда Результат Разряд"
]

cleaned_lines = []
log_lines = []

# Чтение PDF и обработка строк
with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if not text:
            continue
        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped:
                log_lines.append("[EMPTY]")
            elif any(keyword.lower() in stripped.lower() for keyword in trash_keywords):
                log_lines.append(stripped)
            else:
                cleaned_lines.append(stripped)

# Сохранение очищенного текста и лога
output_text_path.write_text("\n".join(cleaned_lines), encoding="utf-8")
log_path.write_text("\n".join(log_lines), encoding="utf-8")

output_text_path, log_path
