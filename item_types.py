"""Deterministic item classification without a pre-authored name catalog.

The encyclopedia defines stable base types and rarity rules. A story or player
may give an owned item any name; that name never creates powers or rarity.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA = Path(__file__).parent / "data"
FALLBACKS = {
    "Weapons": "weapon.other", "Armor & protection": "armor.unspecified",
    "Clothing & adornment": "clothing.general", "Tools & everyday goods": "tool.general",
    "Travel gear & transport": "travel.general", "Food & drink": "food.general",
    "Medicine & alchemy": "medicine.general", "Materials & trade": "material.general",
    "Treasures & relics": "treasure.general",
}


@lru_cache(maxsize=1)
def rarity_contexts() -> dict[str, Any]:
    return json.loads((DATA / "item_rarity_contexts.json").read_text(encoding="utf-8"))


def rarity_guide_for(entry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    context = rarity_contexts()[entry["category"]]
    forms: list[str] = []
    for signal in entry.get("signals", []):
        if signal not in forms:
            forms.append(signal)
        if len(forms) == 3:
            break
    while len(forms) < 3:
        forms.append(entry["label"])
    substitutions = {"a": forms[0], "b": forms[1], "c": forms[2], "label": entry["label"]}
    return {
        rarity_id: {
            "description": profile["description"],
            "examples": [example.format(**substitutions) for example in profile["examples"]],
        }
        for rarity_id, profile in context.items()
    }


@lru_cache(maxsize=1)
def item_types() -> list[dict[str, Any]]:
    entries = json.loads((DATA / "item_types.json").read_text(encoding="utf-8"))
    # References belonged to the retired name catalog. Hide the legacy field.
    cleaned = [{key: value for key, value in entry.items() if key != "reference"} for entry in entries]
    return [{**entry, "rarity_guide": rarity_guide_for(entry)} for entry in cleaned]


@lru_cache(maxsize=1)
def item_rarities() -> list[dict[str, Any]]:
    return json.loads((DATA / "item_rarities.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def type_rules() -> dict[str, Any]:
    return json.loads((DATA / "item_type_rules.json").read_text(encoding="utf-8"))


def baseline_for(base_type_id: str) -> dict[str, str]:
    entry = next((item for item in item_types() if item["id"] == base_type_id), None)
    if not entry:
        return {}
    return type_rules()["types"].get(base_type_id, type_rules()["categories"][entry["category"]])


@lru_cache(maxsize=1)
def catalog_index() -> dict[str, Any]:
    """Compatibility name for the category-and-rarity encyclopedia index."""
    types = [{**entry, "baseline": baseline_for(entry["id"])} for entry in item_types()]
    return {"types": types, "rarities": item_rarities(), "examples": {}}


def classify_item(source: dict[str, Any]) -> dict[str, Any]:
    name = str(source.get("name", "")).strip()
    description = str(source.get("description", "")).strip()
    by_id = {entry["id"]: entry for entry in item_types()}

    selected = str(source.get("base_type_id", "")).strip()
    if selected and selected not in by_id:
        raise ValueError("unknown base item type")

    rarity_by_id = {entry["id"]: entry for entry in item_rarities()}
    selected_rarity = str(source.get("rarity", "")).strip()
    if selected_rarity and selected_rarity not in rarity_by_id:
        raise ValueError("unknown item rarity")
    rarity_id = selected_rarity or "common"
    rarity = rarity_by_id[rarity_id]
    rarity_fields = {
        "rarity": rarity_id,
        "rarity_label": rarity["label"],
        "rarity_description": rarity["description"],
        "rarity_source": "selected" if selected_rarity else "default",
    }

    if selected:
        chosen = by_id[selected]
        return {
            "base_type_id": selected,
            "base_type_label": chosen["label"],
            "catalog_section": chosen["category"],
            "reference_title": None,
            "source": "selected",
            "requires_review": False,
            **rarity_fields,
        }

    candidates: list[tuple[int, dict[str, Any]]] = []
    for entry in item_types():
        for signal in entry["signals"]:
            broad_penalty = 90 if entry["id"] in FALLBACKS.values() else 0
            if signal in name:
                candidates.append((100 + len(signal) * 10 - broad_penalty, entry))
            elif signal in description:
                candidates.append((50 + len(signal) * 10 - broad_penalty, entry))
    if candidates:
        _, chosen = max(candidates, key=lambda pair: pair[0])
        return {
            "base_type_id": chosen["id"],
            "base_type_label": chosen["label"],
            "catalog_section": chosen["category"],
            "reference_title": None,
            "source": "inferred",
            "requires_review": chosen["id"] in FALLBACKS.values(),
            **rarity_fields,
        }

    return {
        "base_type_id": None,
        "base_type_label": "",
        "catalog_section": None,
        "reference_title": None,
        "source": "unresolved",
        "requires_review": True,
        **rarity_fields,
    }
