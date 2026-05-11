"""
routes/media.py
---------------
Flask Blueprint for serving uploaded and processed media files.

Endpoints
~~~~~~~~~
  GET /uploads/<filename>  — serve original uploaded files
  GET /outputs/<filename>  — serve annotated output files
"""

from flask import Blueprint, send_from_directory

from config import UPLOAD_DIR, OUTPUT_DIR

media_bp = Blueprint("media", __name__)


@media_bp.get("/uploads/<filename>")
def serve_upload(filename: str):
    """Serve a file from the uploads directory."""
    return send_from_directory(UPLOAD_DIR, filename)


@media_bp.get("/outputs/<filename>")
def serve_output(filename: str):
    """Serve a file from the outputs directory."""
    return send_from_directory(OUTPUT_DIR, filename)
