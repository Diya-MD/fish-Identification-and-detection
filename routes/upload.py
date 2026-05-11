"""
routes/upload.py
----------------
Flask Blueprint for file upload endpoints.

Endpoints
~~~~~~~~~
  POST /upload        — single file upload
  POST /batch-upload  — up to MAX_BATCH_FILES files in one request
"""

import logging
from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR, MAX_BATCH_FILES, MAX_FILE_SIZE_MB
from services.detector import process_file
from utils.file_utils import allowed_file, is_file_within_size_limit

logger = logging.getLogger(__name__)

upload_bp = Blueprint("upload", __name__)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _save_and_process(file) -> dict:
    """Persist *file* to UPLOAD_DIR and run inference. Returns a result dict."""
    filename = secure_filename(file.filename)
    filepath = UPLOAD_DIR / filename
    file.save(filepath)
    logger.info("Saved upload: %s", filename)
    return process_file(filepath)


# ── Routes ─────────────────────────────────────────────────────────────────────

@upload_bp.post("/upload")
def upload_file():
    """
    Single-file upload.

    Accepts one image (png/jpg/jpeg) or video (mp4/avi/mov) via multipart/form-data
    with the field name ``file``.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    if not is_file_within_size_limit(file):
        return jsonify({"error": f"File too large — maximum allowed size is {MAX_FILE_SIZE_MB} MB"}), 413

    result = _save_and_process(file)
    status = 500 if "error" in result else 200
    return jsonify(result), status


@upload_bp.post("/batch-upload")
def batch_upload():
    """
    Batch upload — up to MAX_BATCH_FILES files per request.

    Send a multipart/form-data request with one or more fields all named ``files``.
    Returns ``{ "results": [...], "total": N }``.
    """
    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files provided"}), 400

    if len(files) > MAX_BATCH_FILES:
        return jsonify({
            "error": f"Too many files — maximum is {MAX_BATCH_FILES} per request"
        }), 400

    invalid = [f.filename for f in files if not allowed_file(f.filename or "")]
    if invalid:
        return jsonify({"error": f"Unsupported file type(s): {', '.join(invalid)}"}), 400

    results = [_save_and_process(f) for f in files]
    return jsonify({"results": results, "total": len(results)})