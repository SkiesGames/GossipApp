import os

IS_CLIENT = bool(os.getenv("IS_CLIENT"))
IS_SERVER = bool(os.getenv("IS_SERVER"))

COORDINATOR_IP = os.getenv("COORDINATOR_IP")
COORDINATOR_PORT = int(os.getenv("COORDINATOR_PORT"))


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
