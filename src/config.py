import os

IS_CLIENT = os.getenv("IS_CLIENT")
IS_SERVER = os.getenv("IS_SERVER")

COORDINATOR_IP = os.getenv("COORDINATOR_IP", "localhost")
COORDINATOR_PORT = int(os.getenv("COORDINATOR_PORT", "8888"))
coordinator_address = f"{COORDINATOR_IP}:{COORDINATOR_PORT}"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")