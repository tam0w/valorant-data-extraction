
# Practistics Scrim OCR

Practistics Scrim OCR is an open-source project designed to capture and process screenshots of VALORANT private scrim match scoreboards, summaries, and timelines. It uses OCR (Optical Character Recognition) to extract data from images and logs the information for further analysis.

Practistics Scrim OCR was intended for teams, to be used to extract tabular data match-by-match, allow technical and non-technical analysts to aggregrate and analyze performance in multiple practice matches. That is where the value would lie in using it. I wrote this OCR script since there wasn't really a way to access hidden scrim data post the scrim. The data output structure of this script is a .csv file. For that reason the code is written to generate CSV files (almost everything is a bunch of lists, far from ideal).

## Features
- Screenshot capture of match data
- OCR processing of game information
- CSV output for analysis

## Quick Start
1. Install Python 3.11
2. Download and unzip Practistics
3. Run `pip install -r requirements.txt`
4. Read [Usage Guide](docs/USAGE.md) to get started

## Documentation
- [Installation Guide](docs/INSTALLATION.md)
- [Usage Guide](docs/USAGE.md)
- [Technical Documentation](docs/TECHNICAL.md)

## Project Status
Not very active, would like contributions

## Support
- Discord: [Join Here](https://discord.gg/2eQ85rcQSQ)
- Twitter: [@tam0w](https://twitter.com/tam0w)

## License
GNU Affero General Public License v3.0
