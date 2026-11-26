# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

from abc import ABC, abstractmethod
import requests
import validators
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.core.exceptions import InvalidURLError

class BaseScanner(ABC):
  def __init__(self, api_key: str, base_url: str):
    self.api_key = api_key
    self.base_url = base_url
    self.session = self._configure_session()

  def _configure_session(self):
    """Configure a requests session with retry logic and timeout."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    return session

  def validate_url(self, url: str):
    if not validators.url(url):
      raise InvalidURLError(f"Invalid URL: {url}")

  @abstractmethod
  def scan_url(self, url: str) -> dict:
    pass

  @abstractmethod
  def retrieve_scan_results(self, scan_id: str) -> dict:
    pass
