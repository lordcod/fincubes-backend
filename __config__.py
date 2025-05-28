from os import getenv
from dotenv import load_dotenv
load_dotenv(override=True)

TOKEN = getenv('TOKEN')
headers = {
    'Authorization': 'Bearer '+TOKEN,
    "origin": "https://fincubes.ru"
}
