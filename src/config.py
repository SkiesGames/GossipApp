import os

# Parse MODE variable (server/client)
MODE = os.getenv("MODE").lower().strip()

COORDINATOR_IP = os.getenv("COORDINATOR_IP", "0.0.0.0")
COORDINATOR_PORT = int(os.getenv("COORDINATOR_PORT", "8888"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
