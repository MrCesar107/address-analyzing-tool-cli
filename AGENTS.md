# Address Analyzing Tool CLI

## Table of Contents
1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Core Modules](#core-modules)
4. [Scanners](#scanners)
5. [Utilities](#utilities)
6. [Dependencies](#dependencies)


## Introduction

The **Address Analyzing Tool CLI** is designed to scan and analyze URLs using third-party APIs. It consists of modular components that handle API interactions, file processing, and result generation.


## System Overview

The system is structured into three main layers:

1. **Core**: Handles logging and exceptions.
2. **Scanners**: Interface with external APIs to scan URLs.
3. **Utilities**: Process input files, manage control files, and generate results.


## Core Modules

| Module | Path | Responsibility |
|--------|------|--------------|
| **Logger** | `src/core/logger.py` | Manages logging configurations and error messages. |
| **Exceptions** | `src/core/exceptions.py` | Defines custom exceptions for error handling (e.g., `InvalidURLError`, `APIError`). |


## Scanners

Scanners interface with external APIs to scan URLs and retrieve results.

| Class | Path | API Provider | Responsibility |
|-------|------|--------------|--------------|
| **BaseScanner** | `src/scanners/base_scanner.py` | Abstract Base Class | Provides shared retry logic and session configuration. |
| **RecordedFutureScanner** | `src/scanners/recorded_future.py` | Recorded Future | Scans URLs using the Recorded Future API. |
| **HybridAnalysisScanner** | `src/scanners/hybrid_analysis.py` | HybridAnalysis | Scans URLs using the Hybrid Analysis API. |


### Scanner Features
- **Retry Logic**: Implements exponential backoff for transient failures.
- **Timeout Handling**: Ensures API calls do not hang indefinitely.
- **Error Propagation**: Provides meaningful error messages for API failures.


## Utilities

Utilities handle file processing, control file management, and result extraction.

| Class | Path | Responsibility |
|-------|------|--------------|
| **URLFileProcessor** | `src/utils/url_file_processor.py` | Processes input files, manages control files, and generates results. |


### Utility Features
- **File I/O**: Reads URLs from input files and writes results to CSV.
- **Control File Management**: Tracks scan status and updates control files.
- **Result Extraction**: Parses API responses into standardized formats.


## Dependencies

### Libraries
- **Requests**: For HTTP requests and API interactions.
- **Urllib3**: Retry logic and connection pooling.
- **Pytest**: Testing framework.
- **Pytest-Mock**: Mocking for isolated tests.
- **Schedule**: Periodic task scheduling.


### Configuration
- **API Keys**: Scanners require API keys for authentication.
- **Base URLs**: Configured per scanner for API endpoints.
- **Timeouts**: Default timeout values for API calls.


## Interaction Flow

1. **Input File Processing**: `URLFileProcessor` reads URLs from input files.
2. **Scanning**: Scanners interface with external APIs to scan URLs.
3. **Control File Management**: Tracks scan status and updates control files.
4. **Result Extraction**: Parses API responses and writes results to CSV.


## Agent Roles

| Agent | Module | Role |
|-------|--------|-----|
| **File Processor** | `URLFileProcessor` | Reads input, manages control files, generates results. |
| **API Scanner** | `BaseScanner` subclasses | Interacts with third-party APIs to scan URLs. |
| **Logger** | `logger.py` | Logs errors and debugging information. |
| **Exception Handler** | `exceptions.py` | Defines custom exceptions for error handling. |


## Minimalist Architecture

The system follows a **modular design** with clear separation of concerns:

1. **Scanners**: Focus on API interactions.
2. **Utilities**: Handle file processing and result generation.
3. **Core**: Manages logging and exceptions.
