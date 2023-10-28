from dotenv import load_dotenv
import os
import logging
from pathlib import Path

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("DB_PORT")

SERVICE_NAME = "telegram"

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_NAME = os.getenv("CHANNEL_NAME")

logger = logging.getLogger("logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    file_handler = logging.FileHandler(os.path.join(Path(__file__).parent.parent, "logs//logs.log"), encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

console_logger = logging.getLogger("console_logger")
console_logger.setLevel(logging.INFO)
if not console_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    console_handler.setFormatter(formatter)
    console_logger.addHandler(console_handler)

GRPC_TELEGRAM_PORT = os.getenv("GRPC_TELEGRAM_PORT")
TELEGRAM_CONTAINER = os.getenv("TELEGRAM_CONTAINER")

TELEGRAM_QUEUE = os.getenv("TELEGRAM_QUEUE")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS")

RABBIT_HOST = os.getenv("RABBIT_HOST")
