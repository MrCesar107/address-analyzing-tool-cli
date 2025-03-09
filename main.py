import argparse
import requests
import os
import schedule
import time
import sys
import csv
from dotenv import load_dotenv

load_dotenv()

class URLAnalyzer:
  def __init__(self):
    self.api_key = os.getenv('HYBRID_ANALYSIS_API_KEY')
    self.base_uri = "https://www.hybrid-analysis.com/api/v2/quick-scan"
    self.request_header = {
      "api-key": self.api_key,
      "Content-Type": "application/x-www-form-urlencoded",
    }
    self.urls = tuple()
    self.control_urls = []
    self.file_control_check = False

  def scan_url(self, url):
    if not url.strip():
      print("URL is not valid. Please insert a valid URL")
      return

    payload = {
      "url": url,
      "scan_type": "all"
    }

    response = requests.post(f"{self.base_uri}/url", headers=self.request_header, data=payload)

    return response.json()

  def retrieve_scan(self, id_scan):
    response = requests.get(f"{self.base_uri}/{id_scan}", headers=self.request_header)

    return response.json()

  def scan_urls_from_file(self, file_path):
    if not os.path.exists(file_path):
      print(f"The specified file in {file_path} doesn't exist")
      return

    print("Scanning URLs in file... (This takes about 5 minutes)")

    self.__read_urls_from_file(file_path)
    self.__generate_urls_file_control()

    # This line schedules the job for generating file control
    schedule.every(1).minutes.do(self.__generate_urls_file_control)

    while not self.file_control_check:
      schedule.run_pending() # Runs pending jobs
      time.sleep(1) # Avoids CPU overload

    print("Retrieving results...")
    self.__generate_result_file()

  def destroy_urls_file_control(self):
    if os.path.exists("urls_control.txt"):
      os.remove("urls_control.txt")
    else:
      print("An error has ocurred")

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
      self.control_urls = []
      with open("urls_control.txt", "w", encoding="utf-8") as file:
        for url in self.urls:
          result = self.scan_url(url)

          if result.get('message') is not None:
            self.control_urls.append([url, f"message: {result.get('message')}"])
            file.write(f"{url}, message: {result.get('message')}\n")
          else:
            self.control_urls.append([url, result.get('id'), result.get('finished')])
            file.write(f"{url}, {result.get('id')}, {result.get('finished')}\n")
    else:
      self.control_urls = []

      with open("urls_control.txt", "r", encoding="utf-8") as file:
        url_lines = csv.reader(file)

        for line in url_lines:
          url, scan_id, state = line
          state = state.strip().lower() == "true"
          self.control_urls.append([url, scan_id, state])

      with open("urls_control.txt", 'w', encoding='utf-8') as file:
        for i, sub in enumerate(self.control_urls):
          url, scan_id, state = sub
          result = self.retrieve_scan(scan_id.strip())

          if result.get('message') is not None:
            file.write(f"{url}, message: {result.get('message')}")

          self.control_urls[i][2] = result.get('finished')
          file.write(f"{url}, {result.get('id')}, {result.get('finished')}\n")

      if all(sub_element[2] == True for sub_element in self.control_urls):
        self.file_control_check = True
        return schedule.CancelJob # Stops scheduling jobs

  def __generate_result_file(self):
    self.control_urls = []

    with open('urls_control.txt', 'r', encoding='utf-8') as file:
      url_lines = csv.reader(file)

      for i, line in enumerate(url_lines):
        url, scan_id, state = line
        result = self.retrieve_scan(scan_id.strip())
        databases = result.get('scanners_v2')


        self.control_urls.append([url, []])

        for key, value in databases.items():
          sub_array = self.control_urls[i][1]

          if isinstance(value, dict):
            sub_array.append([key, value.get('status')])
          else:
            sub_array.append([key, value])

    csv_dynamic_headers = sorted({entry[0] for row in self.control_urls for entry in row[1]})
    csv_headers = ["url"] + csv_dynamic_headers

    with open('scan_results.csv', 'w', encoding='utf-8') as file:
      writer = csv.writer(file)
      writer.writerow(csv_headers)

      for url_entry in self.control_urls:
        url = url_entry[0]
        values = {db: "N/A" for db in csv_dynamic_headers}

        for db, status in url_entry[1]:
          values[db] = status if status is not None else "N/A"

        row = [url] + [values[db] for db in csv_dynamic_headers]
        writer.writerow(row)

    print("Results were printed in scan_results.csv")


def main():
  parser = argparse.ArgumentParser(
                      prog='address-analyzing-tool',
                      description='A CLI tool to analize URLs using Hybrid Analysis API')
  parser.add_argument('-f', '--file', type=str, help='Set a .txt file with URLs to analyze')
  parser.add_argument('-u', '--url', type=str, help='Set a URL address to analyze')
  parser.add_argument('-r', '--retrieve-scan', type=str, help='Retrieve a previous URL scan')

  args = parser.parse_args()
  analyzer = URLAnalyzer()

  if args.file:
    analyzer.scan_urls_from_file(args.file)
    analyzer.destroy_urls_file_control()

  if args.url:
    scan_result = analyzer.scan_url(args.url)
    print(f"Scan results of {args.url}:")
    print(scan_result)

  if args.retrieve_scan:
    result = analyzer.retrieve_scan(args.retrieve_scan)
    print(f"Scan results of {args.retrieve_scan}:")
    print(result)

if __name__ == "__main__":
  main()
