import test from "node:test";
import assert from "node:assert/strict";
import { validateActionFrame } from "../action-contract.mjs";

test("a free-form attempt stays an attempt with a first stopping point", () => {
  const frame = validateActionFrame({
    mode: "play",
    goal: "找到国王", method: "尝试进入宫殿", desired_result: "获准进入",
    interpretation: "尝试进入宫殿",
    first_boundary: "抵达守卫面前",
    verbatim_speech: []
  }, "我想进宫殿，找到国王，说服他帮我，再离开城市");
  assert.equal(frame.mode, "play");
  assert.equal(frame.first_boundary, "抵达守卫面前");
  assert.equal(frame.risk_tolerance, "balanced");
  assert.deepEqual(frame.party_orders, []);
});

test("an agent action plan preserves party, ability, item, and risk references", () => {
  const frame = validateActionFrame({
    mode: "play", intent: "调查", goal: "确认灰屑来源", target: "信上的灰屑",
    method: "让奥林鉴定并由赛芮娅观察窗外", desired_result: "知道它来自哪里",
    interpretation: "调查灰屑来源", first_boundary: "奥林完成初步鉴定",
    party_orders: [{ person_id: "olin", role: "鉴定", instruction: "检查灰屑的材料" }],
    ability_refs: ["lore_ash"], item_refs: ["sealed_letter"], risk_tolerance: "cautious",
    verbatim_speech: []
  }, "让奥林鉴定信上的灰屑，赛芮娅观察窗外", {
    references: { entity: ["olin"], ability: ["lore_ash"], item: ["sealed_letter"] }
  });
  assert.equal(frame.intent, "调查");
  assert.equal(frame.target, "信上的灰屑");
  assert.equal(frame.party_orders[0].person_id, "olin");
  assert.deepEqual(frame.ability_refs, ["lore_ash"]);
  assert.deepEqual(frame.item_refs, ["sealed_letter"]);
  assert.equal(frame.risk_tolerance, "cautious");
  assert.throws(() => validateActionFrame({
    ...frame, ability_refs: ["invented_ability"]
  }, "让奥林鉴定信上的灰屑，赛芮娅观察窗外", {
    references: { entity: ["olin"], ability: ["lore_ash"], item: ["sealed_letter"] }
  }), /unknown ability/);
});

test("literal player dialogue must be copied from the input", () => {
  const input = "我对船长说：‘船什么时候出发？’";
  const frame = validateActionFrame({
    mode: "play", goal: "得知时间", method: "询问船长", desired_result: "获得答复", interpretation: "询问船长出发时间", first_boundary: "船长回应",
    verbatim_speech: ["船什么时候出发？"]
  }, input);
  assert.deepEqual(frame.verbatim_speech, ["船什么时候出发？"]);
  assert.throws(() => validateActionFrame({ ...frame, verbatim_speech: ["带我上船！"] }, input), /did not write/);
});

test("an indirect question does not need invented quotation", () => {
  const frame = validateActionFrame({
    mode: "play", goal: "获得线索", method: "询问守卫", desired_result: "得知是否有人经过", interpretation: "询问守卫是否有人经过", first_boundary: "守卫回应",
    verbatim_speech: []
  }, "我问守卫有没有人经过");
  assert.equal(frame.verbatim_speech.length, 0);
});

test("high-stakes ambiguity can ask one question without a playable outcome", () => {
  const frame = validateActionFrame({
    mode: "clarify", interpretation: "试图使用药瓶", verbatim_speech: [],
    question: "你要把唯一一瓶药给谁？"
  }, "用掉那瓶药");
  assert.equal(frame.question, "你要把唯一一瓶药给谁？");
  assert.throws(() => validateActionFrame({ ...frame, question: "" }, "用掉那瓶药"), /clear question/);
});

test("a missing interpretation or stopping boundary cannot be saved", () => {
  assert.throws(() => validateActionFrame(null, "看看四周"), /did not explain/);
  assert.throws(() => validateActionFrame({ mode: "play", goal: "了解环境", method: "观察", desired_result: "发现线索", interpretation: "看看四周", verbatim_speech: [] }, "看看四周"), /one playable step/);
  assert.throws(() => validateActionFrame({ mode: "play", interpretation: "看看四周", first_boundary: "完成观察", verbatim_speech: [] }, "看看四周"), /goal, method/);
});
