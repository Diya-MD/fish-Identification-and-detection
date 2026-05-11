"""
app.py
------
Application factory and entry point for the Fish Species Detector.

Run locally
~~~~~~~~~~~
  python app.py

Production (example with gunicorn)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  gunicorn "app:create_app()" --bind 0.0.0.0:8000 --workers 2
"""

import logging
from flask import Flask, render_template, jsonify
from werkzeug.exceptions import RequestEntityTooLarge

from config import UPLOAD_DIR, OUTPUT_DIR, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB
from routes.upload  import upload_bp
from routes.species import species_bp
from routes.media   import media_bp

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ── Directory bootstrap ────────────────────────────────────────────────────────
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Application factory ────────────────────────────────────────────────────────
def create_app() -> Flask:
    """Construct and configure the Flask application."""
    app = Flask(__name__)

    # File size limit — Flask rejects oversized requests before they hit a route
    app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE_BYTES

    # Register blueprints
    app.register_blueprint(upload_bp)
    app.register_blueprint(species_bp)
    app.register_blueprint(media_bp)

    # Root view
    @app.get("/")
    def index():
        return render_template("index.html")

    # Handle oversized uploads with a clean JSON response
    @app.errorhandler(RequestEntityTooLarge)
    def file_too_large(e):
        return jsonify({
            "error": f"File too large — maximum allowed size is {MAX_FILE_SIZE_MB} MB"
        }), 413

    logger.info("Application created — blueprints registered.")
    return app


# ── Dev server entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    create_app().run(debug=True)