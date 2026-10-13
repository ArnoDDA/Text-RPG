import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import { dialogueStyleGuide, dialogueStyleInternals } from "../dialogue-style.mjs";

const root = new URL("../", import.meta.url);
const catalog = JSON.parse(await readFile(new URL("data/character_presets.json", root), "utf8"));
const people = catalog.presets[0].setup.people;

test("core preset characters define behavioral speech profiles and varied examples", () => {
  const required = ["rhythm", "register", "directness", "humor", "reactions", "emotional_shifts", "avoids"];
  for (const person of people) {
    assert.deepEqual(Object.keys(person.profile.speech_profile), required, person.id);
    assert.equal(person.profile.dialogue_examples.length, 4, person.id);
    for (const example of person.profile.dialogue_examples) {
      assert.ok(example.situation.length > 0, person.id);
      assert.ok(example.text.includes("“") && example.text.includes("”"), person.id);
    }
  }
});

test("dialogue guide injects anchors only for present preset characters", () => {
  const brief = "- Observable participants: 赛芮娅 (`serya_moontread`; allied; position=窗边); 玛尔卡 (`malka_redanvil`; allied; position=桌旁); 路人 (`passing_sailor`; neutral; position=门边)";
  const guide = dialogueStyleGuide(catalog, brief, "我问玛尔卡这些年过得怎么样");
  assert.match(guide, /赛芮娅.*serya_moontread/);
  assert.match(guide, /玛尔卡.*malka_redanvil/);
  assert.doesNotMatch(guide, /奥林.*orin_veyth/);
  assert.doesNotMatch(guide, /passing_sailor/);
  assert.match(guide, /你的七年不会凉，这锅会/);
});

test("only two relevant present characters contribute examples while all keep anchors", () => {
  const brief = "- Observable participants: 赛芮娅 (`serya_moontread`; allied; position=左侧); 奥林 (`orin_veyth`; allied; position=对面); 玛尔卡 (`malka_redanvil`; allied; position=右侧)";
  const guide = dialogueStyleGuide(catalog, brief, "我请玛尔卡判断这个计划");
  assert.match(guide, /奥林.*orin_veyth/);
  assert.match(guide, /不走那条路/);
  assert.match(guide, /不去.*不是怕死/s);
  assert.doesNotMatch(guide, /两个半/);
});

test("example selection follows the immediate conversational situation", () => {
  const brief = "- Observable participants: 伊芙琳 (`evelyn_nox`; allied; position=对面)";
  const vulnerable = dialogueStyleGuide(catalog, brief, "我问伊芙琳这些年有没有想念我们");
  assert.match(vulnerable, /我没有等你/);
  const danger = dialogueStyleGuide(catalog, brief, "我提醒伊芙琳门外可能有人监视");
  assert.match(danger, /门后两个，楼上一个/);
});

test("participant parsing and generic dialogue rules work without preset matches", () => {
  assert.deepEqual(dialogueStyleInternals.participantIds("- Observable participants: none recorded"), []);
  const guide = dialogueStyleGuide(catalog, "- Observable participants: none recorded", "等待");
  assert.match(guide, /Spoken dialogue — live conversation/);
  assert.doesNotMatch(guide, /Present character speech anchors/);
});
