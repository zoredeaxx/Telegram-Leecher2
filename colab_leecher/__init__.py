import logging
import json
from uvloop import install

try:
    with open("/content/Telegram-Leecher/credentials.json", "r") as file:
        credentials = json.loads(file.read())
except (FileNotFoundError, json.JSONDecodeError):
    logging.critical("credentials.json not found or is invalid!")
    exit()

API_ID = credentials.get("API_ID")
API_HASH = credentials.get("API_HASH")
BOT_TOKEN = credentials.get("BOT_TOKEN")
OWNER = credentials.get("USER_ID")
DUMP_ID = credentials.get("DUMP_ID")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    logging.critical("API_ID, API_HASH, and BOT_TOKEN must be provided!")
    exit()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

colab_bot = None

install()
