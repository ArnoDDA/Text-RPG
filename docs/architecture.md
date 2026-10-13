# Architecture

Secret Fire keeps each responsibility in one place so a long campaign can be
inspected and restored without trusting a model transcript.

```text
public/ browser experience
       │ local HTTP, 127.0.0.1 only
server.mjs local application boundary and Codex adapter
       │ Python subprocess calls
engine.py SQLite ledger, memory retrieval, worlds, saves, and timelines
       │
private SQLite save outside this project by default
```

## Source map

| Location | Owns |
| --- | --- |
| `public/index.html` | Two user-facing states: create/choose a chronicle, then play a chronicle. |
| `public/app.js` | Browser state, local API calls, story rendering, and archive controls. |
| `public/styles.css` | Responsive visual system for the welcome desk, reading room, and archive. |
| `server.mjs` | Local HTTP routes, input validation, model selection, and one ephemeral Codex turn. |
| `engine.py` | SQLite schema, people and party ledger, canonical facts, NPC beliefs, open story threads, worldbook retrieval, saves, and branching. It never calls a model. |
| `prompts/gm-rules.md` | Stable game-master contract included in every turn. |
| `prompts/narrative-profile.md` | Writing direction for the narrator. |
| `data/` | Versioned, fixed World Bible source records; never personal campaign data. |
| `tools/import_world_bible.py` | Idempotent import of fixed canon into a new local save. |
| `tests/` | Ledger recovery and isolation invariants. |

## Durable story model

An SQLite file can hold one shared **universe outline** and many independent
playable **chronicles**. The outline is fixed canon: setting rules, broad
geography, peoples, item classes, and established history. A chronicle does not
replace that outline with a newly generated world. It persists the concrete
instances established during play: its protagonist, visited streets and
buildings, people, organizations, services, routes, events, private facts,
beliefs, threads, branches, and saves. Leaving a scene unloads these records
from the prompt but never deletes them; revisiting resolves the same entities
and applies later state changes. Chronicle records never leak into another save.

Stable identity belongs to a chronicle while mutable state belongs to a branch.
A branch inherits the world visible at its fork point, then isolates later
discoveries and changes. An entity first introduced after a fork must not become
visible in sibling branches merely because its identity row exists. The model
never receives the whole chronicle: each turn retrieves a bounded package
centered on the current place, present people, active events, explicit mentions,
and directly connected canon. See `docs/DYNAMIC_WORLD_MEMORY.md`.

Concrete places and traveled routes reuse the entity ledger. A location entity
is visible only when the active branch has a state row for it. That state owns
its parent location, descriptive anchors, access, last known condition, first
and latest visit, and visit count. Each committed scene resolves the actual
post-turn location locally, updates the player's stable location id, and records
a route only when movement between two different places occurred. The map reads
these records directly. Prompt retrieval is capped to the current place, its
parent, connected places, and old places explicitly named in the action.

Each branch has a full root state. Turns record only changed state rows in
`state_deltas`, and a complete anchor is retained every 25 turns. A named save
only points to an existing turn; it does not copy a full game state.

The prompt for a normal turn uses the current scene, open threads, relevant
facts, NPC beliefs, recent turns, and a 3,600-character world-note budget. The
ledger remains the durable source of truth, while Codex only narrates one
ephemeral turn at a time.

Every database upgrade is recorded in `schema_migrations` and mirrored in
SQLite `user_version`. Complete backups use SQLite's online backup API.
Imports are integrity-checked, migrated in a staging file, and atomically
installed only after validation succeeds.

## People and party continuity

Important people reuse the branch-local entity ledger. Stable identity lives
in an entity profile; relationship, location, current activity, relationship
anchor, and a compact list of high-value shared memories live in branch state.
This makes an NPC's changes recoverable through checkpoints and alternate
timelines without a second persistence system.

The prompt includes at most eight people: up to four party members, two core
people, manually pinned people, then those present or textually relevant to
the scene. The party roster itself has no hard size limit; four is only the
ordinary per-turn accompaniment budget. People who are away, archived, or
deceased remain in the local ledger but do not consume ordinary prompt space.

The archive retains 30 high-value memories for party/core people, 18 for pinned
or recurring people, and 12 for background people. The prompt receives no more
than three memories for each selected person. Codex can propose structured
updates after a scene; the local engine normalizes, deduplicates, caps, and
stores them.

After each committed story turn, the engine compares the people ledger before
and after the transaction. A compact change summary lets the browser visibly
confirm newly recorded people, relationship and location changes, and new
high-value memories without exposing raw manifest bookkeeping.

## Trade and resources

The wallet and transaction history live inside the player's branch-local
mechanics state, so checkpoints and alternate timelines restore them together
with possessions. Money uses a non-negative integer copper base unit; display
conversion never introduces fractional state.

Codex may propose a bounded trade offer only for the current narrated scene.
The offer is stored as non-authoritative scene data and expires when a later
story turn becomes current. Accepting an offer calls one local engine command
that validates funds, quantity, item category, rarity source, and duplicate
submission before changing anything. Wallet settlement, item creation or
transfer, transaction history, the silent local turn, and its state delta are
written in one SQLite transaction. The narrator's ordinary state patch path
cannot modify resources.

## Reviewable reading aids

World Bible search is browser-side because the fixed encyclopedia is already a
bounded local payload. Each SQLite lore row keeps a readable article beside a
structured `record_json` database record. The record has a stable identity,
canonical name, aliases, status, region, tags, retrieval keys, typed fields,
and explicit relations, so callers do not need to infer entities from prose.
Search covers page text and retrieval metadata while keeping storage fields
behind the player-facing article. Exact
page-title mentions become internal links; related pages are ranked from title
mentions, shared retrieval terms, and category proximity.

Chapter summaries are deliberately separate from narrator memory. A draft is
generated from an explicit range of player-facing turns, and the ledger stores
its exact range plus a SHA-256 hash of the source rows. The player can inspect
those turns, edit the draft, and explicitly approve it. Neither draft nor
approved summaries are included in a future turn prompt or used instead of the
original ledger.
