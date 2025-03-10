from pathlib import Path
import sys
import traceback
from datetime import datetime

# Core imports
from core.config import load_config, get_config_value
from core.capture import screenshot_pages, read_images_from_folder
from core.ocr import initialize_ocr
from core.data_processing import create_match_data
from core.export import match_to_csv, match_to_json
from core.logger import logger


def main():
    try:
        # Load configuration
        config = load_config()

        # Initialize OCR engine with config values
        ocr_config = config.get('ocr', {'lang': ['en'], 'download_enabled': True})
        initialize_ocr(ocr_config.get('lang', ['en']), ocr_config.get('download_enabled', True))

        # Get output directory
        output_dir = config.get('output_dir', str(Path.home() / "Documents" / "practistics" / "matches"))

        # Start application
        logger.info("Starting Practistics application")

        # Determine if we're using screenshots or reading from a folder
        if len(sys.argv) > 1 and sys.argv[1] == '--read':
            if len(sys.argv) > 2:
                sub_dir = sys.argv[2]
                logger.info(f"Reading images from folder: {sub_dir}")
                timeline_images, scoreboard_image, summary_image = read_images_from_folder(config, sub_dir)
            else:
                logger.error("No folder specified for --read")
                return
        else:
            logger.info("Capturing screenshots")
            timeline_images, scoreboard_image, summary_image = screenshot_pages()

        # Make sure we have the necessary images
        if not timeline_images or not scoreboard_image or not summary_image:
            logger.error("Missing required screenshots")
            return

        # Process data
        logger.info("Processing match data")
        match_data = create_match_data(timeline_images, scoreboard_image, summary_image)

        # Export data
        logger.info("Exporting data")
        csv_path = match_to_csv(match_data, output_dir)
        json_path = match_to_json(match_data, output_dir)

        logger.info(f"CSV saved to: {csv_path}")
        logger.info(f"JSON saved to: {json_path}")
        logger.info("Data extraction complete")

    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(f"An error occurred: {str(e)}")
        logger.save_logs(config, error_info)
        print(f"An error occurred. Error logs saved with ID: {logger.error_id}")
        print(f"Error details: {str(e)}")


if __name__ == "__main__":
    main()