// A small, testable boundary between the narrator's interpretation and the
// durable story ledger. It cannot prove semantic fidelity, but malformed or
// invented verbatim speech must never become an authoritative turn. The
// optional context contains authoritative ids from the local ledger.
export function validateActionFrame(value, playerInput, context = {}) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("The narrator did not explain how it read this action. Nothing was saved.");
  }
  const mode = value.mode;
  if (mode !== "play" && mode !== "clarify") {
    throw new Error("The narrator returned an invalid action reading. Nothing was saved.");
  }
  const interpretation = String(value.interpretation ?? "").trim();
  if (!interpretation || interpretation.length > 500) {
    throw new Error("The narrator's action reading was incomplete. Nothing was saved.");
  }
  const speech = value.verbatim_speech;
  if (!Array.isArray(speech) || speech.length > 8 || speech.some((line) =>
    typeof line !== "string" || !line.trim() || line.length > 500 || !playerInput.includes(line)
  )) {
    throw new Error("The narrator attributed words you did not write. Nothing was saved.");
  }
  if (mode === "clarify") {
    const question = String(value.question ?? "").trim();
    if (!question || question.length > 240) {
      throw new Error("The narrator requested clarification without a clear question. Nothing was saved.");
    }
    return {
      mode,
      goal: String(value.goal ?? "").trim().slice(0, 300),
      method: String(value.method ?? "").trim().slice(0, 300),
      desired_result: String(value.desired_result ?? "").trim().slice(0, 300),
      interpretation, verbatim_speech: speech, question,
      intent: String(value.intent ?? "").trim().slice(0, 160),
      target: String(value.target ?? "").trim().slice(0, 300),
      risk_tolerance: normalizeRisk(value.risk_tolerance)
    };
  }
  const goal = String(value.goal ?? "").trim();
  const method = String(value.method ?? "").trim();
  const desiredResult = String(value.desired_result ?? "").trim();
  if (!goal || !method || !desiredResult || [goal, method, desiredResult].some((item) => item.length > 300)) {
    throw new Error("The narrator did not separate the goal, method, and desired result. Nothing was saved.");
  }
  const firstBoundary = String(value.first_boundary ?? "").trim();
  if (!firstBoundary || firstBoundary.length > 300) {
    throw new Error("The narrator did not limit this turn to one playable step. Nothing was saved.");
  }
  const plan = normalizePlan(value, context);
  return {
    mode, goal, method, desired_result: desiredResult,
    interpretation, verbatim_speech: speech, first_boundary: firstBoundary,
    ...plan
  };
}

const RISKS = new Set(["cautious", "balanced", "bold"]);

function normalizeRisk(value) {
  const risk = String(value ?? "balanced").trim().toLowerCase();
  return RISKS.has(risk) ? risk : "balanced";
}

function stableId(value, field) {
  const id = String(value ?? "").trim();
  if (!id) throw new Error(`The narrator returned an empty ${field} reference. Nothing was saved.`);
  if (!/^[a-z0-9][a-z0-9_:.-]{0,119}$/.test(id)) {
    throw new Error(`The narrator returned an invalid ${field} reference. Nothing was saved.`);
  }
  return id;
}

function knownReference(context, kind, id) {
  const references = context?.references;
  if (!references || !Array.isArray(references[kind])) return;
  if (!references[kind].includes(id)) {
    throw new Error(`The action plan referenced an unknown ${kind} id. Nothing was saved.`);
  }
}

function normalizeReferenceList(value, kind, limit, field, context) {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.length > limit) {
    throw new Error(`The narrator returned an invalid ${field} list. Nothing was saved.`);
  }
  return value.map((entry) => {
    const id = stableId(entry, field);
    knownReference(context, kind, id);
    return id;
  });
}

function normalizePartyOrders(value, context) {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value) || value.length > 8) {
    throw new Error("The narrator returned an invalid party order list. Nothing was saved.");
  }
  return value.map((entry) => {
    if (!entry || typeof entry !== "object" || Array.isArray(entry)) {
      throw new Error("The narrator returned an invalid party order. Nothing was saved.");
    }
    const personId = stableId(entry.person_id ?? entry.entity_id ?? entry.id, "party");
    knownReference(context, "entity", personId);
    const role = String(entry.role ?? "").trim().slice(0, 120);
    const instruction = String(entry.instruction ?? entry.order ?? "").trim().slice(0, 300);
    if (!role || !instruction) throw new Error("A party order needs a role and instruction. Nothing was saved.");
    return { person_id: personId, role, instruction };
  });
}

function normalizePlan(value, context) {
  return {
    intent: String(value.intent ?? "").trim().slice(0, 160),
    target: String(value.target ?? "").trim().slice(0, 300),
    party_orders: normalizePartyOrders(value.party_orders, context),
    ability_refs: normalizeReferenceList(value.ability_refs, "ability", 6, "ability", context),
    item_refs: normalizeReferenceList(value.item_refs, "item", 6, "item", context),
    risk_tolerance: normalizeRisk(value.risk_tolerance)
  };
}
