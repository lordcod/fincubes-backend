from os import getenv
from dotenv import load_dotenv

load_dotenv(override=True)
BASE_URL = getenv('BASE_URL')
with open('.token', 'rb') as file:
    TOKEN = file.read().decode().strip()

headers = {
    'Authorization': 'Bearer '+TOKEN,
    "origin": "https://fincubes.ru"
}
