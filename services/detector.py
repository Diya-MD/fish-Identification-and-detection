"""
services/detector.py
--------------------
Wraps the YOLOv11 model and exposes clean inference methods for images and videos.

Public API
~~~~~~~~~~
  detector.process_image(path) -> (output_path, [species_names])
  detector.process_video(path) -> (output_path, [species_names])
  detector.process_file(path)  -> JSON-ready result dict
"""

import logging
from pathlib import Path

import cv2
from PIL import Image
from ultralytics import YOLO

from config import (
    MODEL_PATH,
    DETECTION_CONF,
    REPORT_CONF,
    OUTPUT_DIR,
    ALLOWED_IMAGE_EXT,
    VIDEO_CODEC,
    DEFAULT_VIDEO_FPS,
)
from models.species import get_species_card

logger = logging.getLogger(__name__)


# ── Model singleton ────────────────────────────────────────────────────────────

logger.info("Loading YOLOv11 model from %s …", MODEL_PATH)
_model = YOLO(str(MODEL_PATH))
logger.info("Model ready.")


# ── Internal helpers ───────────────────────────────────────────────────────────

def _ext(filename: str) -> str:
    """Return the lowercase extension of *filename* without the leading dot."""
    return Path(filename).suffix.lstrip(".").lower()


def _collect_species(result, threshold: float) -> list[str]:
    """Extract unique species names from a YOLO result above *threshold*."""
    names = []
    for box in result.boxes:
        if float(box.conf[0]) >= threshold:
            names.append(result.names[int(box.cls[0])])
    return list(set(names))


# ── Public inference methods ───────────────────────────────────────────────────

def process_image(image_path: Path) -> tuple[Path, list[str]]:
    """
    Run YOLOv11 inference on a single image.

    Returns
    -------
    (output_path, detected_species)
      output_path      : annotated image saved to OUTPUT_DIR (or original if nothing found)
      detected_species : list of unique species name strings
    """
    results = _model(str(image_path), conf=DETECTION_CONF)
    result  = results[0]

    species = _collect_species(result, REPORT_CONF)
    if not species:
        return image_path, []

    output_path = OUTPUT_DIR / f"output_{image_path.name}"
    annotated   = Image.fromarray(result.plot()[..., ::-1])
    annotated.save(output_path)

    logger.info("Image processed — %d species detected: %s", len(species), species)
    return output_path, species


def process_video(video_path: Path) -> tuple[Path, list[str]]:
    """
    Run YOLOv11 inference on every frame of a video.

    Returns
    -------
    (output_path, detected_species)
      output_path      : annotated video saved to OUTPUT_DIR (or original if nothing found)
      detected_species : list of unique species name strings seen across all frames
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video file: {video_path}")

    fps    = cap.get(cv2.CAP_PROP_FPS) or DEFAULT_VIDEO_FPS
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    output_path = OUTPUT_DIR / f"output_{video_path.name}"
    fourcc      = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
    writer      = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    detected: set[str] = set()
    has_detections     = False

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = _model(frame, conf=DETECTION_CONF)
            result  = results[0]

            if result.boxes:
                has_detections = True
                writer.write(result.plot())
                for name in _collect_species(result, REPORT_CONF):
                    detected.add(name)
            else:
                writer.write(frame)

    finally:
        cap.release()
        writer.release()

    if not has_detections:
        output_path.unlink(missing_ok=True)
        logger.info("Video processed — no detections above threshold.")
        return video_path, []

    species = list(detected)
    logger.info("Video processed — %d species detected: %s", len(species), species)
    return output_path, species


def process_file(filepath: Path) -> dict:
    """
    Dispatch *filepath* to the correct processor and return a JSON-ready result dict.

    Always returns a dict. On processing errors the dict contains an 'error' key
    instead of raising — letting the route handler decide the HTTP status code.
    """
    is_image = _ext(filepath.name) in ALLOWED_IMAGE_EXT

    try:
        if is_image:
            output_path, species_names = process_image(filepath)
        else:
            output_path, species_names = process_video(filepath)

    except Exception as exc:
        logger.exception("Failed to process %s", filepath.name)
        return {"error": str(exc), "filename": filepath.name}

    return {
        "filename":  filepath.name,
        "type":      "image" if is_image else "video",
        "original":  f"/uploads/{filepath.name}",
        "processed": f"/outputs/{output_path.name}" if species_names else f"/uploads/{filepath.name}",
        "species":   [get_species_card(s) for s in species_names],
        "message":   None if species_names else "No fish detected with sufficient confidence (≥85%).",
    }
