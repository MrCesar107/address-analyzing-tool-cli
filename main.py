# =========================================
# Address Analyzing Terminal Tool
# By Cesar Augusto Rodriguez Lara
# https://github.com/MrCesar107
# GNU GPL3 License
# =========================================

import argparse
from src.config.settings import settings
from src.core.logger import logger
from src.scanners.hybrid_analysis import HybridAnalysisScanner
from src.scanners.recorded_future import RecordedFutureScanner
from src.utils.file_handlers import ResultsFileHandler

class URLAnalyzer:
  def __init__(self):
    #print(settings.get_scanner_config("HybridAnalysis"))
    self.scanners = {}
    self._initialize_scanners()
    self.file_handler = ResultsFileHandler()

  def _initialize_scanners(self):
    for engine, config in settings.scanners_config.items():
        if engine == 'HybridAnalysis':
            self.scanners[engine] = HybridAnalysisScanner(
                config['api_key_env'],
                config['base_url']
            )
        elif engine == 'RecordedFuture':
            self.scanners[engine] = RecordedFutureScanner(
                config['api_key_env'],
                config['base_url']
            )

  def analyze_url(self, url: str, engine: str):
    try:
        if not engine or engine not in settings.AVAILABLE_ENGINES:
            raise ValueError("Engine not valid")

        scanner = self.scanners[engine]
        result = scanner.scan_url(url)
        logger.info(f"URL analysis successfull: {url}")
        return result
    except Exception as e:
        logger.error(f"Error analyzing URL {url}: {str(e)}")
        raise

  def retrieve_scan(self, scan_id: str, engine: str):
    try:
      if not engine or engine not in settings.AVAILABLE_ENGINES:
        raise ValueError("Engine not valid")

      scanner = self.scanners[engine]
      result = scanner.retrieve_scan_results(scan_id)
      logger.info(f"URL scanning results:\n")
      return result
    except Exception as e:
      logger.error(f"Error retrieving scan results {str(e)}")
      raise

def main():
  parser = argparse.ArgumentParser(
    prog="address-analyzing-tool",
    description="A CLI tool to analize URLs using Hybrid Analysis API"
  )
  parser.add_argument('-f', '--file', type=str, help='Set a .txt file with URLs to analyze')
  parser.add_argument('-u', '--url', type=str, help='Set a URL address to analyze')
  parser.add_argument('-r', '--retrieve-scan', type=str, help='Retrieve a previous URL scan')
  parser.add_argument('-l', '--list-engines', help='Prints a list with available analyzing engines', action='store_true')
  parser.add_argument(
    "--engine",
    type=str,
    choices=settings.AVAILABLE_ENGINES,
    help='Available URLs analyzing engines'
  )

  args = parser.parse_args()
  analyzer = URLAnalyzer()

  if args.file:
    analyzer.analyze_urls_from_file(args.file)
    analyzer.destroy_urls_file_control()

  if args.url:
    try:
      result = analyzer.analyze_url(args.url, args.engine)
      print(f"Analysis result:\n{result}")
    except Exception as e:
      logger.error(f"Error en la ejecución: {str(e)}")
      print(f"Error: {str(e)}")

  if args.retrieve_scan:
    try:
      result = analyzer.retrieve_scan(args.retrieve_scan, args.engine)
      print(f"Analysis result:\n{result}")
    except Exception as e:
      logger.error(f"Error en la ejecución: {str(e)}")
      print(f"Error: {str(e)}")

if __name__ == "__main__":
  main()
