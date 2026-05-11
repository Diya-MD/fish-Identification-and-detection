"""
config.py
---------
Central configuration for the Fish Species Detector application.
All tunable constants live here — no magic numbers elsewhere in the codebase.
"""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
OUTPUT_DIR = STATIC_DIR / "outputs"

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_PATH     = BASE_DIR / "main_model.pt"
DETECTION_CONF = 0.70   # minimum score to run NMS / draw a box
REPORT_CONF    = 0.85   # minimum score to include a species in the API response

# ── Upload constraints ─────────────────────────────────────────────────────────
ALLOWED_IMAGE_EXT  = {"png", "jpg", "jpeg"}
ALLOWED_VIDEO_EXT  = {"mp4", "avi", "mov"}
ALLOWED_EXT        = ALLOWED_IMAGE_EXT | ALLOWED_VIDEO_EXT
MAX_BATCH_FILES    = 10
MAX_FILE_SIZE_MB   = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024   # 5 242 880 bytes

# ── Video encoding ─────────────────────────────────────────────────────────────
VIDEO_CODEC       = "avc1"   # H.264 — broadly compatible
DEFAULT_VIDEO_FPS = 25.0     # fallback if cap.get(FPS) returns 0