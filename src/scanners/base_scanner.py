# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

from abc import ABC, abstractmethod
import requests
import validators
from src.core.exceptions import InvalidURLError

class BaseScanner(ABC):
  def __init__(self, api_key: str, base_url: str):
    self.api_key = api_key
    self.base_url = base_url
    self.session = requests.Session()

  def validate_url(self, url: str):
    if not validators.url(url):
      raise InvalidURLError(f"Invalid URL: {url}")

  @abstractmethod
  def scan_url(self, url: str) -> dict:
    pass

  @abstractmethod
  def retrieve_scan_results(self, scan_id: str) -> dict:
    pass
