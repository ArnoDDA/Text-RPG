import test from "node:test";
import assert from "node:assert/strict";
import { validateResolution } from "../adjudication-contract.mjs";

const context = {
  threat: "combat",
  entities: ["player", "ancient_dragon", "tired_archmage"],
  attributes: {
    player: { physique: 25, agility: 36, charisma: 31 },
    ancient_dragon: { physique: 95 },
    tired_archmage: { agility: 32 }
  },
  references: {
    ability: ["technique_disarming_cut"], specialty: [], item: ["climbing_rope"],
    entity: ["player", "ancient_dragon", "tired_archmage"],
    scene_element: ["narrow_exit"], scene_participant: ["ancient_dragon", "tired_archmage"],
    scene_pressure: ["spreading_fire"], injury: [], condition: []
  }
};

function contested(overrides = {}) {
  return {
    mode: "contested", primary_attribute: "physique", direct_contest: true,
    opposition: { entity_id: "ancient_dragon", attribute: "physique" },
    evidence: [{ kind: "scene_participant", id: "ancient_dragon" }],
    outcome: "blocked", high_stakes: false, reason: "古龙在纯粹力量上形成不可跨越的压制。",
    consequences: [], ...overrides
  };
}

test("a 20-point direct gap blocks an impossible head-on victory", () => {
  assert.throws(() => validateResolution(contested({ outcome: "success" }), context), /20-point/);
  const result = validateResolution(contested(), context);
  assert.equal(result.attribute_gap.difference, -70);
});

test("changing the method can make escape a different contest", () => {
  const result = validateResolution(contested({
    primary_attribute: "agility", direct_contest: false,
    opposition: { entity_id: "tired_archmage", attribute: "agility" },
    evidence: [{ kind: "scene_element", id: "narrow_exit" }],
    outcome: "success", reason: "狭窄出口与对手分心使逃离不再是力量正面对抗。"
  }), context);
  assert.equal(result.outcome, "success");
  assert.equal(result.attribute_gap.status, "not_applicable");
});

test("legacy resolution aliases are normalized without weakening validation", () => {
  const result = validateResolution({
    action_type: "automatic", outcome: "success", primary_attribute: null,
    direct_contest: false, opposition: { entity_id: null, attribute: null },
    evidence: [], high_stakes: false,
    basis: "信件就在桌上，阅读它不需要对抗。", consequences: []
  }, context);
  assert.equal(result.mode, "automatic");
  assert.equal(result.reason, "信件就在桌上，阅读它不需要对抗。");
  assert.throws(() => validateResolution({
    action_type: "automatic", outcome: "blocked", primary_attribute: null,
    direct_contest: false, opposition: { entity_id: null, attribute: null },
    evidence: [], high_stakes: false, basis: "不应绕过结果校验。", consequences: []
  }, context), /success or limited success/);
});

test("automatic observation may record a clearly bounded partial success", () => {
  const result = validateResolution({
    mode: "automatic", outcome: "limited_success", primary_attribute: null,
    direct_contest: false, opposition: { entity_id: null, attribute: null },
    evidence: [], high_stakes: false,
    reason: "看见了表面痕迹，但无法确认物品此前是否被调换。", consequences: []
  }, context);
  assert.equal(result.outcome, "limited_success");
});

test("unrecorded abilities and surprise permanent harm are rejected", () => {
  assert.throws(() => validateResolution(contested({
    evidence: [{ kind: "ability", id: "invented_teleport" }]
  }), context), /unrecorded/);
  assert.throws(() => validateResolution(contested({
    consequences: [{
      type: "injury", action: "add", id: "lost_hand", stage: "critical", label: "断手",
      affected_functions: ["无法用手"], source: "攻击", recovery_condition: "无法自然恢复", permanent: true
    }]
  }), context), /Permanent harm/);
});

test("unfixed attributes never receive invented numbers", () => {
  const unfixed = structuredClone(context);
  delete unfixed.attributes.player.physique;
  const result = validateResolution(contested(), unfixed);
  assert.deepEqual(result.attribute_gap, { status: "unfixed" });
});
