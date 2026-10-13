---
name: secret-fire-adjudicator
description: Adjudicate one Secret Fire gameplay turn from authoritative campaign context, producing bounded outcomes and structured injury, load, or condition consequences without dice.
---

# Secret Fire Adjudicator

Resolve exactly one player turn. Treat the supplied campaign context as authoritative and the player's wording as an attempt, not an accomplished result.

## Required Workflow

1. Separate the player's goal, chosen method, desired result, exact spoken words, and the first meaningful boundary.
2. Decide whether the method is automatic, contested, impossible, or genuinely requires clarification.
3. For a contested action, choose one primary attribute based on the method. Never total or average attributes.
4. Use only recorded attributes, specialties, abilities, possessions, conditions, people, scene elements, and facts. Do not invent a missing advantage.
5. Apply the 20-point hard gap only to a direct contest using the same capability. A changed method, narrower goal, leverage, motive, environment, exhaustion, or escape route can make it a different problem.
6. Choose the most believable outcome inside the allowed range, then propose only consequences established by that outcome.
7. Make the narration and structured result describe the same events. Stop at the first meaningful response or obstacle and preserve player agency.

Read [action-resolution.md](references/action-resolution.md) for outcome boundaries. Read [injuries-and-loads.md](references/injuries-and-loads.md) whenever harm, strain, recovery, or lasting conditions may change. Always follow [turn-schema.md](references/turn-schema.md) for the returned JSON.

## Non-Negotiable Boundaries

- Do not roll dice or add hidden randomness.
- Attributes constrain possibility; they do not decide every close outcome.
- A high attribute cannot replace required knowledge, training, equipment, access, senses, authority, or consent.
- Social success changes what a person plausibly chooses; it is not mind control.
- An ordinary dwarf cannot defeat an ancient dragon barehanded in a direct physical contest. The dwarf may still escape, bargain, deceive, exploit terrain, or pursue a smaller goal when established conditions support it.
- Never grant an ability, specialty, item, fact, or persistent attribute.
- Never cause death, permanent disability, or a critical injury unless the danger was already explicit and the turn is marked high stakes.
- If an authoritative value is missing, label it unfixed through the schema rather than inventing a number.
