from pathlib import Path
import pdfplumber

pdf_path = Path("Технич.протокол_4день_ПР_Томск_2025.pdf")
output_text_path = Path("output/cleaned_results.txt")
log_path = Path("output/log_removed_lines.txt")

trash = """
Первенство России по подводному спорту
(группы спортивных дисциплин
в классических ластах, подводное плавание, ныряние в ластах в длину)
юниоры, юниорки (14-17 лет)
24 - 30 марта 2025
г. Томск, ЦВВС "Звездный", 50 метров
бассейн оснащен электронной системой хронометража "Swiss Timing"
ИТОГОВЫЙ ПРОТОКОЛ
Место Разряд Фамилия, Имя Г.р. Команда Результат Финал Разряд Очки
"""

trash_keywords = list(filter(bool, trash.split('\n')))

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
