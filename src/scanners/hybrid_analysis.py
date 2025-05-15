# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

from src.scanners.base_scanner import BaseScanner
from src.core.exceptions import APIError
from src.core.logger import logger
import requests

class HybridAnalysisScanner(BaseScanner):
  def __init__(self, api_key: str, base_url: str):
    super().__init__(api_key, base_url)
    self.session.headers.update({"api-key": self.api_key, "Content-Type": "application/x-www-form-urlencoded"})

  def scan_url(self, url: str) -> dict:
    self.validate_url(url)
    logger.info(f"Scanning URL with HybridAnalysis engine: {url}")

    try:
      response = self.session.post(f"{self.base_url}/url", data={"url": url, "scan_type": "all"})
      response.raise_for_status()
      return response.json()
    except requests.exceptions.RequestException as e:
      logger.error(f"Error in HybridAnalysis scanning {str(e)}")
      raise APIError(str(e), getattr(e.response, "status_code", None))

  def retrieve_scan_results(self, scan_id: str) -> dict:
    logger.info(f"Retrieving HybridAnalysis scanning results")

    try:
      response = self.session.get(f"{self.base_url}/{scan_id}")
      response.raise_for_status()
      return response.json()
    except requests.exceptions.RequestException as e:
      logger.error(f"Error retrieving HybridAnalysis scan {str(e)}")
      raise APIError(str(e), getattr(e.response, "status_code", None))
