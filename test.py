import re
relay_start_re = re.compile(
    r".+ - \d+.+х.+\d+.+", re.IGNORECASE)

print(relay_start_re.fullmatch(
    "Плавание в ластах - 4 х 100 метров Юниоры 2007-2010 г.р."))
