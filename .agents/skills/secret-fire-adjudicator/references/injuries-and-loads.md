# Injuries, Loads, And Conditions

Consequences are persistent world state, not dramatic decoration. Propose them only when the narration concretely establishes their source and effect.

## Injuries

Stages are `minor`, `serious`, and `critical`.

- `minor`: Painful or limiting but normally manageable without immediate expert intervention.
- `serious`: Material loss of function, dangerous bleeding, fracture, deep trauma, or comparable harm requiring treatment and time.
- `critical`: Immediate threat to life or fundamental function. Use only after explicit high-stakes danger.

Add a new injury at `minor` during ordinary play. A high-stakes event may add `serious`; only an explicitly high-stakes event may add or worsen to `critical`. Worsening or recovery moves at most one stage in one turn. Recovering a minor injury removes it. Permanent harm requires `critical`, explicit prior risk, and `permanent=true`; it must never be a surprise consequence of a routine failure.

Each injury needs a concrete label, affected functions, source, and recovery condition. Do not use vague entries such as "hurt" or "weakened".

## Loads

Each track has its own ordered stages:

- physical: `稳定 → 疲劳 → 透支 → 崩溃`
- focus: `稳定 → 分散 → 动摇 → 失控`
- mystic: `稳定 → 吃力 → 过载 → 枯竭`

Move a track by at most one stage per turn. Advance it only for meaningful exertion, repeated strain, overextension, or an explicit ability cost. Recovery requires rest, treatment, time, fulfilled conditions, or a relevant ability established in the narration. A routine action does not create load merely because a track exists.

## Conditions

Conditions cover sourced states not represented well by an injury or load, such as poison, restraint, blindness, panic, or a sustained magical effect. Give each a stable lowercase ID, visible label, concrete effect, source, and recovery condition. Add or remove only what the narration establishes.

Do not duplicate one consequence across injury, load, and condition unless each record has a distinct gameplay meaning.
