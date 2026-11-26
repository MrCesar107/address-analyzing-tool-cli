"""Tests for URLFileProcessor using real file operations."""
import pytest
import tempfile
import os
import csv
from unittest.mock import MagicMock
from src.utils.url_file_processor import URLFileProcessor


def setup_control_file(file_path, entries):
    """Helper to create a control file with the given entries."""
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f)
        for entry in entries:
            writer.writerow(entry)


def test_create_new_control_file():
    """Test creation of a new control file using real file operations."""
    mock_scanners = {"RecordedFuture": MagicMock()}
    mock_scanners["RecordedFuture"].scan_url.return_value = {"id": "scan123", "completed": False}
    processor = URLFileProcessor(scanners=mock_scanners)
    processor.urls = ["https://example.com"]
    
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        control_file_path = os.path.join(temp_dir, "urls_control.txt")
        
        # Override the control_file attribute
        processor.control_file = control_file_path
        
        # Ensure control file doesn't exist initially
        assert not os.path.exists(control_file_path)
        
        # Call the method
        processor._create_new_control_file()
        
        # Verify the file content
        with open(control_file_path, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0][0] == "RecordedFuture"
            assert rows[0][1] == "https://example.com"
            assert rows[0][2] == "scan123"
            assert rows[0][3] == "false"


def test_read_control_file():
    """Test reading an existing control file using real file operations."""
    mock_scanners = {"RecordedFuture": MagicMock()}
    
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        control_file_path = os.path.join(temp_dir, "urls_control.txt")
        
        # Set up the file
        setup_control_file(control_file_path, [["RecordedFuture", "https://example.com", "scan123", "false"]])
        
        # Override the control_file attribute
        processor = URLFileProcessor(scanners=mock_scanners)
        processor.control_file = control_file_path
        
        # Call the method
        processor._read_control_file()
        
        assert len(processor.control_urls) == 1
        assert processor.control_urls[0][0] == "RecordedFuture"
        assert processor.control_urls[0][1] == "https://example.com"
        assert processor.control_urls[0][2] == "scan123"
        assert processor.control_urls[0][3] is False


def test_read_control_file_with_multiple_entries():
    """Test reading a control file with multiple entries."""
    mock_scanners = {"RecordedFuture": MagicMock()}
    
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        control_file_path = os.path.join(temp_dir, "urls_control.txt")
        
        # Set up the file with multiple entries
        setup_control_file(control_file_path, [
            ["RecordedFuture", "https://example.com", "scan123", "false"],
            ["RecordedFuture", "https://test.com", "scan456", "true"],
        ])
        
        # Override the control_file attribute
        processor = URLFileProcessor(scanners=mock_scanners)
        processor.control_file = control_file_path
        
        # Call the method
        processor._read_control_file()
        
        assert len(processor.control_urls) == 2
        assert processor.control_urls[0][3] is False
        assert processor.control_urls[1][3] is True


def test_check_scan_status_with_error():
    """Test handling of scan status verification errors using real file operations."""
    mock_scanners = {"RecordedFuture": MagicMock()}
    mock_scanners["RecordedFuture"].retrieve_scan_results.side_effect = Exception("API failed")
    
    # Create a temporary directory and file
    with tempfile.TemporaryDirectory() as temp_dir:
        control_file_path = os.path.join(temp_dir, "urls_control.txt")
        
        # Set up the file
        setup_control_file(control_file_path, [["RecordedFuture", "https://example.com", "scan123", "false"]])
        
        # Override the control_file attribute
        processor = URLFileProcessor(scanners=mock_scanners)
        processor.control_file = control_file_path
        processor.control_urls = [["RecordedFuture", "https://example.com", "scan123", False]]
        
        # Call the method
        processor._check_scan_status()
        
        # Verify the state remains False
        assert len(processor.control_urls) == 1
        assert processor.control_urls[0][0] == "RecordedFuture"
        assert processor.control_urls[0][1] == "https://example.com"
        assert processor.control_urls[0][2] == "scan123"
        assert processor.control_urls[0][3] is False