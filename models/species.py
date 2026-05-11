"""
models/species.py
-----------------
Domain model for fish species data.

Contains:
  - SpeciesInfo  : typed dataclass describing a single species
  - SPECIES_DB   : master lookup table keyed by hyphenated species slug
  - get_species_card() : serialises a species to a JSON-ready dict for API responses
"""

import random
from dataclasses import dataclass, field
from typing import Optional


# ── Domain model ───────────────────────────────────────────────────────────────

@dataclass
class SpeciesInfo:
    """All known facts and metadata for one fish species."""

    facts: list[str]
    habitat: str
    conservation: str
    diet: str                        = "Unknown"
    max_size_cm: Optional[int]       = None
    tags: list[str]                  = field(default_factory=list)


# ── Master species database ────────────────────────────────────────────────────

SPECIES_DB: dict[str, SpeciesInfo] = {
    "blue-tang": SpeciesInfo(
        facts=[
            "Also known as 'Dory' from Finding Nemo, blue tangs are one of the most recognisable reef fish.",
            "They can subtly shift colour depending on stress or mood.",
            "A sharp, retractable spine near the tail is used purely for defence — not attack.",
            "As herbivores they crop algae off coral, directly preventing smothering of reefs.",
            "Juveniles are bright yellow and only develop their blue colouration as they mature.",
        ],
        habitat="Indo-Pacific coral reefs (0–40 m depth)",
        conservation="Least Concern",
        diet="Algae (herbivore)",
        max_size_cm=31,
        tags=["reef", "herbivore", "popular"],
    ),
    "butterflyfish": SpeciesInfo(
        facts=[
            "Many butterflyfish species pair for life, patrolling a shared home territory.",
            "Their laterally compressed bodies let them dart into narrow coral crevices.",
            "Eyespot markings near the tail mislead predators about which end is the head.",
            "Some species are corallivores — specialised to eat living coral polyps.",
            "Butterflyfish are sensitive bio-indicators: their disappearance often signals reef decline.",
        ],
        habitat="Tropical reefs worldwide (1–180 m depth)",
        conservation="Varies by species (mostly Least Concern)",
        diet="Coral polyps, small invertebrates, algae",
        max_size_cm=22,
        tags=["reef", "indicator-species"],
    ),
    "clownfish": SpeciesInfo(
        facts=[
            "All clownfish begin life as males; the dominant individual in a group can become female.",
            "A mucus coating protects them from the stinging tentacles of their host anemone.",
            "They communicate through a series of popping and clicking sounds.",
            "Clownfish actively defend their anemone against intruders much larger than themselves.",
            "The symbiosis benefits the anemone too — clownfish chase away polyp-eating fish.",
        ],
        habitat="Shallow lagoons and reefs in the Pacific and Indian Oceans (1–15 m)",
        conservation="Least Concern",
        diet="Algae, zooplankton, small invertebrates (omnivore)",
        max_size_cm=11,
        tags=["reef", "symbiotic", "popular"],
    ),
    "moorish-idol": SpeciesInfo(
        facts=[
            "The moorish idol is the sole member of family Zanclidae — it has no close relatives.",
            "Its elongated dorsal filament can extend well beyond the length of its body.",
            "Despite being a popular aquarium fish, it rarely survives in captivity.",
            "In Hawaiian tradition it is called 'kihikihi' (curves) and is considered a bringer of good luck.",
            "They feed by probing coral crevices with their long snout for sponges and invertebrates.",
        ],
        habitat="Tropical Indo-Pacific and eastern Pacific reefs (3–180 m)",
        conservation="Least Concern",
        diet="Sponges, tunicates, small invertebrates",
        max_size_cm=23,
        tags=["reef", "iconic"],
    ),
    "neon-tetra": SpeciesInfo(
        facts=[
            "Neon tetras can switch off their iridescent stripe at night to avoid predators.",
            "They school in groups of hundreds in the wild — small groups in aquaria cause stress.",
            "First described from the blackwater Amazon tributaries of Peru in 1934.",
            "Their vivid colours come from specialised light-refracting cells called iridophores.",
            "They are one of the most exported ornamental fish globally — ~1.5 million sold per month.",
        ],
        habitat="Blackwater tributaries of the Amazon basin, South America",
        conservation="Least Concern",
        diet="Micro-invertebrates, algae, small worms (omnivore)",
        max_size_cm=4,
        tags=["freshwater", "schooling", "aquarium"],
    ),
    "ribboned-sweetlips": SpeciesInfo(
        facts=[
            "Juveniles bear bold black-and-white stripes that bear no resemblance to the spotted adult.",
            "They grunt audibly when stressed or handled — hence 'sweetlips' (grunt fish family).",
            "Adults hunt nocturnally, hovering motionless near reef structures by day.",
            "Their thick, fleshy lips give the genus — and the family Haemulidae — their common name.",
            "Young ribboned sweetlips perform an exaggerated wriggling swim thought to mimic toxic flatworms.",
        ],
        habitat="Red Sea through the Western Pacific, coral and rubble reefs (1–35 m)",
        conservation="Least Concern",
        diet="Benthic invertebrates, small fish (carnivore)",
        max_size_cm=45,
        tags=["reef", "nocturnal"],
    ),
    "yellow-tang": SpeciesInfo(
        facts=[
            "Yellow tangs can live more than 30 years in the wild.",
            "They are almost exclusively found in Hawaiian waters — a unique endemic species.",
            "At night their vivid yellow fades to pale grey with a white lateral stripe.",
            "Captive breeding programmes have reduced pressure on wild Hawaiian populations.",
            "Like all surgeonfish, they have a scalpel-like spine on each side of the tail.",
        ],
        habitat="Hawaiian coral reefs, primarily the Big Island (2–46 m)",
        conservation="Near Threatened",
        diet="Filamentous algae (herbivore)",
        max_size_cm=20,
        tags=["reef", "herbivore", "endemic", "near-threatened"],
    ),
}


# ── Serialisation helper ───────────────────────────────────────────────────────

def get_species_card(raw_name: str) -> dict:
    """
    Build a JSON-serialisable species card for API responses.

    Picks one random fact per call so repeated queries feel fresh.
    Returns a 'known=False' fallback card for unrecognised species.
    """
    key  = raw_name.lower().replace(" ", "-")
    info = SPECIES_DB.get(key)

    if info:
        return {
            "name":        raw_name,
            "fact":        random.choice(info.facts),
            "habitat":     info.habitat,
            "conservation": info.conservation,
            "diet":        info.diet,
            "max_size_cm": info.max_size_cm,
            "tags":        info.tags,
            "known":       True,
        }

    return {
        "name":        raw_name,
        "fact":        "Interesting facts about this species are being researched.",
        "habitat":     "Not available",
        "conservation": "Unknown",
        "diet":        "Unknown",
        "max_size_cm": None,
        "tags":        [],
        "known":       False,
    }