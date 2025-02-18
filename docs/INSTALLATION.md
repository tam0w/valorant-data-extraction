# Practistics Installation Guide

This guide will walk you through the process of setting up Practistics on your computer. By the end, you'll have everything you need to start capturing valuable data from your Valorant scrims. 

## Prerequisites

Before we dive into installation, let's make sure your system meets the requirements to run Practistics:

- **Operating System**: Practistics is compatible with Windows, macOS, and Linux operating systems. It may work on other Unix-like systems, but we haven't tested it. 
- **Python Version**: You'll need Python 3.11 or newer installed. If you're not sure which version of Python you have, don't worry - we'll cover checking that in the installation steps.
- **Screen Resolution**: 1920x1080 is a fixed requirement for the resolution of the game. The script will not work correctly otherwise.

> **Note**: Practistics is a data extraction tool, not a game mod. It does not modify Valorant in any way or give you an in-game advantage. It simply captures data from your matches for later analysis.

## Step 1: Install Python

Practistics is built on Python, so our first step is to make sure you have a compatible Python version installed. Here's how:

1. Visit the [Python downloads page](https://www.python.org/downloads/) and download the installer for Python 3.11 or newer for your operating system.
   
2. Run the installer. On Windows, make sure to check the "Add Python to PATH" option during installation. This makes it easier to run Python from the command line.
   
3. Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and type the following command to verify that Python is installed correctly:
   
   ```
   python --version
   ```
   
   You should see the Python version number printed out. If you get an error message, Python may not be installed correctly or not added to your PATH. 

> **Tip**: If you're new to Python or to using the terminal, don't worry! You don't need to be a Python expert to use Practistics. The installation process may seem intimidating at first, but we'll guide you through each step.

## Step 2: Download Practistics

With Python installed, we can now download Practistics itself:

1. Go to the [Practistics releases page](https://github.com/tam0w/valorant-data-extraction/releases) and download the ZIP file for the latest version.

2. Extract the ZIP file to a location on your computer where you can easily find it, like your Documents folder.
   
3. Take note of the location where you extracted Practistics - you'll need to navigate to this folder in the terminal for the next step.

> **Note**: We recommend creating a dedicated folder for Practistics, to keep your data captures and configuration files organized in one place.

## Step 3: Install Dependencies

Practistics relies on a few other Python packages to do its job. We need to install these dependencies before we can run the tool:

1. Open a terminal and navigate to the folder where you extracted Practistics. You can do this using the `cd` command. For example, if you extracted Practistics to a folder called `practistics` in your Documents folder, you would type:
   
   ```
   cd Documents/practistics
   ```
   
2. Once you're in the Practistics folder, run the following command to install the required packages:
   
   ```
   pip install -r requirements.txt
   ```
   
   This tells Python's package manager, pip, to install all the packages listed in the `requirements.txt` file.

> **Troubleshooting**: If you get an error message during this step, double check that you're in the correct folder and that you've typed the command correctly. If the error persists, you may need to check your internet connection or try running the command as an administrator.

## Step 4: Verify Installation

Congratulations, you've installed Practistics! Let's do a quick test run to make sure everything is working:

1. In your terminal, still in the Practistics folder, run the following command:
   
   ```
   python main.py
   ```
   
   This starts the Practistics tool.
   
2. If everything is set up correctly, you should see a startup message indicating that Practistics is running and ready to capture data.
   
3. Practistics will automatically create a few folders in your Documents directory to store its data:
   
   ```
   Documents/
   └── practistics/
       ├── error_logs/     # For storing logs if something goes wrong
       ├── matches/        # Where your match data CSV files will be saved
   ```
   
> **Tip**: If Practistics doesn't start, or you see error messages, don't panic! Jump down to the Troubleshooting section for some common issues and how to resolve them.

## Updating Practistics

We're constantly working to improve Practistics and add new features. To update to the latest version:

1. Download the new release ZIP from the GitHub releases page, just like in Step 2.
2. Delete your old Practistics folder.
3. Extract the new ZIP to replace the old folder.
4. Open a terminal, navigate to the new Practistics folder, and run `pip install -r requirements.txt` again to ensure you have all the latest dependencies.

Updating Practistics won't affect your existing data. Your captured matches and logs will stay safe in your Documents folder.

## Troubleshooting

Even with the clearest instructions, things can sometimes go wrong. Here are some common issues you might encounter and how to solve them:

1. **"Python not found" error when trying to run Practistics**: This usually means Python isn't properly added to your PATH. Try restarting your computer - this often resolves PATH issues. If the error persists, you may need to manually add Python to your PATH.
   
2. **Dependencies fail to install**: First, check your internet connection - pip needs to download the packages from the internet. If you're on a company or school network, you may need to get past a firewall. If that's not the issue, try running the `pip install` command as an administrator.
   
3. **Practistics won't start**: Double check that you've installed all the dependencies (Step 3). If you have, try re-installing them. Also verify that you're using a compatible Python version.

If you're still having trouble, don't hesitate to reach out for help:

- Join our [Discord server](https://discord.gg/2eQ85rcQSQ) to chat with the Practistics community and get live support.
- If you think you've found a bug, open an issue on our [GitHub repository](https://github.com/tam0w/valorant-data-extraction/issues).
- Tweet at us [@tam0w](https://twitter.com/tam0w) on Twitter.

We're here to help you get up and running with Practistics so you can start leveraging your Valorant data. Happy analyzing!
