# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
- **Main execution**: `python main.py`
- **Read from folder**: `python main.py --read FOLDER_NAME`
- **Development mode**: `python main.py --dev` (enables verbose logging)
- **Offline mode**: `python main.py --offline` (uses hardcoded agent/map lists)

### Cache Management
- **View cache info**: `python main.py --cache-info`
- **Refresh all caches**: `python main.py --refresh-cache all`
- **Refresh specific cache**: `python main.py --refresh-cache agents` or `python main.py --refresh-cache maps`

### Dependencies
- **Install dependencies**: `pip install -r requirements.txt`
- **GPU acceleration setup**: Follow PyTorch CUDA installation from [PyTorch website](https://pytorch.org/get-started/locally/)

### Logging Options
- **Set log level**: `python main.py --log-level debug|info|warning|error|critical`
- **Quiet mode**: `python main.py --quiet` (suppress user output)

## Architecture Overview

### Core Data Flow
The application follows a three-stage pipeline:
1. **Image Capture/Input** (`core/capture.py`) - Screenshots or folder reading
2. **OCR Processing** (`core/ocr.py` + `core/image_processing.py`) - Text extraction and image analysis
3. **Data Processing** (`core/data_processing.py`) - Convert OCR results to structured match data
4. **Export** (`core/export.py`) - Output to CSV/JSON formats

### Key Components

**Main Entry Point** (`main.py`):
- Orchestrates the entire pipeline
- Handles CLI argument parsing
- Manages configuration loading and cache initialization
- Provides comprehensive error handling with logging

**Configuration System** (`core/config.py`):
- YAML-based configuration with sensible defaults
- Handles output directories: `~/Documents/practistics/matches` (data), `~/Documents/practistics/error_logs` (logs), `~/Documents/practistics/cache` (API cache)
- Configurable OCR languages and API settings

**Data Types** (`core/types.py`):
- `MatchData`: Complete match information with rounds and player data
- `RoundData`: Individual round with events, economy, first blood, site control
- `PlayerData`: Player statistics and agent assignments
- `EventData`: Timeline events (kills, plants, defuses)

**API Integration** (`core/api.py`):
- Fetches agent and map data from VALORANT API
- Implements intelligent caching (7 days for agents, 14 days for maps)
- Graceful fallback to hardcoded lists in offline mode

**Image Processing Pipeline**:
- `core/image_processing.py`: Image manipulation, color detection, region cropping
- `core/ocr.py`: EasyOCR integration with configurable languages
- Coordinate-based extraction calibrated for 1920x1080 resolution

### Data Processing Logic

**Agent Normalization** (`core/data_processing.py:15`):
- Uses fuzzy matching with 0.6 similarity threshold
- Special handling for KAY/O name variations
- Falls back to API data or hardcoded lists

**Match Data Creation** (`core/data_processing.py`):
- Processes timeline images sequentially to build round data
- Extracts scoreboard for final scores and team composition
- Parses summary screen for map identification

**Output Format**:
- CSV: Flattened round-by-round data for analysis
- JSON: Complete hierarchical match structure

### Critical Constraints

**Resolution Dependency**: The application is hardcoded for 1920x1080 display resolution. All OCR coordinates and image processing regions are calibrated for this specific resolution.

**Match Context Requirements**: Only works with matches from your own match history or concluded matches you participated in. Spectated matches or recordings from other players will cause coordinate misalignment.

**Character Support**: OCR engine may not accurately recognize non-Latin characters (Chinese, Cyrillic, etc.) in player names.