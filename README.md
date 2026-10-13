# Secret Fire

A private, local-first solo text RPG for long-running sword-and-magic stories.
Codex narrates one ephemeral turn at a time; a local SQLite ledger owns every
persistent fact, relationship, branch, save, possession, and important person.

The interface is English by default and includes an English/Chinese switch.
Story narration is Simplified Chinese by default.

## Release status

Secret Fire is ready for **private Agent-mode playtesting and continued
development**. The current build has one complete playable preset, `Arno`, and
the local save, branch, encyclopedia, party, item, trade, map, and narration
workflows are functional. The automated suite currently contains 105 passing
tests.

This repository is not yet a standalone Steam build. Narration currently uses
the Codex account signed in on the player's computer, and the planned offline
mode, desktop packaging, first-run installer, and additional starting presets
remain future product work. See [current state and roadmap](docs/PROJECT_STATUS.md)
for the exact boundary.

## Requirements

- A current Node.js runtime and Python 3.9 or newer.
- Codex desktop or Codex CLI installed and signed in on the same computer.
- A local browser. The game binds to `127.0.0.1` and does not expose a public
  web service.

No npm dependencies or API key are required.

## Start playing

Open this folder as a local project in Codex desktop, then run:

```bash
npm run start
```

Open the printed address, normally `http://127.0.0.1:4179`.

On macOS, the game can also run as a per-user background service. The bundled
LaunchAgent starts it after login and restarts it if the process exits, so the
same local address remains available without keeping a Terminal window open.
The runtime copy lives in `~/Library/Application Support/Secret Fire/app`,
outside macOS-protected Documents folders. Its configuration is stored in
`tools/com.secretfire.local-game.plist`; story data remains in the private data
directory described below.

1. Create or select a world save.
2. Configure the narrator when desired.
3. In the reading room, write an attempted action, exact spoken words, or both
   in separate free-text fields. Neither field requires a preset category.
4. Use Journey during play for character, party, and backpack records; Manage
   holds save points, branches, chapters, and world notes.

The Worlds page can move a chronicle to **Recently removed** and restore it
with its turns, save points, party, and items intact. During play, open
**Journey** for the backpack/equipment and party editors; these local record
changes do not consume a narrated story turn.

During play, **Map** shows the places reached on the active timeline and the
transitions actually recorded in story turns. It is a travel trace, not an
invented coordinate map or a list of every available road. The current place
adds a small atmosphere baseline to the next narrator context: a tavern tends
toward everyday social life, while a dragon-haunted place invites caution.
Established events and the player's action always override that tendency;
neither location forces an encounter. Starting-place profiles and cautious
name-based hints live in `data/location_profiles.json`.

The **Backpack** keeps each named item as a separate, branch-aware record. Its
story role (important/clue/gear/ordinary) is distinct from its stable base
type. The local classifier proposes a type from the item's name and known
description, links it to a World Bible example, and asks the player to choose
when evidence is insufficient. Base uses and limitations live in
`data/item_type_rules.json`; a grand name alone never grants an unverified
ability. See [item encyclopedia](docs/ITEM_ENCYCLOPEDIA.md).

Under **Save protection** in the Archive you can create a one-click local
backup, download a portable SQLite copy, or import a complete Secret Fire
database. Imports are integrity-checked, upgraded through recorded schema
migrations, and installed atomically. The current database is backed up before
an import replaces it.

The game uses the Codex account signed in on the current computer. It needs no
API key and does not put a durable RPG conversation in ordinary Codex history.

## What stays local

The game service binds only to `127.0.0.1`. Personal saves live outside this
portable project by default:

```text
~/.codex-rpg-memory/campaign.sqlite3
```

The project bundle contains code, fixed canon, tests, and documentation. It
contains no account credential and should not contain a personal campaign
SQLite file. See [privacy](docs/privacy.md) for the actual boundary: Codex still
receives the one-turn narration prompt required to generate a response.

Mutating HTTP requests are restricted to the exact localhost origin and carry
a game-specific request marker. JSON bodies are capped at 2 MB, database
imports at 256 MB, and narration calls have bounded RPC and turn timeouts. The
server blocks save mutations while a narration task is active so a completed
turn cannot cross-write into another campaign.

## Long-story design

- **SQLite is authoritative.** Codex proposes the current turn; it does not own
  the campaign transcript or final memory.
- **Saves branch rather than overwrite.** Named checkpoints point to an exact
  turn. Restoring one creates an alternate timeline.
- **Possessions are local records.** The narrator can suggest a change, but the
  system and player control the final item ledger.
- **People are local records.** Every important NPC has a stable identity and
  branch-local relationship, location, activity, anchors, and key memories.
- **Person changes are visible.** After a turn, newly recorded people and
  relationship or status changes are shown to the player for review.
- **The encyclopedia is connected.** Full-text search covers titles, content,
  categories, and retrieval terms. Exact title mentions become links, and each
  page recommends related canon entries.
- **Chapter summaries are reviewable.** Codex can draft a cited summary from an
  exact range of story turns. The player can compare the source, edit the draft,
  and approve it. Summaries never enter narrator memory or replace original
  turns.
- **Context remains bounded.** A turn sees at most eight relevant people. The
  party contribution is capped at four; the roster itself is unlimited.
- **Relationship memories are tiered.** Party/core people retain up to 30 key
  memories, pinned or recurring people 18, and background people 12. A turn
  receives at most the three most useful memories for each selected person.

## Project layout

```text
public/                 Browser interface, styles, UI translations, scene references
prompts/                Runtime narrator contract and narrative profile
data/                   Versioned fixed World Bible source records
tools/                  Canon import, local runtime publishing, and delivery packaging tools
tests/                  SQLite ledger regression tests
docs/                   Architecture, privacy, research notes, project status
engine.py               Durable SQLite memory, retrieval, save, and branch engine
server.mjs              Local HTTP server and ephemeral Codex turn adapter
example-turn.json       Minimal test manifest
```

## Documentation

- [Current state and roadmap](docs/PROJECT_STATUS.md) — completed work, known
  gaps, and recommended next milestones.
- [Architecture](docs/architecture.md) — module boundaries and durable state.
- [Privacy](docs/privacy.md) — save location and security boundary.
- [Narrative study](docs/narrative/writing-study.md) — craft principles behind
  the writing controls.
- [Seven attributes and world adjudication](docs/ATTRIBUTE_SYSTEM.md) — the
  canonical ability scale, attribute boundaries, and fact-first resolution.
- [World-building research](docs/world-building/) — research and design notes
  that informed the fixed setting.
- [Project handoff](docs/PROJECT_HANDOFF.md) — source of truth, maintenance
  commands, data boundaries, and delivery procedure.

## Fixed World Bible

The `world_bible_*.json` files under `data/` are versioned canon sources. Their
stable identities and import order live in `data/world_bible_manifest.json`.
They are separate from personal saves so a fresh local database can reproduce
the setting. After creating a world in the `shattered_realms` universe, import
all fixed canon at once with:

```bash
npm run canon:import
```

The World Bible is also the game's local reference database. Every imported
entry keeps a stable `record_id` and structured metadata in `record_json`
(type, aliases, status, region, retrieval keys, fields, and relations), while
the article remains the player-facing explanation. Search can use those fields
without exposing storage details in the player UI, and the narrator brief
receives the matching metadata together with the prose. The current database source also
includes concrete places, institutions, incident schemas, item provenance,
travel logs, creature registries, and unresolved rumours rather than only
high-level setting chapters.

Set `CODEX_RPG_DB` to target another local database. Imports are idempotent:
they update fixed canon without touching a campaign, its branches, or private
notes. The importer uses a stable `source_id`, so a player-facing title or
section can be renamed without making duplicate encyclopedia pages. Item
categories and rarity rules come from `item_types.json`, `item_type_rules.json`,
and `item_rarities.json`; individual names belong to saves.

## Publish and deliver

The source tree is the only editable project copy. To refresh the independent
always-on macOS runtime after tests pass, run:

```bash
npm run runtime:publish
```

It stages a clean runtime, atomically replaces only the application files, and
restarts `com.secretfire.local-game`. It never copies, deletes, or packages a
personal SQLite save. To create a source-only delivery zip:

```bash
python3 tools/create_delivery_package.py --output /path/to/Secret-Fire-Project.zip
```

## Verify

```bash
npm test
```

The test suite covers turn commits, state retrieval, checkpoints, branches,
compact recovery anchors, World Bible retrieval, possessions, Cast & Party
continuity, schema migrations, complete backup/restore round trips, and
source-audited chapter summaries. The current suite runs 48 Python tests and 57
Node tests. See `docs/UI_TEST_REPORT.md` for the manual browser-flow acceptance
record.
