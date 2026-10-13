#!/usr/bin/env python3
"""A local, Codex-first memory ledger for long-running solo RPG campaigns.

This program deliberately does not call an LLM.  Codex is the narrator; this
ledger owns durable facts, subjective beliefs, story threads, and timelines.
It uses only Python's standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
from uuid import uuid4

from abilities import ability_catalog, abilities_from_player_state, relevant_abilities
from item_types import baseline_for, catalog_index, classify_item, item_rarities, item_types


# Full state anchors make arbitrary rollback cheap. Between anchors we retain
# only the rows that changed, so a campaign no longer writes its entire state
# for every ordinary turn.
SNAPSHOT_INTERVAL = 25
STATE_TABLES = ("entity_states", "facts", "beliefs", "story_threads")
NPC_TYPES = {"npc", "companion"}
NPC_STATUSES = {"party", "core", "known", "away", "archived", "deceased"}
MAX_PARTY_CONTEXT = 4
MAX_CAST_CONTEXT = 8
NPC_MEMORY_LIMITS = {
    "party": 30,
    "core": 30,
    "pinned": 18,
    "recurring": 18,
    "background": 12,
}
CURRENT_SCHEMA_VERSION = 10
LOCATION_PROFILES = json.loads((Path(__file__).parent / "data" / "location_profiles.json").read_text(encoding="utf-8"))
ATTRIBUTE_KEYS = ("physique", "agility", "perception", "intellect", "will", "charisma", "mystic_power")
INJURY_STAGES = ("minor", "serious", "critical")
LOAD_STAGES = {
    key: tuple(ability_catalog()["loads"][key]["stages"])
    for key in ("physical", "focus", "mystic")
}
TRADE_KINDS = {"buy", "sell", "reward", "payment"}
MAX_RESOURCE_BALANCE = 2_000_000_000
MAX_TRANSACTION_HISTORY = 200
LOCATION_TYPES = {"region", "settlement", "district", "street", "building", "room", "wilderness", "landmark", "other"}
LOCATION_STATUSES = {"active", "changed", "closed", "damaged", "destroyed", "inaccessible"}
ROUTE_STATUSES = {"open", "uncertain", "blocked", "dangerous", "closed"}
MAX_PLACE_CONTEXT = 6


def canonical_location(name: str) -> str:
    clean = re.sub(r"\s*·\s*", "·", name.strip())
    for established in LOCATION_PROFILES["exact"]:
        if re.sub(r"\s*·\s*", "·", established) == clean:
            return established
    return name.strip()


def location_profile(name: str) -> dict[str, str]:
    """Return a small narrative baseline, never a mandatory event or world fact."""
    name = canonical_location(name)
    exact = LOCATION_PROFILES["exact"].get(name)
    if exact:
        return {"source": "established_start", "label": name, **exact}
    for archetype in LOCATION_PROFILES["archetypes"]:
        if any(keyword in name for keyword in archetype["keywords"]):
            return {key: value for key, value in archetype.items() if key != "keywords"} | {"source": "name_hint"}
    return {"source": "unclassified", "label": "尚未归类", "mood": "由当前情境决定", "focus": "以已发生的事和玩家行动为先", "danger": "不要仅凭地名预设安全或危险"}


def stable_record_id(value: Any) -> str:
    candidate = str(value or "").strip().lower()
    return candidate if re.fullmatch(r"[a-z0-9_]+", candidate) else ""


def generated_location_id(name: str, parent_id: str = "") -> str:
    """Create a deterministic fallback when the narrator did not supply an id."""
    identity = f"{parent_id}\n{canonical_location(name)}".casefold()
    return f"location_{hashlib.sha256(identity.encode('utf-8')).hexdigest()[:16]}"


def compact_text(value: Any, limit: int) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()[:limit]


def compact_text_list(value: Any, limit: int = 8, item_limit: int = 180) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = compact_text(item, item_limit)
        key = text.casefold()
        if text and key not in seen:
            result.append(text)
            seen.add(key)
        if len(result) == limit:
            break
    return result


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS campaigns (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    active_branch_id TEXT,
    created_at TEXT NOT NULL
);

-- A universe is the shared, high-level setting. Campaigns are individual
-- playable worlds inside it, each with their own protagonist and timelines.
CREATE TABLE IF NOT EXISTS universes (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_universes (
    campaign_id TEXT PRIMARY KEY REFERENCES campaigns(id),
    universe_id TEXT NOT NULL REFERENCES universes(id)
);

CREATE TABLE IF NOT EXISTS app_state (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);

-- Every structural upgrade is recorded here as well as in PRAGMA user_version.
-- This makes upgrades inspectable and prevents a newer save from being opened
-- by an older build that cannot understand it.
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS campaign_starts (
    campaign_id TEXT PRIMARY KEY REFERENCES campaigns(id),
    player_name TEXT NOT NULL,
    player_concept TEXT NOT NULL,
    starting_location TEXT NOT NULL,
    character_json TEXT NOT NULL DEFAULT '{}',
    setup_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS branches (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(id),
    name TEXT NOT NULL,
    parent_branch_id TEXT REFERENCES branches(id),
    forked_from_turn_id TEXT,
    base_turn_number INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(campaign_id, name)
);

CREATE TABLE IF NOT EXISTS entities (
    campaign_id TEXT NOT NULL REFERENCES campaigns(id),
    id TEXT NOT NULL,
    type TEXT NOT NULL,
    name TEXT NOT NULL,
    profile_json TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (campaign_id, id)
);

CREATE TABLE IF NOT EXISTS entity_states (
    branch_id TEXT NOT NULL REFERENCES branches(id),
    entity_id TEXT NOT NULL,
    state_json TEXT NOT NULL,
    updated_turn INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (branch_id, entity_id)
);

CREATE TABLE IF NOT EXISTS turns (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL REFERENCES branches(id),
    turn_number INTEGER NOT NULL,
    game_time TEXT,
    player_action TEXT NOT NULL,
    narration TEXT NOT NULL,
    scene_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE(branch_id, turn_number)
);

CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL REFERENCES branches(id),
    turn_id TEXT NOT NULL REFERENCES turns(id),
    kind TEXT NOT NULL,
    description TEXT NOT NULL,
    truth_status TEXT NOT NULL,
    visibility TEXT NOT NULL,
    witnesses_json TEXT NOT NULL DEFAULT '[]',
    related_entities_json TEXT NOT NULL DEFAULT '[]',
    tags_json TEXT NOT NULL DEFAULT '[]',
    importance INTEGER NOT NULL DEFAULT 5,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS facts (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL REFERENCES branches(id),
    created_turn INTEGER NOT NULL,
    subject_id TEXT,
    predicate TEXT NOT NULL,
    value_json TEXT NOT NULL,
    text TEXT NOT NULL,
    truth_status TEXT NOT NULL,
    visibility TEXT NOT NULL,
    witnesses_json TEXT NOT NULL DEFAULT '[]',
    tags_json TEXT NOT NULL DEFAULT '[]',
    importance INTEGER NOT NULL DEFAULT 5,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS beliefs (
    id TEXT PRIMARY KEY,
    branch_id TEXT NOT NULL REFERENCES branches(id),
    actor_id TEXT NOT NULL,
    created_turn INTEGER NOT NULL,
    text TEXT NOT NULL,
    truth_status TEXT NOT NULL,
    source_event_id TEXT,
    tags_json TEXT NOT NULL DEFAULT '[]',
    importance INTEGER NOT NULL DEFAULT 5,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS story_threads (
    branch_id TEXT NOT NULL REFERENCES branches(id),
    id TEXT NOT NULL,
    kind TEXT NOT NULL,
    title TEXT NOT NULL,
    status TEXT NOT NULL,
    stakes TEXT NOT NULL DEFAULT '',
    summary TEXT NOT NULL DEFAULT '',
    related_entities_json TEXT NOT NULL DEFAULT '[]',
    urgency INTEGER NOT NULL DEFAULT 5,
    last_advanced_turn INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (branch_id, id)
);

-- Worldbook entries are campaign-level authored canon. They are deliberately
-- outside branch snapshots: a setting rule is shared by every possible
-- timeline unless the player explicitly edits or removes it.
CREATE TABLE IF NOT EXISTS lore_entries (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(id),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    keys_json TEXT NOT NULL DEFAULT '[]',
    secondary_keys_json TEXT NOT NULL DEFAULT '[]',
    enabled INTEGER NOT NULL DEFAULT 1,
    constant INTEGER NOT NULL DEFAULT 0,
    selective INTEGER NOT NULL DEFAULT 0,
    case_sensitive INTEGER NOT NULL DEFAULT 0,
    insertion_order INTEGER NOT NULL DEFAULT 100,
    priority INTEGER NOT NULL DEFAULT 50,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS universe_lore_entries (
    id TEXT PRIMARY KEY,
    universe_id TEXT NOT NULL REFERENCES universes(id),
    source_id TEXT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'General',
    visibility TEXT NOT NULL DEFAULT 'public',
    system_entry INTEGER NOT NULL DEFAULT 0,
    keys_json TEXT NOT NULL DEFAULT '[]',
    secondary_keys_json TEXT NOT NULL DEFAULT '[]',
    record_json TEXT NOT NULL DEFAULT '{}',
    enabled INTEGER NOT NULL DEFAULT 1,
    constant INTEGER NOT NULL DEFAULT 0,
    selective INTEGER NOT NULL DEFAULT 0,
    case_sensitive INTEGER NOT NULL DEFAULT 0,
    insertion_order INTEGER NOT NULL DEFAULT 100,
    priority INTEGER NOT NULL DEFAULT 50,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS snapshots (
    branch_id TEXT NOT NULL REFERENCES branches(id),
    turn_id TEXT NOT NULL REFERENCES turns(id),
    turn_number INTEGER NOT NULL,
    snapshot_json TEXT NOT NULL,
    PRIMARY KEY (branch_id, turn_id)
);

-- The opening state (or state at a fork point) has no local turn to reference,
-- so it lives separately from the turn-backed snapshot table.
CREATE TABLE IF NOT EXISTS state_roots (
    branch_id TEXT PRIMARY KEY REFERENCES branches(id),
    turn_number INTEGER NOT NULL,
    snapshot_json TEXT NOT NULL
);

-- A compact journal of changes after each turn. Together with the nearest
-- earlier snapshot it reconstructs the exact state at any turn.
CREATE TABLE IF NOT EXISTS state_deltas (
    branch_id TEXT NOT NULL REFERENCES branches(id),
    turn_id TEXT NOT NULL REFERENCES turns(id),
    turn_number INTEGER NOT NULL,
    delta_json TEXT NOT NULL,
    PRIMARY KEY (branch_id, turn_id)
);

-- A named save is a pointer to an existing immutable turn snapshot. It never
-- duplicates the campaign state, so keeping many manual saves is inexpensive.
CREATE TABLE IF NOT EXISTS checkpoints (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(id),
    branch_id TEXT NOT NULL REFERENCES branches(id),
    turn_id TEXT NOT NULL REFERENCES turns(id),
    turn_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(campaign_id, name)
);

-- Chapter summaries are reviewable reading aids. They never replace turns or
-- enter narrator context, and each keeps a hash of its exact source turns.
CREATE TABLE IF NOT EXISTS chapter_summaries (
    id TEXT PRIMARY KEY,
    campaign_id TEXT NOT NULL REFERENCES campaigns(id),
    branch_id TEXT NOT NULL REFERENCES branches(id),
    title TEXT NOT NULL,
    start_turn INTEGER NOT NULL,
    end_turn INTEGER NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    source_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(branch_id, start_turn, end_turn)
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slug(value: str) -> str:
    clean = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    if not clean:
        raise ValueError("id must contain letters or numbers")
    return clean


def load_json(path: str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("manifest must be a JSON object")
    return value


def connect(path: str) -> sqlite3.Connection:
    save_path = Path(path).expanduser().resolve()
    save_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        os.chmod(save_path.parent, 0o700)
    except OSError:
        pass
    db = sqlite3.connect(str(save_path))
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    apply_schema_migrations(db)
    ensure_default_universe(db)
    db.commit()
    # SQLite data is not application-encrypted. Restrict ordinary local file
    # access; FileVault or an equivalent OS volume encryption remains the
    # protection for data at rest.
    for candidate in (save_path, Path(f"{save_path}-wal"), Path(f"{save_path}-shm")):
        if candidate.exists():
            try:
                os.chmod(candidate, 0o600)
            except OSError:
                pass
    return db


def migration_1_initial_ledger(db: sqlite3.Connection) -> None:
    """Mark the original durable ledger schema as the migration baseline."""


def migration_2_universe_lore_metadata(db: sqlite3.Connection) -> None:
    """Add the metadata used by the browsable shared encyclopedia."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(universe_lore_entries)")}
    additions = (
        ("category", "category TEXT NOT NULL DEFAULT 'General'"),
        ("visibility", "visibility TEXT NOT NULL DEFAULT 'public'"),
        ("system_entry", "system_entry INTEGER NOT NULL DEFAULT 0"),
    )
    for name, definition in additions:
        if name not in columns:
            db.execute(f"ALTER TABLE universe_lore_entries ADD COLUMN {definition}")


def migration_3_character_profiles(db: sqlite3.Connection) -> None:
    """Preserve the structured protagonist profile for old campaign starts."""
    start_columns = {row["name"] for row in db.execute("PRAGMA table_info(campaign_starts)")}
    if "character_json" not in start_columns:
        db.execute("ALTER TABLE campaign_starts ADD COLUMN character_json TEXT NOT NULL DEFAULT '{}'")


def migration_4_reviewable_chapter_summaries(db: sqlite3.Connection) -> None:
    """Add source-linked, player-reviewable long-story summaries."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS chapter_summaries (
            id TEXT PRIMARY KEY,
            campaign_id TEXT NOT NULL REFERENCES campaigns(id),
            branch_id TEXT NOT NULL REFERENCES branches(id),
            title TEXT NOT NULL,
            start_turn INTEGER NOT NULL,
            end_turn INTEGER NOT NULL,
            summary TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            source_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(branch_id, start_turn, end_turn)
        )
    """)


def migration_5_recoverable_world_removal(db: sqlite3.Connection) -> None:
    """Keep deleted worlds restorable without touching their timelines."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(campaigns)")}
    if "trashed_at" not in columns:
        db.execute("ALTER TABLE campaigns ADD COLUMN trashed_at TEXT")


def migration_6_remove_retired_item_data(db: sqlite3.Connection) -> None:
    """Remove item-overview pages and empty inventory fields superseded by possessions."""
    retired_overviews = (
        ("Weapons", "铁剑与常见单手刃"), ("Weapons", "矛、斧与长柄兵器"),
        ("Weapons", "弓弩与投射器具"), ("Armor & protection", "盾牌与随身防护"),
        ("Armor & protection", "软甲、锁甲与重甲"), ("Clothing & adornment", "日常衣着与礼仪服饰"),
        ("Clothing & adornment", "披风、靴与旅行服"), ("Clothing & adornment", "首饰、徽记与印章"),
        ("Tools & everyday goods", "火种、灯具与照明"), ("Tools & everyday goods", "绳索、锁具与修补工具"),
        ("Tools & everyday goods", "书籍、地图与文书"), ("Travel gear & transport", "背包与宿营用品"),
        ("Travel gear & transport", "车、舟与船舶"), ("Food & drink", "粮食、面饼与日常餐食"),
        ("Food & drink", "干粮、腌制品与远行补给"), ("Food & drink", "饮水、茶与酒"),
        ("Medicine & alchemy", "绷带、药草与常用医具"), ("Medicine & alchemy", "药剂与炼金制品"),
        ("Materials & trade", "木、石、金属与织物"), ("Materials & trade", "金银铜币与信用凭据"),
        ("Materials & trade", "香料、盐与常见贸易货物"), ("Treasures & relics", "宝石与工艺珍品"),
        ("Treasures & relics", "遗物与神器的收录原则"),
    )
    db.executemany("DELETE FROM universe_lore_entries WHERE category=? AND title=?", retired_overviews)

    def clean_state_json(raw: str) -> str:
        state = json.loads(raw)
        if state.get("inventory") in (None, []):
            state.pop("inventory", None)
        return json.dumps(state, ensure_ascii=False)

    def clean_snapshot_json(raw: str) -> str:
        document = json.loads(raw)
        for row in document.get("entity_states", []):
            if isinstance(row, dict) and isinstance(row.get("state_json"), str):
                row["state_json"] = clean_state_json(row["state_json"])
        changes = document.get("entity_states", {})
        if isinstance(changes, dict):
            for row in changes.get("upserts", []):
                if isinstance(row, dict) and isinstance(row.get("state_json"), str):
                    row["state_json"] = clean_state_json(row["state_json"])
        return json.dumps(document, ensure_ascii=False)

    for row in db.execute("SELECT branch_id, entity_id, state_json FROM entity_states").fetchall():
        cleaned = clean_state_json(row["state_json"])
        if cleaned != row["state_json"]:
            db.execute("UPDATE entity_states SET state_json=? WHERE branch_id=? AND entity_id=?",
                       (cleaned, row["branch_id"], row["entity_id"]))
    for table in ("state_roots", "snapshots"):
        key_columns = "branch_id" if table == "state_roots" else "branch_id, turn_id"
        for row in db.execute(f"SELECT {key_columns}, snapshot_json FROM {table}").fetchall():
            cleaned = clean_snapshot_json(row["snapshot_json"])
            if cleaned == row["snapshot_json"]:
                continue
            if table == "state_roots":
                db.execute("UPDATE state_roots SET snapshot_json=? WHERE branch_id=?", (cleaned, row["branch_id"]))
            else:
                db.execute("UPDATE snapshots SET snapshot_json=? WHERE branch_id=? AND turn_id=?",
                           (cleaned, row["branch_id"], row["turn_id"]))
    for row in db.execute("SELECT branch_id, turn_id, delta_json FROM state_deltas").fetchall():
        cleaned = clean_snapshot_json(row["delta_json"])
        if cleaned != row["delta_json"]:
            db.execute("UPDATE state_deltas SET delta_json=? WHERE branch_id=? AND turn_id=?",
                       (cleaned, row["branch_id"], row["turn_id"]))


def migration_7_stable_world_bible_identity(db: sqlite3.Connection) -> None:
    """Give versioned canon a stable identity independent of its display text."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(universe_lore_entries)")}
    if "source_id" not in columns:
        db.execute("ALTER TABLE universe_lore_entries ADD COLUMN source_id TEXT")
    db.execute("""CREATE UNIQUE INDEX IF NOT EXISTS universe_lore_source_id_unique
                  ON universe_lore_entries(universe_id, source_id)
                  WHERE source_id IS NOT NULL""")


def migration_8_replayable_campaign_setup(db: sqlite3.Connection) -> None:
    """Keep the complete preset opening so restart restores every initial record."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(campaign_starts)")}
    if "setup_json" not in columns:
        db.execute("ALTER TABLE campaign_starts ADD COLUMN setup_json TEXT NOT NULL DEFAULT '{}'")


def migration_9_structured_world_bible_records(db: sqlite3.Connection) -> None:
    """Keep database fields alongside the player-facing encyclopedia prose."""
    columns = {row["name"] for row in db.execute("PRAGMA table_info(universe_lore_entries)")}
    if "record_json" not in columns:
        db.execute("ALTER TABLE universe_lore_entries ADD COLUMN record_json TEXT NOT NULL DEFAULT '{}'")


def migration_10_lost_lands_world_name(db: sqlite3.Connection) -> None:
    """Adopt the canonical Lost Lands name without changing save identity."""
    db.execute(
        """UPDATE universes SET title=?, description=?
           WHERE id='shattered_realms'
             AND title IN ('The Mirror Sea Realms', '镜海诸境', 'Shattered Realms')""",
        (
            "The Lost Lands",
            "A vast sword-and-magic world of several continents, bay regions, island routes, and lands transformed by magic.",
        ),
    )


MIGRATIONS = (
    (1, "initial durable ledger", migration_1_initial_ledger),
    (2, "shared encyclopedia metadata", migration_2_universe_lore_metadata),
    (3, "structured protagonist profiles", migration_3_character_profiles),
    (4, "reviewable chapter summaries", migration_4_reviewable_chapter_summaries),
    (5, "recoverable world removal", migration_5_recoverable_world_removal),
    (6, "remove retired item overviews and empty inventory fields", migration_6_remove_retired_item_data),
    (7, "stable World Bible source identity", migration_7_stable_world_bible_identity),
    (8, "replayable complete campaign setup", migration_8_replayable_campaign_setup),
    (9, "structured World Bible records", migration_9_structured_world_bible_records),
    (10, "canonical Lost Lands world name", migration_10_lost_lands_world_name),
)


def apply_schema_migrations(db: sqlite3.Connection) -> None:
    """Apply each missing schema migration once and keep an audit trail."""
    recorded = {
        int(row["version"])
        for row in db.execute("SELECT version FROM schema_migrations ORDER BY version")
    }
    pragma_version = int(db.execute("PRAGMA user_version").fetchone()[0])
    highest = max(recorded | {pragma_version}, default=0)
    if highest > CURRENT_SCHEMA_VERSION:
        raise ValueError(
            f"save schema {highest} is newer than this app supports ({CURRENT_SCHEMA_VERSION})"
        )
    for version, name, migrate in MIGRATIONS:
        if version in recorded:
            continue
        with db:
            migrate(db)
            db.execute(
                "INSERT INTO schema_migrations(version, name, applied_at) VALUES (?, ?, ?)",
                (version, name, now()),
            )
            db.execute(f"PRAGMA user_version = {version}")
    # A database may have a correct migration table but an old PRAGMA value
    # after being copied by third-party SQLite tools. Repair that metadata.
    if int(db.execute("PRAGMA user_version").fetchone()[0]) != CURRENT_SCHEMA_VERSION:
        db.execute(f"PRAGMA user_version = {CURRENT_SCHEMA_VERSION}")


def schema_status(args: argparse.Namespace) -> None:
    db = connect(args.db)
    rows = db.execute(
        "SELECT version, name, applied_at FROM schema_migrations ORDER BY version"
    ).fetchall()
    print(json.dumps({
        "current_version": int(db.execute("PRAGMA user_version").fetchone()[0]),
        "supported_version": CURRENT_SCHEMA_VERSION,
        "migrations": [dict(row) for row in rows],
    }, ensure_ascii=False))


def validate_database_file(path: Path) -> dict[str, Any]:
    """Reject corrupt, unrelated, or too-new SQLite files before replacement."""
    if not path.is_file() or path.stat().st_size < 100:
        raise ValueError("the selected file is not a Secret Fire database")
    source = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    try:
        integrity = source.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"database integrity check failed: {integrity}")
        tables = {
            row["name"]
            for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        required = {"campaigns", "branches", "turns", "app_state"}
        if missing := sorted(required - tables):
            raise ValueError(f"not a Secret Fire save; missing tables: {', '.join(missing)}")
        version = int(source.execute("PRAGMA user_version").fetchone()[0])
        if version > CURRENT_SCHEMA_VERSION:
            raise ValueError(
                f"save schema {version} is newer than this app supports ({CURRENT_SCHEMA_VERSION})"
            )
        return {
            "schema_version": version,
            "campaigns": int(source.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]),
        }
    except sqlite3.DatabaseError as error:
        raise ValueError("the selected file is not a readable SQLite database") from error
    finally:
        source.close()


def create_database_backup(source_path: Path, output_path: Path) -> dict[str, Any]:
    """Create a transactionally consistent copy even while SQLite is active."""
    source_path = source_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if source_path == output_path:
        raise ValueError("backup destination must differ from the live database")
    output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if output_path.exists():
        raise ValueError("backup destination already exists")
    source = connect(str(source_path))
    target = sqlite3.connect(str(output_path))
    try:
        source.backup(target)
        target.commit()
    finally:
        target.close()
        source.close()
    os.chmod(output_path, 0o600)
    summary = validate_database_file(output_path)
    return {
        "path": str(output_path),
        "filename": output_path.name,
        "size": output_path.stat().st_size,
        **summary,
    }


def backup_database(args: argparse.Namespace) -> None:
    result = create_database_backup(Path(args.db), Path(args.output))
    print(json.dumps(result, ensure_ascii=False))


def restore_database(args: argparse.Namespace) -> None:
    """Validate, migrate, and atomically install an imported complete save."""
    destination = Path(args.db).expanduser().resolve()
    source_path = Path(args.source).expanduser().resolve()
    if destination == source_path:
        raise ValueError("import source must differ from the live database")
    validate_database_file(source_path)
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    automatic_backup = None
    if destination.exists():
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        backup_path = destination.parent / "backups" / f"before-import-{stamp}-{uuid4().hex[:8]}.sqlite3"
        automatic_backup = create_database_backup(destination, backup_path)

    staging = destination.with_name(f".{destination.name}.import-{uuid4().hex}.sqlite3")
    try:
        source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
        target = sqlite3.connect(str(staging))
        try:
            source.backup(target)
            target.commit()
        finally:
            target.close()
            source.close()

        migrated = connect(str(staging))
        try:
            integrity = migrated.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise ValueError(f"imported database failed integrity check: {integrity}")
            foreign_keys = migrated.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_keys:
                raise ValueError("imported database contains broken references")
            campaigns = int(migrated.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0])
            schema_version = int(migrated.execute("PRAGMA user_version").fetchone()[0])
        finally:
            migrated.close()

        if destination.exists():
            current = sqlite3.connect(str(destination))
            try:
                current.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            finally:
                current.close()
        for suffix in ("-wal", "-shm"):
            Path(f"{destination}{suffix}").unlink(missing_ok=True)
        os.replace(staging, destination)
        os.chmod(destination, 0o600)
        print(json.dumps({
            "restored": True,
            "campaigns": campaigns,
            "schema_version": schema_version,
            "automatic_backup": automatic_backup,
        }, ensure_ascii=False))
    finally:
        staging.unlink(missing_ok=True)


def ensure_universe(db: sqlite3.Connection, universe_id: str, title: Optional[str] = None, description: str = "") -> str:
    universe_id = slug(universe_id)
    db.execute(
        "INSERT OR IGNORE INTO universes(id, title, description, created_at) VALUES (?, ?, ?, ?)",
        (universe_id, title or universe_id.replace("_", " ").title(), description, now()),
    )
    return universe_id


def ensure_default_universe(db: sqlite3.Connection) -> None:
    """Give pre-hub saves a shared universe without changing their stories."""
    universe_id = ensure_universe(
        db,
        "shattered_realms",
        "The Lost Lands",
        "A vast sword-and-magic world of several continents, bay regions, island routes, and lands transformed by magic.",
    )
    db.execute(
        """INSERT OR IGNORE INTO campaign_universes(campaign_id, universe_id)
           SELECT id, ? FROM campaigns""",
        (universe_id,),
    )
def universe_for_campaign(db: sqlite3.Connection, campaign: str) -> sqlite3.Row:
    return fetchone(
        db,
        """SELECT u.* FROM universes u JOIN campaign_universes cu ON cu.universe_id=u.id
           WHERE cu.campaign_id=?""",
        (campaign,),
    )


def fetchone(db: sqlite3.Connection, query: str, values: Iterable[Any] = ()) -> sqlite3.Row:
    row = db.execute(query, tuple(values)).fetchone()
    if row is None:
        raise ValueError("requested campaign, branch, or turn does not exist")
    return row


def branch_row(db: sqlite3.Connection, campaign: str, branch: Optional[str] = None) -> sqlite3.Row:
    if branch:
        return fetchone(
            db,
            "SELECT * FROM branches WHERE campaign_id = ? AND (id = ? OR name = ?)",
            (campaign, branch, branch),
        )
    campaign_row = fetchone(db, "SELECT * FROM campaigns WHERE id = ?", (campaign,))
    return fetchone(db, "SELECT * FROM branches WHERE id = ?", (campaign_row["active_branch_id"],))


def json_value(row: sqlite3.Row, field: str) -> Any:
    return json.loads(row[field])


SCENE_ACTIVITIES = {"everyday", "dialogue", "exploration", "travel", "trade", "rest"}
SCENE_THREATS = {"calm", "tense", "imminent", "combat", "aftermath"}
SCENE_STANCES = {"allied", "neutral", "uncertain", "opposed"}
SCENE_ELEMENT_KINDS = {"route", "terrain", "object", "hazard", "cover", "clue", "service", "other"}
SCENE_PRESSURE_URGENCY = {"present", "immediate"}
GM_MOVE_KINDS = {
    "none", "environment_response", "location_routine", "npc_initiative",
    "thread_development", "time_consequence", "discovery",
}
GM_MOVE_SCOPES = {"immediate", "local", "distant_trace"}


def normalize_scene_state(scene: dict[str, Any], previous: Optional[dict[str, Any]] = None) -> dict[str, str]:
    """Keep the current dramatic state small, durable, and save-compatible."""
    prior = previous if isinstance(previous, dict) else {}
    source = scene.get("state", {}) if isinstance(scene, dict) else {}
    source = source if isinstance(source, dict) else {}
    activity = str(source.get("activity", prior.get("activity", "everyday")))
    threat = str(source.get("threat", prior.get("threat", "calm")))
    if activity not in SCENE_ACTIVITIES:
        activity = str(prior.get("activity", "everyday"))
    if threat not in SCENE_THREATS:
        threat = str(prior.get("threat", "calm"))
    if prior.get("threat") == "combat" and threat == "calm":
        threat = "aftermath"
    basis = str(source.get("basis", prior.get("basis", ""))).strip()[:300]
    return {"activity": activity, "threat": threat, "basis": basis}


def normalize_scene_model(scene: dict[str, Any], previous: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Validate a compact, observable snapshot without inventing affordances."""
    prior = previous if isinstance(previous, dict) else {}
    source = scene.get("model", {}) if isinstance(scene, dict) else {}
    source = source if isinstance(source, dict) else {}

    def short(value: Any, limit: int) -> str:
        return str(value or "").strip()[:limit]

    def stable_id(value: Any) -> str:
        candidate = short(value, 80)
        return candidate if re.fullmatch(r"[a-z0-9_]+", candidate) else ""

    def records(key: str, limit: int, allowed: dict[str, set[str]]) -> list[dict[str, str]]:
        if key not in source:
            values = prior.get(key, [])
            return values if isinstance(values, list) else []
        values = source.get(key, [])
        if not isinstance(values, list):
            return []
        result: list[dict[str, str]] = []
        seen: set[str] = set()
        for value in values:
            if not isinstance(value, dict):
                continue
            record_id = stable_id(value.get("id"))
            name = short(value.get("name"), 100)
            if not record_id or not name or record_id in seen:
                continue
            record = {"id": record_id, "name": name}
            for field, choices in allowed.items():
                text = short(value.get(field), 180)
                if choices and text not in choices:
                    text = ""
                record[field] = text
            result.append(record)
            seen.add(record_id)
            if len(result) == limit:
                break
        return result

    participants = records("participants", 8, {
        "position": set(), "activity": set(), "condition": set(), "stance": SCENE_STANCES,
    })
    elements = records("elements", 8, {
        "kind": SCENE_ELEMENT_KINDS, "position": set(), "state": set(),
    })
    pressures = records("pressures", 4, {
        "text": set(), "source": set(), "urgency": SCENE_PRESSURE_URGENCY,
    })
    player_position = short(source.get("player_position", prior.get("player_position", "")), 180)
    return {
        "player_position": player_position,
        "participants": participants,
        "elements": elements,
        "pressures": pressures,
    }


def normalize_gm_move(scene: dict[str, Any]) -> dict[str, str]:
    """Record at most one grounded world development for the completed turn."""
    source = scene.get("gm_move", {}) if isinstance(scene, dict) else {}
    source = source if isinstance(source, dict) else {}
    kind = compact_text(source.get("kind"), 40)
    if kind not in GM_MOVE_KINDS:
        kind = "none"
    if kind == "none":
        return {"kind": "none", "scope": "immediate", "source_id": "", "thread_id": "", "summary": "", "basis": ""}
    scope = compact_text(source.get("scope"), 40)
    if scope not in GM_MOVE_SCOPES:
        scope = "immediate"
    summary = compact_text(source.get("summary"), 300)
    basis = compact_text(source.get("basis"), 300)
    if not summary or not basis:
        return {"kind": "none", "scope": "immediate", "source_id": "", "thread_id": "", "summary": "", "basis": ""}
    return {
        "kind": kind,
        "scope": scope,
        "source_id": stable_record_id(source.get("source_id")),
        "thread_id": stable_record_id(source.get("thread_id")),
        "summary": summary,
        "basis": basis,
    }


def current_story_scene(db: sqlite3.Connection, branch: sqlite3.Row) -> dict[str, Any]:
    row = db.execute(
        """SELECT scene_json FROM turns WHERE branch_id=? AND narration<>''
           ORDER BY turn_number DESC LIMIT 1""",
        (branch["id"],),
    ).fetchone()
    if row is None and branch["forked_from_turn_id"]:
        row = db.execute("SELECT scene_json FROM turns WHERE id=?", (branch["forked_from_turn_id"],)).fetchone()
    if row:
        return json.loads(row["scene_json"])
    start = db.execute("SELECT setup_json FROM campaign_starts WHERE campaign_id=?", (branch["campaign_id"],)).fetchone()
    setup = json.loads(start["setup_json"] or "{}") if start else {}
    return setup.get("scene", {}) if isinstance(setup.get("scene", {}), dict) else {}


def normalize_opening_mechanics(value: Any) -> dict[str, Any]:
    """Validate mechanics that a versioned preset may establish at turn zero."""
    source = value if isinstance(value, dict) else {}
    mechanics: dict[str, Any] = {}
    attributes: dict[str, int] = {}
    for key, raw in (source.get("attributes", {}) if isinstance(source.get("attributes", {}), dict) else {}).items():
        if key not in ATTRIBUTE_KEYS or isinstance(raw, bool) or not isinstance(raw, (int, float)):
            continue
        number = int(raw)
        if not 1 <= number <= 100:
            raise ValueError(f"opening attribute {key} must be between 1 and 100")
        attributes[key] = number
    if attributes:
        mechanics["attributes"] = attributes

    catalog_ids = {entry["id"] for entry in ability_catalog()["abilities"]}
    mastery_ids = {entry["id"] for entry in ability_catalog()["mastery"]}
    abilities: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in source.get("abilities", []) if isinstance(source.get("abilities", []), list) else []:
        entry = {"id": raw} if isinstance(raw, str) else raw
        if not isinstance(entry, dict):
            continue
        ability_id = str(entry.get("id", "")).strip()
        if ability_id not in catalog_ids:
            raise ValueError(f"opening setup references unknown ability: {ability_id or '<empty>'}")
        if ability_id in seen:
            continue
        mastery = str(entry.get("mastery", "novice"))
        if mastery not in mastery_ids:
            raise ValueError(f"opening ability {ability_id} has unknown mastery: {mastery}")
        abilities.append({
            "id": ability_id, "mastery": mastery,
            "available": entry.get("available", True) is not False,
            "source_detail": compact_text(entry.get("source_detail"), 500),
        })
        seen.add(ability_id)
    if abilities:
        mechanics["abilities"] = abilities

    specialties = source.get("specialties", [])
    if isinstance(specialties, list):
        cleaned_specialties: list[Any] = []
        for raw in specialties[:20]:
            if isinstance(raw, str) and raw.strip():
                cleaned_specialties.append(raw.strip()[:160])
            elif isinstance(raw, dict):
                name = compact_text(raw.get("name"), 160)
                specialty_id = stable_record_id(raw.get("id"))
                if name or specialty_id:
                    cleaned_specialties.append({"id": specialty_id or slug(name), "name": name or specialty_id})
        if cleaned_specialties:
            mechanics["specialties"] = cleaned_specialties

    loads: dict[str, str] = {}
    raw_loads = source.get("loads", {}) if isinstance(source.get("loads", {}), dict) else {}
    for key, stages in LOAD_STAGES.items():
        stage = str(raw_loads.get(key, stages[0]))
        if stage not in stages:
            raise ValueError(f"opening load {key} has unknown stage: {stage}")
        loads[key] = stage
    mechanics["loads"] = loads

    resources = source.get("resources", {}) if isinstance(source.get("resources", {}), dict) else {}
    wallet = resources.get("wallet", {}) if isinstance(resources.get("wallet", {}), dict) else {}
    balance = wallet.get("balance", 0)
    if isinstance(balance, bool) or not isinstance(balance, (int, float)):
        raise ValueError("opening wallet balance must be a number")
    balance = int(balance)
    if not 0 <= balance <= MAX_RESOURCE_BALANCE:
        raise ValueError("opening wallet balance is outside the supported range")
    mechanics["resources"] = {"wallet": {"currency": "copper", "balance": balance}, "transactions": []}
    return mechanics


def normalize_initial_setup(value: Any) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    if not isinstance(value, dict):
        raise ValueError("opening setup must be a JSON object")
    setup: dict[str, Any] = {}
    scene = value.get("scene", {})
    if isinstance(scene, dict):
        setup["scene"] = scene
    player_state = value.get("player_state", {})
    if isinstance(player_state, dict):
        setup["player_state"] = {
            "condition": compact_text(player_state.get("condition") or "unhurt", 120),
            "mechanics": normalize_opening_mechanics(player_state.get("mechanics", {})),
        }
    for key, limit in (("places", 20), ("people", 12), ("items", 80), ("facts", 40), ("threads", 20)):
        records = value.get(key, [])
        if not isinstance(records, list):
            raise ValueError(f"opening setup {key} must be a list")
        setup[key] = [record for record in records[:limit] if isinstance(record, dict)]
    return setup


def install_opening_state(
    db: sqlite3.Connection,
    campaign: str,
    branch_id: str,
    player_name: str,
    character: dict[str, Any],
    starting_location: str,
    setup: dict[str, Any],
) -> None:
    """Install one complete opening as the recoverable branch root."""
    starting_place: Optional[dict[str, Any]] = None
    for place in setup.get("places", []):
        name = compact_text(place.get("name"), 160)
        if not name:
            raise ValueError("every opening place needs a name")
        arrived = canonical_location(name).casefold() == canonical_location(starting_location).casefold()
        saved = ensure_location_instance(db, campaign, branch_id, name, 0, place, arrived=arrived)
        if arrived:
            starting_place = saved
    if starting_place is None and starting_location.strip() and starting_location.strip().casefold() != "unknown":
        starting_place = ensure_location_instance(
            db, campaign, branch_id, starting_location, 0,
            {"name": starting_location, "kind": "other", "status": "active"}, arrived=True,
        )

    player_location = starting_place["name"] if starting_place else starting_location
    source_player_state = setup.get("player_state", {}) if isinstance(setup.get("player_state", {}), dict) else {}
    player_state = {
        "location": player_location,
        "condition": compact_text(source_player_state.get("condition") or "unhurt", 120),
    }
    mechanics = source_player_state.get("mechanics", {})
    if isinstance(mechanics, dict) and mechanics:
        player_state["mechanics"] = mechanics
    if starting_place:
        player_state["location_id"] = starting_place["id"]
    upsert_entity(db, campaign, branch_id, {
        "id": "player", "type": "player", "name": player_name,
        "profile": character, "state": player_state,
    }, 0)

    people_ids: set[str] = set()
    for person in setup.get("people", []):
        person_id = stable_record_id(person.get("id"))
        name = compact_text(person.get("name"), 120)
        if not person_id or not name or person_id == "player":
            raise ValueError("every opening person needs a stable non-player id and name")
        profile = dict(person.get("profile", {})) if isinstance(person.get("profile", {}), dict) else {}
        state = dict(person.get("state", {})) if isinstance(person.get("state", {}), dict) else {}
        attributes = profile.get("attributes", {})
        profile["attributes"] = normalize_opening_mechanics({"attributes": attributes})["attributes"] if attributes else {}
        if isinstance(state.get("mechanics"), dict):
            state["mechanics"] = normalize_opening_mechanics(state["mechanics"])
        upsert_entity(db, campaign, branch_id, {
            "id": person_id, "type": "npc", "name": name, "profile": profile, "state": state,
        }, 0)
        people_ids.add(person_id)

    valid_holders = {"player", "world", "archive", *people_ids}
    for item in setup.get("items", []):
        item_id = stable_record_id(item.get("id"))
        name = compact_text(item.get("name"), 120)
        profile = dict(item.get("profile", {})) if isinstance(item.get("profile", {}), dict) else {}
        state = dict(item.get("state", {})) if isinstance(item.get("state", {}), dict) else {}
        if not item_id or not name:
            raise ValueError("every opening item needs a stable id and name")
        classification = classify_item({"name": name, **profile})
        if not classification["base_type_id"]:
            raise ValueError(f"opening item has no valid base type: {name}")
        holder = stable_record_id(state.get("holder")) or str(state.get("holder", "player"))
        if holder not in valid_holders:
            raise ValueError(f"opening item holder is not a recorded person: {holder}")
        state["holder"] = holder
        profile.update({
            "base_type_id": classification["base_type_id"],
            "rarity": classification["rarity"],
        })
        upsert_entity(db, campaign, branch_id, {
            "id": item_id, "type": "item", "name": name, "profile": profile, "state": state,
        }, 0)

    for fact in setup.get("facts", []):
        fact_id = stable_record_id(fact.get("id"))
        text = compact_text(fact.get("text"), 1600)
        if not fact_id or not text:
            raise ValueError("every opening fact needs a stable id and text")
        db.execute(
            """INSERT INTO facts(id, branch_id, created_turn, subject_id, predicate, value_json, text,
                                  truth_status, visibility, witnesses_json, tags_json, importance, status)
               VALUES (?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')""",
            (
                f"{campaign}:initial:{fact_id}", branch_id, stable_record_id(fact.get("subject_id")) or None,
                compact_text(fact.get("predicate") or "opening_fact", 120),
                json.dumps(fact.get("value"), ensure_ascii=False), text,
                compact_text(fact.get("truth_status") or "true", 40),
                compact_text(fact.get("visibility") or "shared", 40),
                json.dumps(compact_text_list(fact.get("witnesses"), 12, 80), ensure_ascii=False),
                json.dumps(compact_text_list(fact.get("tags"), 12, 80), ensure_ascii=False),
                max(0, min(10, int(fact.get("importance", 5)))),
            ),
        )

    for thread in setup.get("threads", []):
        thread_id = stable_record_id(thread.get("id"))
        title = compact_text(thread.get("title"), 240)
        if not thread_id or not title:
            raise ValueError("every opening thread needs a stable id and title")
        db.execute(
            """INSERT INTO story_threads(branch_id, id, kind, title, status, stakes, summary,
                                           related_entities_json, urgency, last_advanced_turn)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
            (
                branch_id, thread_id, compact_text(thread.get("kind") or "mystery", 60), title,
                compact_text(thread.get("status") or "active", 40), compact_text(thread.get("stakes"), 1200),
                compact_text(thread.get("summary"), 1600),
                json.dumps(compact_text_list(thread.get("related_entities"), 16, 80), ensure_ascii=False),
                max(0, min(10, int(thread.get("urgency", 5)))),
            ),
        )


def init_campaign(args: argparse.Namespace) -> None:
    campaign_id = slug(args.campaign)
    branch_id = f"{campaign_id}:main"
    try:
        character = json.loads(args.character)
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError("character must be a JSON object") from error
    if not isinstance(character, dict):
        raise ValueError("character must be a JSON object")
    character = {key: value.strip() for key, value in character.items()
                 if isinstance(key, str) and isinstance(value, str) and value.strip()}
    character["concept"] = args.concept
    try:
        setup = normalize_initial_setup(json.loads(args.setup))
    except json.JSONDecodeError as error:
        raise ValueError("setup must be a JSON object") from error
    db = connect(args.db)
    with db:
        if db.execute("SELECT 1 FROM campaigns WHERE id = ?", (campaign_id,)).fetchone():
            raise ValueError(f"campaign already exists: {campaign_id}")
        db.execute(
            "INSERT INTO campaigns(id, title, active_branch_id, created_at) VALUES (?, ?, ?, ?)",
            (campaign_id, args.title, branch_id, now()),
        )
        universe_id = ensure_universe(db, args.universe, args.universe_title, args.universe_description)
        db.execute(
            "INSERT INTO campaign_universes(campaign_id, universe_id) VALUES (?, ?)",
            (campaign_id, universe_id),
        )
        db.execute(
            """INSERT INTO campaign_starts(campaign_id, player_name, player_concept, starting_location,
                                            character_json, setup_json) VALUES (?, ?, ?, ?, ?, ?)""",
            (campaign_id, args.player, args.concept, args.location, json.dumps(character, ensure_ascii=False),
             json.dumps(setup, ensure_ascii=False)),
        )
        db.execute(
            "INSERT INTO branches(id, campaign_id, name, base_turn_number, created_at) VALUES (?, ?, 'main', 0, ?)",
            (branch_id, campaign_id, now()),
        )
        install_opening_state(db, campaign_id, branch_id, args.player, character, args.location, setup)
        # Turn zero is the root anchor from which compact turn deltas replay.
        write_root(db, branch_id, 0, snapshot(db, branch_id))
        db.execute(
            """INSERT INTO app_state(key, value_json) VALUES ('active_campaign', ?)
               ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json""",
            (json.dumps(campaign_id),),
        )
    print(f"Created campaign '{campaign_id}' on branch main in {args.db}")


def normalize_npc_state(existing: dict[str, Any], incoming: dict[str, Any], turn: int) -> dict[str, Any]:
    """Merge a person update without letting one short scene erase a life.

    NPC identity is campaign-level, but their relationship, whereabouts and
    memory belong to a branch. Memories remain intentionally compact: they are
    durable turning points, not a hidden transcript.
    """
    state = dict(existing) if isinstance(existing, dict) else {}
    update = dict(incoming) if isinstance(incoming, dict) else {}
    raw_memories = update.pop("memories", [])
    memory_event = update.pop("memory_event", None)
    if memory_event:
        raw_memories = [*raw_memories, memory_event] if isinstance(raw_memories, list) else [memory_event]
    state.update(update)
    status = str(state.get("status", "known"))
    state["status"] = status if status in NPC_STATUSES else "known"
    state["tier"] = str(state.get("tier", "recurring")) if str(state.get("tier", "recurring")) in {"core", "recurring", "background"} else "recurring"
    state["pinned"] = bool(state.get("pinned", state["status"] in {"party", "core"}))
    memories = state.get("memories", []) if isinstance(state.get("memories", []), list) else []
    candidates = [item for item in [*memories, *(raw_memories if isinstance(raw_memories, list) else [])] if isinstance(item, dict)]
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in candidates:
        text = str(item.get("text", item.get("event", ""))).strip()[:600]
        if not text:
            continue
        importance = item.get("importance", 5)
        try:
            importance = max(1, min(10, int(importance)))
        except (TypeError, ValueError):
            importance = 5
        item_turn = item.get("turn", turn)
        try:
            item_turn = max(0, int(item_turn))
        except (TypeError, ValueError):
            item_turn = turn
        key = re.sub(r"\s+", " ", text).lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append({"text": text, "importance": importance, "turn": item_turn, "kind": str(item.get("kind", "memory"))[:60]})
    # Keep the most consequential moments, then the newest among equals. The
    # local archive can hold a longer relationship history than a single turn
    # can see; prompt selection below remains deliberately much smaller.
    normalized.sort(key=lambda item: (item["importance"], item["turn"]), reverse=True)
    if state["status"] in {"party", "core"} or state["tier"] == "core":
        memory_limit = NPC_MEMORY_LIMITS["party"]
    elif state["pinned"]:
        memory_limit = NPC_MEMORY_LIMITS["pinned"]
    elif state["tier"] == "recurring":
        memory_limit = NPC_MEMORY_LIMITS["recurring"]
    else:
        memory_limit = NPC_MEMORY_LIMITS["background"]
    state["memories"] = normalized[:memory_limit]
    return state


def upsert_entity(db: sqlite3.Connection, campaign: str, branch_id: str, payload: dict[str, Any], turn: int) -> None:
    entity_id = slug(payload["id"])
    existing_entity = db.execute(
        "SELECT type, name, profile_json FROM entities WHERE campaign_id=? AND id=?", (campaign, entity_id)
    ).fetchone()
    entity_type = payload.get("type") or (existing_entity["type"] if existing_entity else "concept")
    name = payload.get("name") or (existing_entity["name"] if existing_entity else entity_id)
    profile = payload.get("profile", {})
    profile = profile if isinstance(profile, dict) else {}
    state = payload.get("state")
    # Item updates are usually small narrative changes ("the key is now
    # concealed"), rather than a complete re-description. Merge them so the
    # known purpose and prior physical description cannot disappear when Codex
    # records a move, use, or change of owner.
    if entity_type == "item" or entity_type in NPC_TYPES:
        existing = existing_entity
        if existing:
            saved_profile = json.loads(existing["profile_json"])
            saved_profile.update(profile if isinstance(profile, dict) else {})
            profile = saved_profile
        if state is not None:
            existing_state = db.execute(
                "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id=?", (branch_id, entity_id)
            ).fetchone()
            if existing_state:
                saved_state = json.loads(existing_state["state_json"])
                saved_state.update(state if isinstance(state, dict) else {})
                state = saved_state
            if entity_type in NPC_TYPES:
                state = normalize_npc_state(json.loads(existing_state["state_json"]) if existing_state else {}, state if isinstance(state, dict) else {}, turn)
        elif entity_type in NPC_TYPES:
            state = normalize_npc_state({}, state if isinstance(state, dict) else {}, turn)
    db.execute(
        """INSERT INTO entities(campaign_id, id, type, name, profile_json)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(campaign_id, id) DO UPDATE SET
             type=excluded.type, name=excluded.name, profile_json=excluded.profile_json""",
        (campaign, entity_id, entity_type, name, json.dumps(profile, ensure_ascii=False)),
    )
    if state is not None:
        db.execute(
            """INSERT INTO entity_states(branch_id, entity_id, state_json, updated_turn)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(branch_id, entity_id) DO UPDATE SET
                 state_json=excluded.state_json, updated_turn=excluded.updated_turn""",
            (branch_id, entity_id, json.dumps(state, ensure_ascii=False), turn),
        )


def location_rows(db: sqlite3.Connection, campaign: str, branch_id: str) -> list[dict[str, Any]]:
    """Return only location identities visible in this branch."""
    rows = db.execute(
        """SELECT e.id, e.name, s.state_json, s.updated_turn
           FROM entity_states s JOIN entities e
             ON e.id=s.entity_id AND e.campaign_id=?
           WHERE s.branch_id=? AND e.type='location'""",
        (campaign, branch_id),
    ).fetchall()
    result: list[dict[str, Any]] = []
    for row in rows:
        state = json.loads(row["state_json"] or "{}")
        result.append({
            "id": row["id"], "name": row["name"],
            "kind": str(state.get("kind", "other")),
            "parent_id": str(state.get("parent_id", "")),
            "parent_name": str(state.get("parent_name", "")),
            "description": str(state.get("description", "")),
            "atmosphere": str(state.get("atmosphere", "")),
            "features": state.get("features", []) if isinstance(state.get("features", []), list) else [],
            "aliases": state.get("aliases", []) if isinstance(state.get("aliases", []), list) else [],
            "status": str(state.get("status", "active")),
            "current_summary": str(state.get("current_summary", "")),
            "access": str(state.get("access", "")),
            "first_seen_turn": int(state.get("first_seen_turn", 0) or 0),
            "first_visited_turn": int(state.get("first_visited_turn", 0) or 0),
            "last_visited_turn": int(state.get("last_visited_turn", 0) or 0),
            "visits": int(state.get("visits", 0) or 0),
            "visited": bool(state.get("visited", False)),
            "updated_turn": int(row["updated_turn"]),
        })
    return result


def route_rows(db: sqlite3.Connection, campaign: str, branch_id: str) -> list[dict[str, Any]]:
    rows = db.execute(
        """SELECT e.id, e.name, s.state_json, s.updated_turn
           FROM entity_states s JOIN entities e
             ON e.id=s.entity_id AND e.campaign_id=?
           WHERE s.branch_id=? AND e.type='route'""",
        (campaign, branch_id),
    ).fetchall()
    result: list[dict[str, Any]] = []
    for row in rows:
        state = json.loads(row["state_json"] or "{}")
        result.append({
            "id": row["id"], "name": row["name"],
            "from_id": str(state.get("from_id", "")), "from": str(state.get("from_name", "")),
            "to_id": str(state.get("to_id", "")), "to": str(state.get("to_name", "")),
            "status": str(state.get("status", "open")),
            "travel_mode": str(state.get("travel_mode", "")),
            "description": str(state.get("description", "")),
            "first_turn": int(state.get("first_traveled_turn", 0) or 0),
            "last_turn": int(state.get("last_traveled_turn", 0) or 0),
            "uses": int(state.get("uses", 0) or 0),
            "updated_turn": int(row["updated_turn"]),
        })
    return result


def ensure_location_instance(
    db: sqlite3.Connection,
    campaign: str,
    branch_id: str,
    name: str,
    turn: int,
    record: Optional[dict[str, Any]] = None,
    *,
    arrived: bool,
) -> dict[str, Any]:
    """Persist one concrete place without relying on the narrator's memory."""
    source = record if isinstance(record, dict) else {}
    place_name = canonical_location(compact_text(source.get("name") or name, 160))
    if not place_name or place_name.casefold() == "unknown":
        raise ValueError("scene location must name the place actually reached")
    known = location_rows(db, campaign, branch_id)
    requested_id = stable_record_id(source.get("id"))
    existing = next((item for item in known if requested_id and item["id"] == requested_id), None)
    if existing is None:
        folded = place_name.casefold()
        existing = next((item for item in known if item["name"].casefold() == folded or folded in {
            str(alias).casefold() for alias in item.get("aliases", [])
        }), None)
    parent_id = stable_record_id(source.get("parent_id"))
    parent_name = canonical_location(compact_text(source.get("parent_name"), 160))
    if parent_name and not parent_id:
        parent = next((item for item in known if item["name"].casefold() == parent_name.casefold()), None)
        parent_id = parent["id"] if parent else generated_location_id(parent_name)
    if parent_id:
        parent_collision = db.execute(
            "SELECT type FROM entities WHERE campaign_id=? AND id=?", (campaign, parent_id)
        ).fetchone()
        if parent_collision and parent_collision["type"] != "location":
            parent_id = generated_location_id(parent_name or parent_id)
    if existing:
        place_name = existing["name"]
    place_id = existing["id"] if existing else requested_id or generated_location_id(place_name, parent_id)
    collision = db.execute(
        "SELECT type FROM entities WHERE campaign_id=? AND id=?", (campaign, place_id)
    ).fetchone()
    if collision and collision["type"] != "location":
        place_id = generated_location_id(place_name, parent_id)
    if parent_id == place_id:
        parent_id = ""
        parent_name = ""

    if parent_name and parent_id and not db.execute(
        """SELECT 1 FROM entity_states s JOIN entities e ON e.id=s.entity_id AND e.campaign_id=?
           WHERE s.branch_id=? AND s.entity_id=? AND e.type='location'""",
        (campaign, branch_id, parent_id),
    ).fetchone():
        db.execute(
            """INSERT INTO entities(campaign_id, id, type, name, profile_json) VALUES (?, ?, 'location', ?, '{}')
               ON CONFLICT(campaign_id, id) DO NOTHING""",
            (campaign, parent_id, parent_name),
        )
        parent_state = {
            "kind": "other", "status": "active", "visited": False, "visits": 0,
            "first_seen_turn": turn, "aliases": [], "features": [],
        }
        db.execute(
            """INSERT INTO entity_states(branch_id, entity_id, state_json, updated_turn)
               VALUES (?, ?, ?, ?) ON CONFLICT(branch_id, entity_id) DO NOTHING""",
            (branch_id, parent_id, json.dumps(parent_state, ensure_ascii=False), turn),
        )

    state_row = db.execute(
        "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id=?",
        (branch_id, place_id),
    ).fetchone()
    state = json.loads(state_row["state_json"]) if state_row else {
        "kind": "other", "status": "active", "visited": False, "visits": 0,
        "first_seen_turn": turn, "aliases": [], "features": [],
    }
    kind = compact_text(source.get("kind"), 40)
    if kind in LOCATION_TYPES:
        state["kind"] = kind
    status = compact_text(source.get("status"), 40)
    if status in LOCATION_STATUSES:
        state["status"] = status
    for key, limit in (("description", 1200), ("atmosphere", 500), ("current_summary", 900), ("access", 500)):
        value = compact_text(source.get(key), limit)
        if value:
            state[key] = value
    aliases = compact_text_list(source.get("aliases"), 12, 160)
    if aliases:
        state["aliases"] = compact_text_list([*state.get("aliases", []), *aliases], 12, 160)
    features = compact_text_list(source.get("features"), 10, 240)
    if features:
        state["features"] = features
    if parent_id:
        state["parent_id"] = parent_id
    if parent_name:
        state["parent_name"] = parent_name
    state["last_seen_turn"] = turn
    if arrived:
        if not state.get("visited"):
            state["first_visited_turn"] = turn
        state["visited"] = True
        state["last_visited_turn"] = turn
        state["visits"] = max(0, int(state.get("visits", 0) or 0)) + 1

    db.execute(
        """INSERT INTO entities(campaign_id, id, type, name, profile_json) VALUES (?, ?, 'location', ?, '{}')
           ON CONFLICT(campaign_id, id) DO UPDATE SET type='location'""",
        (campaign, place_id, place_name),
    )
    db.execute(
        """INSERT INTO entity_states(branch_id, entity_id, state_json, updated_turn)
           VALUES (?, ?, ?, ?) ON CONFLICT(branch_id, entity_id) DO UPDATE SET
             state_json=excluded.state_json, updated_turn=excluded.updated_turn""",
        (branch_id, place_id, json.dumps(state, ensure_ascii=False), turn),
    )
    return {"id": place_id, "name": place_name, **state}


def ensure_route_instance(
    db: sqlite3.Connection,
    campaign: str,
    branch_id: str,
    origin: dict[str, Any],
    destination: dict[str, Any],
    turn: int,
    record: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Record an observed connection between two persistent places."""
    source = record if isinstance(record, dict) else {}
    pair = sorted((origin["id"], destination["id"]))
    fallback = f"route_{hashlib.sha256('|'.join(pair).encode('utf-8')).hexdigest()[:16]}"
    route_id = stable_record_id(source.get("id")) or fallback
    collision = db.execute(
        "SELECT type FROM entities WHERE campaign_id=? AND id=?", (campaign, route_id)
    ).fetchone()
    if collision and collision["type"] != "route":
        route_id = fallback
    row = db.execute(
        "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id=?",
        (branch_id, route_id),
    ).fetchone()
    state = json.loads(row["state_json"]) if row else {
        "from_id": origin["id"], "from_name": origin["name"],
        "to_id": destination["id"], "to_name": destination["name"],
        "status": "open", "uses": 0, "first_traveled_turn": turn,
    }
    status = compact_text(source.get("status"), 40)
    if status in ROUTE_STATUSES:
        state["status"] = status
    for key, limit in (("travel_mode", 120), ("description", 700)):
        value = compact_text(source.get(key), limit)
        if value:
            state[key] = value
    state["last_traveled_turn"] = turn
    state["uses"] = max(0, int(state.get("uses", 0) or 0)) + 1
    route_name = compact_text(source.get("name"), 180) or f"{origin['name']}—{destination['name']}"
    db.execute(
        """INSERT INTO entities(campaign_id, id, type, name, profile_json) VALUES (?, ?, 'route', ?, '{}')
           ON CONFLICT(campaign_id, id) DO UPDATE SET type='route'""",
        (campaign, route_id, route_name),
    )
    db.execute(
        """INSERT INTO entity_states(branch_id, entity_id, state_json, updated_turn)
           VALUES (?, ?, ?, ?) ON CONFLICT(branch_id, entity_id) DO UPDATE SET
             state_json=excluded.state_json, updated_turn=excluded.updated_turn""",
        (branch_id, route_id, json.dumps(state, ensure_ascii=False), turn),
    )
    return {"id": route_id, "name": route_name, **state}


def patch_state(db: sqlite3.Connection, branch_id: str, payload: dict[str, Any], turn: int) -> None:
    entity_id = slug(payload["entity_id"])
    item = db.execute(
        """SELECT 1 FROM entities e JOIN branches b ON b.campaign_id=e.campaign_id
           WHERE b.id=? AND e.id=? AND e.type='item'""", (branch_id, entity_id),
    ).fetchone()
    if item:
        # Narration may suggest a transfer, but only a reviewed local
        # possession revision can make it authoritative.
        return
    row = db.execute(
        "SELECT state_json FROM entity_states WHERE branch_id = ? AND entity_id = ?", (branch_id, entity_id)
    ).fetchone()
    current = json.loads(row["state_json"]) if row else {}
    incoming = dict(payload.get("patch", {})) if isinstance(payload.get("patch", {}), dict) else {}
    if entity_id == "player":
        # The narrator describes outcomes, while dedicated local paths own
        # attributes, learned capabilities, injuries, loads, and conditions.
        incoming.pop("condition", None)
        incoming.pop("attributes", None)
    if entity_id == "player" and isinstance(incoming.get("mechanics"), dict):
        mechanics_patch = dict(incoming["mechanics"])
        for protected in ("abilities", "specialties", "attributes", "loads", "injuries", "conditions", "resources"):
            mechanics_patch.pop(protected, None)
        saved_mechanics = current.get("mechanics", {})
        incoming["mechanics"] = {
            **(saved_mechanics if isinstance(saved_mechanics, dict) else {}),
            **mechanics_patch,
        }
    is_npc_state = (str(current.get("status", "")) in NPC_STATUSES or str(current.get("tier", "")) in {"core", "recurring", "background"}
                    or "memory_event" in incoming or "memories" in incoming)
    current = normalize_npc_state(current, incoming, turn) if is_npc_state else {**current, **incoming}
    db.execute(
        """INSERT INTO entity_states(branch_id, entity_id, state_json, updated_turn)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(branch_id, entity_id) DO UPDATE SET
             state_json=excluded.state_json, updated_turn=excluded.updated_turn""",
        (branch_id, entity_id, json.dumps(current, ensure_ascii=False), turn),
    )


def consequence_state(player_state: dict[str, Any] | None) -> dict[str, Any]:
    """Return a stable, UI-safe view of injuries, conditions, and loads."""
    state = player_state if isinstance(player_state, dict) else {}
    mechanics = state.get("mechanics", {})
    mechanics = mechanics if isinstance(mechanics, dict) else {}
    ability_state = abilities_from_player_state(state)
    injuries: list[dict[str, Any]] = []
    for item in mechanics.get("injuries", []) if isinstance(mechanics.get("injuries", []), list) else []:
        if not isinstance(item, dict) or str(item.get("stage", "")) not in INJURY_STAGES:
            continue
        injury_id = str(item.get("id", "")).strip()
        label = str(item.get("label", "")).strip()
        if not injury_id or not label:
            continue
        injuries.append({
            "id": injury_id, "stage": item["stage"], "label": label[:120],
            "affected_functions": [str(value)[:160] for value in item.get("affected_functions", []) if str(value).strip()][:6],
            "source": str(item.get("source", ""))[:300],
            "recovery_condition": str(item.get("recovery_condition", ""))[:500],
            "permanent": bool(item.get("permanent", False)),
            "started_turn": max(0, int(item.get("started_turn", 0) or 0)),
        })
    conditions: list[dict[str, Any]] = []
    for item in mechanics.get("conditions", []) if isinstance(mechanics.get("conditions", []), list) else []:
        if not isinstance(item, dict):
            continue
        condition_id = str(item.get("id", "")).strip()
        label = str(item.get("label", "")).strip()
        if not condition_id or not label:
            continue
        conditions.append({
            "id": condition_id, "label": label[:120], "effect": str(item.get("effect", ""))[:500],
            "source": str(item.get("source", ""))[:300],
            "recovery_condition": str(item.get("recovery_condition", ""))[:500],
            "started_turn": max(0, int(item.get("started_turn", 0) or 0)),
        })
    return {"loads": ability_state["loads"], "injuries": injuries, "conditions": conditions}


def apply_player_consequences(
    db: sqlite3.Connection, branch_id: str, consequences: list[dict[str, Any]],
    high_stakes: bool, prior_threat: str, turn: int,
) -> dict[str, Any]:
    """Apply already validated consequences through legal one-step transitions."""
    if not consequences:
        row = db.execute(
            "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'", (branch_id,)
        ).fetchone()
        return consequence_state(json.loads(row["state_json"]) if row else {})
    if len(consequences) > 4:
        raise ValueError("a turn may apply at most four persistent consequences")
    if high_stakes and prior_threat not in {"imminent", "combat"}:
        raise ValueError("high-stakes harm was not established before this turn")
    row = fetchone(db, "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'", (branch_id,))
    state = json.loads(row["state_json"])
    mechanics = dict(state.get("mechanics", {})) if isinstance(state.get("mechanics", {}), dict) else {}
    current_view = consequence_state(state)
    loads = dict(current_view["loads"])
    injuries = {item["id"]: dict(item) for item in current_view["injuries"]}
    conditions = {item["id"]: dict(item) for item in current_view["conditions"]}

    for consequence in consequences:
        kind = consequence.get("type")
        if kind == "load":
            track = str(consequence.get("track", ""))
            direction = str(consequence.get("direction", ""))
            if track not in LOAD_STAGES or direction not in {"advance", "recover"}:
                raise ValueError("invalid load consequence")
            stages = LOAD_STAGES[track]
            index = stages.index(loads[track])
            next_index = min(len(stages) - 1, index + 1) if direction == "advance" else max(0, index - 1)
            if next_index == index:
                raise ValueError("load consequence cannot move beyond its legal range")
            loads[track] = stages[next_index]
            continue

        consequence_id = str(consequence.get("id", "")).strip()
        if not re.fullmatch(r"[a-z0-9][a-z0-9_:.-]{0,119}", consequence_id):
            raise ValueError("persistent consequence has an invalid id")
        action = str(consequence.get("action", ""))
        if kind == "condition":
            if action == "remove":
                if consequence_id not in conditions:
                    raise ValueError("cannot remove an unrecorded condition")
                conditions.pop(consequence_id)
            elif action == "add":
                if consequence_id in conditions:
                    raise ValueError("condition already exists; use a distinct sourced condition")
                conditions[consequence_id] = {
                    "id": consequence_id, "label": str(consequence.get("label", ""))[:120],
                    "effect": str(consequence.get("effect", ""))[:500],
                    "source": str(consequence.get("source", ""))[:300],
                    "recovery_condition": str(consequence.get("recovery_condition", ""))[:500],
                    "started_turn": turn,
                }
            else:
                raise ValueError("invalid condition transition")
            continue
        if kind != "injury" or str(consequence.get("stage", "")) not in INJURY_STAGES:
            raise ValueError("invalid injury consequence")
        stage = str(consequence["stage"])
        permanent = bool(consequence.get("permanent", False))
        if permanent and (not high_stakes or stage != "critical"):
            raise ValueError("permanent harm requires an explicit critical risk")
        if action == "add":
            if consequence_id in injuries:
                raise ValueError("injury already exists")
            if stage == "critical" and not high_stakes:
                raise ValueError("critical injury requires explicit high stakes")
            if stage == "serious" and not high_stakes:
                raise ValueError("ordinary failure cannot begin with a serious injury")
            injuries[consequence_id] = {
                "id": consequence_id, "stage": stage, "label": str(consequence.get("label", ""))[:120],
                "affected_functions": [str(value)[:160] for value in consequence.get("affected_functions", [])][:6],
                "source": str(consequence.get("source", ""))[:300],
                "recovery_condition": str(consequence.get("recovery_condition", ""))[:500],
                "permanent": permanent, "started_turn": turn,
            }
        elif action == "worsen":
            current = injuries.get(consequence_id)
            if not current:
                raise ValueError("cannot worsen an unrecorded injury")
            expected = INJURY_STAGES[min(len(INJURY_STAGES) - 1, INJURY_STAGES.index(current["stage"]) + 1)]
            if expected == current["stage"] or stage != expected:
                raise ValueError("injury worsening must move exactly one stage")
            if stage == "critical" and not high_stakes:
                raise ValueError("critical injury requires explicit high stakes")
            injuries[consequence_id] = {**current, **{
                key: value for key, value in consequence.items()
                if key in {"stage", "label", "affected_functions", "source", "recovery_condition", "permanent"}
            }}
        elif action == "recover":
            current = injuries.get(consequence_id)
            if not current or stage != current["stage"]:
                raise ValueError("injury recovery must name its current stage")
            index = INJURY_STAGES.index(current["stage"])
            if index == 0:
                injuries.pop(consequence_id)
            else:
                injuries[consequence_id] = {**current, "stage": INJURY_STAGES[index - 1], "permanent": False}
        else:
            raise ValueError("invalid injury transition")

    mechanics["loads"] = loads
    mechanics["injuries"] = list(injuries.values())
    mechanics["conditions"] = list(conditions.values())
    state["mechanics"] = mechanics
    severity = {"minor": 1, "serious": 2, "critical": 3}
    worst = max(injuries.values(), key=lambda item: severity[item["stage"]], default=None)
    state["condition"] = (f"{worst['label']}（{worst['stage']}）" if worst else next(
        (item["label"] for item in conditions.values()), "unhurt"
    ))
    db.execute(
        "UPDATE entity_states SET state_json=?, updated_turn=? WHERE branch_id=? AND entity_id='player'",
        (json.dumps(state, ensure_ascii=False), turn, branch_id),
    )
    return consequence_state(state)


def snapshot(db: sqlite3.Connection, branch_id: str) -> dict[str, list[dict[str, Any]]]:
    return {
        "entity_states": [dict(row) for row in db.execute("SELECT * FROM entity_states WHERE branch_id = ?", (branch_id,))],
        "facts": [dict(row) for row in db.execute("SELECT * FROM facts WHERE branch_id = ?", (branch_id,))],
        "beliefs": [dict(row) for row in db.execute("SELECT * FROM beliefs WHERE branch_id = ?", (branch_id,))],
        "story_threads": [dict(row) for row in db.execute("SELECT * FROM story_threads WHERE branch_id = ?", (branch_id,))],
    }


def restore_snapshot(db: sqlite3.Connection, branch_id: str, data: dict[str, list[dict[str, Any]]]) -> None:
    for table in STATE_TABLES:
        db.execute(f"DELETE FROM {table} WHERE branch_id = ?", (branch_id,))
        rows = data.get(table, [])
        for row in rows:
            row = dict(row)
            row["branch_id"] = branch_id
            # Facts and beliefs retain their contents across a fork but need a
            # new database identity because their primary keys are global.
            if table in {"facts", "beliefs"}:
                row["id"] = f"{branch_id}:inherited:{row['id']}"
            fields = list(row)
            db.execute(
                f"INSERT INTO {table} ({', '.join(fields)}) VALUES ({', '.join('?' for _ in fields)})",
                tuple(row[field] for field in fields),
            )


def state_key(table: str, row: dict[str, Any]) -> str:
    """Return the branch-local identity used by the compact journal."""
    if table == "entity_states":
        return str(row["entity_id"])
    return str(row["id"])


def state_delta(before: dict[str, list[dict[str, Any]]], after: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, list[Any]]]:
    """Encode only changed state rows; immutable events already have a log."""
    result: dict[str, dict[str, list[Any]]] = {}
    for table in STATE_TABLES:
        old_rows = {state_key(table, row): row for row in before.get(table, [])}
        new_rows = {state_key(table, row): row for row in after.get(table, [])}
        upserts = [row for key, row in new_rows.items() if old_rows.get(key) != row]
        deletes = [key for key in old_rows if key not in new_rows]
        if upserts or deletes:
            result[table] = {"upserts": upserts, "deletes": deletes}
    return result


def apply_delta(data: dict[str, list[dict[str, Any]]], delta: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Apply a journal entry in memory without touching the current branch."""
    result = {table: [dict(row) for row in data.get(table, [])] for table in STATE_TABLES}
    for table, changes in delta.items():
        if table not in STATE_TABLES:
            continue
        rows = {state_key(table, row): row for row in result[table]}
        for key in changes.get("deletes", []):
            rows.pop(str(key), None)
        for row in changes.get("upserts", []):
            rows[state_key(table, row)] = dict(row)
        result[table] = list(rows.values())
    return result


def write_snapshot(db: sqlite3.Connection, branch_id: str, turn_id: str, turn_number: int, data: dict[str, list[dict[str, Any]]]) -> None:
    db.execute(
        """INSERT INTO snapshots(branch_id, turn_id, turn_number, snapshot_json) VALUES (?, ?, ?, ?)
           ON CONFLICT(branch_id, turn_id) DO UPDATE SET turn_number=excluded.turn_number, snapshot_json=excluded.snapshot_json""",
        (branch_id, turn_id, turn_number, json.dumps(data, ensure_ascii=False)),
    )


def write_root(db: sqlite3.Connection, branch_id: str, turn_number: int, data: dict[str, list[dict[str, Any]]]) -> None:
    db.execute(
        """INSERT INTO state_roots(branch_id, turn_number, snapshot_json) VALUES (?, ?, ?)
           ON CONFLICT(branch_id) DO UPDATE SET turn_number=excluded.turn_number, snapshot_json=excluded.snapshot_json""",
        (branch_id, turn_number, json.dumps(data, ensure_ascii=False)),
    )


def state_at(db: sqlite3.Connection, branch_id: str, turn_number: int) -> dict[str, list[dict[str, Any]]]:
    """Materialize exact branch state from the nearest full anchor and deltas.

    Old saves are compatible: their legacy every-turn snapshots act as anchors
    even before any compact delta has been written.
    """
    snapshot_anchor = db.execute(
        """SELECT turn_number, snapshot_json FROM snapshots
           WHERE branch_id=? AND turn_number<=? ORDER BY turn_number DESC LIMIT 1""",
        (branch_id, turn_number),
    ).fetchone()
    root_anchor = db.execute(
        "SELECT turn_number, snapshot_json FROM state_roots WHERE branch_id=? AND turn_number<=?",
        (branch_id, turn_number),
    ).fetchone()
    anchors = [row for row in (snapshot_anchor, root_anchor) if row is not None]
    anchor = max(anchors, key=lambda row: row["turn_number"]) if anchors else None
    if anchor is None:
        raise ValueError("the selected turn has no recoverable state anchor")
    data = json.loads(anchor["snapshot_json"])
    deltas = db.execute(
        """SELECT delta_json FROM state_deltas WHERE branch_id=?
           AND turn_number>? AND turn_number<=? ORDER BY turn_number""",
        (branch_id, anchor["turn_number"], turn_number),
    ).fetchall()
    for row in deltas:
        data = apply_delta(data, json.loads(row["delta_json"]))
    return data


def summarize_cast_changes(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return player-facing evidence of automatic person continuity updates."""
    previous = {person["id"]: person for person in before}
    current = {person["id"]: person for person in after}
    watched = (
        "name", "role", "status", "tier", "relationship", "location", "activity",
        "objective", "availability", "next_move", "anchor", "pinned",
    )
    changes: list[dict[str, Any]] = []
    for person_id, person in current.items():
        old = previous.get(person_id)
        if old is None:
            changes.append({
                "kind": "created",
                "id": person_id,
                "name": person["name"],
                "status": person["status"],
                "role": person.get("role", ""),
                "relationship": person.get("relationship", ""),
            })
            continue
        fields = []
        for field in watched:
            if old.get(field) != person.get(field):
                fields.append({"field": field, "before": old.get(field), "after": person.get(field)})
        old_memories = old.get("memories", [])
        new_memories = person.get("memories", [])
        if old_memories != new_memories and new_memories:
            old_texts = {item.get("text") for item in old_memories if isinstance(item, dict)}
            added = [item for item in new_memories if isinstance(item, dict) and item.get("text") not in old_texts]
            for memory in added[:2]:
                fields.append({"field": "memory", "before": None, "after": memory.get("text", "")})
        if fields:
            changes.append({"kind": "updated", "id": person_id, "name": person["name"], "fields": fields})
    return changes


def commit_turn(args: argparse.Namespace) -> None:
    manifest = load_json(args.manifest)
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    cast_before = cast_rows(db, campaign, branch["id"])
    required = ("player_action", "narration")
    if missing := [field for field in required if not manifest.get(field)]:
        raise ValueError(f"manifest missing: {', '.join(missing)}")
    with db:
        previous = db.execute("SELECT MAX(turn_number) AS number FROM turns WHERE branch_id = ?", (branch["id"],)).fetchone()["number"]
        turn_number = max(previous or 0, branch["base_turn_number"]) + 1
        turn_id = f"{branch['id']}:turn:{turn_number}"
        before = snapshot(db, branch["id"])
        scene = manifest.get("scene", {})
        scene = dict(scene) if isinstance(scene, dict) else {}
        previous_scene = current_story_scene(db, branch)
        scene["state"] = normalize_scene_state(scene, normalize_scene_state(previous_scene))
        scene["model"] = normalize_scene_model(scene, normalize_scene_model(previous_scene))
        scene["gm_move"] = normalize_gm_move(scene)
        player_row = db.execute(
            "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'",
            (branch["id"],),
        ).fetchone()
        prior_player_state = json.loads(player_row["state_json"]) if player_row else {}
        previous_location_name = canonical_location(str(
            prior_player_state.get("location") or previous_scene.get("location") or ""
        ).strip())
        previous_place: Optional[dict[str, Any]] = None
        previous_location_id = stable_record_id(prior_player_state.get("location_id"))
        known_places = location_rows(db, campaign, branch["id"])
        if previous_location_id:
            previous_place = next((item for item in known_places if item["id"] == previous_location_id), None)
        if previous_place is None and previous_location_name and previous_location_name.casefold() != "unknown":
            previous_place = ensure_location_instance(
                db, campaign, branch["id"], previous_location_name, turn_number,
                {"name": previous_location_name}, arrived=True,
            )

        requested_location = canonical_location(str(scene.get("location") or previous_location_name).strip())
        current_place: Optional[dict[str, Any]] = None
        if requested_location and requested_location.casefold() != "unknown":
            raw_location_record = scene.get("location_record", {})
            raw_location_record = dict(raw_location_record) if isinstance(raw_location_record, dict) else {}
            if scene.get("location_id") and not raw_location_record.get("id"):
                raw_location_record["id"] = scene.get("location_id")
            current_place = ensure_location_instance(
                db, campaign, branch["id"], requested_location, turn_number,
                raw_location_record, arrived=False,
            )
            is_arrival = (
                not current_place.get("visited")
                or previous_place is None
                or previous_place["id"] != current_place["id"]
            )
            if is_arrival:
                current_place = ensure_location_instance(
                    db, campaign, branch["id"], requested_location, turn_number,
                    raw_location_record, arrived=True,
                )
            scene["location"] = current_place["name"]
            scene["location_id"] = current_place["id"]
            scene["location_record"] = {
                key: current_place[key] for key in (
                    "id", "name", "kind", "parent_id", "parent_name", "description",
                    "atmosphere", "features", "aliases", "status", "current_summary", "access",
                ) if current_place.get(key) not in (None, "", [])
            }
            if previous_place and previous_place["id"] != current_place["id"]:
                route = ensure_route_instance(
                    db, campaign, branch["id"], previous_place, current_place,
                    turn_number, scene.get("route_record"),
                )
                scene["route_id"] = route["id"]
        resolution = scene.get("resolution", {})
        if not isinstance(resolution, dict):
            raise ValueError("scene resolution must be an object")
        consequences = resolution.get("consequences", [])
        if not isinstance(consequences, list):
            raise ValueError("resolution consequences must be a list")
        db.execute(
            """INSERT INTO turns(id, branch_id, turn_number, game_time, player_action, narration, scene_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (turn_id, branch["id"], turn_number, manifest.get("game_time"), manifest["player_action"], manifest["narration"], json.dumps(scene, ensure_ascii=False), now()),
        )
        for entity in manifest.get("entities", []):
            if entity.get("type") in {"location", "route"}:
                continue
            upsert_entity(db, campaign, branch["id"], entity, turn_number)
        for update in manifest.get("state_updates", []):
            patch_state(db, branch["id"], update, turn_number)
        if current_place:
            patch_state(db, branch["id"], {
                "entity_id": "player",
                "patch": {"location": current_place["name"], "location_id": current_place["id"]},
            }, turn_number)
        consequence_view = apply_player_consequences(
            db, branch["id"], consequences, bool(resolution.get("high_stakes", False)),
            normalize_scene_state(previous_scene)["threat"], turn_number,
        )
        for index, event in enumerate(manifest.get("events", []), 1):
            event_id = event.get("id", f"{turn_id}:event:{index}")
            db.execute(
                """INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (event_id, branch["id"], turn_id, event.get("kind", "scene_event"), event["description"], event.get("truth_status", "canonical"), event.get("visibility", "public_world"), json.dumps(event.get("witnesses", []), ensure_ascii=False), json.dumps(event.get("related_entities", []), ensure_ascii=False), json.dumps(event.get("tags", []), ensure_ascii=False), int(event.get("importance", 5)), now()),
            )
        for index, fact in enumerate(manifest.get("facts", []), 1):
            fact_id = fact.get("id", f"{turn_id}:fact:{index}")
            db.execute(
                """INSERT INTO facts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (fact_id, branch["id"], turn_number, fact.get("subject_id"), fact["predicate"], json.dumps(fact.get("value"), ensure_ascii=False), fact["text"], fact.get("truth_status", "canonical"), fact.get("visibility", "public_world"), json.dumps(fact.get("witnesses", []), ensure_ascii=False), json.dumps(fact.get("tags", []), ensure_ascii=False), int(fact.get("importance", 5)), fact.get("status", "active")),
            )
        for index, belief in enumerate(manifest.get("beliefs", []), 1):
            belief_id = belief.get("id", f"{turn_id}:belief:{index}")
            db.execute(
                """INSERT INTO beliefs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (belief_id, branch["id"], belief["actor_id"], turn_number, belief["text"], belief.get("truth_status", "belief"), belief.get("source_event_id"), json.dumps(belief.get("tags", []), ensure_ascii=False), int(belief.get("importance", 5)), belief.get("status", "active")),
            )
        for thread in manifest.get("threads", []):
            thread_id = slug(thread["id"])
            action = thread.get("action", "open")
            if action == "resolve":
                db.execute("UPDATE story_threads SET status='resolved', last_advanced_turn=? WHERE branch_id=? AND id=?", (turn_number, branch["id"], thread_id))
                continue
            db.execute(
                """INSERT INTO story_threads VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(branch_id, id) DO UPDATE SET kind=excluded.kind, title=excluded.title,
                   status=excluded.status, stakes=excluded.stakes, summary=excluded.summary,
                   related_entities_json=excluded.related_entities_json, urgency=excluded.urgency,
                   last_advanced_turn=excluded.last_advanced_turn""",
                (branch["id"], thread_id, thread.get("kind", "question"), thread["title"], thread.get("status", "active"), thread.get("stakes", ""), thread.get("summary", ""), json.dumps(thread.get("related_entities", []), ensure_ascii=False), int(thread.get("urgency", 5)), turn_number),
            )
        after = snapshot(db, branch["id"])
        db.execute(
            "INSERT INTO state_deltas(branch_id, turn_id, turn_number, delta_json) VALUES (?, ?, ?, ?)",
            (branch["id"], turn_id, turn_number, json.dumps(state_delta(before, after), ensure_ascii=False)),
        )
        if (turn_number - branch["base_turn_number"]) % SNAPSHOT_INTERVAL == 0:
            write_snapshot(db, branch["id"], turn_id, turn_number, after)
    cast_changes = summarize_cast_changes(cast_before, cast_rows(db, campaign, branch["id"]))
    print(json.dumps({
        "turn_number": turn_number,
        "turn_id": turn_id,
        "timeline": branch["name"],
        "scene_state": scene["state"],
        "scene_model": scene["model"],
        "gm_move": scene["gm_move"],
        "consequences": consequence_view,
        "cast_changes": cast_changes,
    }, ensure_ascii=False))


def create_branch(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    new_name = slug(args.name)
    db = connect(args.db)
    source = branch_row(db, campaign, args.branch)
    turn = fetchone(
        db,
        "SELECT * FROM turns WHERE branch_id = ? AND turn_number = ?",
        (source["id"], args.from_turn),
    )
    target_id = f"{campaign}:{new_name}"
    with db:
        db.execute(
            "INSERT INTO branches(id, campaign_id, name, parent_branch_id, forked_from_turn_id, base_turn_number, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (target_id, campaign, new_name, source["id"], turn["id"], turn["turn_number"], now()),
        )
        data = state_at(db, source["id"], turn["turn_number"])
        restore_snapshot(db, target_id, data)
        # Every derived timeline starts with an anchor at its fork point.
        write_root(db, target_id, turn["turn_number"], snapshot(db, target_id))
        db.execute("UPDATE campaigns SET active_branch_id = ? WHERE id = ?", (target_id, campaign))
    print(f"Created and checked out branch '{new_name}' from turn {turn['turn_number']} of '{source['name']}'")


def checkout(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    with db:
        db.execute("UPDATE campaigns SET active_branch_id = ? WHERE id = ?", (branch["id"], campaign))
    print(f"Checked out branch '{branch['name']}'")


def create_checkpoint(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    name = args.name.strip()
    if not name:
        raise ValueError("checkpoint name cannot be empty")
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    turn = db.execute(
        "SELECT * FROM turns WHERE branch_id=? ORDER BY turn_number DESC LIMIT 1", (branch["id"],)
    ).fetchone()
    if turn is None:
        raise ValueError("play at least one turn before creating a checkpoint")
    state_at(db, branch["id"], turn["turn_number"])
    checkpoint_id = f"{campaign}:checkpoint:{uuid4().hex}"
    with db:
        db.execute(
            "INSERT INTO checkpoints(id, campaign_id, branch_id, turn_id, turn_number, name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (checkpoint_id, campaign, branch["id"], turn["id"], turn["turn_number"], name, now()),
        )
    print(f"Saved checkpoint '{name}' at turn {turn['turn_number']} on '{branch['name']}'")


def list_checkpoints(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    rows = db.execute(
        """SELECT c.id, c.name, c.turn_number, c.created_at, b.name AS branch_name
           FROM checkpoints c JOIN branches b ON b.id=c.branch_id
           WHERE c.campaign_id=? ORDER BY c.created_at DESC""",
        (campaign,),
    ).fetchall()
    if args.json:
        print(json.dumps([dict(row) for row in rows], ensure_ascii=False))
        return
    if not rows:
        print("No checkpoints.")
        return
    for row in rows:
        print(f"{row['id']}  {row['name']} — {row['branch_name']} turn {row['turn_number']}")


def restore_checkpoint(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    new_name = slug(args.name)
    db = connect(args.db)
    checkpoint = fetchone(db, "SELECT * FROM checkpoints WHERE campaign_id=? AND id=?", (campaign, args.checkpoint))
    source = fetchone(db, "SELECT * FROM branches WHERE id=?", (checkpoint["branch_id"],))
    turn = fetchone(db, "SELECT * FROM turns WHERE id=?", (checkpoint["turn_id"],))
    target_id = f"{campaign}:{new_name}"
    with db:
        db.execute(
            "INSERT INTO branches(id, campaign_id, name, parent_branch_id, forked_from_turn_id, base_turn_number, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (target_id, campaign, new_name, source["id"], turn["id"], turn["turn_number"], now()),
        )
        data = state_at(db, source["id"], turn["turn_number"])
        restore_snapshot(db, target_id, data)
        write_root(db, target_id, turn["turn_number"], snapshot(db, target_id))
        db.execute("UPDATE campaigns SET active_branch_id=? WHERE id=?", (target_id, campaign))
    print(f"Restored checkpoint '{checkpoint['name']}' as timeline '{new_name}'")


def delete_checkpoint(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    with db:
        deleted = db.execute("DELETE FROM checkpoints WHERE campaign_id=? AND id=?", (campaign, args.checkpoint)).rowcount
    if not deleted:
        raise ValueError("checkpoint does not exist")
    print("Deleted checkpoint marker. Story data was unchanged.")


def delete_branch(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    target = branch_row(db, campaign, args.branch)
    active = branch_row(db, campaign, None)
    if target["id"] == active["id"]:
        raise ValueError("switch to another timeline before deleting this one")
    child = db.execute("SELECT 1 FROM branches WHERE parent_branch_id=?", (target["id"],)).fetchone()
    if child:
        raise ValueError("delete child timelines before deleting this one")
    with db:
        db.execute("DELETE FROM chapter_summaries WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM checkpoints WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM events WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM state_deltas WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM state_roots WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM snapshots WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM turns WHERE branch_id=?", (target["id"],))
        for table in STATE_TABLES:
            db.execute(f"DELETE FROM {table} WHERE branch_id=?", (target["id"],))
        db.execute("DELETE FROM branches WHERE id=?", (target["id"],))
    db.execute("VACUUM")
    print(f"Deleted timeline '{target['name']}' and reclaimed unused SQLite pages.")


def restart_campaign(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    start = db.execute("SELECT * FROM campaign_starts WHERE campaign_id=?", (campaign,)).fetchone()
    if start is None:
        # Campaigns created before save slots existed have no immutable opening
        # record. Preserve their current player setup once so future restarts
        # are still possible without touching other campaign data.
        active = branch_row(db, campaign, None)
        player = fetchone(db, "SELECT * FROM entities WHERE campaign_id=? AND id='player'", (campaign,))
        state = db.execute("SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'", (active["id"],)).fetchone()
        profile = json.loads(player["profile_json"])
        location = json.loads(state["state_json"]).get("location", "unknown") if state else "unknown"
        with db:
            db.execute(
            "INSERT INTO campaign_starts(campaign_id, player_name, player_concept, starting_location, character_json) VALUES (?, ?, ?, ?, ?)",
                (campaign, player["name"], profile.get("concept", "adventurer"), location, json.dumps(profile, ensure_ascii=False)),
            )
        start = fetchone(db, "SELECT * FROM campaign_starts WHERE campaign_id=?", (campaign,))
    branch_id = f"{campaign}:main"
    with db:
        db.execute("DELETE FROM checkpoints WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM chapter_summaries WHERE campaign_id=?", (campaign,))
        branch_ids = [row["id"] for row in db.execute("SELECT id FROM branches WHERE campaign_id=?", (campaign,))]
        for old_branch_id in branch_ids:
            db.execute("DELETE FROM events WHERE branch_id=?", (old_branch_id,))
            db.execute("DELETE FROM state_deltas WHERE branch_id=?", (old_branch_id,))
            db.execute("DELETE FROM state_roots WHERE branch_id=?", (old_branch_id,))
            db.execute("DELETE FROM snapshots WHERE branch_id=?", (old_branch_id,))
            db.execute("DELETE FROM turns WHERE branch_id=?", (old_branch_id,))
            for table in STATE_TABLES:
                db.execute(f"DELETE FROM {table} WHERE branch_id=?", (old_branch_id,))
        db.execute("DELETE FROM branches WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM entities WHERE campaign_id=?", (campaign,))
        db.execute(
            "INSERT INTO branches(id, campaign_id, name, base_turn_number, created_at) VALUES (?, ?, 'main', 0, ?)",
            (branch_id, campaign, now()),
        )
        character = json.loads(start["character_json"] or "{}")
        if not isinstance(character, dict):
            character = {"concept": start["player_concept"]}
        setup = normalize_initial_setup(json.loads(start["setup_json"] or "{}"))
        install_opening_state(
            db, campaign, branch_id, start["player_name"], character,
            start["starting_location"], setup,
        )
        write_root(db, branch_id, 0, snapshot(db, branch_id))
        db.execute("UPDATE campaigns SET active_branch_id=? WHERE id=?", (branch_id, campaign))
    db.execute("VACUUM")
    print("Restarted this campaign from its original setup and reclaimed unused SQLite pages.")


def compact_storage(args: argparse.Namespace) -> None:
    """Convert legacy per-turn snapshots into anchors plus state deltas.

    The operation is lossless: each removable full snapshot first becomes a
    row-level delta from the previous materialized state. It is useful for
    campaigns created before compact journals were introduced.
    """
    campaign = slug(args.campaign)
    db = connect(args.db)
    branches = db.execute("SELECT * FROM branches WHERE campaign_id=?", (campaign,)).fetchall()
    created_deltas = 0
    removed_snapshots = 0
    with db:
        for branch in branches:
            root = db.execute("SELECT snapshot_json FROM state_roots WHERE branch_id=?", (branch["id"],)).fetchone()
            previous_data = json.loads(root["snapshot_json"]) if root else None
            rows = db.execute(
                "SELECT * FROM snapshots WHERE branch_id=? ORDER BY turn_number", (branch["id"],)
            ).fetchall()
            for row in rows:
                current_data = json.loads(row["snapshot_json"])
                has_delta = db.execute(
                    "SELECT 1 FROM state_deltas WHERE branch_id=? AND turn_id=?", (branch["id"], row["turn_id"])
                ).fetchone()
                if not has_delta and previous_data is not None:
                    db.execute(
                        "INSERT INTO state_deltas(branch_id, turn_id, turn_number, delta_json) VALUES (?, ?, ?, ?)",
                        (branch["id"], row["turn_id"], row["turn_number"], json.dumps(state_delta(previous_data, current_data), ensure_ascii=False)),
                    )
                    created_deltas += 1
                # A branch without a root needs its first historical snapshot
                # as its recoverable starting anchor. Periodic anchors remain.
                is_first_anchor = previous_data is None
                is_periodic_anchor = (row["turn_number"] - branch["base_turn_number"]) % SNAPSHOT_INTERVAL == 0
                if not is_first_anchor and not is_periodic_anchor:
                    db.execute("DELETE FROM snapshots WHERE branch_id=? AND turn_id=?", (branch["id"], row["turn_id"]))
                    removed_snapshots += 1
                previous_data = current_data
    db.execute("VACUUM")
    print(json.dumps({"created_deltas": created_deltas, "removed_snapshots": removed_snapshots}, ensure_ascii=False))


def relevant_rows(db: sqlite3.Connection, query: str, branch_id: str, action: str, limit: int) -> list[sqlite3.Row]:
    terms = {word.lower() for word in re.findall(r"[\w\u4e00-\u9fff]{2,}", action)}
    rows = db.execute(query, (branch_id,)).fetchall()
    def score(row: sqlite3.Row) -> tuple[int, int]:
        haystack = " ".join(str(value) for value in row).lower()
        return (sum(term in haystack for term in terms), int(row["importance"]))
    return sorted(rows, key=score, reverse=True)[:limit]


def cast_for_brief(db: sqlite3.Connection, campaign: str, branch_id: str, scene: dict[str, Any], action: str) -> list[dict[str, Any]]:
    """Choose the small group of people whose continuity affects this turn."""
    people = [person for person in cast_rows(db, campaign, branch_id) if person["status"] not in {"archived", "deceased"}]
    selected: list[dict[str, Any]] = []
    chosen: set[str] = set()

    def add(person: dict[str, Any]) -> None:
        if person["id"] not in chosen and len(selected) < MAX_CAST_CONTEXT:
            selected.append(person)
            chosen.add(person["id"])

    for person in [person for person in people if person["status"] == "party"][:MAX_PARTY_CONTEXT]:
        add(person)
    for person in [person for person in people if person["status"] == "core"][:2]:
        add(person)
    for person in [person for person in people if person["pinned"] and person["status"] not in {"party", "core"}][:2]:
        add(person)
    present = {str(value) for value in scene.get("present_entities", []) if isinstance(value, str)}
    for person in people:
        if person["id"] in present:
            add(person)
    terms = {word.lower() for word in re.findall(r"[\w\u4e00-\u9fff]{2,}", "\n".join([action, str(scene.get("location", "")), str(scene.get("immediate_situation", ""))]))}
    def score(person: dict[str, Any]) -> tuple[int, int, int]:
        haystack = " ".join(str(value) for key, value in person.items() if key != "memories").lower()
        memory_text = " ".join(str(memory.get("text", "")) for memory in person["memories"]).lower()
        return (sum(term in haystack or term in memory_text for term in terms), int(person["pinned"]), person["updated_turn"])
    for person in sorted(people, key=score, reverse=True):
        if score(person)[0] > 0:
            add(person)
    return selected


def places_for_brief(
    db: sqlite3.Connection,
    campaign: str,
    branch_id: str,
    current_id: str,
    action: str,
) -> tuple[Optional[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Retrieve a small location graph around the current action."""
    places = location_rows(db, campaign, branch_id)
    by_id = {item["id"]: item for item in places}
    current = by_id.get(current_id)
    selected: list[dict[str, Any]] = []
    chosen: set[str] = set()

    def add(place: Optional[dict[str, Any]]) -> None:
        if place and place["id"] not in chosen and len(selected) < MAX_PLACE_CONTEXT:
            selected.append(place)
            chosen.add(place["id"])

    add(current)
    if current:
        add(by_id.get(current["parent_id"]))
    action_folded = action.casefold()
    for place in sorted(places, key=lambda item: item["last_visited_turn"], reverse=True):
        names = [place["name"], *[str(alias) for alias in place.get("aliases", [])]]
        if any(name and name.casefold() in action_folded for name in names):
            add(place)
    routes = route_rows(db, campaign, branch_id)
    connected: list[dict[str, Any]] = []
    if current:
        for route in sorted(routes, key=lambda item: item["last_turn"], reverse=True):
            if current["id"] not in {route["from_id"], route["to_id"]}:
                continue
            other_id = route["to_id"] if route["from_id"] == current["id"] else route["from_id"]
            other = by_id.get(other_id)
            if other:
                add(other)
                connected.append(route)
    relevant_routes = [
        route for route in routes
        if route in connected or (route["from_id"] in chosen and route["to_id"] in chosen)
    ][:MAX_PLACE_CONTEXT]
    return current, selected, relevant_routes


# Possessions deliberately reuse the durable entity ledger. This means an item
# travels with the same branch, checkpoint, and rollback machinery as people
# and places; there is no second inventory database that can drift out of sync.
INACTIVE_ITEM_STATUSES = {"consumed", "lost", "destroyed", "archived"}


def resource_state(player_state: dict[str, Any] | None) -> dict[str, Any]:
    """Return a stable branch-local wallet and bounded transaction history."""
    state = player_state if isinstance(player_state, dict) else {}
    mechanics = state.get("mechanics", {})
    mechanics = mechanics if isinstance(mechanics, dict) else {}
    resources = mechanics.get("resources", {})
    resources = resources if isinstance(resources, dict) else {}
    wallet = resources.get("wallet", {})
    wallet = wallet if isinstance(wallet, dict) else {}
    try:
        balance = max(0, min(MAX_RESOURCE_BALANCE, int(wallet.get("balance", 0))))
    except (TypeError, ValueError):
        balance = 0
    transactions: list[dict[str, Any]] = []
    for item in resources.get("transactions", []) if isinstance(resources.get("transactions", []), list) else []:
        if not isinstance(item, dict) or not str(item.get("id", "")).strip():
            continue
        transactions.append(dict(item))
    return {
        "wallet": {"currency": "copper", "balance": balance},
        "transactions": transactions[-MAX_TRANSACTION_HISTORY:],
    }


def player_state_row(db: sqlite3.Connection, branch_id: str) -> tuple[sqlite3.Row, dict[str, Any]]:
    row = fetchone(
        db,
        "SELECT * FROM entity_states WHERE branch_id=? AND entity_id='player'",
        (branch_id,),
    )
    return row, json.loads(row["state_json"])


def current_story_turn(db: sqlite3.Connection, branch: sqlite3.Row) -> Optional[sqlite3.Row]:
    row = db.execute(
        """SELECT * FROM turns WHERE branch_id=? AND narration<>''
           ORDER BY turn_number DESC LIMIT 1""",
        (branch["id"],),
    ).fetchone()
    if row is None and branch["forked_from_turn_id"]:
        row = db.execute("SELECT * FROM turns WHERE id=?", (branch["forked_from_turn_id"],)).fetchone()
    return row


def pending_trade_offers(
    db: sqlite3.Connection,
    campaign: str,
    branch: sqlite3.Row,
    resources: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Read only the offers attached to the current narrated scene."""
    turn = current_story_turn(db, branch)
    if turn is None:
        return []
    scene = json.loads(turn["scene_json"])
    raw_offers = scene.get("_trade_offers", [])
    if not isinstance(raw_offers, list):
        return []
    accepted = {
        str(item.get("offer_id", ""))
        for item in (resources or {}).get("transactions", [])
        if isinstance(item, dict)
    }
    possessions = {item["id"]: item for item in possession_rows(db, campaign, branch["id"])}
    offers: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in raw_offers[:4]:
        if not isinstance(source, dict):
            continue
        offer_id = str(source.get("id", "")).strip()
        kind = str(source.get("kind", "")).strip()
        if not re.fullmatch(r"trade_[a-f0-9]{32}", offer_id) or kind not in TRADE_KINDS:
            continue
        if offer_id in accepted or offer_id in seen:
            continue
        try:
            quantity = max(1, min(999, int(source.get("quantity", 1))))
            unit_price = int(source.get("unit_price", 0))
        except (TypeError, ValueError):
            continue
        if unit_price <= 0 or unit_price > MAX_RESOURCE_BALANCE or unit_price * quantity > MAX_RESOURCE_BALANCE:
            continue
        offer = {
            "id": offer_id,
            "kind": kind,
            "counterparty_id": str(source.get("counterparty_id", "")).strip()[:80],
            "counterparty": str(source.get("counterparty", "")).strip()[:120],
            "quantity": quantity,
            "unit_price": unit_price,
            "total": unit_price * quantity,
            "currency": "copper",
            "reason": str(source.get("reason", "")).strip()[:300],
            "source_turn_id": str(turn["id"]),
            "source_turn": int(turn["turn_number"]),
        }
        if not offer["counterparty"]:
            continue
        if kind == "buy":
            item = source.get("item", {})
            if not isinstance(item, dict) or not str(item.get("name", "")).strip():
                continue
            classification = classify_item(item)
            if not classification["base_type_id"]:
                continue
            rarity = classification["rarity"]
            rarity_context = str(item.get("rarity_context", "everyday"))
            permitted_contexts = {
                "common": {"everyday", "specialist_access", "restricted_source", "historic_provenance", "mythic_provenance", "existing_record"},
                "rare": {"specialist_access", "restricted_source", "historic_provenance", "mythic_provenance", "existing_record"},
                "exceptional": {"restricted_source", "historic_provenance", "mythic_provenance", "existing_record"},
                "legendary": {"historic_provenance", "mythic_provenance", "existing_record"},
                "mythic": {"mythic_provenance", "existing_record"},
            }
            if rarity_context not in permitted_contexts.get(rarity, set()):
                continue
            if rarity != "common" and not str(item.get("rarity_basis", "")).strip():
                continue
            offer["item"] = {
                **{key: value for key, value in item.items() if key in {
                    "name", "category", "base_type_id", "rarity", "rarity_known",
                    "rarity_context", "rarity_basis", "description", "known_purpose", "importance",
                }},
                **classification,
            }
        elif kind == "sell":
            item_id = str(source.get("item_id", "")).strip()
            item = possessions.get(item_id)
            if not item or item["holder"] != "player" or item["status"] == "given":
                continue
            offer["item_id"] = item_id
            offer["item_name"] = item["name"]
        offers.append(offer)
        seen.add(offer_id)
    return offers


def resources_payload(db: sqlite3.Connection, campaign: str, branch: sqlite3.Row) -> dict[str, Any]:
    _, player_state = player_state_row(db, branch["id"])
    resources = resource_state(player_state)
    return {
        "timeline": branch["name"],
        **resources,
        "pending_offers": pending_trade_offers(db, campaign, branch, resources),
    }


def list_resources(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    print(json.dumps(resources_payload(db, campaign, branch), ensure_ascii=False))


def commit_trade(args: argparse.Namespace) -> None:
    """Atomically settle one current-scene offer and its item transfer."""
    campaign = slug(args.campaign)
    offer_id = str(args.offer).strip()
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    player_row, player_state = player_state_row(db, branch["id"])
    resources = resource_state(player_state)
    offer = next(
        (item for item in pending_trade_offers(db, campaign, branch, resources) if item["id"] == offer_id),
        None,
    )
    if offer is None:
        raise ValueError("trade offer is unavailable, expired, or already completed")

    kind = offer["kind"]
    total = int(offer["total"])
    balance = int(resources["wallet"]["balance"])
    if kind in {"buy", "payment"} and balance < total:
        raise ValueError("insufficient funds for this trade")

    possessions = {item["id"]: item for item in possession_rows(db, campaign, branch["id"])}
    sold_item = possessions.get(str(offer.get("item_id", ""))) if kind == "sell" else None
    if kind == "sell" and (
        sold_item is None or sold_item["holder"] != "player" or sold_item["status"] == "given"
        or sold_item["quantity"] < offer["quantity"]
    ):
        raise ValueError("the item or requested quantity is no longer available")

    with db:
        previous = db.execute(
            "SELECT MAX(turn_number) AS number FROM turns WHERE branch_id=?", (branch["id"],)
        ).fetchone()["number"]
        turn_number = max(previous or 0, branch["base_turn_number"]) + 1
        turn_id = f"{branch['id']}:turn:{turn_number}"
        before = snapshot(db, branch["id"])
        item_id = ""
        item_name = ""

        if kind == "buy":
            item = offer["item"]
            item_id = f"item_trade_{uuid4().hex}"
            item_name = str(item["name"]).strip()[:120]
            profile = {
                "category": str(item.get("category", "ordinary")) if str(item.get("category", "ordinary")) in {"important", "clue", "gear", "ordinary"} else "ordinary",
                "base_type_id": item["base_type_id"],
                "rarity": item["rarity"],
                "rarity_known": item.get("rarity_known", True) is not False,
            }
            for key, limit in (("rarity_basis", 500), ("description", 1200), ("known_purpose", 1200)):
                value = str(item.get(key, "")).strip()[:limit]
                if value:
                    profile[key] = value
            try:
                importance = max(0, min(10, int(item.get("importance", 3))))
            except (TypeError, ValueError):
                importance = 3
            upsert_entity(db, campaign, branch["id"], {
                "id": item_id,
                "type": "item",
                "name": item_name,
                "profile": profile,
                "state": {
                    "holder": "player", "location": "", "status": "carried",
                    "importance": importance, "quantity": offer["quantity"], "equipped_as": "",
                },
            }, turn_number)
        elif kind == "sell" and sold_item is not None:
            item_id = sold_item["id"]
            item_name = sold_item["name"]
            remaining = sold_item["quantity"] - offer["quantity"]
            if remaining:
                state = {
                    "holder": "player", "location": sold_item["location"],
                    "status": sold_item["status"], "importance": sold_item["importance"],
                    "quantity": remaining, "equipped_as": sold_item["equipped_as"],
                }
            else:
                counterparty_id = offer["counterparty_id"]
                recorded_person = db.execute(
                    """SELECT 1 FROM entities e JOIN entity_states s ON s.entity_id=e.id
                       WHERE e.campaign_id=? AND e.id=? AND e.type IN ('npc', 'companion') AND s.branch_id=?""",
                    (campaign, counterparty_id, branch["id"]),
                ).fetchone() if counterparty_id else None
                state = {
                    "holder": counterparty_id if recorded_person else "world",
                    "location": str(player_state.get("location", ""))[:240],
                    "status": "given", "importance": sold_item["importance"],
                    "quantity": sold_item["quantity"], "equipped_as": "",
                }
            upsert_entity(db, campaign, branch["id"], {
                "id": item_id, "type": "item", "name": item_name, "profile": {}, "state": state,
            }, turn_number)

        signed_amount = total if kind in {"sell", "reward"} else -total
        new_balance = balance + signed_amount
        if new_balance < 0 or new_balance > MAX_RESOURCE_BALANCE:
            raise ValueError("wallet balance would exceed the supported range")
        transaction = {
            "id": f"transaction_{uuid4().hex}",
            "offer_id": offer_id,
            "kind": kind,
            "amount": signed_amount,
            "balance_after": new_balance,
            "counterparty_id": offer["counterparty_id"],
            "counterparty": offer["counterparty"],
            "item_id": item_id,
            "item_name": item_name,
            "quantity": offer["quantity"],
            "unit_price": offer["unit_price"],
            "reason": offer["reason"],
            "source_turn_id": offer["source_turn_id"],
            "source_turn": offer["source_turn"],
            "recorded_turn": turn_number,
            "created_at": now(),
        }
        resources["wallet"]["balance"] = new_balance
        resources["transactions"] = [*resources["transactions"], transaction][-MAX_TRANSACTION_HISTORY:]
        mechanics = player_state.get("mechanics", {})
        mechanics = dict(mechanics) if isinstance(mechanics, dict) else {}
        mechanics["resources"] = resources
        player_state["mechanics"] = mechanics
        db.execute(
            "UPDATE entity_states SET state_json=?, updated_turn=? WHERE branch_id=? AND entity_id='player'",
            (json.dumps(player_state, ensure_ascii=False), turn_number, branch["id"]),
        )

        story_turn = current_story_turn(db, branch)
        scene = json.loads(story_turn["scene_json"]) if story_turn else {}
        scene["local_record"] = "trade"
        scene["trade_receipt"] = transaction
        db.execute(
            """INSERT INTO turns(id, branch_id, turn_number, game_time, player_action, narration, scene_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (turn_id, branch["id"], turn_number, story_turn["game_time"] if story_turn else None,
             "[Local trade completed]", "", json.dumps(scene, ensure_ascii=False), now()),
        )
        after = snapshot(db, branch["id"])
        db.execute(
            "INSERT INTO state_deltas(branch_id, turn_id, turn_number, delta_json) VALUES (?, ?, ?, ?)",
            (branch["id"], turn_id, turn_number, json.dumps(state_delta(before, after), ensure_ascii=False)),
        )
        if (turn_number - branch["base_turn_number"]) % SNAPSHOT_INTERVAL == 0:
            write_snapshot(db, branch["id"], turn_id, turn_number, after)

    print(json.dumps({
        "transaction": transaction,
        "resources": resources_payload(db, campaign, branch),
        "possessions": possessions_payload(db, campaign, branch),
    }, ensure_ascii=False))


def possession_rows(db: sqlite3.Connection, campaign: str, branch_id: str) -> list[dict[str, Any]]:
    rows = db.execute(
        """SELECT e.id, e.name, e.profile_json, s.state_json, s.updated_turn
           FROM entity_states s JOIN entities e ON e.id=s.entity_id AND e.campaign_id=?
           WHERE s.branch_id=? AND e.type='item'""",
        (campaign, branch_id),
    ).fetchall()
    items: list[dict[str, Any]] = []
    for row in rows:
        profile = json.loads(row["profile_json"])
        state = json.loads(row["state_json"])
        if state.get("status", "carried") in INACTIVE_ITEM_STATUSES:
            continue
        importance = state.get("importance", profile.get("importance", 0))
        try:
            importance = max(0, min(10, int(importance)))
        except (TypeError, ValueError):
            importance = 0
        quantity = state.get("quantity", 1)
        try:
            quantity = max(1, int(quantity))
        except (TypeError, ValueError):
            quantity = 1
        classification = classify_item({"name": row["name"], "description": profile.get("description", ""),
                                        "base_type_id": profile.get("base_type_id", ""),
                                        # Records created before rarity existed remain common;
                                        # reading a save must not silently promote an item.
                                        "rarity": profile.get("rarity", "common")})
        items.append({
            "id": row["id"], "name": row["name"],
            "category": str(profile.get("category", "ordinary")),
            **classification,
            "rarity_known": profile.get("rarity_known", True) is not False,
            "rarity_basis": str(profile.get("rarity_basis", "")),
            "type_baseline": baseline_for(classification["base_type_id"]) if classification["base_type_id"] else {},
            "description": str(profile.get("description", profile.get("appearance", ""))),
            "known_purpose": str(profile.get("known_purpose", "")),
            "tags": profile.get("tags", []) if isinstance(profile.get("tags", []), list) else [],
            "status": str(state.get("status", "carried")),
            "holder": str(state.get("holder", "player")),
            "location": str(state.get("location", "")),
            "importance": importance, "quantity": quantity,
            "equipped_as": str(state.get("equipped_as", "")),
            "updated_turn": int(row["updated_turn"]),
        })
    return sorted(items, key=lambda item: (-item["importance"], -item["updated_turn"], item["name"]))


def list_possessions(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    payload = possessions_payload(db, campaign, branch)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    for group, values in payload.items():
        if group == "timeline":
            continue
        print(f"{group.title()}:")
        for item in values:
            print(f"- {item['name']} ({item['status']}; importance {item['importance']})")


def possessions_payload(db: sqlite3.Connection, campaign: str, branch: sqlite3.Row) -> dict[str, Any]:
    items = possession_rows(db, campaign, branch["id"])
    player_items = [item for item in items if item["holder"] == "player" and item["status"] != "given"]
    equipped = [item for item in player_items if item["status"] == "equipped"]
    important = [item for item in player_items if item not in equipped and (item["importance"] >= 7 or item["category"] in {"important", "clue"})]
    carried = [item for item in player_items if item not in equipped and item not in important]
    elsewhere = [item for item in items if item not in player_items]
    return {"timeline": branch["name"], "equipped": equipped, "important": important, "carried": carried, "elsewhere": elsewhere}


def record_local_possession(args: argparse.Namespace) -> None:
    """Create or amend a player-owned item without involving the narrator.

    This creates a silent save revision: it participates in all snapshots and
    checkpoint restores, but is not rendered as a story turn or sent to Codex.
    """
    campaign = slug(args.campaign)
    try:
        source = json.loads(args.item)
    except json.JSONDecodeError as error:
        raise ValueError("item must be valid JSON") from error
    if not isinstance(source, dict):
        raise ValueError("item must be an object")
    name = str(source.get("name", "")).strip()
    if not name or len(name) > 120:
        raise ValueError("item name is required and must be at most 120 characters")
    category = str(source.get("category", "ordinary"))
    if category not in {"important", "clue", "gear", "ordinary"}:
        raise ValueError("unknown item category")
    classification = classify_item(source)
    if not classification["base_type_id"]:
        raise ValueError("item base category cannot be inferred; choose a base category")
    status = str(source.get("status", "carried"))
    if status not in {"carried", "equipped", "concealed", "stored", "consumed", "lost", "given", "destroyed", "archived"}:
        raise ValueError("unknown item status")
    try:
        importance = max(0, min(10, int(source.get("importance", 5))))
        quantity = max(1, min(999, int(source.get("quantity", 1))))
    except (TypeError, ValueError) as error:
        raise ValueError("item importance and quantity must be numbers") from error
    item_id = str(source.get("id", "")).strip()
    if item_id:
        item_id = slug(item_id)
    else:
        item_id = f"item_{uuid4().hex}"
    profile = {"category": category, "base_type_id": classification["base_type_id"],
               "rarity": classification["rarity"],
               "rarity_known": source.get("rarity_known", True) is not False}
    rarity_basis = str(source.get("rarity_basis", "")).strip()[:500]
    if rarity_basis:
        profile["rarity_basis"] = rarity_basis
    description = str(source.get("description", "")).strip()[:1200]
    known_purpose = str(source.get("known_purpose", "")).strip()[:1200]
    if description:
        profile["description"] = description
    if known_purpose:
        profile["known_purpose"] = known_purpose
    holder = str(source.get("holder", "player" if status not in INACTIVE_ITEM_STATUSES | {"given"} else "archive")).strip()
    if holder not in {"player", "world", "archive"}:
        holder = slug(holder)
    location = str(source.get("location", "")).strip()[:240]
    if status == "given" and holder == "player":
        raise ValueError("a given item must name another holder or a location")
    if status in INACTIVE_ITEM_STATUSES:
        holder = "archive"
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    if holder not in {"player", "world", "archive"}:
        person = db.execute(
            """SELECT 1 FROM entities e JOIN entity_states s ON s.entity_id=e.id
               WHERE e.campaign_id=? AND e.id=? AND e.type IN ('npc', 'companion') AND s.branch_id=?""",
            (campaign, holder, branch["id"]),
        ).fetchone()
        if not person:
            raise ValueError("item holder must be a recorded person")
    state = {
        "holder": holder, "location": location,
        "status": status, "importance": importance, "quantity": quantity,
        "equipped_as": str(source.get("equipped_as", "")).strip()[:120],
    }
    with db:
        previous = db.execute("SELECT MAX(turn_number) AS number FROM turns WHERE branch_id=?", (branch["id"],)).fetchone()["number"]
        turn_number = max(previous or 0, branch["base_turn_number"]) + 1
        turn_id = f"{branch['id']}:turn:{turn_number}"
        before = snapshot(db, branch["id"])
        latest = db.execute("SELECT scene_json, game_time FROM turns WHERE branch_id=? ORDER BY turn_number DESC LIMIT 1", (branch["id"],)).fetchone()
        scene = json.loads(latest["scene_json"]) if latest else {}
        scene["local_record"] = "possessions"
        db.execute(
            """INSERT INTO turns(id, branch_id, turn_number, game_time, player_action, narration, scene_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (turn_id, branch["id"], turn_number, latest["game_time"] if latest else None,
             "[Local possessions updated]", "", json.dumps(scene, ensure_ascii=False), now()),
        )
        upsert_entity(db, campaign, branch["id"], {
            "id": item_id, "type": "item", "name": name, "profile": profile, "state": state,
        }, turn_number)
        after = snapshot(db, branch["id"])
        db.execute(
            "INSERT INTO state_deltas(branch_id, turn_id, turn_number, delta_json) VALUES (?, ?, ?, ?)",
            (branch["id"], turn_id, turn_number, json.dumps(state_delta(before, after), ensure_ascii=False)),
        )
        if (turn_number - branch["base_turn_number"]) % SNAPSHOT_INTERVAL == 0:
            write_snapshot(db, branch["id"], turn_id, turn_number, after)
    print(json.dumps({"id": item_id, "turn_number": turn_number}, ensure_ascii=False))


def describe_item_type(args: argparse.Namespace) -> None:
    source = json.loads(args.item)
    if not isinstance(source, dict):
        raise ValueError("item must be an object")
    print(json.dumps(classify_item(source), ensure_ascii=False))


def list_item_types(args: argparse.Namespace) -> None:
    print(json.dumps(item_types(), ensure_ascii=False))


def list_item_rarities(args: argparse.Namespace) -> None:
    print(json.dumps(item_rarities(), ensure_ascii=False))


def list_item_catalog_index(args: argparse.Namespace) -> None:
    print(json.dumps(catalog_index(), ensure_ascii=False))


def list_ability_catalog(args: argparse.Namespace) -> None:
    print(json.dumps(ability_catalog(), ensure_ascii=False))


def list_abilities(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    row = db.execute(
        "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'",
        (branch["id"],),
    ).fetchone()
    player_state = json.loads(row["state_json"]) if row else {}
    payload = {
        "timeline": branch["name"], **abilities_from_player_state(player_state),
        **{key: value for key, value in consequence_state(player_state).items() if key != "loads"},
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    for ability in payload["abilities"]:
        print(f"- {ability['name']} ({ability['mastery_label']})")


def attribute_values(profile: dict[str, Any], state: dict[str, Any]) -> dict[str, int]:
    sources = []
    mechanics = state.get("mechanics", {}) if isinstance(state.get("mechanics", {}), dict) else {}
    for value in (mechanics.get("attributes"), state.get("attributes"), profile.get("attributes")):
        if isinstance(value, dict):
            sources.append(value)
    result: dict[str, int] = {}
    for key in ATTRIBUTE_KEYS:
        for source in sources:
            raw = source.get(key)
            if isinstance(raw, dict):
                raw = raw.get("value")
            if isinstance(raw, (int, float)) and not isinstance(raw, bool) and 1 <= raw:
                result[key] = int(raw)
                break
    return result


def adjudication_context(args: argparse.Namespace) -> None:
    """Return only authoritative IDs and values needed by the local validator."""
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    scene = current_story_scene(db, branch)
    scene_state = normalize_scene_state(scene)
    scene_model = normalize_scene_model(scene)
    rows = db.execute(
        """SELECT e.id, e.type, e.profile_json, s.state_json FROM entities e
           LEFT JOIN entity_states s ON s.entity_id=e.id AND s.branch_id=?
           WHERE e.campaign_id=?""", (branch["id"], campaign),
    ).fetchall()
    attributes: dict[str, dict[str, int]] = {}
    entity_ids: list[str] = []
    player_state: dict[str, Any] = {}
    for row in rows:
        entity_ids.append(row["id"])
        profile = json.loads(row["profile_json"] or "{}")
        state = json.loads(row["state_json"] or "{}")
        values = attribute_values(profile, state)
        if values:
            attributes[row["id"]] = values
        if row["id"] == "player":
            player_state = state
    ability_state = abilities_from_player_state(player_state)
    consequences = consequence_state(player_state)
    specialty_ids: list[str] = []
    raw_specialties = ability_state.get("specialties", [])
    iterable = raw_specialties.values() if isinstance(raw_specialties, dict) else raw_specialties
    for item in iterable if isinstance(iterable, Iterable) and not isinstance(iterable, (str, bytes)) else []:
        value = item.get("id", item.get("name", "")) if isinstance(item, dict) else item
        if str(value).strip():
            specialty_ids.append(str(value).strip())
    possessions = possession_rows(db, campaign, branch["id"])
    active_item_ids = [
        item["id"] for item in possessions
        if item["holder"] == "player" and item["status"] in {"carried", "equipped", "concealed"}
    ]
    payload = {
        "campaign": campaign, "timeline": branch["name"], "threat": scene_state["threat"],
        "attributes": attributes,
        "entities": entity_ids,
        "references": {
            "ability": [item["id"] for item in ability_state["abilities"] if item.get("available", True)],
            "specialty": specialty_ids,
            "item": active_item_ids,
            "entity": entity_ids,
            "scene_element": [item["id"] for item in scene_model["elements"]],
            "scene_participant": [item["id"] for item in scene_model["participants"]],
            "scene_pressure": [item["id"] for item in scene_model["pressures"]],
            "injury": [item["id"] for item in consequences["injuries"]],
            "condition": [item["id"] for item in consequences["conditions"]],
        },
    }
    print(json.dumps(payload, ensure_ascii=False))


def cast_rows(db: sqlite3.Connection, campaign: str, branch_id: str) -> list[dict[str, Any]]:
    """Return the branch-local people ledger in a UI- and prompt-ready shape."""
    rows = db.execute(
        """SELECT e.id, e.type, e.name, e.profile_json, s.state_json, s.updated_turn
           FROM entity_states s JOIN entities e ON e.id=s.entity_id AND e.campaign_id=?
           WHERE s.branch_id=? AND e.type IN ('npc', 'companion')""",
        (campaign, branch_id),
    ).fetchall()
    people: list[dict[str, Any]] = []
    for row in rows:
        profile = json.loads(row["profile_json"])
        state = normalize_npc_state({}, json.loads(row["state_json"]), int(row["updated_turn"]))
        mechanics = abilities_from_player_state(state)
        people.append({
            "id": row["id"], "name": row["name"], "type": row["type"],
            "aliases": profile.get("aliases", []) if isinstance(profile.get("aliases", []), list) else [],
            "description": str(profile.get("description", profile.get("appearance", "")))[:1200],
            "appearance": str(profile.get("appearance", ""))[:1200],
            "personality": str(profile.get("personality", ""))[:1200],
            "background": str(profile.get("background", ""))[:1600],
            "role": str(profile.get("role", ""))[:240],
            "voice": str(profile.get("voice", ""))[:240],
            "ancestry": str(profile.get("ancestry", ""))[:120],
            "gender": str(profile.get("gender", ""))[:80],
            "age_stage": str(profile.get("age_stage", ""))[:120],
            "height_cm": profile.get("height_cm"),
            "weight_kg": profile.get("weight_kg"),
            "attributes": attribute_values(profile, state),
            "abilities": mechanics["abilities"],
            "specialties": mechanics["specialties"],
            "loads": mechanics["loads"],
            "status": state["status"], "tier": state["tier"], "pinned": state["pinned"],
            "relationship": str(state.get("relationship", ""))[:600],
            "location": str(state.get("location", ""))[:240],
            "activity": str(state.get("activity", ""))[:600],
            "objective": str(state.get("objective", ""))[:600],
            "availability": str(state.get("availability", ""))[:240],
            "next_move": str(state.get("next_move", ""))[:600],
            "anchor": str(state.get("anchor", ""))[:900],
            "memories": state["memories"], "updated_turn": int(row["updated_turn"]),
        })
    rank = {"party": 0, "core": 1, "known": 2, "away": 3, "archived": 4, "deceased": 5}
    return sorted(people, key=lambda item: (rank.get(item["status"], 9), not item["pinned"], -item["updated_turn"], item["name"]))


def list_cast(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    people = cast_rows(db, campaign, branch["id"])
    groups = {
        "party": [person for person in people if person["status"] == "party"],
        "core": [person for person in people if person["status"] == "core"],
        "known": [person for person in people if person["status"] == "known"],
        "away": [person for person in people if person["status"] == "away"],
        "archived": [person for person in people if person["status"] in {"archived", "deceased"}],
    }
    payload = {"timeline": branch["name"], "people": people, **groups}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    for group, values in groups.items():
        print(f"{group.title()}:")
        for person in values:
            print(f"- {person['name']} ({person['relationship'] or person['role'] or person['status']})")


def record_local_cast(args: argparse.Namespace) -> None:
    """Create or amend a person without creating a visible narration turn."""
    campaign = slug(args.campaign)
    try:
        source = json.loads(args.person)
    except json.JSONDecodeError as error:
        raise ValueError("person must be valid JSON") from error
    if not isinstance(source, dict):
        raise ValueError("person must be an object")
    name = str(source.get("name", "")).strip()
    if not name or len(name) > 120:
        raise ValueError("person name is required and must be at most 120 characters")
    status = str(source.get("status", "known"))
    if status not in NPC_STATUSES:
        raise ValueError("unknown person status")
    tier = str(source.get("tier", "recurring"))
    if tier not in {"core", "recurring", "background"}:
        raise ValueError("unknown person tier")
    person_id = slug(str(source.get("id", "")).strip()) if source.get("id") else f"npc_{uuid4().hex}"
    aliases = source.get("aliases", [])
    if isinstance(aliases, str):
        aliases = [item.strip() for item in aliases.split(",") if item.strip()]
    aliases = [str(item).strip()[:120] for item in aliases if str(item).strip()][:12] if isinstance(aliases, list) else []
    profile = {"role": str(source.get("role", "")).strip()[:240], "description": str(source.get("description", "")).strip()[:1200], "voice": str(source.get("voice", "")).strip()[:240], "aliases": aliases}
    profile = {key: value for key, value in profile.items() if value}
    state = {
        "status": status, "tier": tier, "pinned": bool(source.get("pinned", status in {"party", "core"})),
        "relationship": str(source.get("relationship", "")).strip()[:600],
        "location": str(source.get("location", "")).strip()[:240],
        "activity": str(source.get("activity", "")).strip()[:600],
        "objective": str(source.get("objective", "")).strip()[:600],
        "availability": str(source.get("availability", "")).strip()[:240],
        "next_move": str(source.get("next_move", "")).strip()[:600],
        "anchor": str(source.get("anchor", "")).strip()[:900],
    }
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    with db:
        previous = db.execute("SELECT MAX(turn_number) AS number FROM turns WHERE branch_id=?", (branch["id"],)).fetchone()["number"]
        turn_number = max(previous or 0, branch["base_turn_number"]) + 1
        turn_id = f"{branch['id']}:turn:{turn_number}"
        before = snapshot(db, branch["id"])
        latest = db.execute("SELECT scene_json, game_time FROM turns WHERE branch_id=? ORDER BY turn_number DESC LIMIT 1", (branch["id"],)).fetchone()
        scene = json.loads(latest["scene_json"]) if latest else {}
        scene["local_record"] = "cast"
        db.execute(
            """INSERT INTO turns(id, branch_id, turn_number, game_time, player_action, narration, scene_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (turn_id, branch["id"], turn_number, latest["game_time"] if latest else None,
             "[Local cast updated]", "", json.dumps(scene, ensure_ascii=False), now()),
        )
        upsert_entity(db, campaign, branch["id"], {"id": person_id, "type": "npc", "name": name, "profile": profile, "state": state}, turn_number)
        after = snapshot(db, branch["id"])
        db.execute("INSERT INTO state_deltas(branch_id, turn_id, turn_number, delta_json) VALUES (?, ?, ?, ?)",
                   (branch["id"], turn_id, turn_number, json.dumps(state_delta(before, after), ensure_ascii=False)))
        if (turn_number - branch["base_turn_number"]) % SNAPSHOT_INTERVAL == 0:
            write_snapshot(db, branch["id"], turn_id, turn_number, after)
    print(json.dumps({"id": person_id, "turn_number": turn_number}, ensure_ascii=False))


def lore_matches(row: sqlite3.Row, scan_text: str) -> bool:
    """Return whether a campaign lore entry is active for this turn.

    This is intentionally a small, deterministic subset of the Character
    Book convention: constant entries always apply; otherwise any primary
    keyword must match, with optional secondary-key gating. Deterministic
    retrieval makes the prompt inspector truthful and keeps lore from being
    silently invented by a semantic search model.
    """
    if not row["enabled"]:
        return False
    if row["constant"]:
        return True
    haystack = scan_text if row["case_sensitive"] else scan_text.lower()
    def prepare(value: str) -> str:
        return value if row["case_sensitive"] else value.lower()
    primary = [prepare(value) for value in json.loads(row["keys_json"]) if value.strip()]
    if not primary or not any(value in haystack for value in primary):
        return False
    if row["selective"]:
        secondary = [prepare(value) for value in json.loads(row["secondary_keys_json"]) if value.strip()]
        return bool(secondary) and any(value in haystack for value in secondary)
    return True


def lore_record_json(row: sqlite3.Row) -> str:
    """Read structured metadata when present; campaign-authored lore predates it."""
    return str(row["record_json"] or "{}") if "record_json" in row.keys() else "{}"


def active_lore(db: sqlite3.Connection, campaign: str, scan_text: str, char_budget: int = 3600) -> tuple[list[sqlite3.Row], int]:
    """Select authored lore within a fixed character budget.

    Character count is a provider-neutral approximation. It is conservative
    for Chinese prose and keeps the ordinary turn prompt bounded even as the
    worldbook grows without limit.
    """
    campaign_rows = db.execute(
        "SELECT * FROM lore_entries WHERE campaign_id=? ORDER BY constant DESC, priority DESC, insertion_order ASC, created_at ASC",
        (campaign,),
    ).fetchall()
    universe = universe_for_campaign(db, campaign)
    universe_rows = db.execute(
        "SELECT * FROM universe_lore_entries WHERE universe_id=? ORDER BY constant DESC, priority DESC, insertion_order ASC, created_at ASC",
        (universe["id"],),
    ).fetchall()
    rows = sorted(
        [*universe_rows, *campaign_rows],
        key=lambda row: (-int(row["constant"]), -int(row["priority"]), int(row["insertion_order"]), row["created_at"]),
    )
    selected: list[sqlite3.Row] = []
    used = 0
    for row in rows:
        if not lore_matches(row, scan_text):
            continue
        cost = len(row["title"]) + len(row["content"]) + len(lore_record_json(row)) + 12
        if selected and used + cost > char_budget:
            continue
        # A single deliberately authored entry is more useful than an empty
        # lore block, even if it alone exceeds the nominal budget.
        selected.append(row)
        used += cost
    return selected, used


def create_lore(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    title = args.title.strip()
    content = args.content.strip()
    if not title or not content:
        raise ValueError("lore title and content cannot be empty")
    def parse_keywords(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]
    db = connect(args.db)
    fetchone(db, "SELECT id FROM campaigns WHERE id=?", (campaign,))
    with db:
        entry_id = f"{campaign}:lore:{uuid4().hex}"
        db.execute(
            """INSERT INTO lore_entries(id, campaign_id, title, content, keys_json, secondary_keys_json,
               enabled, constant, selective, case_sensitive, insertion_order, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)""",
            (entry_id, campaign, title, content, json.dumps(parse_keywords(args.keys), ensure_ascii=False),
             json.dumps(parse_keywords(args.secondary_keys), ensure_ascii=False), int(args.constant),
             int(args.selective), int(args.case_sensitive), args.order, args.priority, now()),
        )
    print(f"Created lore entry '{title}'")


def list_lore(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    rows = db.execute(
        "SELECT * FROM lore_entries WHERE campaign_id=? ORDER BY constant DESC, priority DESC, insertion_order ASC, created_at ASC",
        (campaign,),
    ).fetchall()
    values = [dict(row) for row in rows]
    for value in values:
        value["keys"] = json.loads(value.pop("keys_json"))
        value["secondary_keys"] = json.loads(value.pop("secondary_keys_json"))
        for field in ("enabled", "constant", "selective", "case_sensitive"):
            value[field] = bool(value[field])
    if args.json:
        print(json.dumps(values, ensure_ascii=False))
        return
    if not values:
        print("No lore entries.")
        return
    for row in values:
        trigger = "always" if row["constant"] else ", ".join(row["keys"]) or "no trigger"
        print(f"{row['id']}  {row['title']} — {trigger}")


def delete_lore(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    with db:
        deleted = db.execute("DELETE FROM lore_entries WHERE campaign_id=? AND id=?", (campaign, args.entry)).rowcount
    if not deleted:
        raise ValueError("lore entry does not exist")
    print("Deleted lore entry.")


def create_universe_lore(args: argparse.Namespace) -> None:
    universe_id = slug(args.universe)
    title = args.title.strip()
    content = args.content.strip()
    category = args.category.strip() or "General"
    visibility = args.visibility.strip() or "public"
    if not title or not content:
        raise ValueError("universe lore title and content cannot be empty")
    if len(category) > 80 or len(visibility) > 40:
        raise ValueError("universe lore metadata is too long")
    db = connect(args.db)
    fetchone(db, "SELECT id FROM universes WHERE id=?", (universe_id,))
    keys = [item.strip() for item in args.keys.split(",") if item.strip()]
    secondary = [item.strip() for item in args.secondary_keys.split(",") if item.strip()]
    with db:
        db.execute(
            """INSERT INTO universe_lore_entries(id, universe_id, title, content, category, visibility,
               keys_json, secondary_keys_json, enabled, constant, selective, case_sensitive,
               insertion_order, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?)""",
            (f"{universe_id}:lore:{uuid4().hex}", universe_id, title, content, category, visibility,
             json.dumps(keys, ensure_ascii=False), json.dumps(secondary, ensure_ascii=False),
             int(args.constant), int(args.selective), int(args.case_sensitive), args.order, args.priority, now()),
        )
    print(f"Created universe lore entry '{title}'")


def update_universe_lore(args: argparse.Namespace) -> None:
    universe_id = slug(args.universe)
    title = args.title.strip()
    content = args.content.strip()
    category = args.category.strip() or "General"
    visibility = args.visibility.strip() or "public"
    if not title or not content:
        raise ValueError("universe lore title and content cannot be empty")
    if len(category) > 80 or len(visibility) > 40:
        raise ValueError("universe lore metadata is too long")
    db = connect(args.db)
    keys = [item.strip() for item in args.keys.split(",") if item.strip()]
    secondary = [item.strip() for item in args.secondary_keys.split(",") if item.strip()]
    with db:
        updated = db.execute(
            """UPDATE universe_lore_entries
               SET title=?, content=?, category=?, visibility=?, keys_json=?, secondary_keys_json=?,
                   constant=?, selective=?, case_sensitive=?, insertion_order=?, priority=?
               WHERE universe_id=? AND id=?""",
            (title, content, category, visibility, json.dumps(keys, ensure_ascii=False),
             json.dumps(secondary, ensure_ascii=False), int(args.constant), int(args.selective),
             int(args.case_sensitive), args.order, args.priority, universe_id, args.entry),
        ).rowcount
    if not updated:
        raise ValueError("universe lore entry does not exist")
    print(f"Updated universe lore entry '{title}'")


LORE_TITLE_SEPARATORS = re.compile(r"[、，,：:（）()\-—与之的和]+")
LORE_TITLE_SUFFIXES = (
    "共和国", "自由领", "诸侯领", "城邦同盟", "绿洲联邦", "风原盟约", "商盟",
    "王国", "联邦", "同盟", "议会", "协会", "圣约", "守望团", "大公", "领主",
    "诸城", "群岛", "海峡", "山脉", "河谷", "荒漠", "林海", "航路", "时代",
    "协定", "事故", "战争", "条约", "盟约", "禁忌", "血统", "存在", "现象",
)

# Compact aliases supplement title-derived terms. They deliberately name things a
# player might type, rather than every word in an entry, so a relevant turn can
# retrieve a few facts without turning the whole encyclopedia into prompt text.
LORE_TITLE_ALIASES = {
    "已知世界": ["世界", "世界观", "背景"],
    "文明与共同生活": ["文明", "社会", "共同生活", "族群"],
    "魔法与日常生活": ["魔法", "施法", "法术", "日常"],
    "道路、海域与边界": ["旅行", "道路", "航路", "边境"],
    "宇宙的秩序": ["宇宙", "位面", "天幕"],
    "物质位面": ["物质位面", "凡世", "现世"],
    "映照位面": ["妖精荒野", "阴影堕界", "映照位面"],
    "过渡位面与位面通路": ["以太界", "星界", "梦境", "传送", "位面通路"],
    "元素位面": ["元素", "火元素", "水元素", "风元素", "土元素"],
    "界外与未知": ["界外", "未知", "异界"],
    "神性与天幕盟约": ["神明", "诸神", "天幕盟约", "神性"],
    "十四主神": ["神明", "诸神", "艾芮娅", "莫兰", "索拉恩", "露涅", "阿德兰", "维岚", "凯瑟尔", "伊赛文", "瑟芙拉", "梅丽莎", "瓦尔卡", "多拉姆", "艾洛雅", "维斯珀"],
    "信仰、教会与地方教派": ["神殿", "教会", "祭司", "信仰"],
    "天界与列翼者": ["天界", "天使", "列翼者"],
    "七位列翼者": ["赛利昂", "奈芙娅", "阿尔丹", "希莱恩", "安芮尔", "塔莉娅", "维伽尔", "大天使"],
    "地狱与魔鬼": ["地狱", "魔鬼", "契约"],
    "七位地狱大公": ["阿兹拉克", "梅菲妲", "卡尔德恩", "维拉斯", "纳赫尔", "赛尔维恩", "摩尔格拉", "地狱大公"],
    "深渊与恶魔": ["深渊", "恶魔"],
    "六位深渊领主": ["格罗玛克", "伊莎拉", "乌鲁姆", "奈萨尔", "巴勒格拉", "卡索斯", "深渊领主"],
    "静门、灵魂与死后世界": ["死亡", "灵魂", "静门", "复生"],
    "独立高位存在": ["妖精领主", "元素领主", "祖灵", "巫妖", "半神"],
    "祖源、文化、血统与状态": ["祖源", "文化", "血统", "出身"],
    "精灵诸族": ["精灵", "高等精灵", "木精灵", "黑暗精灵"],
    "矮人、半身人与侏儒": ["矮人", "半身人", "侏儒"],
    "兽人与地精诸族": ["兽人", "地精", "哥布林", "熊地精"],
    "龙裔、狗头人与巨人裔": ["龙裔", "狗头人", "巨人裔"],
    "兽形与混源族群": ["兽形族", "豹人", "肯库", "鸟人", "龟人", "蜥蜴人", "牛头人", "半人马", "萨提尔", "变形者"],
    "罕见族群与远方来客": ["特里同", "变形怪", "妖精", "仙灵", "菲尔博格", "蛇人", "吉斯", "远方来客"],
    "超自然血统": ["天界血统", "提夫林", "元素血统", "龙血"],
    "非凡状态与特殊存在": ["构装体", "不死者", "真龙", "天使", "魔鬼", "恶魔"],
    "魔法与世界的织理": ["魔法", "施法", "法术", "奥术"],
    "施法传统与力量道路": ["施法", "法术", "法师", "牧师", "德鲁伊", "术士"],
    "魔法教育、许可与日常生活": ["学院", "许可", "附魔", "炼金", "法师"],
    "冒险者、佣兵与自由职业者": ["冒险者", "委托", "佣兵", "护卫", "赏金"],
    "学院、行会与专业组织": ["学院", "行会", "工坊", "公会"],
    "禁术、秘密结社与魔法监管": ["禁术", "秘密结社", "监管", "违法魔法"],
    "遗物、高阶魔法与施法的代价": ["遗物", "高阶魔法", "复活", "位面旅行"],
    "地下世界、遗址带与无主之地": ["地下世界", "地城", "遗址", "无主之地"],
    "国家、城邦与权力的边界": ["国家", "城邦", "政治", "领主"],
    "白塔议会": ["白塔", "法师学院", "秘法议会"],
    "七路商盟": ["商盟", "商队", "贸易", "货运"],
    "灰钥协会": ["灰钥", "冒险者协会", "遗迹委托"],
    "灯塔圣约": ["灯塔圣约", "救济", "医疗", "收容所"],
    "银枝守望团": ["银枝", "灵脉", "自然", "巡护"],
    "黑帆会": ["黑帆", "走私", "地下网络"],
    "镜海历与历史的记录": ["镜海历", "年份", "历史", "纪年"],
    "历史的多种声音": ["历史", "传说", "档案", "口述"],
    "怪物、危险生物与处置原则": ["怪物", "危险生物", "猎杀", "处置"],
    "野兽、魔兽与觉醒生命": ["魔兽", "野兽", "觉醒", "动物"],
    "观察、研究与公共防护": ["调查", "研究", "防护", "异常"],
    "西潮航路与彼岸群陆": ["西潮", "外洋", "远航", "彼岸"],
    "极北白夜海": ["白夜海", "极北", "冰海"],
    "南方外洋与星坠群岛": ["南方外洋", "星坠群岛", "火山岛"],
    "古道之前的诸城": ["前古", "古城", "遗址"],
    "深岩第六门": ["深岩", "第六门", "封门"],
    "沉没港与失落航图": ["沉没港", "航图", "沉城"],
    "天幕盟约的三种解释": ["天幕盟约", "天幕", "高位存在"],
    "静门彼岸": ["静门", "死后", "灵魂"],
    "界外的低语": ["界外", "低语", "异常梦境"],
    "静塔失去的七日": ["静塔", "失去的七日", "记忆事故"],
    "灰岸协定的附页": ["灰岸协定", "停战", "附页"],
    "深岩矿权的旧债": ["深岩", "矿权", "旧债"],
    "消失的第七路": ["第七路", "商盟", "失踪商路"],
    "镜海夜灯": ["镜海", "夜灯", "失踪船"],
    "北湾的雪名禁忌": ["北湾", "雪名", "失踪者"],
    "绿洲井边的铜币": ["绿洲", "水井", "商队"],
    "林海的空田": ["林海", "空田", "旧约"],
    "真名、誓言与强制契约": ["真名", "誓言", "契约"],
    "记忆、身份与失去的自我": ["记忆", "身份", "失忆"],
    "灵魂容器、位面之门与时间残响": ["灵魂容器", "位面之门", "时间残响"],
}


def derived_lore_keywords(title: str) -> list[str]:
    """Build small deterministic triggers from a canonical encyclopedia title."""
    candidates = [title.strip(), *LORE_TITLE_SEPARATORS.split(title)]
    for fragment in tuple(candidates):
        for suffix in LORE_TITLE_SUFFIXES:
            if fragment.endswith(suffix) and len(fragment) > len(suffix):
                candidates.append(fragment[:-len(suffix)])
    candidates.extend(LORE_TITLE_ALIASES.get(title, []))
    result: list[str] = []
    for candidate in candidates:
        candidate = candidate.strip()
        if len(candidate) < 2 or candidate in result:
            continue
        result.append(candidate)
    return result


def index_universe_lore(args: argparse.Namespace) -> None:
    """Backfill deterministic retrieval metadata for a universe's World Bible."""
    universe_id = slug(args.universe)
    db = connect(args.db)
    fetchone(db, "SELECT id FROM universes WHERE id=?", (universe_id,))
    rows = db.execute(
        "SELECT id, title FROM universe_lore_entries WHERE universe_id=? ORDER BY created_at",
        (universe_id,),
    ).fetchall()
    with db:
        for row in rows:
            keywords = derived_lore_keywords(row["title"])
            if not keywords:
                raise ValueError(f"unable to derive retrieval keywords for '{row['title']}'")
            db.execute(
                """UPDATE universe_lore_entries
                   SET keys_json=?, secondary_keys_json=?, selective=1, constant=0
                   WHERE id=?""",
                (json.dumps(keywords, ensure_ascii=False), json.dumps(keywords, ensure_ascii=False), row["id"]),
            )
    print(f"Indexed {len(rows)} universe lore entries.")


def rename_universe(args: argparse.Namespace) -> None:
    """Rename a shared universe without changing its stable id or campaign links."""
    universe_id = slug(args.universe)
    title = args.title.strip()
    description = args.description.strip()
    if not title:
        raise ValueError("universe title cannot be empty")
    db = connect(args.db)
    with db:
        updated = db.execute(
            "UPDATE universes SET title=?, description=? WHERE id=?",
            (title, description, universe_id),
        ).rowcount
    if not updated:
        raise ValueError("universe does not exist")
    print(f"Renamed universe to '{title}'.")


def list_universe_lore(args: argparse.Namespace) -> None:
    db = connect(args.db)
    universe_id = slug(args.universe)
    rows = db.execute(
        "SELECT * FROM universe_lore_entries WHERE universe_id=? ORDER BY constant DESC, priority DESC, insertion_order ASC, created_at ASC",
        (universe_id,),
    ).fetchall()
    values = [dict(row) for row in rows]
    for value in values:
        value["keys"] = json.loads(value.pop("keys_json"))
        value["secondary_keys"] = json.loads(value.pop("secondary_keys_json"))
        try:
            value["record"] = json.loads(value.pop("record_json") or "{}")
        except json.JSONDecodeError:
            value["record"] = {}
        for field in ("enabled", "constant", "selective", "case_sensitive", "system_entry"):
            value[field] = bool(value[field])
    if args.json:
        print(json.dumps(values, ensure_ascii=False))
        return
    for row in values:
        trigger = "always" if row["constant"] else ", ".join(row["keys"]) or "no trigger"
        print(f"{row['id']}  {row['title']} — {trigger}")


def delete_universe_lore(args: argparse.Namespace) -> None:
    db = connect(args.db)
    universe_id = slug(args.universe)
    with db:
        deleted = db.execute("DELETE FROM universe_lore_entries WHERE universe_id=? AND id=?", (universe_id, args.entry)).rowcount
    if not deleted:
        raise ValueError("universe lore entry does not exist")
    print("Deleted universe lore entry.")


def list_worlds(args: argparse.Namespace) -> None:
    db = connect(args.db)
    active_row = db.execute("SELECT value_json FROM app_state WHERE key='active_campaign'").fetchone()
    active = json.loads(active_row["value_json"]) if active_row else None
    worlds = db.execute(
        """SELECT c.id, c.title, c.created_at, c.trashed_at, u.id AS universe_id, u.title AS universe_title,
                  cs.player_name, cs.player_concept, cs.starting_location, cs.character_json,
                  c.active_branch_id, es.state_json AS player_state_json,
                  COALESCE((SELECT MAX(t.turn_number) FROM turns t WHERE t.branch_id=c.active_branch_id), b.base_turn_number) AS turn_count
           FROM campaigns c
           JOIN branches b ON b.id=c.active_branch_id
           JOIN campaign_universes cu ON cu.campaign_id=c.id
           JOIN universes u ON u.id=cu.universe_id
           LEFT JOIN campaign_starts cs ON cs.campaign_id=c.id
           LEFT JOIN entity_states es ON es.branch_id=c.active_branch_id AND es.entity_id='player'
           ORDER BY c.created_at DESC"""
    ).fetchall()
    universes = db.execute(
        "SELECT id, title, description, created_at FROM universes ORDER BY created_at"
    ).fetchall()
    world_payload = []
    trashed_payload = []
    for row in worlds:
        item = dict(row)
        item["character"] = json.loads(item.pop("character_json") or "{}")
        item["player_state"] = json.loads(item.pop("player_state_json") or "{}")
        active_branch = fetchone(db, "SELECT * FROM branches WHERE id=?", (item["active_branch_id"],))
        current_scene = current_story_scene(db, active_branch)
        item["scene_state"] = normalize_scene_state(current_scene)
        item["scene_model"] = normalize_scene_model(current_scene)
        item["current_scene"] = {
            "location": str(current_scene.get("location", "")),
            "immediate_situation": str(current_scene.get("immediate_situation", "")),
        }
        item.pop("active_branch_id", None)
        (trashed_payload if item["trashed_at"] else world_payload).append(item)
    if active not in {world["id"] for world in world_payload}:
        active = world_payload[0]["id"] if world_payload else None
    payload = {
        "active_campaign": active,
        "worlds": world_payload,
        "trashed_worlds": trashed_payload,
        "universes": [dict(row) for row in universes],
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
        return
    print(f"Active world: {active or 'none'}")
    for world in world_payload:
        print(f"{world['id']} — {world['title']} ({world['universe_title']})")


def select_world(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    fetchone(db, "SELECT id FROM campaigns WHERE id=? AND trashed_at IS NULL", (campaign,))
    with db:
        db.execute(
            """INSERT INTO app_state(key, value_json) VALUES ('active_campaign', ?)
               ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json""",
            (json.dumps(campaign),),
        )
    print(f"Selected world '{campaign}'")


def trash_world(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    world = fetchone(db, "SELECT id FROM campaigns WHERE id=? AND trashed_at IS NULL", (campaign,))
    with db:
        db.execute("UPDATE campaigns SET trashed_at=? WHERE id=?", (now(), world["id"]))
        active_row = db.execute("SELECT value_json FROM app_state WHERE key='active_campaign'").fetchone()
        if active_row and json.loads(active_row["value_json"]) == campaign:
            next_world = db.execute(
                "SELECT id FROM campaigns WHERE trashed_at IS NULL ORDER BY created_at DESC, id DESC LIMIT 1"
            ).fetchone()
            db.execute(
                "UPDATE app_state SET value_json=? WHERE key='active_campaign'",
                (json.dumps(next_world["id"] if next_world else None),),
            )
    print(f"Moved world '{campaign}' to recoverable trash.")


def restore_world(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    world = fetchone(db, "SELECT id FROM campaigns WHERE id=? AND trashed_at IS NOT NULL", (campaign,))
    with db:
        db.execute("UPDATE campaigns SET trashed_at=NULL WHERE id=?", (world["id"],))
        active_row = db.execute("SELECT value_json FROM app_state WHERE key='active_campaign'").fetchone()
        if not active_row or json.loads(active_row["value_json"]) is None:
            db.execute(
                """INSERT INTO app_state(key, value_json) VALUES ('active_campaign', ?)
                   ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json""",
                (json.dumps(campaign),),
            )
    print(f"Restored world '{campaign}'.")


def purge_world(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    # Only recoverable-trash entries can be purged. The shared universe and
    # its encyclopedia are deliberately outside this campaign's ownership.
    fetchone(db, "SELECT id FROM campaigns WHERE id=? AND trashed_at IS NOT NULL", (campaign,))
    with db:
        branch_ids = [row["id"] for row in db.execute("SELECT id FROM branches WHERE campaign_id=?", (campaign,))]
        db.execute("DELETE FROM checkpoints WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM chapter_summaries WHERE campaign_id=?", (campaign,))
        for branch_id in branch_ids:
            db.execute("DELETE FROM events WHERE branch_id=?", (branch_id,))
            db.execute("DELETE FROM state_deltas WHERE branch_id=?", (branch_id,))
            db.execute("DELETE FROM state_roots WHERE branch_id=?", (branch_id,))
            db.execute("DELETE FROM snapshots WHERE branch_id=?", (branch_id,))
            db.execute("DELETE FROM turns WHERE branch_id=?", (branch_id,))
            for table in STATE_TABLES:
                db.execute(f"DELETE FROM {table} WHERE branch_id=?", (branch_id,))
        # A branch may refer to a parent within this same world.
        db.execute("UPDATE branches SET parent_branch_id=NULL WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM branches WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM lore_entries WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM entities WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM campaign_starts WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM campaign_universes WHERE campaign_id=?", (campaign,))
        db.execute("DELETE FROM campaigns WHERE id=?", (campaign,))
    db.execute("VACUUM")
    print(f"Permanently deleted removed world '{campaign}' from the current database.")


def build_brief(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    universe = universe_for_campaign(db, campaign)
    branch_turns = db.execute("SELECT * FROM turns WHERE branch_id = ? ORDER BY turn_number DESC", (branch["id"],)).fetchall()
    latest = next((row for row in branch_turns if not json_value(row, "scene_json").get("local_record")), None)
    # A freshly created timeline has no new turn yet. Its fork turn remains
    # the current scene until the player makes the first divergent choice.
    if latest is None and branch["forked_from_turn_id"]:
        latest = fetchone(db, "SELECT * FROM turns WHERE id = ?", (branch["forked_from_turn_id"],))
    scene = json_value(latest, "scene_json") if latest else current_story_scene(db, branch)
    if not scene:
        scene = {"immediate_situation": "Begin the story."}
    scene_state = normalize_scene_state(scene)
    scene_model = normalize_scene_model(scene)
    previous_gm_move = normalize_gm_move(scene)
    states = db.execute(
        """SELECT e.id, e.type, e.name, e.profile_json, s.state_json FROM entity_states s
           JOIN entities e ON e.id=s.entity_id AND e.campaign_id=? WHERE s.branch_id=?""",
        (campaign, branch["id"]),
    ).fetchall()
    present = set(scene.get("present_entities", []))
    player = next((row for row in states if row["id"] == "player"), None)
    start = fetchone(db, "SELECT starting_location FROM campaign_starts WHERE campaign_id=?", (campaign,))
    player_state = json.loads(player["state_json"]) if player else {}
    ability_state = abilities_from_player_state(player_state)
    active_abilities = relevant_abilities(ability_state, args.action, limit=3)
    scene_location = str(scene.get("location") or "").strip()
    current_location = canonical_location(scene_location if scene_location and scene_location.lower() != "unknown" else str(player_state.get("location") or start["starting_location"]))
    current_location_id = stable_record_id(scene.get("location_id") or player_state.get("location_id"))
    saved_place, place_context, place_routes = places_for_brief(
        db, campaign, branch["id"], current_location_id, args.action,
    )
    if saved_place:
        current_location = saved_place["name"]
    place = location_profile(current_location)
    if saved_place and saved_place["atmosphere"]:
        place["mood"] = saved_place["atmosphere"]
        place["source"] = "saved_instance"
    cast = [row for row in states if row["id"] in present and row["type"] not in NPC_TYPES]
    people = cast_for_brief(db, campaign, branch["id"], scene, args.action)
    active_threads = db.execute(
        "SELECT * FROM story_threads WHERE branch_id=? AND status='active' ORDER BY urgency DESC, last_advanced_turn ASC LIMIT 6", (branch["id"],)
    ).fetchall()
    facts = relevant_rows(db, "SELECT * FROM facts WHERE branch_id=? AND status='active'", branch["id"], args.action, 8)
    beliefs = db.execute(
        "SELECT * FROM beliefs WHERE branch_id=? AND status='active' ORDER BY importance DESC, created_turn DESC", (branch["id"],)
    ).fetchall()
    beliefs = [row for row in beliefs if row["actor_id"] in present][:5]
    possessions = possession_rows(db, campaign, branch["id"])
    # Only state anchors that can change a decision occupy every turn's prompt
    # budget. Ordinary carried goods remain in the local ledger and are still
    # visible in the UI, but are not repeated to the narrator indefinitely.
    prompt_possessions = [
        item for item in possessions
        if item["holder"] == "player" and (item["status"] == "equipped" or item["importance"] >= 7 or item["category"] in {"important", "clue"})
    ][:8]
    mentioned_possessions = [
        item for item in possessions if item not in prompt_possessions and item["name"] in args.action
    ][:3]
    # Keep a small recent prose window; the durable scene model carries the
    # current state so the narrator does not reread the whole transcript.
    recent = [row for row in branch_turns if not json_value(row, "scene_json").get("local_record")][:4][::-1]
    if not recent and branch["parent_branch_id"]:
        recent = db.execute(
            "SELECT * FROM turns WHERE branch_id=? AND turn_number<=? ORDER BY turn_number DESC LIMIT 4",
            (branch["parent_branch_id"], branch["base_turn_number"]),
        ).fetchall()[::-1]
    lore_scan = "\n".join([
        args.action,
        current_location,
        str(scene.get("immediate_situation", "")),
        *(f"{row['player_action']}\n{row['narration']}" for row in recent),
    ])
    lore, lore_characters = active_lore(db, campaign, lore_scan, char_budget=3600)

    def entity_line(row: sqlite3.Row) -> str:
        profile = json.loads(row["profile_json"])
        state = json.loads(row["state_json"])
        return f"- {row['name']} (`{row['id']}`, {row['type']}): profile={json.dumps(profile, ensure_ascii=False)}; state={json.dumps(state, ensure_ascii=False)}"

    def player_line(row: sqlite3.Row) -> str:
        profile = json.loads(row["profile_json"])
        state = json.loads(row["state_json"])
        mechanics = state.get("mechanics")
        if isinstance(mechanics, dict):
            compact_mechanics = {key: value for key, value in mechanics.items() if key not in {"abilities", "specialties", "maintained"}}
            if isinstance(compact_mechanics.get("resources"), dict):
                compact_mechanics["resources"] = {
                    "wallet": resource_state(state)["wallet"],
                }
            if compact_mechanics:
                state["mechanics"] = compact_mechanics
            else:
                state.pop("mechanics", None)
        return f"- {row['name']} (`{row['id']}`, {row['type']}): profile={json.dumps(profile, ensure_ascii=False)}; state={json.dumps(state, ensure_ascii=False)}"

    def possession_line(item: dict[str, Any]) -> str:
        equipped_as = f" as {item['equipped_as']}" if item["equipped_as"] else ""
        description = f": {item['description']}" if item["description"] else ""
        purpose = f" Known purpose: {item['known_purpose']}." if item["known_purpose"] else ""
        item_type = f"; base type {item['base_type_label']}" if item["base_type_id"] else ""
        rarity = f"; rarity {item['rarity_label']}" if item["rarity_known"] else "; rarity not yet identified"
        baseline = item["type_baseline"]
        type_rule = f" Type baseline: {baseline['use']} Limits: {baseline['limits']}" if baseline else ""
        return f"- {item['name']} (`{item['id']}`; holder={item['holder']}; status={item['status']}{equipped_as}; quantity={item['quantity']}; importance={item['importance']}{item_type}{rarity}){description}{purpose}{type_rule}"

    def person_line(person: dict[str, Any]) -> str:
        identity = "; ".join(part for part in [
            person["role"], person["description"], person["personality"], person["background"], person["voice"],
        ] if part)
        current = "; ".join(part for part in [
            f"relationship={person['relationship']}" if person["relationship"] else "",
            f"location={person['location']}" if person["location"] else "",
            f"activity={person['activity']}" if person["activity"] else "",
            f"objective={person['objective']}" if person["objective"] else "",
            f"next={person['next_move']}" if person["next_move"] else "",
            f"anchor={person['anchor']}" if person["anchor"] else "",
        ] if part)
        memories = "; ".join(memory["text"] for memory in person["memories"][:3])
        attributes = json.dumps(person["attributes"], ensure_ascii=False) if person["attributes"] else "unfixed"
        specialties = ", ".join(
            str(item.get("name", item.get("id", ""))) if isinstance(item, dict) else str(item)
            for item in (person["specialties"].values() if isinstance(person["specialties"], dict) else person["specialties"])
        ) or "none recorded"
        abilities = "; ".join(
            f"{ability['name']} (`{ability['id']}`): can={ability['known_effect']} cannot={ability['limits']}"
            for ability in person["abilities"]
        ) or "none recorded"
        return (
            f"- {person['name']} (`{person['id']}`, {person['status']}/{person['tier']}): "
            f"{identity or 'identity not yet detailed'}; {current or 'current state not yet detailed'}; "
            f"attributes={attributes}; specialties={specialties}; abilities={abilities}"
            f"{'; remembered: ' + memories if memories else ''}"
        )

    def place_line(saved: dict[str, Any]) -> str:
        parent = f"; inside {saved['parent_name']} (`{saved['parent_id']}`)" if saved["parent_id"] else ""
        details = "; ".join(part for part in (
            saved["description"],
            f"current={saved['current_summary']}" if saved["current_summary"] else "",
            f"access={saved['access']}" if saved["access"] else "",
            f"features={', '.join(saved['features'])}" if saved["features"] else "",
        ) if part)
        return (
            f"- {saved['name']} (`{saved['id']}`; {saved['kind']}; status={saved['status']}{parent}; "
            f"visited={saved['visited']}; visits={saved['visits']}): {details or 'no further durable detail established'}"
        )

    def route_line(route: dict[str, Any]) -> str:
        detail = "; ".join(part for part in (route["travel_mode"], route["description"]) if part)
        return (
            f"- {route['from']} (`{route['from_id']}`) <-> {route['to']} (`{route['to_id']}`) "
            f"via `{route['id']}`; status={route['status']}; traveled={route['uses']}"
            f"{'; ' + detail if detail else ''}"
        )

    ability_lines: list[str] = []
    if active_abilities:
        ability_lines = ["", "## Relevant owned abilities — authoritative boundaries"]
        for ability in active_abilities:
            maintained = "; currently maintained" if ability["id"] in ability_state["maintained"] else ""
            requirements = "; ".join(ability["requirements"]) or "none"
            cost = json.dumps(ability["cost"], ensure_ascii=False) if ability["cost"] else "none"
            ability_lines.append(
                f"- {ability['name']} (`{ability['id']}`; {ability['mastery_label']}{maintained}): "
                f"can={ability['known_effect']} cannot={ability['limits']} "
                f"requirements={requirements}; cost={cost}; scale={ability['minimum_scale']}–{ability['scale_cap']}."
            )

    lines = [
        "# Campaign context — authoritative",
        f"Campaign: {campaign}; timeline: {branch['name']}; current turn: {latest['turn_number'] if latest else 0}",
        f"Universe: {universe['title']} — {universe['description'] or 'no description recorded'}",
        "", "## Current scene",
        f"- Location: {current_location}",
        f"- Time: {latest['game_time'] if latest and latest['game_time'] else 'unspecified'}",
        f"- Immediate situation: {scene.get('immediate_situation', 'none recorded')}",
        f"- Activity: {scene_state['activity']}; threat phase: {scene_state['threat']}",
        f"- State basis: {scene_state['basis'] or 'no exceptional pressure established'}",
        f"- Player position: {scene_model['player_position'] or 'not separately established'}",
        "- Observable participants: " + ("; ".join(
            f"{item['name']} (`{item['id']}`; {item['stance'] or 'stance unclear'}; position={item['position'] or 'unspecified'}; doing={item['activity'] or 'unspecified'}; condition={item['condition'] or 'no visible condition recorded'})"
            for item in scene_model["participants"]
        ) or "none recorded"),
        "- Usable scene elements: " + ("; ".join(
            f"{item['name']} (`{item['id']}`; {item['kind'] or 'other'}; position={item['position'] or 'unspecified'}; state={item['state'] or 'unspecified'})"
            for item in scene_model["elements"]
        ) or "none recorded"),
        "- Active pressures: " + ("; ".join(
            f"{item['text']} (`{item['id']}`; {item['urgency'] or 'present'}; source={item['source'] or 'unspecified'})"
            for item in scene_model["pressures"]
        ) or "none recorded"),
        "- Previous GM move: " + (
            f"{previous_gm_move['kind']} ({previous_gm_move['scope']}) — {previous_gm_move['summary']}; "
            f"basis={previous_gm_move['basis'] or 'not recorded'}"
            if previous_gm_move["kind"] != "none" else "none"
        ),
        "", "## Place baseline — atmosphere, not a scripted encounter",
        f"- Source: {place['source']}; mood: {place['mood']}",
        f"- Ordinary story material: {place['focus']}",
        f"- Risk character: {place['danger']}",
        "- Treat this as a soft tendency. The player's action, established people, and present facts take priority. Do not force danger into a social place or force combat in a dangerous place. A name-based hint is not proof that a creature or event exists. On travel, set scene.location to the place actually reached, not a destination merely mentioned.",
        "", "## Persistent places relevant to this turn — authoritative",
        *((place_line(item) for item in place_context) if place_context else ["- No concrete place instance has been established yet."]),
        "", "## Observed routes relevant to this turn — authoritative",
        *((route_line(item) for item in place_routes) if place_routes else ["- No relevant traveled route recorded."]),
        "", "## Player",
        player_line(player) if player else "- No player state recorded.",
        *ability_lines,
        "", "## Key possessions — authoritative",
        *((possession_line(item) for item in prompt_possessions) if prompt_possessions else ["- None recorded."]),
        "", "## Other known items mentioned in this action",
        *((possession_line(item) for item in mentioned_possessions) if mentioned_possessions else ["- None relevant."]),
        "", "## Present cast",
        *((entity_line(row) for row in cast) if cast else ["- No named NPC is currently present."]),
        "", "## Party and important people — local ledger",
        *((person_line(person) for person in people) if people else ["- None recorded."]),
        "", "## Active story threads",
        *((
            f"- [{row['kind']}] {row['title']} — stakes: {row['stakes'] or 'unspecified'}; {row['summary'] or 'not yet summarized'}"
            for row in active_threads
        ) if active_threads else ["- None."]),
        "", "## Relevant canonical facts",
        *((f"- {row['text']}" for row in facts) if facts else ["- None retrieved."]),
        "", f"## Activated authored lore database ({lore_characters} characters; fixed 3600-character budget)",
        *((f"- [{row['title']}] record={lore_record_json(row)}; article={row['content']}" for row in lore) if lore else ["- No worldbook entry matched this turn."]),
        "", "## Private beliefs of NPCs in this scene",
        *((f"- {row['actor_id']}: {row['text']}" for row in beliefs) if beliefs else ["- None retrieved."]),
        "", "## Recent turns",
        *((f"- Turn {row['turn_number']}: Player: {row['player_action']} | Outcome: {row['narration']}" for row in recent) if recent else ["- Campaign has not started."]),
        "", "## Current player action", args.action,
    ]
    output = "\n".join(lines) + "\n"
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote context brief to {args.out}")
    else:
        print(output)


def timeline_rows(db: sqlite3.Connection, branch: sqlite3.Row) -> list[sqlite3.Row]:
    """Return the readable history for a branch, including its fork ancestry."""
    lineage = [branch]
    current = branch
    while current["parent_branch_id"]:
        current = fetchone(db, "SELECT * FROM branches WHERE id=?", (current["parent_branch_id"],))
        lineage.append(current)
    lineage.reverse()
    rows: list[sqlite3.Row] = []
    for index, item in enumerate(lineage):
        child = lineage[index + 1] if index + 1 < len(lineage) else None
        if child:
            segment = db.execute(
                "SELECT turn_number, player_action, narration, scene_json FROM turns WHERE branch_id=? AND turn_number<=? ORDER BY turn_number",
                (item["id"], child["base_turn_number"]),
            ).fetchall()
        else:
            segment = db.execute(
                "SELECT turn_number, player_action, narration, scene_json FROM turns WHERE branch_id=? ORDER BY turn_number", (item["id"],)
            ).fetchall()
        rows.extend(row for row in segment if not json_value(row, "scene_json").get("local_record"))
    return rows


def map_data(db: sqlite3.Connection, campaign: str, branch: sqlite3.Row) -> dict[str, Any]:
    """Return persistent visited places and observed, branch-local routes."""
    stored_places = [item for item in location_rows(db, campaign, branch["id"]) if item["visited"]]
    if stored_places:
        player = db.execute(
            "SELECT state_json FROM entity_states WHERE branch_id=? AND entity_id='player'",
            (branch["id"],),
        ).fetchone()
        player_state = json.loads(player["state_json"]) if player else {}
        current_id = stable_record_id(player_state.get("location_id"))
        current = next((item for item in stored_places if item["id"] == current_id), None)
        if current is None:
            current_name = canonical_location(str(player_state.get("location", "")))
            current = next((item for item in stored_places if item["name"] == current_name), None)
        if current is None:
            current = max(stored_places, key=lambda item: (item["last_visited_turn"], item["updated_turn"]))
        profile = location_profile(current["name"])
        if current["atmosphere"]:
            profile["mood"] = current["atmosphere"]
            profile["source"] = "saved_instance"
        place_ids = {item["id"] for item in stored_places}
        routes = [
            route for route in route_rows(db, campaign, branch["id"])
            if route["from_id"] in place_ids and route["to_id"] in place_ids
        ]
        places = []
        for item in stored_places:
            places.append({
                **item,
                "first_turn": item["first_visited_turn"],
                "last_turn": item["last_visited_turn"],
                "profile": location_profile(item["name"]),
            })
        return {
            "timeline": branch["name"], "current": current["name"], "current_id": current["id"],
            "current_place": current, "current_profile": profile,
            "places": sorted(places, key=lambda item: (-item["last_turn"], item["name"])),
            "routes": sorted(routes, key=lambda item: (item["first_turn"], item["name"])),
        }

    # Compatibility for a save created before persistent location instances.
    # Its old turn history remains readable and the next committed scene will
    # promote the current place into the entity ledger.
    start = fetchone(db, "SELECT starting_location FROM campaign_starts WHERE campaign_id=?", (campaign,))
    first = canonical_location(start["starting_location"])
    places: dict[str, dict[str, Any]] = {}
    routes: dict[tuple[str, str], dict[str, Any]] = {}

    def visit(name: str, turn: int) -> None:
        if name not in places:
            places[name] = {"name": name, "first_turn": turn, "last_turn": turn, "visits": 0, "profile": location_profile(name)}
        places[name]["visits"] += 1
        places[name]["last_turn"] = turn

    visit(first, 0)
    current = first
    for turn in timeline_rows(db, branch):
        scene = json_value(turn, "scene_json")
        destination = canonical_location(str(scene.get("location") or ""))
        if not destination or destination.lower() == "unknown" or destination == current:
            continue
        number = int(turn["turn_number"])
        visit(destination, number)
        key = (current, destination)
        if key not in routes:
            routes[key] = {"from": current, "to": destination, "first_turn": number, "uses": 0}
        routes[key]["uses"] += 1
        current = destination
    return {
        "timeline": branch["name"], "current": current, "current_id": "", "current_place": {},
        "current_profile": location_profile(current),
        "places": sorted(places.values(), key=lambda item: (-item["last_turn"], item["name"])),
        "routes": sorted(routes.values(), key=lambda item: item["first_turn"]),
    }


def list_map(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    result = map_data(db, campaign, branch)
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(f"Current place: {result['current']} ({result['timeline']})")
        for place in result["places"]:
            print(f"- {place['name']}")


def list_timeline(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    rows = timeline_rows(db, branch)
    if args.json:
        print(json.dumps([dict(row) for row in rows], ensure_ascii=False))
        return
    print(f"Timeline: {branch['name']}")
    for row in rows:
        print(f"{row['turn_number']:>4}  {row['player_action']}\n      {row['narration']}")


def show_scene_state(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    scene = current_story_scene(db, branch)
    print(json.dumps(normalize_scene_state(scene), ensure_ascii=False))


def chapter_source_data(db: sqlite3.Connection, branch: sqlite3.Row, start_turn: int, end_turn: int) -> dict[str, Any]:
    """Return the immutable player-facing turns and a reproducible audit hash."""
    if start_turn < 1 or end_turn < start_turn:
        raise ValueError("chapter turn range is invalid")
    if end_turn - start_turn + 1 > 50:
        raise ValueError("a chapter summary may cover at most 50 turns")
    selected = [
        {
            "turn_number": int(row["turn_number"]),
            "player_action": row["player_action"],
            "narration": row["narration"],
            "scene": json.loads(row["scene_json"]),
        }
        for row in timeline_rows(db, branch)
        if start_turn <= int(row["turn_number"]) <= end_turn
    ]
    if not selected:
        raise ValueError("the selected range contains no story turns")
    exact = json.dumps(selected, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "timeline": branch["name"],
        "start_turn": start_turn,
        "end_turn": end_turn,
        "turns": selected,
        "source_hash": hashlib.sha256(exact.encode("utf-8")).hexdigest(),
    }


def chapter_state_payload(db: sqlite3.Connection, campaign: str, branch: sqlite3.Row) -> dict[str, Any]:
    story_turns = timeline_rows(db, branch)
    rows = db.execute(
        """SELECT id, title, start_turn, end_turn, summary, status, source_hash, created_at, updated_at
           FROM chapter_summaries WHERE campaign_id=? AND branch_id=?
           ORDER BY start_turn, end_turn, created_at""",
        (campaign, branch["id"]),
    ).fetchall()
    chapters = []
    for row in rows:
        chapter = dict(row)
        try:
            current_hash = chapter_source_data(
                db, branch, int(row["start_turn"]), int(row["end_turn"])
            )["source_hash"]
            chapter["source_matches"] = current_hash == row["source_hash"]
        except ValueError:
            chapter["source_matches"] = False
        chapters.append(chapter)
    minimum_turn = int(story_turns[0]["turn_number"]) if story_turns else 0
    maximum_turn = int(story_turns[-1]["turn_number"]) if story_turns else 0
    latest_end = max((int(row["end_turn"]) for row in rows), default=minimum_turn - 1)
    suggested_start = latest_end + 1
    if maximum_turn and suggested_start > maximum_turn:
        suggested_start = max(minimum_turn, maximum_turn - 19)
    return {
        "timeline": branch["name"],
        "minimum_turn": minimum_turn,
        "maximum_turn": maximum_turn,
        "suggested_start": suggested_start if maximum_turn else 0,
        "suggested_end": min(maximum_turn, suggested_start + 19) if maximum_turn else 0,
        "chapters": chapters,
    }


def list_chapters(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    print(json.dumps(chapter_state_payload(db, campaign, branch), ensure_ascii=False))


def chapter_source(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    print(json.dumps(chapter_source_data(db, branch, args.start, args.end), ensure_ascii=False))


def parse_chapter(value: str) -> dict[str, Any]:
    try:
        chapter = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("chapter must be valid JSON") from error
    if not isinstance(chapter, dict):
        raise ValueError("chapter must be an object")
    return chapter


def save_chapter(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    payload = parse_chapter(args.chapter)
    title = str(payload.get("title", "")).strip()[:120]
    summary = str(payload.get("summary", "")).strip()[:12000]
    status_value = str(payload.get("status", "draft"))
    if not title or not summary:
        raise ValueError("chapter title and summary are required")
    if status_value not in {"draft", "approved"}:
        raise ValueError("chapter status must be draft or approved")
    try:
        start_turn = int(payload.get("start_turn"))
        end_turn = int(payload.get("end_turn"))
    except (TypeError, ValueError) as error:
        raise ValueError("chapter start and end turns must be numbers") from error
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    source = chapter_source_data(db, branch, start_turn, end_turn)
    existing = db.execute(
        "SELECT id, created_at FROM chapter_summaries WHERE branch_id=? AND start_turn=? AND end_turn=?",
        (branch["id"], start_turn, end_turn),
    ).fetchone()
    chapter_id = existing["id"] if existing else f"{campaign}:chapter:{uuid4().hex}"
    created_at = existing["created_at"] if existing else now()
    with db:
        db.execute(
            """INSERT INTO chapter_summaries(
                   id, campaign_id, branch_id, title, start_turn, end_turn, summary,
                   status, source_hash, created_at, updated_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(branch_id, start_turn, end_turn) DO UPDATE SET
                   title=excluded.title, summary=excluded.summary, status=excluded.status,
                   source_hash=excluded.source_hash, updated_at=excluded.updated_at""",
            (chapter_id, campaign, branch["id"], title, start_turn, end_turn, summary,
             status_value, source["source_hash"], created_at, now()),
        )
    print(json.dumps(chapter_state_payload(db, campaign, branch), ensure_ascii=False))


def update_chapter(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    payload = parse_chapter(args.chapter_data)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    current = fetchone(
        db,
        "SELECT * FROM chapter_summaries WHERE id=? AND campaign_id=? AND branch_id=?",
        (args.chapter, campaign, branch["id"]),
    )
    title = str(payload.get("title", current["title"])).strip()[:120]
    summary = str(payload.get("summary", current["summary"])).strip()[:12000]
    status_value = str(payload.get("status", current["status"]))
    if not title or not summary:
        raise ValueError("chapter title and summary are required")
    if status_value not in {"draft", "approved"}:
        raise ValueError("chapter status must be draft or approved")
    source = chapter_source_data(db, branch, int(current["start_turn"]), int(current["end_turn"]))
    with db:
        db.execute(
            """UPDATE chapter_summaries SET title=?, summary=?, status=?, source_hash=?, updated_at=?
               WHERE id=?""",
            (title, summary, status_value, source["source_hash"], now(), current["id"]),
        )
    print(json.dumps(chapter_state_payload(db, campaign, branch), ensure_ascii=False))


def delete_chapter(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    with db:
        deleted = db.execute(
            "DELETE FROM chapter_summaries WHERE id=? AND campaign_id=? AND branch_id=?",
            (args.chapter, campaign, branch["id"]),
        ).rowcount
    if not deleted:
        raise ValueError("chapter summary does not exist")
    print(json.dumps(chapter_state_payload(db, campaign, branch), ensure_ascii=False))


def recent_prose(args: argparse.Namespace) -> None:
    """Return recent player-facing narration for local repetition checking.

    This is deliberately separate from story memory. It carries no new story
    facts into the prompt; it lets the narrator service detect repeated surface
    phrasing before a turn is committed.
    """
    campaign = slug(args.campaign)
    db = connect(args.db)
    branch = branch_row(db, campaign, args.branch)
    limit = max(1, min(8, args.limit))
    rows = timeline_rows(db, branch)[-limit:]
    payload = [{"turn_number": row["turn_number"], "narration": row["narration"]} for row in rows if row["narration"]]
    print(json.dumps(payload, ensure_ascii=False))


def status(args: argparse.Namespace) -> None:
    campaign = slug(args.campaign)
    db = connect(args.db)
    current = branch_row(db, campaign, None)
    rows = db.execute("SELECT name, base_turn_number, parent_branch_id FROM branches WHERE campaign_id=? ORDER BY created_at", (campaign,)).fetchall()
    if args.json:
        storage = {
            "full_snapshots": db.execute(
                "SELECT COUNT(*) FROM snapshots WHERE branch_id IN (SELECT id FROM branches WHERE campaign_id=?)", (campaign,)
            ).fetchone()[0],
            "state_roots": db.execute(
                "SELECT COUNT(*) FROM state_roots WHERE branch_id IN (SELECT id FROM branches WHERE campaign_id=?)", (campaign,)
            ).fetchone()[0],
            "state_deltas": db.execute(
                "SELECT COUNT(*) FROM state_deltas WHERE branch_id IN (SELECT id FROM branches WHERE campaign_id=?)", (campaign,)
            ).fetchone()[0],
        }
        print(json.dumps({
            "campaign": campaign,
            "active_branch": current["name"],
            "branches": [dict(row) for row in rows],
            "storage": storage,
        }, ensure_ascii=False))
        return
    print(f"Campaign: {campaign}\nActive timeline: {current['name']}")
    for row in rows:
        marker = "*" if row["name"] == current["name"] else " "
        print(f"{marker} {row['name']} (fork point: {row['base_turn_number']})")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    default_db = Path.home() / ".codex-rpg-memory" / "campaign.sqlite3"
    root.add_argument("--db", default=str(default_db), help="SQLite save file")
    commands = root.add_subparsers(dest="command", required=True)
    schema = commands.add_parser("schema-status", help="show schema version and applied migration history")
    schema.set_defaults(func=schema_status)
    backup = commands.add_parser("backup-database", help="create a consistent complete database backup")
    backup.add_argument("--output", required=True)
    backup.set_defaults(func=backup_database)
    restore_database_parser = commands.add_parser("restore-database", help="validate and atomically import a complete database")
    restore_database_parser.add_argument("--source", required=True)
    restore_database_parser.set_defaults(func=restore_database)
    init = commands.add_parser("init", help="create a campaign")
    init.add_argument("--campaign", required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--player", required=True)
    init.add_argument("--concept", default="adventurer")
    init.add_argument("--location", default="unknown")
    init.add_argument("--character", default="{}", help="JSON profile for the player character")
    init.add_argument("--setup", default="{}", help="JSON turn-zero setup for versioned character presets")
    init.add_argument("--universe", default="shattered_realms")
    init.add_argument("--universe-title")
    init.add_argument("--universe-description", default="")
    init.set_defaults(func=init_campaign)
    commit = commands.add_parser("commit", help="commit a Codex-authored turn manifest")
    commit.add_argument("--campaign", required=True)
    commit.add_argument("--branch")
    commit.add_argument("--manifest", required=True)
    commit.set_defaults(func=commit_turn)
    brief = commands.add_parser("brief", help="render the small context package for the next turn")
    brief.add_argument("--campaign", required=True)
    brief.add_argument("--branch")
    brief.add_argument("--action", required=True)
    brief.add_argument("--out")
    brief.set_defaults(func=build_brief)
    prose = commands.add_parser("recent-prose", help="return recent narration for local repetition checking")
    prose.add_argument("--campaign", required=True)
    prose.add_argument("--branch")
    prose.add_argument("--limit", type=int, default=5)
    prose.set_defaults(func=recent_prose)
    chapters = commands.add_parser("chapters", help="list reviewable chapter summaries for a timeline")
    chapters.add_argument("--campaign", required=True)
    chapters.add_argument("--branch")
    chapters.set_defaults(func=list_chapters)
    chapter_source_parser = commands.add_parser("chapter-source", help="return exact story turns for a chapter draft")
    chapter_source_parser.add_argument("--campaign", required=True)
    chapter_source_parser.add_argument("--branch")
    chapter_source_parser.add_argument("--start", type=int, required=True)
    chapter_source_parser.add_argument("--end", type=int, required=True)
    chapter_source_parser.set_defaults(func=chapter_source)
    chapter_save = commands.add_parser("chapter-save", help="save or replace a reviewable chapter summary")
    chapter_save.add_argument("--campaign", required=True)
    chapter_save.add_argument("--branch")
    chapter_save.add_argument("--chapter", required=True, help="JSON chapter draft")
    chapter_save.set_defaults(func=save_chapter)
    chapter_update = commands.add_parser("chapter-update", help="edit or approve a chapter summary")
    chapter_update.add_argument("--campaign", required=True)
    chapter_update.add_argument("--branch")
    chapter_update.add_argument("--chapter", required=True, help="chapter id")
    chapter_update.add_argument("--chapter-data", required=True, help="JSON fields to update")
    chapter_update.set_defaults(func=update_chapter)
    chapter_delete = commands.add_parser("chapter-delete", help="delete a chapter summary without touching story turns")
    chapter_delete.add_argument("--campaign", required=True)
    chapter_delete.add_argument("--branch")
    chapter_delete.add_argument("--chapter", required=True)
    chapter_delete.set_defaults(func=delete_chapter)
    possessions = commands.add_parser("possessions", help="list the protagonist's durable possessions")
    possessions.add_argument("--campaign", required=True)
    possessions.add_argument("--branch")
    possessions.add_argument("--json", action="store_true")
    possessions.set_defaults(func=list_possessions)
    possession_upsert = commands.add_parser("possession-upsert", help="locally save a key possession without a narrator turn")
    possession_upsert.add_argument("--campaign", required=True)
    possession_upsert.add_argument("--branch")
    possession_upsert.add_argument("--item", required=True, help="JSON object for the local item record")
    possession_upsert.set_defaults(func=record_local_possession)
    resources = commands.add_parser("resources", help="show the branch-local wallet, offers, and trade history")
    resources.add_argument("--campaign", required=True)
    resources.add_argument("--branch")
    resources.set_defaults(func=list_resources)
    trade_commit = commands.add_parser("trade-commit", help="atomically settle one current-scene trade offer")
    trade_commit.add_argument("--campaign", required=True)
    trade_commit.add_argument("--branch")
    trade_commit.add_argument("--offer", required=True)
    trade_commit.set_defaults(func=commit_trade)
    type_list = commands.add_parser("item-types", help="list stable base item types")
    type_list.set_defaults(func=list_item_types)
    rarity_list = commands.add_parser("item-rarities", help="list stable item rarity levels")
    rarity_list.set_defaults(func=list_item_rarities)
    catalog_types = commands.add_parser("item-catalog-index", help="read-only item category and rarity index")
    catalog_types.set_defaults(func=list_item_catalog_index)
    ability_catalog_parser = commands.add_parser("ability-catalog", help="read the stable ability catalog")
    ability_catalog_parser.set_defaults(func=list_ability_catalog)
    abilities = commands.add_parser("abilities", help="list the protagonist's recorded abilities")
    abilities.add_argument("--campaign", required=True)
    abilities.add_argument("--branch")
    abilities.add_argument("--json", action="store_true")
    abilities.set_defaults(func=list_abilities)
    adjudication = commands.add_parser("adjudication-context", help="return authoritative references for local turn validation")
    adjudication.add_argument("--campaign", required=True)
    adjudication.add_argument("--branch")
    adjudication.set_defaults(func=adjudication_context)
    type_preview = commands.add_parser("item-classify", help="preview a non-authoritative item classification")
    type_preview.add_argument("--item", required=True, help="JSON item name and known physical description")
    type_preview.set_defaults(func=describe_item_type)
    cast = commands.add_parser("cast", help="list important people and party members")
    cast.add_argument("--campaign", required=True)
    cast.add_argument("--branch")
    cast.add_argument("--json", action="store_true")
    cast.set_defaults(func=list_cast)
    cast_upsert = commands.add_parser("cast-upsert", help="locally save an important person or party member")
    cast_upsert.add_argument("--campaign", required=True)
    cast_upsert.add_argument("--branch")
    cast_upsert.add_argument("--person", required=True, help="JSON object for the local person record")
    cast_upsert.set_defaults(func=record_local_cast)
    fork = commands.add_parser("branch", help="create a new timeline from a saved turn")
    fork.add_argument("--campaign", required=True)
    fork.add_argument("--branch", help="source timeline; defaults to active")
    fork.add_argument("--from-turn", type=int, required=True)
    fork.add_argument("--name", required=True)
    fork.set_defaults(func=create_branch)
    checkout_cmd = commands.add_parser("checkout", help="make an existing timeline active")
    checkout_cmd.add_argument("--campaign", required=True)
    checkout_cmd.add_argument("--branch", required=True)
    checkout_cmd.set_defaults(func=checkout)
    checkpoint = commands.add_parser("checkpoint", help="create a lightweight named save at the current turn")
    checkpoint.add_argument("--campaign", required=True)
    checkpoint.add_argument("--branch")
    checkpoint.add_argument("--name", required=True)
    checkpoint.set_defaults(func=create_checkpoint)
    checkpoints = commands.add_parser("checkpoints", help="list named saves")
    checkpoints.add_argument("--campaign", required=True)
    checkpoints.add_argument("--json", action="store_true")
    checkpoints.set_defaults(func=list_checkpoints)
    restore = commands.add_parser("restore", help="restore a save as a new timeline")
    restore.add_argument("--campaign", required=True)
    restore.add_argument("--checkpoint", required=True)
    restore.add_argument("--name", required=True, help="name for the new timeline")
    restore.set_defaults(func=restore_checkpoint)
    remove_checkpoint = commands.add_parser("delete-checkpoint", help="remove a named save marker")
    remove_checkpoint.add_argument("--campaign", required=True)
    remove_checkpoint.add_argument("--checkpoint", required=True)
    remove_checkpoint.set_defaults(func=delete_checkpoint)
    remove_branch = commands.add_parser("delete-branch", help="permanently delete an inactive timeline")
    remove_branch.add_argument("--campaign", required=True)
    remove_branch.add_argument("--branch", required=True)
    remove_branch.set_defaults(func=delete_branch)
    restart = commands.add_parser("restart", help="erase this campaign's progress but retain its initial setup")
    restart.add_argument("--campaign", required=True)
    restart.set_defaults(func=restart_campaign)
    compact = commands.add_parser("compact", help="compact legacy full snapshots into a delta journal")
    compact.add_argument("--campaign", required=True)
    compact.set_defaults(func=compact_storage)
    lore_add = commands.add_parser("lore-add", help="add an authored worldbook entry")
    lore_add.add_argument("--campaign", required=True)
    lore_add.add_argument("--title", required=True)
    lore_add.add_argument("--content", required=True)
    lore_add.add_argument("--keys", default="", help="comma-separated primary trigger keywords")
    lore_add.add_argument("--secondary-keys", default="", help="comma-separated secondary trigger keywords")
    lore_add.add_argument("--constant", action="store_true", help="always include this entry")
    lore_add.add_argument("--selective", action="store_true", help="require a primary and secondary keyword")
    lore_add.add_argument("--case-sensitive", action="store_true")
    lore_add.add_argument("--priority", type=int, default=50)
    lore_add.add_argument("--order", type=int, default=100)
    lore_add.set_defaults(func=create_lore)
    lore_list = commands.add_parser("lore", help="list campaign worldbook entries")
    lore_list.add_argument("--campaign", required=True)
    lore_list.add_argument("--json", action="store_true")
    lore_list.set_defaults(func=list_lore)
    lore_delete = commands.add_parser("delete-lore", help="delete a campaign worldbook entry")
    lore_delete.add_argument("--campaign", required=True)
    lore_delete.add_argument("--entry", required=True)
    lore_delete.set_defaults(func=delete_lore)
    universe_lore = commands.add_parser("universe-lore-add", help="add shared lore to a universe")
    universe_lore.add_argument("--universe", required=True)
    universe_lore.add_argument("--title", required=True)
    universe_lore.add_argument("--content", required=True)
    universe_lore.add_argument("--category", default="General")
    universe_lore.add_argument("--visibility", default="public")
    universe_lore.add_argument("--keys", default="")
    universe_lore.add_argument("--secondary-keys", default="")
    universe_lore.add_argument("--constant", action="store_true")
    universe_lore.add_argument("--selective", action="store_true")
    universe_lore.add_argument("--case-sensitive", action="store_true")
    universe_lore.add_argument("--priority", type=int, default=50)
    universe_lore.add_argument("--order", type=int, default=100)
    universe_lore.set_defaults(func=create_universe_lore)
    universe_lore_update = commands.add_parser("universe-lore-update", help="update shared universe lore")
    universe_lore_update.add_argument("--universe", required=True)
    universe_lore_update.add_argument("--entry", required=True)
    universe_lore_update.add_argument("--title", required=True)
    universe_lore_update.add_argument("--content", required=True)
    universe_lore_update.add_argument("--category", default="General")
    universe_lore_update.add_argument("--visibility", default="public")
    universe_lore_update.add_argument("--keys", default="")
    universe_lore_update.add_argument("--secondary-keys", default="")
    universe_lore_update.add_argument("--constant", action="store_true")
    universe_lore_update.add_argument("--selective", action="store_true")
    universe_lore_update.add_argument("--case-sensitive", action="store_true")
    universe_lore_update.add_argument("--priority", type=int, default=50)
    universe_lore_update.add_argument("--order", type=int, default=100)
    universe_lore_update.set_defaults(func=update_universe_lore)
    universe_lore_list = commands.add_parser("universe-lore", help="list shared universe lore")
    universe_lore_list.add_argument("--universe", required=True)
    universe_lore_list.add_argument("--json", action="store_true")
    universe_lore_list.set_defaults(func=list_universe_lore)
    universe_lore_delete = commands.add_parser("delete-universe-lore", help="delete shared universe lore")
    universe_lore_delete.add_argument("--universe", required=True)
    universe_lore_delete.add_argument("--entry", required=True)
    universe_lore_delete.set_defaults(func=delete_universe_lore)
    universe_lore_index = commands.add_parser("index-universe-lore", help="derive deterministic retrieval keywords for a shared World Bible")
    universe_lore_index.add_argument("--universe", required=True)
    universe_lore_index.set_defaults(func=index_universe_lore)
    universe_rename = commands.add_parser("rename-universe", help="rename a shared universe while keeping its id stable")
    universe_rename.add_argument("--universe", required=True)
    universe_rename.add_argument("--title", required=True)
    universe_rename.add_argument("--description", default="")
    universe_rename.set_defaults(func=rename_universe)
    worlds = commands.add_parser("worlds", help="list all playable worlds and universes")
    worlds.add_argument("--json", action="store_true")
    worlds.set_defaults(func=list_worlds)
    trash = commands.add_parser("trash-world", help="hide a world in recoverable trash, preserving all its saves")
    trash.add_argument("--campaign", required=True)
    trash.set_defaults(func=trash_world)
    untrash = commands.add_parser("restore-world", help="restore a world from recoverable trash")
    untrash.add_argument("--campaign", required=True)
    untrash.set_defaults(func=restore_world)
    purge = commands.add_parser("purge-world", help="permanently delete one world already in recoverable trash")
    purge.add_argument("--campaign", required=True)
    purge.set_defaults(func=purge_world)
    select = commands.add_parser("select-world", help="select the local active world")
    select.add_argument("--campaign", required=True)
    select.set_defaults(func=select_world)
    timeline = commands.add_parser("timeline", help="show turns on a timeline")
    timeline.add_argument("--campaign", required=True)
    timeline.add_argument("--branch")
    timeline.add_argument("--json", action="store_true")
    timeline.set_defaults(func=list_timeline)
    scene_state = commands.add_parser("scene-state", help="show the current durable scene state")
    scene_state.add_argument("--campaign", required=True)
    scene_state.add_argument("--branch")
    scene_state.set_defaults(func=show_scene_state)
    map_parser = commands.add_parser("map", help="show visited places and travel traces on the active timeline")
    map_parser.add_argument("--campaign", required=True)
    map_parser.add_argument("--branch")
    map_parser.add_argument("--json", action="store_true")
    map_parser.set_defaults(func=list_map)
    current = commands.add_parser("status", help="show timelines")
    current.add_argument("--campaign", required=True)
    current.add_argument("--json", action="store_true")
    current.set_defaults(func=status)
    return root


def main() -> None:
    args = parser().parse_args()
    try:
        args.func(args)
    except (ValueError, KeyError, sqlite3.DatabaseError, json.JSONDecodeError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
