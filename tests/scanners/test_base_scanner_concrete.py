# tests/scanners/test_base_scanner_concrete.py
"""Test the BaseScanner class using a function-based approach."""

import pytest
from src.scanners.base_scanner import BaseScanner
from src.core.exceptions import InvalidURLError


@pytest.fixture
def test_scanner():
    """Fixture to provide a concrete TestScanner instance."""
    class TestScanner(BaseScanner):
        def scan_url(self, url: str) -> dict:
            return {"status": "success"}

        def retrieve_scan_results(self, scan_id: str) -> dict:
            return {"status": "success", "id": scan_id}

    scanner = TestScanner(api_key="test", base_url="https://sandbox.recordedfuture.com")
    return scanner

def test_base_scanner_initialization(test_scanner):
    """Test that BaseScanner initializes correctly with retry logic."""
    # Verify session is configured with retry logic
    adapter = test_scanner.session.get_adapter("https://")
    assert adapter.max_retries.total == 3  # 3 retries
    assert adapter.max_retries.backoff_factor == 1

def test_validate_url_valid(test_scanner):
    """Test URL validation for valid URLs."""
    test_scanner.base_url = "http://example.com"
    test_scanner.validate_url("https://www.example.com")  # Should not raise an exception

def test_validate_url_invalid(test_scanner):
    """Test URL validation for invalid URLs."""
    test_scanner.base_url = "http://example.com"
    with pytest.raises(InvalidURLError):
        test_scanner.validate_url("not-a-url")