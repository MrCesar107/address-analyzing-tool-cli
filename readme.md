# Address analyzing terminal tool

A CLI tool to analyze URL addresses using Hybrid Analysis API

## Requirements

- Python (3.13.2 recommended)

## Installation

You need to execute the installation script

**If you are in unix system (macOS/Linux)**

``$ bash install.sh``

If you use zsh:

``$ zsh install.sh``

**If you are in windows**

`Set-ExecutionPolicy Unrestricted -Scope Process
./install.ps1`

**⚠️ YOU NEED A VALID HYBRID ANALYSIS AND RECORDED FUTURE API KEYS TO USE THIS SCRIPT ⚠️**

You must put your Hybrid Analysis and Recorded Future API keys in a .env file in the directory where the script was installed

**If you are in unix system (macOS/Linux)**

`$ cd /usr/local/bin/address_analyzing_tool`

`$ nano .env`

**If you are in windows**

You must place your .env file in the directory where you executed the intall powershell script

```
RECORDED_FUTURE_BEARER_TOKEN=YOUR_API_KEY
HYBRID_ANALYSIS_API_KEY=YOUR_API_KEY
```

## Usage
These are the basic commands to use this script

To analyze a single URL address:

`$ address_analyzing_tool -u YOUR_URL --engine ENGINE_NAME`

To retrive a previous analysis

`$ address_analyzing_tool -u SCAN_ID --engine ENGINE_NAME`

To analyze multiple URL addresses in a file. Please use a simple text file with your addresses

`$ address_analyzing_tool -f YOUR_FILE_PATH`

To print the scanning engines available in the script
`$ address_analyzing_tool -l`

To print the help manual of the script
`$ address_analyzing_tool -h`
