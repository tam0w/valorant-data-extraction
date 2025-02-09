# Practistics

Practistics is an open-source project designed to capture and process screenshots of game scoreboards, summaries, and timelines. It uses OCR (Optical Character Recognition) to extract data from images and logs the information for further analysis.

## Features

- Capture screenshots of game scoreboards, summaries, and timelines.
- Process and extract data from images using OCR.
- Log and save the captured data and images for analysis.

## Requirements

- Python 3.8+
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

### Running the Application

1. Navigate to the project directory:
    ```sh
    cd practistics
    ```

2. Run the main script:
    ```sh
    python core/data_capture_module/capture.py
    ```

### Capturing Screenshots

- **Summary Screenshot**: Press `s` to capture the summary screenshot.
- **Scoreboard Screenshot**: Press `b` to capture the scoreboard screenshot.
- **Timeline Screenshot**: Press `p` to capture a timeline screenshot.
- **Finish Capturing**: Press `q` to finish capturing timeline screenshots.

### Reading Images from Folder

To read images from a folder for testing purposes, use the `read_images_from_folder` function in `core/data_capture_module/capture.py`.

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
├── requirements.txt
└── README.md
```

### Core Modules

- **data_capture_module**: Contains the script for capturing screenshots and reading images.
- **logger_module**: Contains the custom logger for logging messages and saving images.
- **ocr_module**: Contains the OCR setup for reading text from images.
- **processing_module**: Contains helper functions for processing text data from images.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature-name
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "Add your message here"
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature-name
    ```
5. Create a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or suggestions, please open an issue on GitHub.

---

Thank you for using Practistics! We hope you find it useful for your projects.