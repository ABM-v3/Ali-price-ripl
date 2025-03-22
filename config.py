import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7827167607:AAH67veOWXZvlKo8EriBvgfqWLRneQl0Fcs")
BOT_NAME = "Ali Best Price"

# AliExpress API credentials
ALIEXPRESS_APP_KEY = os.getenv("ALIEXPRESS_APP_KEY", "512082")
ALIEXPRESS_APP_SECRET = os.getenv("ALIEXPRESS_APP_SECRET", "8ZR7b0XNh0DDSokcdW50ACF7yUCatSVY")

# Webhook settings
BASE_WEBHOOK_URL = os.getenv("BASE_WEBHOOK_URL", "https://alibestpricebot.vercel.app")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}"

# Admin user IDs (for admin commands like /stats)
ADMIN_USER_IDS = [int(id) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id]

# Rate limiting settings
MAX_REQUESTS_PER_MINUTE = 30
