"""
Smoke test for match data extraction using real screenshot data.
Reads from tests/data/<match_folder> and runs the full processing pipeline.

Usage:
    python -m tests.test_match_processing                     # runs all matches in tests/data/
    python -m tests.test_match_processing --match match-1     # runs a specific match
"""

import argparse
import sys
from pathlib import Path

# Add project root to path so imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import load_config
from core.capture import read_images_from_folder
from core.ocr import initialize_ocr
from core.data_processing import create_match_data
from core.logger import logger


def run_match(match_name: str, config: dict):
    """Run the full processing pipeline on a single match folder."""
    logger.set_log_level("DEBUG")
    logger.user_output(f"\n{'=' * 50}")
    logger.user_output(f"processing: {match_name}")
    logger.user_output(f"{'=' * 50}")

    timeline_images, scoreboard_image, summary_image = read_images_from_folder(
        config, match_name
    )

    if not timeline_images or scoreboard_image is None or summary_image is None:
        logger.user_output(f"FAIL: {match_name} - missing images")
        return False

    logger.user_output(f"loaded {len(timeline_images)} timelines, scoreboard, summary")

    try:
        match_data = create_match_data(
            timeline_images, scoreboard_image, summary_image, config
        )
        logger.user_output("\nresults:")
        logger.user_output(f"  map: {match_data['map_name']}")
        logger.user_output(f"  score: {match_data['final_score']}")
        logger.user_output(f"  result: {match_data['result']}")
        logger.user_output(f"  rounds: {match_data['total_rounds']}")
        logger.user_output(f"  players: {len(match_data['players'])}")
        logger.user_output(f"\nPASS: {match_name}")
        return True
    except Exception as e:
        logger.user_output(f"\nFAIL: {match_name} - {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test match processing with real screenshots"
    )
    parser.add_argument("--match", help="Specific match folder to test (e.g. match-1)")
    args = parser.parse_args()

    config = load_config()
    # Point log_dir at our test data directory
    config["log_dir"] = str(Path(__file__).parent / "data")

    logger.user_output("initializing ocr...")
    initialize_ocr()

    data_dir = Path(__file__).parent / "data"
    if args.match:
        matches = [args.match]
    else:
        matches = [d.name for d in sorted(data_dir.iterdir()) if d.is_dir()]

    if not matches:
        logger.user_output("no match folders found in tests/data/")
        sys.exit(1)

    results = {}
    for match_name in matches:
        results[match_name] = run_match(match_name, config)

    logger.user_output(f"\n{'=' * 50}")
    logger.user_output("summary")
    logger.user_output(f"{'=' * 50}")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        logger.user_output(f"  {name}: {status}")

    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
