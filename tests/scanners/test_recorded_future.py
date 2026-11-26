# tests/scanners/test_recorded_future.py
"""Test the RecordedFutureScanner class."""

import pytest
import requests
from unittest.mock import patch, MagicMock
from src.scanners.recorded_future import RecordedFutureScanner
from src.core.exceptions import APIError


def test_scan_url_success(recorded_future_scanner, mock_recorded_future_api):
    """Test successful URL scanning."""
    post_mock, _ = mock_recorded_future_api
    
    # Setup mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "scan123", "status": "queued"}
    mock_response.raise_for_status.return_value = None
    post_mock.return_value = mock_response
    
    result = recorded_future_scanner.scan_url("https://example.com")
    assert result["id"] == "scan123"


def test_scan_url_timeout(recorded_future_scanner):
    """Test timeout during URL scanning."""
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(APIError) as exc_info:
            recorded_future_scanner.scan_url("https://example.com")
        
        assert "timed out" in str(exc_info.value)


def test_scan_url_http_error(recorded_future_scanner, mock_recorded_future_api):
    """Test HTTP error during URL scanning."""
    post_mock, _ = mock_recorded_future_api
    
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server error")
    post_mock.return_value = mock_response
    
    with pytest.raises(APIError):
        recorded_future_scanner.scan_url("https://example.com")


def test_retrieve_scan_results_success(recorded_future_scanner, mock_recorded_future_api):
    """Test successful retrieval of scan results."""
    _, get_mock = mock_recorded_future_api
    
    mock_response = MagicMock()
    mock_response.json.return_value = {"completed": True, "tasks": {}}
    mock_response.raise_for_status.return_value = None
    get_mock.return_value = mock_response
    
    result = recorded_future_scanner.retrieve_scan_results("scan123")
    assert result["completed"] is True


def test_retrieve_scan_results_timeout(recorded_future_scanner):
    """Test timeout during scan result retrieval."""
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        with pytest.raises(APIError) as exc_info:
            recorded_future_scanner.retrieve_scan_results("scan123")
        
        assert "timed out" in str(exc_info.value)


def test_retrieve_scan_results_http_error(recorded_future_scanner, mock_recorded_future_api):
    """Test HTTP error during scan result retrieval."""
    _, get_mock = mock_recorded_future_api
    
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Not found")
    get_mock.return_value = mock_response
    
    with pytest.raises(APIError):
        recorded_future_scanner.retrieve_scan_results("scan123")