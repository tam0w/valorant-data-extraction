# Practistics Scrim OCR

Practistics is an open-source OCR tool designed to capture and analyze VALORANT private scrim matches. It automatically extracts data from match scoreboards, summaries, and timelines, converting them into structured CSV data for analysis.

## Quick Start

1. Install Python 3.11 from the [Python website](https://www.python.org/downloads/)
2. Download and unzip Practistics
3. Install Dependencies

GPU Acceleration (Optional but Recommended)
If you have an **NVIDIA GPU** that supports **CUDA** for faster processing, follow these steps:

1. Install the **NVIDIA CUDA Toolkit** incase you havent:  
   [Download CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) (Recommended Toolkit Version=12.4)

2. Verify the installation:
   ```sh
   nvcc --version
   ```

3. Go to [PyTorch's official website](https://pytorch.org/get-started/locally/) and select the appropriate PyTorch build for your CUDA version.

4. If you have **CUDA 12.4**, install PyTorch with the following command:
   ```sh
   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```
   If you have a **different CUDA version** that is not listed in the PyTorch documentation, you may need to **build PyTorch from source** to ensure compatibility.

Install Other Dependencies
For all users, install the required dependencies:

```sh
pip install -r requirements.txt
```


4. Run the tool with the `python main.py` command and press:
   - `S` on match summary screen
   - `B` on scoreboard
   - `P` on each round timeline
   - `Q` when finished
   - Let it process

Find your data in `Documents/practistics/matches/`

Before using Practistics, please ensure:

- **Display Resolution:** Your display must be set to 1920x1080 (native resolution). The OCR coordinates are precisely calibrated for this resolution, and other resolutions will cause misalignments when capturing data.
- **Match Access:** Practistics is designed to work only with matches accessed from your own match history or concluded matches that you have participated in. The tool relies on specific screen coordinates that align with - this view. Spectated matches or recordings from other players will likely cause misalignment issues.
- **Character Support:** Player names with non-Latin characters (Chinese, Cyrillic, etc.) may not be accurately recognized by the OCR engine.


## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Getting started with Practistics (includes GPU setup)
- [Understanding the Data](docs/DATA_STRUCTURE.md) - Complete data points documentation
- [Practical Usage Guide](docs/USAGE.md) - Making the most of your scrim data
- [Technical Documentation](docs/TECHNICAL.md) - Under the hood details

## Why Practistics?

Traditional scrim reviews often miss the subtle patterns that emerge across multiple matches. Practistics captures these patterns by converting match data into structured formats, allowing teams to:
- Track performance trends across multiple scrims
- Analyze round-specific strategies and outcomes
- Identify patterns in economy management and site control
- Build data-driven practice routines

## Project Status

This project is currently not in active development. It was created to fill the gap in accessing hidden scrim data and help teams analyze their practice matches. While functional, it's one of my earlier projects and contributions/improvements are welcome.

## Support & Community

- Join our [Discord server](https://discord.gg/2eQ85rcQSQ)
- Follow on [Twitter](https://twitter.com/tam0w)
- Report issues on [GitHub](https://github.com/yourusername/practistics/issues)

## Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
