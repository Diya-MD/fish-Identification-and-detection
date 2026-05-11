"""
routes/species.py
-----------------
Flask Blueprint exposing the species knowledge base as a REST sub-API.

Endpoints
~~~~~~~~~
  GET /species           — list all known species (summary cards)
  GET /species/<id>      — full detail for a single species slug
"""

from flask import Blueprint, jsonify

from models.species import SPECIES_DB

species_bp = Blueprint("species", __name__)


@species_bp.get("/species")
def list_species():
    """
    Return summary cards for every species in the database.

    Useful for front-end autocomplete, filter dropdowns, or info pages.
    Does NOT include the full facts list — use the detail endpoint for that.
    """
    data = [
        {
            "id":           key,
            "habitat":      info.habitat,
            "conservation": info.conservation,
            "diet":         info.diet,
            "max_size_cm":  info.max_size_cm,
            "tags":         info.tags,
            "fact_count":   len(info.facts),
        }
        for key, info in SPECIES_DB.items()
    ]
    return jsonify(data)


@species_bp.get("/species/<species_id>")
def species_detail(species_id: str):
    """
    Return full detail (including all facts) for a single species.

    ``species_id`` must match a hyphenated slug from the database,
    e.g. ``blue-tang``, ``clownfish``, ``yellow-tang``.
    Returns 404 if the slug is not recognised.
    """
    info = SPECIES_DB.get(species_id)
    if not info:
        return jsonify({"error": f"Species '{species_id}' not found"}), 404

    return jsonify({
        "id":           species_id,
        "facts":        info.facts,
        "habitat":      info.habitat,
        "conservation": info.conservation,
        "diet":         info.diet,
        "max_size_cm":  info.max_size_cm,
        "tags":         info.tags,
    })