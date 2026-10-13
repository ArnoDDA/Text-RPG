#!/usr/bin/env python3
"""Import versioned fixed World Bible sources into a local save database.

Canon is identified by a stable source_id rather than player-facing title or
category. This makes later wording and navigation changes safe to re-import.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data" / "world_bible_manifest.json"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import engine  # noqa: E402  # The importer must use the engine's migrations.


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def terms(title: str) -> list[str]:
    """Small deterministic trigger set; the engine can refine it afterwards."""
    separators = "、，,：:（）()—-与之的和"
    chunks = [title]
    current = ""
    for char in title:
        if char in separators:
            if current:
                chunks.append(current)
            current = ""
        else:
            current += char
    if current:
        chunks.append(current)
    suffixes = ("共和国", "自由领", "诸侯领", "城邦同盟", "绿洲联邦", "风原盟约", "王国", "联邦", "同盟", "议约", "议会", "协会", "圣约", "守望团", "城市", "生活", "旅行", "阶层")
    values: list[str] = []
    for item in chunks:
        item = item.strip()
        if item and item not in values:
            values.append(item)
        for suffix in suffixes:
            if item.endswith(suffix) and len(item) > len(suffix):
                short = item[:-len(suffix)]
                if short not in values:
                    values.append(short)
    return values[:8]


def source_paths(args: argparse.Namespace) -> list[Path]:
    if not args.all:
        return [Path(args.source).resolve()]
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    if manifest.get("version") != 1 or not isinstance(manifest.get("sources"), list):
        raise ValueError("World Bible manifest must contain version 1 and a sources array")
    data_dir = (ROOT / "data").resolve()
    result: list[Path] = []
    for item in manifest["sources"]:
        relative_path = item.get("path") if isinstance(item, dict) else None
        if not isinstance(relative_path, str) or not relative_path:
            raise ValueError("Each World Bible manifest source needs a path")
        path = (data_dir / relative_path).resolve()
        if data_dir not in path.parents or path.suffix != ".json":
            raise ValueError(f"Invalid World Bible source path: {relative_path}")
        if not path.is_file():
            raise ValueError(f"World Bible source is missing: {relative_path}")
        result.append(path)
    return result


def source_entries(paths: list[Path]) -> list[dict]:
    entries: list[dict] = []
    seen_source_ids: set[str] = set()
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, list):
            raise ValueError(f"World Bible source must be an array: {path.name}")
        for entry in document:
            if not isinstance(entry, dict):
                raise ValueError(f"World Bible entry must be an object: {path.name}")
            source_id = entry.get("source_id")
            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(f"World Bible entry needs a stable source_id: {path.name}")
            if source_id in seen_source_ids:
                raise ValueError(f"Duplicate World Bible source_id: {source_id}")
            seen_source_ids.add(source_id)
            entries.append(entry)
    return entries


RECORD_TYPES = {
    "World overview": "concept",
    "Continents, seas & underworlds": "place",
    "Nations, city-states & powers": "faction_or_settlement",
    "Peoples & bloodlines": "people",
    "Gods, celestials, fiends & otherworld": "cosmic_entity",
    "Historical ages & major events": "historical_event",
    "Magic, professions & organizations": "institution_or_practice",
    "Magic rules": "rule",
    "Magic & rituals": "spell",
    "Monsters, dragons & supernatural phenomena": "creature_or_phenomenon",
    "Attributes & rules": "rule",
    "Abilities & techniques": "ability_rule",
    "Items & equipment": "item_rule",
}


def structured_record(entry: dict) -> dict:
    """Return a stable database record while preserving the readable article.

    The article is the narrative-facing description. These fields are the
    catalogue-facing identity and retrieval metadata, so callers can treat
    the World Bible as a small read-only database instead of parsing prose.
    """
    supplied = entry.get("record")
    record = dict(supplied) if isinstance(supplied, dict) else {}
    keys = entry.get("keys") if isinstance(entry.get("keys"), list) else []
    paragraphs = [part.strip() for part in str(entry.get("content", "")).split("\n\n") if part.strip()]
    source_id = str(entry.get("source_id", "")).strip()
    category = str(entry.get("category", "General")).strip() or "General"
    content = str(entry.get("content", ""))
    record.setdefault("record_type", RECORD_TYPES.get(entry.get("category"), "reference"))
    record.setdefault("canonical_name", entry.get("title", ""))
    record.setdefault("aliases", keys[:12])
    record.setdefault("summary", paragraphs[0][:360] if paragraphs else "")
    record.setdefault("status", "established")
    record.setdefault("tags", [category])
    record.setdefault("relations", [])
    record.setdefault("record_id", source_id)
    record.setdefault("source_id", source_id)
    record.setdefault("source_category", category)
    record.setdefault("retrieval", {
        "primary_keys": keys,
        "secondary_keys": entry.get("secondary_keys", []),
        "match_mode": "any_primary_key",
    })
    fields = record.setdefault("fields", {})
    if not isinstance(fields, dict):
        fields = {}
        record["fields"] = fields
    fields.setdefault("article_chars", len(content))
    fields.setdefault("source_category", category)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--universe", default="shattered_realms")
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--source", help="Import one World Bible JSON source")
    input_group.add_argument("--all", action="store_true", help="Import every source from the manifest")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="Manifest used with --all")
    args = parser.parse_args()
    entries = source_entries(source_paths(args))

    # Do not open an un-migrated save directly. All database tools share the
    # engine connection so newly added schema columns are present everywhere.
    db = engine.connect(args.db)
    with db:
        exists = db.execute("SELECT id FROM universes WHERE id=?", (args.universe,)).fetchone()
        if not exists:
            raise SystemExit(f"Universe does not exist: {args.universe}")
        created = updated = 0
        for position, entry in enumerate(entries, start=1):
            source_id = entry["source_id"].strip()
            title = entry["title"].strip()
            category = entry["category"].strip()
            content = entry["content"].strip()
            keys = entry.get("keys") or terms(title)
            keys_json = json.dumps(keys, ensure_ascii=False)
            record_json = json.dumps(structured_record(entry), ensure_ascii=False, separators=(",", ":"))
            row = db.execute(
                "SELECT id FROM universe_lore_entries WHERE universe_id=? AND source_id=?",
                (args.universe, source_id),
            ).fetchone()
            # One-time compatibility path for canon imported before source_id
            # existed. A successful update writes the permanent identity.
            if not row:
                row = db.execute(
                    """SELECT id FROM universe_lore_entries
                       WHERE universe_id=? AND category=? AND title=? AND source_id IS NULL""",
                    (args.universe, category, title),
                ).fetchone()
            if not row:
                row = db.execute(
                    "SELECT id FROM universe_lore_entries WHERE universe_id=? AND title=? AND source_id IS NULL",
                    (args.universe, title),
                ).fetchone()
            # Older magic catalogues used the insertion position only during a
            # title rename. New sources never depend on this fallback.
            if not row and entry.get("rename_by_order"):
                row = db.execute(
                    """SELECT id FROM universe_lore_entries
                       WHERE universe_id=? AND category=? AND insertion_order=? AND source_id IS NULL""",
                    (args.universe, category, int(entry.get("order", position))),
                ).fetchone()
            insertion_order = int(entry.get("order", position))
            priority = int(entry.get("priority", 66))
            params = (source_id, title, category, content, keys_json, keys_json, record_json, 1, 1, insertion_order, priority, row["id"] if row else "")
            if row:
                db.execute(
                    """UPDATE universe_lore_entries SET source_id=?, title=?, category=?, content=?, keys_json=?, secondary_keys_json=?,
                       record_json=?, selective=?, enabled=?, insertion_order=?, priority=?
                       WHERE id=?""",
                    params,
                )
                updated += 1
            else:
                db.execute(
                    """INSERT INTO universe_lore_entries
                       (id, universe_id, source_id, title, content, category, visibility, keys_json, secondary_keys_json,
                        record_json, enabled, constant, selective, case_sensitive, insertion_order, priority, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, 'public', ?, ?, ?, 1, 0, 1, 0, ?, ?, ?)""",
                    (f"{args.universe}:lore:{uuid4().hex}", args.universe, source_id, title, content, category,
                     keys_json, keys_json, record_json, insertion_order, priority, now()),
                )
                created += 1
    print(f"World Bible import complete: {created} created, {updated} updated, {len(entries)} total.")


if __name__ == "__main__":
    main()
