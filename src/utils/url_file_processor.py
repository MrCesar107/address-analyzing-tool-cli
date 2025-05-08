import csv
from pathlib import Path
from typing import List, Dict, Set
import schedule
import time
from datetime import datetime
import pytz
from ..core.logger import logger
from ..core.exceptions import ScannerError

class URLFileProcessor:
  def __init__(self, scanners: Dict, results_file: str = "scan_results.csv"):
    self.scanners = scanners
    self.results_file = Path(results_file)
    self.control_file = Path("urls_control.txt")
    self.urls = []
    self.control_urls = []
    self.file_control_check = False

  def process_file(self, file_path: str) -> None:
    try:
      self._read_urls(file_path)
      self._process_urls()
      self._generate_results()
      self._destroy_file_control()
      logger.info("URLs processment completed successfully")
    except Exception as e:
      logger.error(f"Error processing file: {str(e)}")
      raise

  def _read_urls(self, file_path: str) -> None:
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        self.urls = [url.strip() for url in file.readlines() if url.strip()]
      logger.info(f"{len(self.urls)} URLs read from file")
    except Exception as e:
      logger.error(f"Error reading URLs file: {str(e)}")
      raise

  def _process_urls(self) -> None:
    logger.info("Starting URLs processment...")
    self._initialize_control_file()
    schedule.every(1).minutes.do(self._check_scan_status)

    while not self.file_control_check:
      schedule.run_pending()
      time.sleep(1)

  def _initialize_control_file(self) -> None:
    if not self.control_file.exists() or self.control_file.stat().st_size == 0:
      self._create_new_control_file()
    else:
      self._read_control_file()

  def _create_new_control_file(self) -> None:
    with open(self.control_file, 'w', encoding='utf-8') as file:
      writer = csv.writer(file)

      for url in self.urls:
        for engine_name, scanner in self.scanners.items():
          try:
            result = scanner.scan_url(url)
            scan_id = result.get('id')
            completed = result.get('completed', result.get('finished', False))
            writer.writerow([engine_name, url, scan_id, completed])
            self.control_urls.append([engine_name, url, scan_id, completed])
          except Exception as e:
            logger.error(f"Error while scanning {url} with {engine_name}: {str(e)}")
            writer.writerow([engine_name, url, "error", str(e)])

  def _read_control_file(self) -> None:
    self.control_urls = []

    with open(self.control_file, 'r', encoding='utf-8') as file:
      reader = csv.reader(file)

      for row in reader:
        if len(row) == 4:
          engine, url, scan_id, state = row
          state = state.lower() == 'true'
          self.control_urls.append([engine, url, scan_id, state])

  def _check_scan_status(self) -> None:
    updated_control_urls = []
    all_completed = True

    with open(self.control_file, 'w', encoding='utf-8') as file:
      writer = csv.writer(file)

      for entry in self.control_urls:
        engine, url, scan_id, state = entry

        if not state and scan_id != "error":
          try:
            result = self.scanners[engine].retrieve_scan_results(scan_id)
            state = result.get('completed', result.get('finished', False))
          except Exception as e:
            logger.error(f"Error verifying state for {url}: {str(e)}")
            state = False

        writer.writerow([engine, url, scan_id, state])
        updated_control_urls.append([engine, url, scan_id, state])
        all_completed = all_completed and state

    self.control_urls = updated_control_urls

    if all_completed:
      self.file_control_check = True
      return schedule.CancelJob

  def _extract_scan_data(self, engine: str, result: Dict, scan_id: str = None) -> Dict:
    """Extracts and formats scan results from different engines into a standardized format"""
    data = {}

    if engine == 'RecordedFuture':
      if isinstance(result, dict):
        tasks = result.get('tasks', {})
        for task_id, task_data in tasks.items():
          if isinstance(task_data, dict):
            # Verify that the task_id starts with the provided scan_id
            if scan_id and not task_id.startswith(scan_id):
              continue

            status = task_data.get('status', 'No results')
            score = task_data.get('score', 'No results')
            # Extract the engine name from the task_id
            engine_name = task_id.split('-')[-1]
            data[f'rf_{engine_name}'] = status
            data[f'rf_{engine_name}_score'] = score
        # If there are no tasks, add empty columns for RecordedFuture
        if not tasks:
          data['rf_behavioral1'] = 'No results'
          data['rf_behavioral1_score'] = 'No results'
          data['rf_static1'] = 'No results'
          data['rf_static1_score'] = 'No results'
          data['rf_urlscan1'] = 'No results'
          data['rf_urlscan1_score'] = 'No results'
    else:  # HybridAnalysis
      scanners = result.get('scanners_v2', {})
      for scanner_name, scanner_data in scanners.items():
        if isinstance(scanner_data, dict):
          data[f'ha_{scanner_name}'] = scanner_data.get('status', 'No results')
        else:
          data[f'ha_{scanner_name}'] = scanner_data

    return data

  def _generate_results(self) -> None:
    # Dictionary to store results grouped by URL
    url_results = {}

    # Process RecordedFutureResults
    for entry in self.control_urls:
      engine, url, scan_id, state = entry
      if engine == 'RecordedFuture' and state and scan_id != "error":
        try:
          result = self.scanners[engine].retrieve_scan_results(scan_id)
          scan_data = self._extract_scan_data(engine, result, scan_id)
          if url not in url_results:
            url_results[url] = {
              'url': url,
              'generated_at': int(datetime.now(pytz.timezone("America/Mexico_City")).timestamp())
            }
          url_results[url].update(scan_data)
        except Exception as e:
          logger.error(f"Error processing RecordedFuture results for {url}: {str(e)}")

    # Process HybridAnalysis results
    for entry in self.control_urls:
      engine, url, scan_id, state = entry
      if engine == 'HybridAnalysis' and state and scan_id != "error":
        try:
          result = self.scanners[engine].retrieve_scan_results(scan_id)
          scan_data = self._extract_scan_data(engine, result)

          if url not in url_results:
            url_results[url] = {
              'url': url,
              'generated_at': int(datetime.now(pytz.timezone("America/Mexico_City")).timestamp())
            }
          url_results[url].update(scan_data)
        except Exception as e:
          logger.error(f"Error processing HybridAnalysis results for {url}: {str(e)}")

    # Convert dictionary to list for writing
    results_data = list(url_results.values())

    # Define the order of columns
    base_headers = ['url', 'generated_at']
    ha_headers = sorted([h for h in url_results[next(iter(url_results))].keys() if h.startswith('ha_')])
    rf_headers = sorted([h for h in url_results[next(iter(url_results))].keys() if h.startswith('rf_')])

    # Combine headers in desired order
    headers = base_headers + ha_headers + rf_headers

    self._write_results(results_data, headers)

  def _write_results(self, results: List[Dict], headers: List[str]) -> None:
    try:
      # Read the file if it exists
      existing_data = []
      if self.results_file.exists() and self.results_file.stat().st_size > 0:
        with open(self.results_file, 'r', newline='', encoding='utf-8') as file:
          reader = csv.DictReader(file)
          existing_data = list(reader)

      # Combine existing data with new results
      all_results = existing_data + results

      # Write all results
      with open(self.results_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for row in all_results:
          row_data = {header: row.get(header, 'No results') for header in headers}
          writer.writerow(row_data)

      logger.info(f"Results written in {self.results_file}")
    except Exception as e:
      logger.error(f"Error writing results: {str(e)}")
      raise

  def _destroy_file_control(self) -> None:
    try:
      if self.control_file.exists():
        self.control_file.unlink()
        logger.info(f"Control file deleted successfully")
      else:
        logger.warning(f"File control not found or doesn't exist.")
    except Exception as e:
      logger.error(f"An error ocurred while eliminating control file: {str(e)}")
      raise