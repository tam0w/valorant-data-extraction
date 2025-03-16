from pathlib import Path
import sys
import traceback
import argparse
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
        # Parse command line arguments
        args = parse_arguments()

        # Configure logger based on arguments
        if args.dev:
            logger.set_dev_mode(True)
        else:
            logger.set_log_level(args.log_level.upper())

        if args.quiet:
            logger.enable_user_output(False)

        # Load configuration
        config = load_config()
        logger.debug("Configuration loaded")

        # Initialize OCR engine with config values
        ocr_config = config.get('ocr', {'lang': ['en'], 'download_enabled': True})
        initialize_ocr(ocr_config.get('lang', ['en']), ocr_config.get('download_enabled', True))
        logger.debug("OCR engine initialized")

        # Get output directory
        output_dir = config.get('output_dir', str(Path.home() / "Documents" / "practistics" / "matches"))
        logger.debug(f"Output directory: {output_dir}")

        # Start application
        logger.info("Starting Practistics application")
        logger.user_output("Welcome to Practistics - VALORANT Scrim OCR Tool")

        # Determine if we're using screenshots or reading from a folder
        if args.read:
            sub_dir = args.read
            logger.info(f"Reading images from folder: {sub_dir}")
            logger.user_output(f"Reading screenshots from folder: {sub_dir}")

            logger.push_context(operation="read_images", folder=sub_dir)
            timeline_images, scoreboard_image, summary_image = read_images_from_folder(config, sub_dir)
            logger.clear_context()
        else:
            logger.info("Capturing screenshots")
            logger.user_output("Please capture screenshots:")
            logger.user_output("  • Press 'S' on match summary screen")
            logger.user_output("  • Press 'B' on scoreboard")
            logger.user_output("  • Press 'P' on each round timeline")
            logger.user_output("  • Press 'Q' when finished")

            logger.push_context(operation="capture_screenshots")
            timeline_images, scoreboard_image, summary_image = screenshot_pages()
            logger.clear_context()

        if timeline_images is None:
            logger.error("No timeline images captured")
            logger.user_output("Error: No timeline images captured. Please try again.")
            return

        if scoreboard_image is None:
            logger.error("No scoreboard image captured")
            logger.user_output("Error: No scoreboard image captured. Please try again.")
            return

        if summary_image is None:
            logger.error("No summary image captured")
            logger.user_output("Error: No summary image captured. Please try again.")
            return

        logger.info(f"Processing match data from {len(timeline_images)} rounds")
        logger.user_output(f"Processing data from {len(timeline_images)} rounds...")

        logger.push_context(operation="process_match_data", rounds=len(timeline_images))
        match_data = create_match_data(timeline_images, scoreboard_image, summary_image)
        logger.clear_context()

        # Export data
        logger.info("Exporting data")
        logger.user_output("Exporting data...")

        logger.push_context(operation="export_data", format="csv")
        csv_path = match_to_csv(match_data, output_dir)
        logger.clear_context()

        logger.push_context(operation="export_data", format="json")
        json_path = match_to_json(match_data, output_dir)
        logger.clear_context()

        logger.info(f"CSV saved to: {csv_path}")
        logger.info(f"JSON saved to: {json_path}")

        logger.user_output(f"✓ Data exported successfully!")
        logger.user_output(f"  CSV: {csv_path}")
        logger.user_output(f"  JSON: {json_path}")

        logger.info("Data extraction complete")
        logger.user_output("Data extraction complete. Thank you for using Practistics!")

    except Exception as e:
        error_info = traceback.format_exc()
        logger.error(f"An error occurred: {str(e)}")
        logger.save_logs(config, error_info)

        logger.user_output(f"An error occurred. Error logs saved with ID: {logger.error_id}")
        logger.user_output(f"Error details: {str(e)}")

        # In dev mode, show the full traceback
        if hasattr(logger, 'dev_mode') and logger.dev_mode:
            logger.user_output("\nTraceback:")
            logger.user_output(error_info)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Practistics - VALORANT Scrim OCR Tool")

    # Input mode
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('--read', metavar='FOLDER', help='Read screenshots from specified folder')

    # Logging options
    parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                        default='info', help='Set logging level (default: info)')
    parser.add_argument('--dev', action='store_true', help='Enable development mode with verbose logging')
    parser.add_argument('--quiet', action='store_true', help='Suppress user output, show only logs')

    return parser.parse_args()

if __name__ == "__main__":
    main()