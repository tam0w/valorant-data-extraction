"""
Interactive coordinate selector for OCR regions.
Generates an HTML tool where you can click-drag on screenshots to find coordinates.

Usage:
    uv run python -m tests.coordinate_selector --dir new-ui
    uv run python -m tests.coordinate_selector                    # defaults to new-ui
"""

import argparse
import base64
import sys
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.constants import (
    SUMMARY_SIDES_REGION,
    SUMMARY_SCORE_REGION,
    SUMMARY_MAP_REGION,
    TIMELINE_OUTCOME_REGION,
    TIMELINE_ECONOMY_REGION,
    TIMELINE_AWP_REGION,
    TIMELINE_MINIMAP_REGION,
)


def image_to_base64(img: np.ndarray) -> str:
    _, buffer = cv2.imencode(".png", img)
    return base64.b64encode(buffer).decode("utf-8")


ALL_REGIONS = {
    "summary": [
        ("SUMMARY_SIDES_REGION", SUMMARY_SIDES_REGION),
        ("SUMMARY_SCORE_REGION", SUMMARY_SCORE_REGION),
        ("SUMMARY_MAP_REGION", SUMMARY_MAP_REGION),
    ],
    "timeline": [
        ("TIMELINE_OUTCOME_REGION", TIMELINE_OUTCOME_REGION),
        ("TIMELINE_ECONOMY_REGION", TIMELINE_ECONOMY_REGION),
        ("TIMELINE_AWP_REGION", TIMELINE_AWP_REGION),
        ("TIMELINE_MINIMAP_REGION", TIMELINE_MINIMAP_REGION),
    ],
    "scoreboard": [],
}

REGION_COLORS = {
    "SUMMARY_SIDES_REGION": "#00ffff",
    "SUMMARY_SCORE_REGION": "#00ff00",
    "SUMMARY_MAP_REGION": "#ff00ff",
    "TIMELINE_OUTCOME_REGION": "#ffff00",
    "TIMELINE_ECONOMY_REGION": "#ffa500",
    "TIMELINE_AWP_REGION": "#ff69b4",
    "TIMELINE_MINIMAP_REGION": "#87ceeb",
}


def generate_html(
    match_name: str,
    summary_img: np.ndarray,
    timeline_imgs: list[np.ndarray],
    scoreboard_img: np.ndarray,
) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    summary_b64 = image_to_base64(summary_img)
    timeline_b64 = image_to_base64(timeline_imgs[0])
    scoreboard_b64 = image_to_base64(scoreboard_img)

    h, w = summary_img.shape[:2]

    region_data = {
        "summary": [
            {
                "name": n,
                "y1": r.y_start,
                "y2": r.y_end,
                "x1": r.x_start,
                "x2": r.x_end,
                "color": REGION_COLORS.get(n, "#00ff00"),
            }
            for n, r in ALL_REGIONS["summary"]
        ],
        "timeline": [
            {
                "name": n,
                "y1": r.y_start,
                "y2": r.y_end,
                "x1": r.x_start,
                "x2": r.x_end,
                "color": REGION_COLORS.get(n, "#00ff00"),
            }
            for n, r in ALL_REGIONS["timeline"]
        ],
        "scoreboard": [
            {
                "name": n,
                "y1": r.y_start,
                "y2": r.y_end,
                "x1": r.x_start,
                "x2": r.x_end,
                "color": REGION_COLORS.get(n, "#00ff00"),
            }
            for n, r in ALL_REGIONS["scoreboard"]
        ],
    }

    region_json = str(region_data).replace("'", '"')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Coordinate Selector - {match_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0f1117; color: #e4e4e7; padding: 24px; }}
        .header {{ margin-bottom: 24px; }}
        .header h1 {{ font-size: 24px; margin-bottom: 8px; color: #fff; }}
        .header .meta {{ color: #71717a; font-size: 14px; }}
        
        .layout {{ display: grid; grid-template-columns: 1fr 380px; gap: 24px; }}
        
        .image-section {{ background: #1c1c22; border-radius: 12px; padding: 16px; }}
        .tabs {{ display: flex; gap: 8px; margin-bottom: 16px; }}
        .tab {{ background: #27272a; border: 1px solid #3f3f46; color: #a1a1aa; padding: 8px 20px; border-radius: 8px; cursor: pointer; font-size: 14px; }}
        .tab:hover {{ background: #3f3f46; }}
        .tab.active {{ background: #3b82f6; color: #fff; border-color: #3b82f6; }}
        
        .canvas-container {{ position: relative; display: inline-block; cursor: crosshair; }}
        .canvas-container canvas {{ position: absolute; top: 0; left: 0; }}
        .canvas-container img {{ display: block; border-radius: 8px; max-width: 100%; }}
        
        .sidebar {{ display: flex; flex-direction: column; gap: 16px; }}
        
        .panel {{ background: #1c1c22; border-radius: 12px; padding: 16px; }}
        .panel h3 {{ font-size: 14px; color: #a1a1aa; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.05em; }}
        
        .selection-output {{ background: #0f1117; border-radius: 8px; padding: 12px; font-family: monospace; }}
        .selection-output .label {{ color: #71717a; font-size: 12px; margin-bottom: 8px; }}
        .selection-output .coords {{ font-size: 13px; color: #22c55e; word-break: break-all; }}
        .selection-output .code {{ background: #27272a; padding: 12px; border-radius: 6px; margin-top: 8px; font-size: 12px; }}
        .selection-output .code pre {{ white-space: pre-wrap; color: #e4e4e7; }}
        
        .copy-btn {{ background: #3b82f6; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; margin-top: 8px; width: 100%; }}
        .copy-btn:hover {{ background: #2563eb; }}
        .copy-btn:disabled {{ background: #3f3f46; cursor: not-allowed; }}
        
        .regions-list {{ max-height: 400px; overflow-y: auto; }}
        .region-item {{ display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: 6px; margin-bottom: 4px; cursor: pointer; }}
        .region-item:hover {{ background: #27272a; }}
        .region-item .color-box {{ width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }}
        .region-item .name {{ flex: 1; font-size: 13px; color: #e4e4e7; }}
        .region-item .coords-text {{ font-size: 11px; color: #71717a; font-family: monospace; }}
        
        .instructions {{ font-size: 13px; color: #71717a; line-height: 1.6; }}
        .instructions ul {{ margin-top: 8px; padding-left: 20px; }}
        .instructions li {{ margin-bottom: 6px; }}
        
        .toast {{ position: fixed; bottom: 24px; right: 24px; background: #22c55e; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 14px; opacity: 0; transform: translateY(10px); transition: all 0.2s; }}
        .toast.show {{ opacity: 1; transform: translateY(0); }}
    </style>
</head>
<body>
    <div class="header">
        <h1>coordinate selector</h1>
        <div class="meta">{match_name} &middot; {w}x{h} &middot; {timestamp}</div>
    </div>

    <div class="layout">
        <div class="image-section">
            <div class="tabs">
                <button class="tab active" onclick="switchImage('summary')">summary</button>
                <button class="tab" onclick="switchImage('timeline')">timeline</button>
                <button class="tab" onclick="switchImage('scoreboard')">scoreboard</button>
            </div>
            <div class="canvas-container" id="canvasContainer">
                <img id="baseImage" src="data:image/png;base64,{summary_b64}" alt="screenshot">
                <canvas id="overlayCanvas"></canvas>
            </div>
        </div>

        <div class="sidebar">
            <div class="panel">
                <h3>selection</h3>
                <div class="selection-output">
                    <div class="label">click and drag on image to select region</div>
                    <div class="coords" id="coordsDisplay">no selection</div>
                    <div class="code" id="codeOutput" style="display: none;">
                        <pre id="codeText"></pre>
                    </div>
                    <button class="copy-btn" id="copyBtn" onclick="copyCode()" disabled>copy code</button>
                </div>
            </div>

            <div class="panel">
                <h3>existing regions</h3>
                <div class="regions-list" id="regionsList"></div>
            </div>

            <div class="panel">
                <h3>instructions</h3>
                <div class="instructions">
                    <ul>
                        <li>click and drag to select a region</li>
                        <li>click existing regions to highlight them</li>
                        <li>coordinates format: <code>ImageRegion(y1, y2, x1, x2)</code></li>
                        <li>toggle regions with the checkbox</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast">copied to clipboard</div>

    <script>
        const images = {{
            summary: "data:image/png;base64,{summary_b64}",
            timeline: "data:image/png;base64,{timeline_b64}",
            scoreboard: "data:image/png;base64,{scoreboard_b64}"
        }};
        
        const allRegions = {region_json};
        
        let currentImage = 'summary';
        let isDrawing = false;
        let startX, startY;
        let selection = null;
        let enabledRegions = new Set();
        
        const container = document.getElementById('canvasContainer');
        const canvas = document.getElementById('overlayCanvas');
        const ctx = canvas.getContext('2d');
        const img = document.getElementById('baseImage');
        
        img.onload = initCanvas;
        
        function initCanvas() {{
            canvas.width = img.naturalWidth;
            canvas.height = img.naturalHeight;
            canvas.style.width = img.width + 'px';
            canvas.style.height = img.height + 'px';
            drawOverlay();
        }}
        
        function switchImage(type) {{
            currentImage = type;
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            img.src = images[type];
            selection = null;
            updateCoordsDisplay();
            renderRegionsList();
        }}
        
        function getMousePos(e) {{
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            return {{
                x: Math.round((e.clientX - rect.left) * scaleX),
                y: Math.round((e.clientY - rect.top) * scaleY)
            }};
        }}
        
        canvas.addEventListener('mousedown', (e) => {{
            const pos = getMousePos(e);
            isDrawing = true;
            startX = pos.x;
            startY = pos.y;
        }});
        
        canvas.addEventListener('mousemove', (e) => {{
            if (!isDrawing) return;
            const pos = getMousePos(e);
            selection = {{
                x1: Math.min(startX, pos.x),
                x2: Math.max(startX, pos.x),
                y1: Math.min(startY, pos.y),
                y2: Math.max(startY, pos.y)
            }};
            drawOverlay();
            updateCoordsDisplay();
        }});
        
        canvas.addEventListener('mouseup', () => {{
            isDrawing = false;
        }});
        
        canvas.addEventListener('mouseleave', () => {{
            isDrawing = false;
        }});
        
        function drawOverlay() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw existing regions
            const regions = allRegions[currentImage] || [];
            regions.forEach(r => {{
                if (!enabledRegions.has(r.name)) return;
                ctx.strokeStyle = r.color;
                ctx.lineWidth = 2;
                ctx.strokeRect(r.x1, r.y1, r.x2 - r.x1, r.y2 - r.y1);
                
                ctx.fillStyle = r.color + '33';
                ctx.fillRect(r.x1, r.y1, r.x2 - r.x1, r.y2 - r.y1);
                
                ctx.font = '12px monospace';
                ctx.fillStyle = r.color;
                ctx.fillText(r.name, r.x1 + 4, r.y1 - 4);
            }});
            
            // Draw current selection
            if (selection) {{
                ctx.strokeStyle = '#ff0000';
                ctx.lineWidth = 2;
                ctx.setLineDash([5, 5]);
                ctx.strokeRect(selection.x1, selection.y1, selection.x2 - selection.x1, selection.y2 - selection.y1);
                ctx.setLineDash([]);
                
                ctx.fillStyle = '#ff000066';
                ctx.fillRect(selection.x1, selection.y1, selection.x2 - selection.x1, selection.y2 - selection.y1);
            }}
        }}
        
        function updateCoordsDisplay() {{
            const display = document.getElementById('coordsDisplay');
            const codeOutput = document.getElementById('codeOutput');
            const codeText = document.getElementById('codeText');
            const copyBtn = document.getElementById('copyBtn');
            
            if (selection) {{
                const y1 = Math.min(selection.y1, selection.y2);
                const y2 = Math.max(selection.y1, selection.y2);
                const x1 = Math.min(selection.x1, selection.x2);
                const x2 = Math.max(selection.x1, selection.x2);
                
                display.textContent = `y: ${{y1}}-${{y2}}, x: ${{x1}}-${{x2}}`;
                codeText.textContent = `ImageRegion(${{y1}}, ${{y2}}, ${{x1}}, ${{x2}})`;
                codeOutput.style.display = 'block';
                copyBtn.disabled = false;
            }} else {{
                display.textContent = 'no selection';
                codeOutput.style.display = 'none';
                copyBtn.disabled = true;
            }}
        }}
        
        function renderRegionsList() {{
            const list = document.getElementById('regionsList');
            const regions = allRegions[currentImage] || [];
            
            list.innerHTML = regions.map(r => `
                <div class="region-item" onclick="toggleRegion('${{r.name}}')">
                    <input type="checkbox" ${{enabledRegions.has(r.name) ? 'checked' : ''}} onclick="event.stopPropagation(); toggleRegion('${{r.name}}')">
                    <div class="color-box" style="background: ${{r.color}}"></div>
                    <div class="name">${{r.name}}</div>
                    <div class="coords-text">${{r.y1}},${{r.y2}},${{r.x1}},${{r.x2}}</div>
                </div>
            `).join('');
        }}
        
        function toggleRegion(name) {{
            if (enabledRegions.has(name)) {{
                enabledRegions.delete(name);
            }} else {{
                enabledRegions.add(name);
            }}
            renderRegionsList();
            drawOverlay();
        }}
        
        function copyCode() {{
            if (!selection) return;
            const y1 = Math.min(selection.y1, selection.y2);
            const y2 = Math.max(selection.y1, selection.y2);
            const x1 = Math.min(selection.x1, selection.x2);
            const x2 = Math.max(selection.x1, selection.x2);
            
            navigator.clipboard.writeText(`ImageRegion(${{y1}}, ${{y2}}, ${{x1}}, ${{x2}})`);
            showToast();
        }}
        
        function showToast() {{
            const toast = document.getElementById('toast');
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }}
        
        // Initialize
        ALL_REGIONS['summary'].forEach(r => enabledRegions.add(r.name));
        ALL_REGIONS['timeline'].forEach(r => enabledRegions.add(r.name));
        renderRegionsList();
        setTimeout(initCanvas, 100);
    </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Interactive coordinate selector")
    parser.add_argument(
        "--dir", help="directory with images (e.g. new-ui, match-1)", default="new-ui"
    )
    args = parser.parse_args()

    data_dir = Path(__file__).parent / "data" / args.dir
    if not data_dir.exists():
        print(f"directory not found: {data_dir}")
        sys.exit(1)

    summary_path = data_dir / "summary.png"
    scoreboard_path = data_dir / "scoreboard.png"
    timeline_paths = sorted(data_dir.glob("timeline_*.png"))

    if not summary_path.exists():
        print(f"missing summary.png in {data_dir}")
        sys.exit(1)
    if not scoreboard_path.exists():
        print(f"missing scoreboard.png in {data_dir}")
        sys.exit(1)
    if not timeline_paths:
        print(f"no timeline_*.png files in {data_dir}")
        sys.exit(1)

    summary_image = cv2.imread(str(summary_path))
    scoreboard_image = cv2.imread(str(scoreboard_path))
    timeline_images = [cv2.imread(str(p)) for p in timeline_paths]

    if (
        summary_image is None
        or scoreboard_image is None
        or any(img is None for img in timeline_images)
    ):
        print("failed to load one or more images")
        sys.exit(1)

    html = generate_html(args.dir, summary_image, timeline_images, scoreboard_image)

    report_dir = Path(__file__).parent / "reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"{args.dir}-selector.html"
    report_path.write_text(html)

    print(f"selector saved: {report_path}")
    print("open in browser to select coordinates")


if __name__ == "__main__":
    main()
