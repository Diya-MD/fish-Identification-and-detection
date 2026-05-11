# 🐟 Fish Species Detector

> A Flask-powered web application that uses YOLOv11 to detect and identify fish species in images and videos, enriched with a built-in species knowledge base.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Species Database](#species-database)
- [Configuration](#configuration)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Tech Stack](#tech-stack)

---

## Overview

Fish Species Detector accepts single or batched image/video uploads, runs them through a custom-trained YOLOv11 model, and returns annotated output files alongside structured species data (habitat, diet, conservation status, fun facts, and more). A built-in REST sub-API exposes the species knowledge base independently for use in other clients or pipelines.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client / Browser                     │
│              (multipart/form-data upload requests)          │
└────────────────────────────┬────────────────────────────────┘
                             │  HTTP
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                      │
│                        (app.py)                             │
│                                                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────┐  │
│  │  upload_bp      │  │   species_bp     │  │ media_bp  │  │
│  │  /upload        │  │   /species       │  │ /uploads/ │  │
│  │  /batch-upload  │  │   /species/<id>  │  │ /outputs/ │  │
│  └────────┬────────┘  └──────────────────┘  └───────────┘  │
│           │                    │                            │
│           ▼                    ▼                            │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ services/        │  │ models/          │                │
│  │ detector.py      │  │ species.py       │                │
│  │ (YOLOv11)        │  │ (SPECIES_DB)     │                │
│  └────────┬─────────┘  └──────────────────┘                │
│           │                                                 │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                     File System                             │
│                                                             │
│   static/uploads/   ←── original uploads saved here        │
│   static/outputs/   ←── annotated outputs written here     │
│   main_model.pt     ←── YOLOv11 weights                    │
└─────────────────────────────────────────────────────────────┘
```

### Request Lifecycle

1. Client sends a `POST` request with one or more media files.
2. `upload_bp` validates the file type and size, then writes the file to `static/uploads/`.
3. `services/detector.py` runs YOLOv11 inference using `main_model.pt`.
4. Annotated output (bounding boxes, labels, confidence scores) is written to `static/outputs/`.
5. A JSON response is returned containing detection results and species metadata sourced from `SPECIES_DB`.
6. Client can fetch the annotated media via `GET /outputs/<filename>` or browse species info via `/species`.

---

## Project Structure

```
fish-species-detector/
│
├── app.py                  # Application factory & dev entry point
├── config.py               # All tunable constants (paths, thresholds, limits)
├── requirements.txt        # Python dependencies
├── main_model.pt           # YOLOv11 model weights (not tracked in git)
│
├── routes/
│   ├── upload.py           # POST /upload, POST /batch-upload
│   ├── species.py          # GET /species, GET /species/<id>
│   └── media.py            # GET /uploads/<f>, GET /outputs/<f>
│
├── models/
│   └── species.py          # SpeciesInfo dataclass + SPECIES_DB + get_species_card()
│
├── services/
│   └── detector.py         # YOLOv11 inference pipeline (process_file)
│
├── utils/
│   └── file_utils.py       # allowed_file(), is_file_within_size_limit()
│
├── templates/
│   └── index.html          # Frontend UI
│
└── static/
    ├── uploads/            # Auto-created — stores original uploaded files
    └── outputs/            # Auto-created — stores annotated output files
```

---

## API Reference

### `POST /upload`

Upload a single image or video file for species detection.

| Field | Value |
|---|---|
| Content-Type | `multipart/form-data` |
| Field name | `file` |
| Accepted types | `png`, `jpg`, `jpeg`, `mp4`, `avi`, `mov` |
| Max size | 5 MB |


## Species Database

The built-in knowledge base (`models/species.py`) currently covers 7 species:

| Slug | Common Name | Conservation |
|---|---|---|
| `blue-tang` | Blue Tang | Least Concern |
| `butterflyfish` | Butterflyfish | Least Concern (varies) |
| `clownfish` | Clownfish | Least Concern |
| `moorish-idol` | Moorish Idol | Least Concern |
| `neon-tetra` | Neon Tetra | Least Concern |
| `ribboned-sweetlips` | Ribboned Sweetlips | Least Concern |
| `yellow-tang` | Yellow Tang | Near Threatened |

Each species entry includes habitat, diet, conservation status, max size, tags, and 5 curated facts. The `get_species_card()` helper returns a random fact per call, keeping repeated queries fresh.

---

## Configuration

All constants are centralised in `config.py` — no magic numbers elsewhere in the codebase.

| Constant | Default | Description |
|---|---|---|
| `UPLOAD_DIR` | `static/uploads/` | Where uploaded files are saved |
| `OUTPUT_DIR` | `static/outputs/` | Where annotated outputs are written |
| `MODEL_PATH` | `main_model.pt` | Path to YOLOv11 weights |
| `DETECTION_CONF` | `0.70` | Minimum confidence to draw a bounding box |
| `REPORT_CONF` | `0.85` | Minimum confidence to include in API response |
| `ALLOWED_IMAGE_EXT` | `png, jpg, jpeg` | Accepted image formats |
| `ALLOWED_VIDEO_EXT` | `mp4, avi, mov` | Accepted video formats |
| `MAX_BATCH_FILES` | `10` | Maximum files per batch upload |
| `MAX_FILE_SIZE_MB` | `5` | Per-file upload size limit |
| `VIDEO_CODEC` | `avc1` (H.264) | Output video codec |
| `DEFAULT_VIDEO_FPS` | `25.0` | Fallback FPS when source metadata is missing |

---

## Installation

**Prerequisites:** Python 3.10+, pip

```bash
# 1. Clone the repository
git clone https://github.com/your-username/fish-species-detector.git
cd fish-species-detector

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your model weights
# Place main_model.pt in the project root
```

---

## Running the App

**Development**
```bash
python app.py
# Server starts at http://127.0.0.1:5000
```

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | [Flask 3.x](https://flask.palletsprojects.com/) |
| Object detection | [YOLOv11 via Ultralytics 8.3+](https://docs.ultralytics.com/) |
| Image processing | [Pillow 10+](https://pillow.readthedocs.io/), [OpenCV 4.10+](https://opencv.org/) |

---

## 📸 Demo

### Image Detection
<!-- Replace the path below with your image file -->
![Image Detection Demo](https://raw.githubusercontent.com/Diya-MD/fish-Identification-and-detection/main/assets/output_moorish-idol.jpg)

### Video Detection
<!-- Replace the path below with your video file -->
![Demo](https://raw.githubusercontent.com/Diya-MD/fish-Identification-and-detection/main/assets/demo.gif)

> _Upload a short screen recording or GIF of the app in action._

---
| Request handling | [Werkzeug 3+](https://werkzeug.palletsprojects.com/) |

---
