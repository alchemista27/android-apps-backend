import logging
from logging.handlers import RotatingFileHandler
import os

# Buat folder logs jika belum ada
os.makedirs("logs", exist_ok=True)

# Setup logger
logger = logging.getLogger("pjblms_logger")
logger.setLevel(logging.INFO)

# Rotating file handler supaya file log tidak membesar terus
file_handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=5)
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
file_handler.setFormatter(formatter)

# Tambahkan handler ke logger
logger.addHandler(file_handler)
logger.propagate = False
