# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

from pathlib import Path
import csv
from typing import List, Dict
from src.core.logger import logger

class ResultsFileHandler:
  def __init__(self, filename: str = "scan_results.csv"):
    self.filename = Path(filename)
    self._ensure_file_exists()

  def _ensure_file_exists(self):
    self.filename.touch(exist_ok=True)

  def write_results(self, data: List[Dict], headers: List[str]):
    try:
      with open(self.filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)

        if self.filename.stat().st_size == 0:
          writer.writeheader()
        writer.writerows(data)

      logger.info(f"Results written in file {self.filename}")
    except Exception as e:
      logger.error(f"Error writing results: {str(e)}")
      raise
