"""Stable ability definitions and branch-local player ability views."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


DATA = Path(__file__).parent / "data" / "ability_catalog.json"
LOAD_KEYS = ("physical", "focus", "mystic")
STABLE_LOAD = "稳定"


@lru_cache(maxsize=1)
def ability_catalog() -> dict[str, Any]:
    catalog = json.loads(DATA.read_text(encoding="utf-8"))
    ability_ids: set[str] = set()
    forms = {entry["id"] for entry in catalog["forms"]}
    sources = set(catalog["sources"])
    tags = set(catalog["function_tags"])
    required = {
        "id", "name", "aliases", "form", "source", "function_tags", "trigger_terms",
        "known_effect", "limits", "requirements", "primary_attributes", "minimum_scale",
        "scale_cap", "activation", "cost", "range", "duration", "counters", "visibility",
    }
    for ability in catalog["abilities"]:
        missing = required - set(ability)
        if missing:
            raise ValueError(f"ability {ability.get('id', '<unknown>')} is missing: {sorted(missing)}")
        if ability["id"] in ability_ids:
            raise ValueError(f"duplicate ability id: {ability['id']}")
        if ability["form"] not in forms or ability["source"] not in sources:
            raise ValueError(f"ability {ability['id']} has an unknown form or source")
        if not set(ability["function_tags"]).issubset(tags):
            raise ValueError(f"ability {ability['id']} has an unknown function tag")
        if not 1 <= int(ability["minimum_scale"]) <= int(ability["scale_cap"]):
            raise ValueError(f"ability {ability['id']} has an invalid scale range")
        ability_ids.add(ability["id"])
    return catalog


def ability_by_id(ability_id: str) -> dict[str, Any] | None:
    return next((entry for entry in ability_catalog()["abilities"] if entry["id"] == ability_id), None)


def abilities_from_player_state(player_state: dict[str, Any] | None) -> dict[str, Any]:
    state = player_state if isinstance(player_state, dict) else {}
    mechanics = state.get("mechanics", {})
    mechanics = mechanics if isinstance(mechanics, dict) else {}
    mastery_ids = {entry["id"] for entry in ability_catalog()["mastery"]}
    mastery_labels = {entry["id"]: entry["label"] for entry in ability_catalog()["mastery"]}
    owned: list[dict[str, Any]] = []
    seen: set[str] = set()
    raw_abilities = mechanics.get("abilities", [])
    if not isinstance(raw_abilities, list):
        raw_abilities = []
    for record in raw_abilities:
        source = {"id": record} if isinstance(record, str) else record
        if not isinstance(source, dict):
            continue
        ability_id = str(source.get("id", "")).strip()
        base = ability_by_id(ability_id)
        if not base or ability_id in seen:
            continue
        mastery = str(source.get("mastery", "novice"))
        if mastery not in mastery_ids:
            mastery = "novice"
        owned.append({
            **base,
            "mastery": mastery,
            "mastery_label": mastery_labels[mastery],
            "available": source.get("available", True) is not False,
            "source_detail": str(source.get("source_detail", "")).strip()[:500],
        })
        seen.add(ability_id)

    raw_loads = mechanics.get("loads", {})
    if not isinstance(raw_loads, dict):
        resources = mechanics.get("resources", {})
        raw_loads = resources.get("loads", {}) if isinstance(resources, dict) else {}
    loads: dict[str, str] = {}
    for key in LOAD_KEYS:
        valid_stages = ability_catalog()["loads"][key]["stages"]
        value = str(raw_loads.get(key, STABLE_LOAD))
        loads[key] = value if value in valid_stages else STABLE_LOAD

    maintained = mechanics.get("maintained", [])
    if not isinstance(maintained, list):
        maintained = []
    maintained_ids = [str(value) for value in maintained if str(value) in seen]
    specialties = mechanics.get("specialties", [])
    if not isinstance(specialties, (list, dict)):
        specialties = []
    return {"abilities": owned, "specialties": specialties, "loads": loads, "maintained": maintained_ids}


def relevant_abilities(ability_state: dict[str, Any], action: str, limit: int = 3) -> list[dict[str, Any]]:
    """Select only abilities that can materially constrain this action."""
    action_text = str(action).casefold()
    maintained = set(ability_state.get("maintained", []))
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for index, ability in enumerate(ability_state.get("abilities", [])):
        if not ability.get("available", True):
            continue
        score = 1000 if ability["id"] in maintained else 0
        for phrase in [ability["name"], *ability.get("aliases", [])]:
            if str(phrase).casefold() in action_text:
                score = max(score, 300 + len(str(phrase)))
        for term in ability.get("trigger_terms", []):
            if str(term).casefold() in action_text:
                score += 30 + len(str(term))
        for tag in ability.get("function_tags", []):
            if len(str(tag)) > 2 and str(tag).casefold() in action_text:
                score += 10
        if score:
            scored.append((score, -index, ability))
    scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [item[2] for item in scored[:max(0, limit)]]
