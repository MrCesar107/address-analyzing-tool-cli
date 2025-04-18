from src.scanners.hybrid_analysis import HybridAnalysisScanner
from src.scanners.recorded_future import RecordedFutureScanner
from src.scanners.base_scanner import URLScanner
from src.core.exceptions import ConfigurationError

class ScannerFactory:
  _engines = {
    "HybridAnalysis": HybridAnalysisScanner,
    "RecordedFuture": RecordedFutureScanner
  }

  @classmethod
  def create_scanner(cls, engine: str) -> URLScanner:
    if engine not in cls._engines:
      raise ConfigurationError(f"Scanner {engine} is not supported")

    return cls._engines[engine]()

  @classmethod
  def list_engines(cls):
    return list(cls.__engines.keys())
