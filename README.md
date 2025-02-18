
# Practistics Scrim OCR

Practistics Scrim OCR is an open-source project designed to capture and process screenshots of VALORANT private scrim match scoreboards, summaries, and timelines. It uses OCR (Optical Character Recognition) to extract data from images and logs the information for further analysis.

Practistics Scrim OCR was intended for teams, to be used to extract tabular data match-by-match, allow technical and non-technical analysts to aggregrate and analyze performance in multiple practice matches. That is where the value would lie in using it. I wrote this OCR script since there wasn't really a way to access hidden scrim data post the scrim. The data output structure of this script is a .csv file. For that reason the code is written to generate CSV files (almost everything is a bunch of lists, far from ideal).

## Features

- Capture screenshots of game scoreboards, summaries, and timelines.
- Process and extract data from images using OCR.
- Log and save the captured data and images for analysis.

## Requirements

- Python 3.11 (recommended)
- pip (Python package installer)

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/practistics.git
    cd practistics
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### 1. Running the Application

1. Navigate to the project directory:
    ```sh
    cd practistics
    ```

2. Run the main script:
    ```sh
    python main.py
    ```

### 2. Capturing Screenshots

- **Summary Screenshot**: Press `s` to capture the summary screenshot.
- **Scoreboard Screenshot**: Press `b` to capture the scoreboard screenshot.
- **Timeline Screenshot**: Press `p` to capture a timeline screenshot.
- **Finish Capturing**: Press `q` to finish capturing timeline screenshots.

You can also read images from a folder. They are saved in a folder whenever an error occurs mid process. To read images from a folder for testing purposes, use the `read_images_from_folder` function in `core/data_capture_module/capture.py`.

### 3. Analysis

Once the processing of the images is completed, an output .csv will be generated. This can be used to perform analysis on the game in applications like Tableau, PowerBI, or just R and Python. As of right now, the web dashboard to view analytics is not LIVE.

## Project Structure

```
practistics/
├── core/
│   ├── data_capture_module/
│   │   └── capture.py
│   ├── logger_module/
│   │   └── logger.py
│   ├── ocr_module/
│   │   └── ocr.py
│   └── processing_module/
│       └── text_helpers.py
│       └── img_helpers.py
├── requirements.txt
└── README.md
```

### Core Modules

- **data_capture_module**: Contains the script for capturing screenshots and reading images.
- **logger_module**: Contains the custom logger for logging messages and saving images.
- **ocr_module**: Contains the OCR setup for reading text from images.
- **processing_module**: Contains helper functions for processing text data and images.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "feat/fix/remove/update: Add your message here"
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature-name
    ```
5. Create a pull request.

## License

This project is licensed under the GNU Affero General Public License v3.0 - see the LICENSE file for details.

## Contact

For any questions or suggestions, please open an issue on GitHub. You can also reach out to me on my [twitter](https://twitter.com/tam0w), or on the project's [discord server](https://discord.gg/yourdiscordserver).

---


