# tests/conftest.py
# Fixtures and shared setup for pytest

import pytest
from unittest.mock import MagicMock, patch
from src.scanners.base_scanner import BaseScanner
from src.scanners.recorded_future import RecordedFutureScanner
from src.utils.url_file_processor import URLFileProcessor
from pathlib import Path
import csv
import tempfile
import os

@pytest.fixture
def mock_recorded_future_api():
    """Mock the RecordedFuture API for session.post and session.get."""
    with patch("requests.Session.post") as post_mock, \
         patch("requests.Session.get") as get_mock:
        post_mock.return_value = MagicMock()
        get_mock.return_value = MagicMock()
        yield post_mock, get_mock

@pytest.fixture
def valid_api_key():
    """Fixture for a valid API key."""
    return "test_api_key_123"

@pytest.fixture
def base_url():
    """Fixture for a base URL."""
    return "https://sandbox.recordedfuture.com"

@pytest.fixture
def valid_url():
    """Fixture for a valid URL."""
    return "https://www.example.com"

@pytest.fixture
def invalid_url():
    """Fixture for an invalid URL."""
    return "not-a-url"

@pytest.fixture
def recorded_future_scanner(valid_api_key, base_url):
    """Fixture for a RecordedFutureScanner instance."""
    return RecordedFutureScanner(api_key=valid_api_key, base_url=base_url)

@pytest.fixture
def mock_scanners():
    """Fixture to create mock scanners for URLFileProcessor."""
    return {
        "RecordedFuture": MagicMock(),
        "HybridAnalysis": MagicMock()
    }

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file with sample URLs."""
    file_path = Path(tempfile.mktemp(suffix=".csv"))
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["https://example.com"])
        writer.writerow(["https://google.com"])
    yield file_path
    os.unlink(file_path)

@pytest.fixture
def temp_control_file():
    """Create a temporary control file for testing URLFileProcessor."""
    file_path = Path(tempfile.mktemp(suffix="_control.txt"))
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["RecordedFuture", "https://example.com", "scan123", "false"])
    yield file_path
    os.unlink(file_path)