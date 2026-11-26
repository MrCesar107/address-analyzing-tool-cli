# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

from src.scanners.base_scanner import BaseScanner
from src.core.exceptions import APIError
from src.core.logger import logger
import json
import requests

class RecordedFutureScanner(BaseScanner):
  def __init__(self, api_key: str, base_url: str):
    super().__init__(api_key, base_url)
    self.session.headers.update(
      {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    )

  def scan_url(self, url: str) -> dict:
    self.validate_url(url)
    logger.info(f"Scanning URL with RecordedFuture engine: {url}")

    try:
      response = self.session.post(
          f"{self.base_url}/samples", 
          data=json.dumps({"url": url}),
          timeout=30  # 30 seconds timeout for the entire request
      )
      response.raise_for_status()
      return response.json()
    except requests.exceptions.Timeout as e:
      logger.error(f"RecordedFuture scan timeout for {url}: {str(e)}")
      raise APIError("Request timed out while contacting RecordedFuture API.", None)
    except requests.exceptions.RequestException as e:
      logger.error(f"Error in RecordedFuture scanning for {url}: {str(e)}")
      status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None
      raise APIError(str(e), status_code)

  def retrieve_scan_results(self, scan_id: str) -> dict:
    logger.info(f"Retrieving RecordedFuture scanning results")

    try:
      response = self.session.get(
          f"{self.base_url}/samples/{scan_id}/summary",
          timeout=30  # 30 seconds timeout for the entire request
      )
      response.raise_for_status()
      return response.json()
    except requests.exceptions.Timeout as e:
      logger.error(f"Timeout retrieving RecordedFuture scan results for {scan_id}: {str(e)}")
      raise APIError("Request timed out while retrieving RecordedFuture scan results.", None)
    except requests.exceptions.RequestException as e:
      logger.error(f"Error retrieving RecordedFuture scan results for {scan_id}: {str(e)}")
      status_code = getattr(e.response, "status_code", None) if hasattr(e, "response") else None
      raise APIError(str(e), status_code)
