# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

import os
from typing import Dict
from dataclasses import dataclass
from pytz import timezone
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
  TIMEZONE: timezone = timezone("America/Mexico_City")
  REQUEST_TIMEOUT: int = 30
  MAX_RETRIES: int = 3
  CACHE_TTL: int = 3600 #seconds
  AVAILABLE_ENGINES = ("RecordedFuture", "HybridAnalysis")

  @property
  def scanners_config(self) -> Dict[str, Dict]:
    return {
      "HybridAnalysis": {
        "api_key_env": os.getenv("HYBRID_ANALYSIS_API_KEY"),
        "base_url": "https://hybrid-analysis.com/api/v2"
      },
      "RecordedFuture": {
        "api_key_env": os.getenv("RECORDED_FUTURE_BEARER_TOKEN"),
        "base_url": "https://sandbox.recordedfuture.com/api/v0"
      }
    }

  def get_scanner_config(self, scanner_name: str) -> dict:
    config = self.scanners_config.get(scanner_name)

    if not config:
      raise ValueError(f"Config not found for {scanner_name}")

    return config

settings = Settings()
