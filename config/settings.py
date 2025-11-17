"""Configuration settings for the scraper"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Groww URLs
GROWW_BASE_URL = "https://groww.in"
GROWW_ICICI_AMC_URL = "https://groww.in/mutual-funds/amc/icici-prudential-mutual-funds"

# Database configuration
# On Render, use absolute path for SQLite to ensure writable location
_default_db_path = os.path.join(os.getcwd(), "icici_funds.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")

# Scraping configuration
REQUEST_DELAY = 2  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Target fund categories
TARGET_CATEGORIES = ["Large Cap", "Mid Cap", "Small Cap", "Large & MidCap", "Large & Mid Cap"]

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "scraper.log"

# Gemini AI Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

