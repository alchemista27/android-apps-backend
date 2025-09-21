import logging
from logging.handlers import RotatingFileHandler
import os

# Buat folder logs jika belum ada
os.makedirs("logs", exist_ok=True)

# Ambil level log dari ENV (default: INFO)
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Setup logger utama
logger = logging.getLogger("pjblms_logger")
logger.setLevel(getattr(logging, log_level, logging.INFO))

# Format log
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# --- File handler dengan rotasi ---
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)

# --- Console handler (stdout) ---
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Tambahkan handler ke logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Supaya tidak double log
logger.propagate = False