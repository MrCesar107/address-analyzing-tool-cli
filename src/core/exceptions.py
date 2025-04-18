class ScannerError(Exception):
  # Base exception for scanning-related errors
  pass

class ConfigurationError(ScannerError):
  # Raised when there is an issue with the configuration
  pass

class InvalidURLError(ScannerError):
  # Raised when an invalid URL is provided
  pass

class APIError(ScannerError):
  "Raised when an API request fails"

  def __init__(self, message: str, status_code: int = None):
    super().__init__(message)
    self.status_code = status_code
