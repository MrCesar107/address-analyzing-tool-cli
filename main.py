import argparse
import requests
import os

from pathlib import Path
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
    print("You used the file flag")

  if args.url:
    scan_result = analyzer.scan_url(args.url)
    print(f"Scan results of #{args.url}:")
    print(scan_result)

  if args.retrieve_scan:
    result = analyzer.retrieve_scan(args.retrieve_scan)
    print(f"Scan results of #{args.url}:")
    print(result)


if __name__ == "__main__":
  main()
