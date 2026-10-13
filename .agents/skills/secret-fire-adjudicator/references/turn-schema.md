# Turn Output Schema

Return exactly one JSON object and no Markdown.

For a playable turn:

```json
{
  "action_frame": {
    "mode": "play",
    "goal": "what the player is trying to achieve now",
    "method": "the method explicitly attempted",
    "desired_result": "the result the player wants, not an accomplished fact",
    "interpretation": "one concise authorized attempted step",
    "first_boundary": "the first response or obstacle where this turn stops",
    "verbatim_speech": []
  },
  "resolution": {
    "mode": "automatic | contested | impossible",
    "primary_attribute": "physique | agility | perception | intellect | will | charisma | mystic_power | null",
    "direct_contest": false,
    "opposition": {"entity_id": "stable id or null", "attribute": "attribute id or null"},
    "evidence": [{"kind": "ability | specialty | item | entity | scene_element | scene_participant | scene_pressure | injury | condition", "id": "authoritative id"}],
    "outcome": "impossible | blocked | limited_success | success | strong_success",
    "high_stakes": false,
    "reason": "short concrete reason based on established facts",
    "consequences": []
  },
  "narration": "player-facing Simplified Chinese prose",
  "manifest": {
    "scene": {}, "entities": [], "state_updates": [], "events": [], "facts": [], "beliefs": [], "threads": []
  }
}
```

Consequence shapes:

```json
{"type":"injury","action":"add | worsen | recover","id":"stable_lowercase_id","stage":"minor | serious | critical","label":"具体伤势","affected_functions":["具体受影响功能"],"source":"本回合已发生的来源","recovery_condition":"恢复所需条件","permanent":false}
{"type":"load","track":"physical | focus | mystic","direction":"advance | recover","source":"负荷变化来源"}
{"type":"condition","action":"add | remove","id":"stable_lowercase_id","label":"具体状态","effect":"实际影响","source":"来源","recovery_condition":"解除条件"}
```

For clarification:

```json
{"action_frame":{"mode":"clarify","goal":"...","method":"...","desired_result":"...","interpretation":"what is clear","question":"one concise question","verbatim_speech":[]},"narration":"","manifest":{}}
```

Rules:

- `verbatim_speech` contains exact substrings of the player's input only.
- `primary_attribute` is required only for `contested`.
- `direct_contest=true` requires an opposition entity and attribute.
- `automatic` uses `success`; `impossible` uses `impossible`.
- Use no consequences when durable harm, strain, recovery, or condition change did not occur.
- Do not put consequence-controlled player mechanics in `manifest.state_updates`; the local system applies validated consequences.
