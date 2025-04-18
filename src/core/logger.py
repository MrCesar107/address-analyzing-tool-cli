import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_loggin():
  logger = logging.getLogger("aatt")
  logger.setLevel(logging.INFO)

  formatter = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s")

  # Console handler
  console = logging.StreamHandler()
  console.setFormatter(formatter)
  logger.addHandler(console)

  # File handler
  log_dir = Path("logs")
  log_dir.mkdir(exist_ok=True)

  file_handler = RotatingFileHandler(log_dir/"aatt.log", maxBytes=10*1024*1024, backupCount=3)
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)

  return logger

logger = setup_loggin()
