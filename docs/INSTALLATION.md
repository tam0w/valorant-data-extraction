# Installation Guide

This guide will walk you through setting up Practistics on your system.

## System Requirements

- Python 3.11 or newer
- Windows/MacOS/Linux
- At least 2GB of free disk space
- Screen resolution of 1920x1080 or higher recommended

## Step-by-Step Installation

### 1. Install Python

1. Download Python 3.11 from the [Python website](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt/Terminal and typing:
   ```sh
   python --version
   ```

### 2. Get Practistics

1. Download the latest release from the [releases page](https://github.com/tam0w/valorant-data-extraction/releases)
2. Extract the ZIP file to a location you can easily find
3. Note the folder location - you'll need it in the next step

### 3. Install Dependencies

1. Open Command Prompt (Windows) or Terminal (Mac/Linux)
2. Navigate to the Practistics folder:
   ```sh
   cd path/to/practistics
   ```
3. Install required packages:
   ```sh
   pip install -r requirements.txt
   ```

### 4. Verify Installation

1. Run the tool:
   ```sh
   python main.py
   ```
2. You should see a startup message
3. The tool will create necessary folders in your Documents directory

## Folder Structure

After installation, Practistics creates these folders:
```
Documents/
└── practistics/
    ├── error_logs/     # Screenshot storage
    ├── matches/        # Output CSV files
```

## Troubleshooting

### Common Issues

1. **"Python not found" error**
   - Ensure Python is added to PATH
   - Try restarting your computer

2. **Installation fails with error messages**
   - Make sure you have internet connection
   - Try running as administrator
   - Check Python version matches requirements

3. **Tool doesn't start**
   - Check if all dependencies are installed
   - Verify Python installation
   - Try reinstalling dependencies

### Still Having Problems?

- Check our [Discord server](https://discord.gg/2eQ85rcQSQ) for help
- Open an issue on GitHub
- Reach out on [Twitter](https://twitter.com/tam0w)

## Updating

To update Practistics:
1. Download the latest release
2. Delete the old folder.
3. Go into the new downloaded release's folder.
4. Run `pip install -r requirements.txt` again, and use.

Your existing data will not be affected by updates.
