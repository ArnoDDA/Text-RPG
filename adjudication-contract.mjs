const ATTRIBUTES = new Set(["physique", "agility", "perception", "intellect", "will", "charisma", "mystic_power"]);
const MODES = new Set(["automatic", "contested", "impossible"]);
const OUTCOMES = new Set(["impossible", "blocked", "limited_success", "success", "strong_success"]);
const EVIDENCE_KINDS = new Set(["ability", "specialty", "item", "entity", "scene_element", "scene_participant", "scene_pressure", "injury", "condition"]);
const INJURY_STAGES = new Set(["minor", "serious", "critical"]);
const CONSEQUENCE_TYPES = new Set(["injury", "load", "condition"]);
const LOAD_TRACKS = new Set(["physical", "focus", "mystic"]);

function text(value, field, limit = 500) {
  const normalized = String(value ?? "").trim();
  if (!normalized || normalized.length > limit) throw new Error(`Invalid adjudication ${field}. Nothing was saved.`);
  return normalized;
}

function optionalId(value) {
  if (value === null || value === undefined || value === "") return null;
  const id = String(value).trim();
  if (!/^[a-z0-9][a-z0-9_:.-]{0,119}$/.test(id)) throw new Error("An adjudication reference used an invalid id. Nothing was saved.");
  return id;
}

function referenceSets(context = {}) {
  const values = context.references && typeof context.references === "object" ? context.references : {};
  return Object.fromEntries([...EVIDENCE_KINDS].map((kind) => [kind, new Set(Array.isArray(values[kind]) ? values[kind] : [])]));
}

function normalizeConsequence(value, highStakes) {
  if (!value || typeof value !== "object" || !CONSEQUENCE_TYPES.has(value.type)) {
    throw new Error("The adjudicator proposed an invalid consequence. Nothing was saved.");
  }
  if (value.type === "load") {
    if (!LOAD_TRACKS.has(value.track) || !["advance", "recover"].includes(value.direction)) {
      throw new Error("The adjudicator proposed an invalid load change. Nothing was saved.");
    }
    return { type: "load", track: value.track, direction: value.direction, source: text(value.source, "load source", 300) };
  }
  const action = String(value.action ?? "");
  const id = optionalId(value.id);
  if (!id) throw new Error("A persistent consequence needs a stable id. Nothing was saved.");
  if (value.type === "condition") {
    if (!["add", "remove"].includes(action)) throw new Error("The adjudicator proposed an invalid condition change. Nothing was saved.");
    if (action === "remove") return { type: "condition", action, id, source: text(value.source, "condition recovery source", 300) };
    return {
      type: "condition", action, id, label: text(value.label, "condition label", 120),
      effect: text(value.effect, "condition effect", 500), source: text(value.source, "condition source", 300),
      recovery_condition: text(value.recovery_condition, "condition recovery", 500)
    };
  }
  if (!["add", "worsen", "recover"].includes(action) || !INJURY_STAGES.has(value.stage)) {
    throw new Error("The adjudicator proposed an invalid injury change. Nothing was saved.");
  }
  const permanent = value.permanent === true;
  if (permanent && (!highStakes || value.stage !== "critical")) {
    throw new Error("Permanent harm was proposed without an explicit critical risk. Nothing was saved.");
  }
  const affected = Array.isArray(value.affected_functions)
    ? value.affected_functions.map((item) => String(item).trim()).filter(Boolean).slice(0, 6)
    : [];
  if (action !== "recover" && !affected.length) throw new Error("An injury needs a concrete functional effect. Nothing was saved.");
  return {
    type: "injury", action, id, stage: value.stage, label: text(value.label, "injury label", 120),
    affected_functions: affected, source: text(value.source, "injury source", 300),
    recovery_condition: text(value.recovery_condition, "injury recovery", 500), permanent
  };
}

export function validateResolution(value, context = {}) {
  // Some narrator completions still emit the older names used by the first
  // scene schema. Accept those names only as a lossless boundary conversion;
  // all adjudication rules below remain unchanged.
  const candidate = value && typeof value === "object" && !Array.isArray(value)
    ? {
        ...value,
        mode: value.mode ?? value.action_type,
        reason: value.reason ?? value.basis
      }
    : value;
  if (!candidate || typeof candidate !== "object" || Array.isArray(candidate) || !MODES.has(candidate.mode)) {
    throw new Error("The narrator did not return a valid adjudication. Nothing was saved.");
  }
  const mode = candidate.mode;
  const outcome = candidate.outcome;
  if (!OUTCOMES.has(outcome)) throw new Error("The adjudicator returned an invalid outcome. Nothing was saved.");
  if (mode === "automatic" && !["success", "limited_success"].includes(outcome)) {
    throw new Error("An automatic action must resolve as success or limited success. Nothing was saved.");
  }
  if (mode === "impossible" && outcome !== "impossible") throw new Error("An impossible method must remain impossible. Nothing was saved.");
  const primaryAttribute = candidate.primary_attribute === null || candidate.primary_attribute === undefined ? null : String(candidate.primary_attribute);
  if ((mode === "contested") !== ATTRIBUTES.has(primaryAttribute)) {
    throw new Error("A contested action needs exactly one valid primary attribute. Nothing was saved.");
  }
  const directContest = candidate.direct_contest === true;
  const oppositionValue = candidate.opposition && typeof candidate.opposition === "object" ? candidate.opposition : {};
  const opposition = {
    entity_id: optionalId(oppositionValue.entity_id),
    attribute: oppositionValue.attribute === null || oppositionValue.attribute === undefined ? null : String(oppositionValue.attribute)
  };
  if (opposition.attribute !== null && !ATTRIBUTES.has(opposition.attribute)) throw new Error("The opposition used an invalid attribute. Nothing was saved.");
  if (directContest && (mode !== "contested" || !opposition.entity_id || !opposition.attribute)) {
    throw new Error("A direct contest needs a recorded opposing entity and attribute. Nothing was saved.");
  }
  const knownEntities = new Set(context.entities ?? []);
  if (opposition.entity_id && !knownEntities.has(opposition.entity_id)) throw new Error("The adjudicator referenced an unknown opponent. Nothing was saved.");

  const sets = referenceSets(context);
  const evidence = Array.isArray(candidate.evidence) ? candidate.evidence.slice(0, 12).map((entry) => {
    if (!entry || typeof entry !== "object" || !EVIDENCE_KINDS.has(entry.kind)) throw new Error("The adjudicator used an invalid evidence type. Nothing was saved.");
    const id = optionalId(entry.id);
    if (!id || !sets[entry.kind].has(id)) throw new Error("The adjudicator relied on an unrecorded fact or capability. Nothing was saved.");
    return { kind: entry.kind, id };
  }) : [];
  const highStakes = candidate.high_stakes === true;
  if (highStakes && !["imminent", "combat"].includes(context.threat)) {
    throw new Error("High-stakes harm was not established before this turn. Nothing was saved.");
  }
  const consequences = Array.isArray(candidate.consequences)
    ? candidate.consequences.slice(0, 4).map((entry) => normalizeConsequence(entry, highStakes))
    : [];

  let attributeGap = { status: "not_applicable" };
  if (directContest) {
    const actorValue = context.attributes?.player?.[primaryAttribute];
    const oppositionValueNumber = context.attributes?.[opposition.entity_id]?.[opposition.attribute];
    if (Number.isFinite(actorValue) && Number.isFinite(oppositionValueNumber)) {
      const difference = actorValue - oppositionValueNumber;
      attributeGap = { status: "known", actor: actorValue, opposition: oppositionValueNumber, difference };
      if (difference <= -20 && !["impossible", "blocked"].includes(outcome)) {
        throw new Error("The proposed direct-contest result crosses a recorded 20-point capability gap. Nothing was saved.");
      }
      if (difference >= 20 && !["success", "strong_success"].includes(outcome)) {
        throw new Error("The proposed direct-contest result contradicts a recorded 20-point advantage. Nothing was saved.");
      }
    } else {
      attributeGap = { status: "unfixed" };
    }
  }

  return {
    mode, primary_attribute: primaryAttribute, direct_contest: directContest, opposition, evidence,
    outcome, high_stakes: highStakes, reason: text(candidate.reason, "reason", 700), consequences, attribute_gap: attributeGap
  };
}
