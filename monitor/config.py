import os
from pathlib import Path

# Загружаем .env файл
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    for line in env_path.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

MONITOR_BOT_TOKEN = os.environ.get("MONITOR_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("CHINAGUARD_ADMIN_ID", "0"))

AITUNNEL_API_KEY = os.environ.get("AITUNNEL_API_KEY", "")
AITUNNEL_BASE_URL = "https://api.aitunnel.ru/v1"
AI_MODEL = "openai/gpt-4o-mini"

TELEGRAM_API_ID = int(os.environ.get("TELEGRAM_API_ID", "0"))
TELEGRAM_API_HASH = os.environ.get("TELEGRAM_API_HASH", "")

CHECK_INTERVAL = 1800
DB_PATH = os.path.join(os.path.dirname(__file__), "monitor.db")
