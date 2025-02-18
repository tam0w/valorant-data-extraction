# Practistics Scrim OCR

Practistics is an open-source OCR tool designed to capture and analyze VALORANT private scrim matches. It automatically extracts data from match scoreboards, summaries, and timelines, converting them into structured CSV data for analysis.

## Quick Start

1. Install Python 3.11 from the [Python website](https://www.python.org/downloads/)
2. Download and unzip Practistics
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Run the tool and press:
   - `S` on match summary screen
   - `B` on scoreboard
   - `P` on each round timeline
   - `Q` when finished
   - Let it process

Find your data in `Documents/practistics/matches/`

## Documentation

- [Installation Guide](docs/INSTALLATION.md) - Getting started with Practistics
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


