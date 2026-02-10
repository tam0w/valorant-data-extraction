"""
Visual OCR diagnostic report generator.
Runs OCR on all regions from test match data and produces an HTML report
showing each cropped region alongside what OCR extracted, with pass/fail status.

Usage:
    uv run python -m tests.test_ocr_report --match match-1
    uv run python -m tests.test_ocr_report                    # runs all matches
"""

import argparse
import base64
import sys
import time
import traceback
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import cv2
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import load_config
from core.capture import read_images_from_folder
from core.ocr import initialize_ocr, extract_text, extract_numeric_value
from core.image_processing import crop_image, enhance_for_ocr
from core.types import ImageRegion
from core.constants import (
    SUMMARY_SIDES_REGION, SUMMARY_SCORE_REGION, SUMMARY_MAP_REGION,
    TIMELINE_OUTCOME_REGION, TIMELINE_ECONOMY_REGION,
    EVENT_START_Y, EVENT_ROW_HEIGHT, EVENT_TIMESTAMP_X,
    PLAYER_TEAM_START_Y, PLAYER_CHECK_X, PLAYER_NAME_OFFSET,
    PLAYER_ROW_HEIGHT, PLAYER_REGION_WIDTH, PLAYER_ROW_SPACING,
)
from core.logger import logger


class OCRProbe:
    """Captures an OCR attempt with its input image, region, result, and status."""

    def __init__(self, name: str, source: str, region: ImageRegion, image: np.ndarray):
        self.name = name
        self.source = source  # which screenshot this came from (summary, scoreboard, timeline_N)
        self.region = region
        self.image = image  # the cropped region
        self.ocr_result: List[str] = []
        self.expected: Optional[str] = None
        self.status: str = "unknown"  # pass, fail, warn, error
        self.error: Optional[str] = None
        self.elapsed: float = 0
        self.notes: str = ""

    def run_ocr(self, **kwargs):
        start = time.time()
        try:
            self.ocr_result = extract_text(self.image, detail=0, region_name=self.name, **kwargs)
            self.elapsed = time.time() - start

            if not self.ocr_result:
                self.status = "warn"
                self.notes = "no text detected"
            else:
                self.status = "pass"
        except Exception as e:
            self.elapsed = time.time() - start
            self.status = "error"
            self.error = traceback.format_exc()
            self.notes = str(e)

    def validate(self, check_fn):
        """Run a validation function on the result. check_fn(result) -> (status, note)"""
        try:
            self.status, self.notes = check_fn(self.ocr_result)
        except Exception as e:
            self.status = "error"
            self.notes = str(e)


def image_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode('.png', img)
    return base64.b64encode(buffer).decode('utf-8')


def collect_probes(timeline_images, scoreboard_image, summary_image) -> List[OCRProbe]:
    """Run OCR on every region the app extracts and collect results."""
    probes = []

    # === SUMMARY SCREEN ===
    # Sides (ATK/DEF)
    sides_region = crop_image(summary_image, SUMMARY_SIDES_REGION, "sides_region")
    p = OCRProbe("sides", "summary", SUMMARY_SIDES_REGION, sides_region)
    p.run_ocr()
    p.validate(lambda r: ("pass", f"detected: {r[0]}") if r and any(k in r[0].lower() for k in ['atk', 'def']) else ("fail", f"expected ATK/DEF, got: {r}"))
    probes.append(p)

    # Score
    score_region = crop_image(summary_image, SUMMARY_SCORE_REGION, "score_region")
    p = OCRProbe("score", "summary", SUMMARY_SCORE_REGION, score_region)
    p.run_ocr()
    def validate_score(r):
        if len(r) < 3:
            return ("fail", f"expected 3+ parts [score, result, score], got {len(r)}: {r}")
        team, result_text, opp = r[0], r[1], r[2]
        issues = []
        if not team.isdigit():
            issues.append(f"team score '{team}' is not numeric")
        if not opp.isdigit():
            issues.append(f"opponent score '{opp}' is not numeric")
        if result_text.upper() not in ['VICTORY', 'DEFEAT', 'DRAW']:
            issues.append(f"result '{result_text}' not recognized")
        if issues:
            return ("fail", "; ".join(issues))
        return ("pass", f"{team} - {opp} ({result_text})")
    p.validate(validate_score)
    probes.append(p)

    # Map name
    map_region = crop_image(summary_image, SUMMARY_MAP_REGION, "map_region")
    p = OCRProbe("map_name", "summary", SUMMARY_MAP_REGION, map_region)
    p.run_ocr()
    p.validate(lambda r: ("pass", f"detected: {r[0]}") if r else ("fail", "no map name detected"))
    probes.append(p)

    # === SCOREBOARD - first timeline image (player names + agents) ===
    first_timeline = timeline_images[0]

    # Round outcome from first timeline
    outcome_region = crop_image(first_timeline, TIMELINE_OUTCOME_REGION, "outcome_region")
    p = OCRProbe("round_outcome", "timeline_1", TIMELINE_OUTCOME_REGION, outcome_region)
    p.run_ocr()
    p.validate(lambda r: ("pass", f"detected: {r}") if r else ("warn", "no outcome text"))
    probes.append(p)

    # Economy from first timeline
    eco_region = crop_image(first_timeline, TIMELINE_ECONOMY_REGION, "economy_region")
    p = OCRProbe("economy", "timeline_1", TIMELINE_ECONOMY_REGION, eco_region)
    p.run_ocr()
    p.validate(lambda r: ("pass", f"detected: {r}") if len(r) >= 2 else ("warn", f"expected 2 economy values, got: {r}"))
    probes.append(p)

    # Player names from first timeline (team side, first player)
    # Just probe a few representative regions to check alignment
    start_y = PLAYER_TEAM_START_Y
    check_x = PLAYER_CHECK_X
    for i in range(2):
        y = start_y
        region = ImageRegion(y, y + PLAYER_ROW_HEIGHT, check_x + PLAYER_NAME_OFFSET, check_x + PLAYER_REGION_WIDTH)
        player_region = crop_image(first_timeline, region, f"player_{i+1}_region")
        p = OCRProbe(f"player_{i+1}", "timeline_1", region, player_region)
        p.run_ocr(width_ths=25)
        p.validate(lambda r: ("pass", f"detected: {r}") if r else ("warn", "no player text"))
        probes.append(p)
        start_y += PLAYER_ROW_SPACING

    # === SAMPLE TIMELINES - check a few rounds for event regions ===
    sample_indices = [0, len(timeline_images) // 2, len(timeline_images) - 1]
    for idx in sample_indices:
        img = timeline_images[idx]
        round_num = idx + 1

        # Timestamp region (first event slot) — matches main script's crop pattern
        ts_box = ImageRegion(EVENT_START_Y, EVENT_START_Y + EVENT_ROW_HEIGHT, EVENT_TIMESTAMP_X[0], EVENT_TIMESTAMP_X[1])
        ts_region = crop_image(img, ts_box, f"r{round_num}_timestamp")
        p = OCRProbe(f"r{round_num}_timestamp", f"timeline_{round_num}", ts_box, ts_region)
        p.run_ocr(detail=0)
        probes.append(p)

    # === FULL SOURCE IMAGES with region overlays ===
    # We'll add the original images too so the report can show where regions are being cropped

    return probes


def build_source_overlay(image: np.ndarray, regions: List[Tuple[str, ImageRegion]], label: str) -> np.ndarray:
    """Draw region rectangles on a copy of the source image."""
    overlay = image.copy()
    colors = {
        "sides": (0, 255, 255),
        "score": (0, 255, 0),
        "map_name": (255, 0, 255),
        "outcome": (255, 255, 0),
        "economy": (0, 165, 255),
        "player": (255, 128, 0),
        "timestamp": (128, 128, 255),
    }
    for name, region in regions:
        color = (0, 200, 200)
        for key, c in colors.items():
            if key in name:
                color = c
                break
        cv2.rectangle(overlay,
                      (region.x_start, region.y_start),
                      (region.x_end, region.y_end),
                      color, 2)
        cv2.putText(overlay, name,
                    (region.x_start, region.y_start - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    return overlay


def generate_html(probes: List[OCRProbe], match_name: str, summary_img: np.ndarray, timeline_imgs: List[np.ndarray]) -> str:
    """Generate an HTML report from collected probes."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    total = len(probes)
    passed = sum(1 for p in probes if p.status == "pass")
    failed = sum(1 for p in probes if p.status == "fail")
    warned = sum(1 for p in probes if p.status == "warn")
    errors = sum(1 for p in probes if p.status == "error")

    # Build overlays for summary
    summary_regions = [(p.name, p.region) for p in probes if p.source == "summary"]
    summary_overlay = build_source_overlay(summary_img, summary_regions, "summary")

    # Build overlay for first timeline
    t1_regions = [(p.name, p.region) for p in probes if p.source == "timeline_1"]
    t1_overlay = build_source_overlay(timeline_imgs[0], t1_regions, "timeline_1")

    status_colors = {
        "pass": "#22c55e",
        "fail": "#ef4444",
        "warn": "#f59e0b",
        "error": "#dc2626",
        "unknown": "#6b7280",
    }

    probe_cards = ""
    for p in probes:
        color = status_colors.get(p.status, "#6b7280")
        img_b64 = image_to_base64(p.image)
        ocr_text = "<br>".join(f"<code>{t}</code>" for t in p.ocr_result) if p.ocr_result else "<em>nothing detected</em>"
        error_block = f'<div class="error-block"><pre>{p.error}</pre></div>' if p.error else ""

        probe_cards += f'''
        <div class="probe-card">
            <div class="probe-header" style="border-left: 4px solid {color};">
                <span class="status-badge" style="background: {color};">{p.status.upper()}</span>
                <strong>{p.name}</strong>
                <span class="source-tag">{p.source}</span>
                <span class="timing">{p.elapsed:.3f}s</span>
            </div>
            <div class="probe-body">
                <div class="probe-image">
                    <img src="data:image/png;base64,{img_b64}" alt="{p.name}">
                    <div class="region-info">region: y={p.region.y_start}:{p.region.y_end} x={p.region.x_start}:{p.region.x_end}</div>
                </div>
                <div class="probe-result">
                    <div class="result-label">OCR output:</div>
                    <div class="result-text">{ocr_text}</div>
                    <div class="notes">{p.notes}</div>
                    {error_block}
                </div>
            </div>
        </div>
        '''

    summary_b64 = image_to_base64(summary_overlay)
    t1_b64 = image_to_base64(t1_overlay)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OCR Diagnostic Report - {match_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0f1117; color: #e4e4e7; padding: 24px; }}
        .header {{ margin-bottom: 32px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; color: #fff; }}
        .header .meta {{ color: #71717a; font-size: 14px; }}
        .stats {{ display: flex; gap: 16px; margin-bottom: 32px; }}
        .stat {{ background: #1c1c22; border-radius: 8px; padding: 16px 24px; min-width: 120px; }}
        .stat .value {{ font-size: 28px; font-weight: 700; }}
        .stat .label {{ font-size: 12px; color: #71717a; text-transform: uppercase; letter-spacing: 0.05em; }}
        .section {{ margin-bottom: 32px; }}
        .section h2 {{ font-size: 18px; margin-bottom: 16px; color: #a1a1aa; border-bottom: 1px solid #27272a; padding-bottom: 8px; }}
        .overlay-container {{ margin-bottom: 16px; }}
        .overlay-container img {{ max-width: 100%; border-radius: 8px; border: 1px solid #27272a; }}
        .overlay-label {{ font-size: 13px; color: #71717a; margin-bottom: 6px; }}
        .probe-card {{ background: #1c1c22; border-radius: 8px; margin-bottom: 12px; overflow: hidden; }}
        .probe-header {{ padding: 12px 16px; display: flex; align-items: center; gap: 12px; background: #18181b; }}
        .status-badge {{ color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px; text-transform: uppercase; }}
        .source-tag {{ background: #27272a; color: #a1a1aa; font-size: 11px; padding: 2px 8px; border-radius: 4px; }}
        .timing {{ color: #52525b; font-size: 12px; margin-left: auto; }}
        .probe-body {{ display: flex; gap: 20px; padding: 16px; }}
        .probe-image {{ flex-shrink: 0; }}
        .probe-image img {{ border: 1px solid #3f3f46; border-radius: 4px; image-rendering: pixelated; min-width: 80px; max-height: 120px; }}
        .region-info {{ font-size: 11px; color: #52525b; margin-top: 4px; font-family: monospace; }}
        .probe-result {{ flex: 1; }}
        .result-label {{ font-size: 12px; color: #71717a; margin-bottom: 4px; }}
        .result-text {{ font-size: 14px; margin-bottom: 8px; }}
        .result-text code {{ background: #27272a; padding: 2px 6px; border-radius: 3px; font-size: 13px; }}
        .notes {{ font-size: 13px; color: #a1a1aa; }}
        .error-block {{ margin-top: 8px; }}
        .error-block pre {{ background: #1a0000; color: #fca5a5; padding: 8px; border-radius: 4px; font-size: 11px; overflow-x: auto; }}
        .filters {{ margin-bottom: 16px; display: flex; gap: 8px; }}
        .filter-btn {{ background: #27272a; border: 1px solid #3f3f46; color: #a1a1aa; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 13px; }}
        .filter-btn:hover, .filter-btn.active {{ background: #3f3f46; color: #fff; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>ocr diagnostic report</h1>
        <div class="meta">{match_name} &middot; {timestamp} &middot; {len(timeline_imgs)} rounds</div>
    </div>

    <div class="stats">
        <div class="stat"><div class="value">{total}</div><div class="label">total probes</div></div>
        <div class="stat"><div class="value" style="color: #22c55e;">{passed}</div><div class="label">passed</div></div>
        <div class="stat"><div class="value" style="color: #ef4444;">{failed}</div><div class="label">failed</div></div>
        <div class="stat"><div class="value" style="color: #f59e0b;">{warned}</div><div class="label">warnings</div></div>
        <div class="stat"><div class="value" style="color: #dc2626;">{errors}</div><div class="label">errors</div></div>
    </div>

    <div class="section">
        <h2>region overlays</h2>
        <p style="font-size: 13px; color: #52525b; margin-bottom: 12px;">colored rectangles show where each OCR region is being cropped from the source image</p>
        <div class="overlay-container">
            <div class="overlay-label">summary screen</div>
            <img src="data:image/png;base64,{summary_b64}" alt="summary overlay">
        </div>
        <div class="overlay-container">
            <div class="overlay-label">timeline 1 (scoreboard + round data)</div>
            <img src="data:image/png;base64,{t1_b64}" alt="timeline 1 overlay">
        </div>
    </div>

    <div class="section">
        <h2>ocr probes</h2>
        <div class="filters">
            <button class="filter-btn active" onclick="filterProbes('all')">all</button>
            <button class="filter-btn" onclick="filterProbes('fail')">failures</button>
            <button class="filter-btn" onclick="filterProbes('warn')">warnings</button>
            <button class="filter-btn" onclick="filterProbes('pass')">passed</button>
        </div>
        <div id="probes">
            {probe_cards}
        </div>
    </div>

    <script>
        function filterProbes(status) {{
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
            document.querySelectorAll('.probe-card').forEach(card => {{
                const badge = card.querySelector('.status-badge').textContent.toLowerCase();
                card.style.display = (status === 'all' || badge === status) ? 'block' : 'none';
            }});
        }}
    </script>
</body>
</html>'''
    return html


def run_report(match_name: str, config: dict) -> bool:
    logger.set_log_level("DEBUG")
    logger.user_output(f"\nprocessing: {match_name}")

    timeline_images, scoreboard_image, summary_image = read_images_from_folder(config, match_name)

    if not timeline_images or scoreboard_image is None or summary_image is None:
        logger.user_output(f"missing images for {match_name}")
        return False

    logger.user_output(f"loaded {len(timeline_images)} timelines, running ocr probes...")

    probes = collect_probes(timeline_images, scoreboard_image, summary_image)

    failed = sum(1 for p in probes if p.status in ("fail", "error"))
    passed = sum(1 for p in probes if p.status == "pass")
    logger.user_output(f"probes done: {passed} passed, {failed} failed")

    html = generate_html(probes, match_name, summary_image, timeline_images)

    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"{match_name}-ocr-report.html"
    report_path.write_text(html)

    logger.user_output(f"report saved: {report_path}")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="OCR diagnostic report generator")
    parser.add_argument('--match', help='specific match folder (e.g. match-1)')
    args = parser.parse_args()

    config = load_config()
    config['log_dir'] = str(Path(__file__).parent / "data")

    logger.user_output("initializing ocr...")
    initialize_ocr()

    data_dir = Path(__file__).parent / "data"
    if args.match:
        matches = [args.match]
    else:
        matches = [d.name for d in sorted(data_dir.iterdir()) if d.is_dir()]

    all_passed = True
    for match_name in matches:
        if not run_report(match_name, config):
            all_passed = False

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
