# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# =========================================

import argparse
import requests
import os
import schedule
import time
import sys
import csv
import json
import validators
import pytz
from dotenv import load_dotenv
from abc import abstractmethod
from abc import ABCMeta
from datetime import datetime

load_dotenv()

class URLScanner(metaclass=ABCMeta):
  @abstractmethod
  def scan_url(self, url):
    pass

  @abstractmethod
  def retrieve_scan_results(self, scan_id):
    pass

class HybridAnalysisScanner(URLScanner):
  def __init__(self):
    self.api_key = os.getenv('HYBRID_ANALYSIS_API_KEY')
    self.base_uri = "https://www.hybrid-analysis.com/api/v2/quick-scan"
    self.request_header = {
      "api-key": self.api_key,
      "Content-Type": "application/x-www-form-urlencoded",
    }

  def scan_url(self, url):
    if not validators.url(url):
      print("URL is not valid. Please insert a valid URL")
      return

    payload = {
      "url": url,
      "scan_type": "all"
    }
    response = requests.post(f"{self.base_uri}/url", headers=self.request_header, data=payload)

    return response.json()

  def retrieve_scan_results(self, id_scan):
    if not id_scan:
      print("Please provide a valid ID to retrieve a previous scan")
      return

    response = requests.get(f"{self.base_uri}/{id_scan}", headers=self.request_header)

    return response.json()

class RecordedFutureScanner(URLScanner):
  def __init__(self):
    self.api_token = os.getenv('RECORDED_FUTURE_BEARER_TOKEN')
    self.base_uri = 'https://sandbox.recordedfuture.com/api/v0'
    self.request_header = {
      "Authorization": f'Bearer {self.api_token}',
      "Content-Type": 'application/json',
    }

  def scan_url(self, url):
    if not validators.url(url):
      print("URL is not valid. Please insert a valid URL")
      return

    payload = {
      "url": url
    }
    response = requests.post(f"{self.base_uri}/samples", headers=self.request_header, data=json.dumps(payload))

    return response.json()

  def retrieve_scan_results(self, id_scan):
    if not id_scan:
      print("Please provide a valid ID to retrieve a previous scan")
      return

    response = requests.get(f"{self.base_uri}/samples/{id_scan}", headers=self.request_header)

    return response.json()

class ResultsFileGenerator:
  def __init__(self):
    self.hybrid_analysis_scanner = HybridAnalysisScanner()
    self.recorded_future_scanner = RecordedFutureScanner()
    self.control_urls = []

  def generate(self):
    with open('urls_control.txt', 'r', encoding='utf-8') as file:
      url_lines = csv.reader(file)

      for i, line in enumerate(url_lines):
        engine, url, scan_id, state = line

        if engine == "RecordedFuture":
          result = self.recorded_future_scanner.retrieve_scan_results(scan_id.strip())
          databases = result.get('tasks')
        else:
          result = self.hybrid_analysis_scanner.retrieve_scan_results(scan_id.strip())
          databases = result.get('scanners_v2')

        self.control_urls.append([engine.strip(), url.strip(), []])

        if engine == "RecordedFuture":
          for element in databases:
            sub_array = self.control_urls[i][-1]
            sub_array.append([element['id'], element['status']])
        else:
          for key, value in databases.items():
            sub_array = self.control_urls[i][-1]

            if isinstance(value, dict):
              sub_array.append([key, value.get('status')])
            else:
              sub_array.append([key, value])

    engines_prefixes_map = {
      "HybridAnalysis": "ha",
      "RecordedFuture": "rf"
    }

    csv_dynamic_headers = sorted({
      f"{engines_prefixes_map.get(item[0], item[0][:2].lower())}_{subitem[0]}"
      for item in self.control_urls for subitem in item[2]
    })
    csv_headers = ["url"] + csv_dynamic_headers + ["generated_at"]
    urls_dict = {}

    for url_entry in self.control_urls:
        source = url_entry[0]
        url = url_entry[1]
        report_results = url_entry[2]
        prefix = engines_prefixes_map.get(source, source[:2].lower())

        if url not in urls_dict:
          urls_dict[url] = {col: "N/A" for col in csv_dynamic_headers}

        for subitem in report_results:
          key_header = f"{prefix}_{subitem[0]}"
          urls_dict[url][key_header] = subitem[1] if subitem[1] is not None else "N/A"

    with open('scan_results.csv', 'w', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(csv_headers)

      for url, values in urls_dict.items():
        timestamp = datetime.now(pytz.timezone("America/Mexico_City")).strftime("%a, %d %b %Y %H:%M:%S.%f000 %Z %z")
        row = [url] + [values[col] for col in csv_dynamic_headers] + [timestamp]
        writer.writerow(row)

    print("Results were printed in scan_results.csv")

class URLFileScanner:
  def __init__(self):
    self.urls = tuple()
    self.control_urls = []
    self.file_control_check = False
    self.hybrid_analysis_scanner = HybridAnalysisScanner()
    self.recorded_future_scanner = RecordedFutureScanner()
    self.results_file_generator = ResultsFileGenerator()
    self.available_analysis_engines = ('RecordedFuture', 'HybridAnalysis')

  def scan_file(self, file_path):
    if not os.path.exists(file_path):
      print(f"The specified file in {file_path} doesn't exist")
      sys.exit()

    print("Scanning URLs in file... (This takes about 5 minutes)")

    self.__read_urls_from_file(file_path)
    self.__generate_urls_file_control()

    # This line schedules the job for generating file control
    schedule.every(1).minutes.do(self.__generate_urls_file_control)

    while not self.file_control_check:
      schedule.run_pending() # Runs pending jobs
      time.sleep(1) # Avoids CPU overload

    print("Retrieving results...")
    self.results_file_generator.generate()

  # Private methods
  def __read_urls_from_file(self, file_path):
    try:
      with open(file_path, 'r', encoding='utf-8') as file:
        self.urls = tuple(file.read().splitlines())
        return
    except Exception as e:
      print("An error has ocurred reading the file")
      return

  def __generate_urls_file_control(self):
    if any(isinstance(item, str) and "message:" in item for sub in self.control_urls for item in sub):
      print(f"An error has ocurred {self.control_urls[0][1]}")
      sys.exit()

    if not os.path.exists('urls_control.txt'):
      open("urls_control.txt", 'w').close()

    if os.stat("urls_control.txt").st_size == 0:
      with open("urls_control.txt", "w", encoding="utf-8") as file:
        for engine in self.available_analysis_engines:
          for url in self.urls:
            if engine == "RecordedFuture":
              result = self.recorded_future_scanner.scan_url(url)
            else:
              result = self.hybrid_analysis_scanner.scan_url(url)

            if result.get('message') is not None:
              self.control_urls.append([url, f"message: {result.get('message')}"])
              file.write(f"{url}, message: {result.get('message')}\n")
            else:
              if engine == 'RecordedFuture':
                self.control_urls.append([engine, url, result.get('id'), True if result.get('completed') else False])
                file.write(f"{engine}, {url}, {result.get('id')}, {True if result.get('completed') else False}\n")
              else:
                self.control_urls.append([engine, url, result.get('id'), result.get('finished')])
                file.write(f"{engine}, {url}, {result.get('id')}, {result.get('finished')}\n")
    else:
      self.control_urls = []
      with open("urls_control.txt", "r", encoding="utf-8") as file:
        url_lines = csv.reader(file)

        for line in url_lines:
          engine, url, scan_id, state = line
          state = state.strip().lower() == "true"
          self.control_urls.append([engine, url, scan_id, state])

      with open("urls_control.txt", 'w', encoding='utf-8') as file:
        for i, element in enumerate(self.control_urls):
          engine, url, scan_id, state = element

          if engine == "RecordedFuture":
            result = self.recorded_future_scanner.retrieve_scan_results(scan_id.strip())
          else:
            result = self.hybrid_analysis_scanner.retrieve_scan_results(scan_id.strip())

          if result.get('message') is not None:
            file.write(f"{url}, message: {result.get('message')}")

          if engine == "RecordedFuture":
            self.control_urls[i][-1] = True if result.get('completed') else False
            file.write(f"{engine}, {url}, {result.get('id')}, {True if result.get('completed') else False}\n")
          else:
            self.control_urls[i][-1] = result.get('finished')
            file.write(f"{engine}, {url}, {result.get('id')}, {result.get('finished')}\n")

      if all(sub_element[-1] == True for sub_element in self.control_urls):
        self.file_control_check = True
        return schedule.CancelJob # Stops scheduling jobs

class URLAnalyzer:
  def __init__(self):
    self.available_analysis_engines = ('RecordedFuture', 'HybridAnalysis')
    self.recorded_future_scanner = RecordedFutureScanner()
    self.hybrid_analysis_scanner = HybridAnalysisScanner()
    self.url_file_scanner = URLFileScanner()

  def analyze_url(self, *args, **kwargs):
    if not kwargs['engine']:
      print("Please provide an engine (use --list commant to list all available engines)")
      sys.exit()

    if not kwargs['engine'] in self.available_analysis_engines:
      print("Ivalid analysis engine. Use a valid engine (use --list commant to list all available engines)")
      sys.exit()

    if kwargs['engine'] == 'RecordedFuture':
      result = self.recorded_future_scanner.scan_url(args[0])
      self.__print_console_results(args[0], result)
    else:
      result = self.hybrid_analysis_scanner.scan_url(args[0])
      self.__print_console_results(args[0], result)

  def retrive_url_analysis(self, *args, **kwargs):
    if not kwargs['engine']:
      print("Please provide an engine (use --list commant to list all available engines)")
      sys.exit()

    if not kwargs['engine'] in self.available_analysis_engines:
      print("Ivalid analysis engine. Use a valid engine (use --list commant to list all available engines)")
      sys.exit()

    if kwargs['engine'] == 'RecordedFuture':
      result = self.recorded_future_scanner.retrieve_scan_results(args[0])
      self.__print_console_results(args[0], result)
    else:
      result = self.hybrid_analysis_scanner.retrieve_scan_results(args[0])
      self.__print_console_results(args[0], result)

  def analyze_urls_from_file(self, file_path):
    self.url_file_scanner.scan_file(file_path)

  def destroy_urls_file_control(self):
    if os.path.exists("urls_control.txt"):
      os.remove("urls_control.txt")
    else:
      print("An error has ocurred")

  def print_engines_list(self):
    print("Available engines:\n")

    for engine in self.available_analysis_engines:
      print(engine)

  def __print_console_results(self, element, results):
    print(f'Scan results of {element}:\n')
    print(results)

def main():
  parser = argparse.ArgumentParser(
                      prog='address-analyzing-tool',
                      description='A CLI tool to analize URLs using Hybrid Analysis API')
  parser.add_argument('-f', '--file', type=str, help='Set a .txt file with URLs to analyze')
  parser.add_argument('-u', '--url', type=str, help='Set a URL address to analyze')
  parser.add_argument('-r', '--retrieve-scan', type=str, help='Retrieve a previous URL scan')
  parser.add_argument('-l', '--list-engines', help='Prints a list with available analyzing engines', action='store_true')
  parser.add_argument('--engine', type=str, help='Select an analyzing engine (use --list command to print available analyzing engines)')

  args = parser.parse_args()
  analyzer = URLAnalyzer()

  if args.file:
    analyzer.analyze_urls_from_file(args.file)
    analyzer.destroy_urls_file_control()

  if args.url:
    analyzer.analyze_url(args.url, engine=args.engine)

  if args.retrieve_scan:
    analyzer.retrive_url_analysis(args.retrieve_scan, engine=args.engine)

  if args.list_engines:
    analyzer.print_engines_list()

if __name__ == "__main__":
  main()
