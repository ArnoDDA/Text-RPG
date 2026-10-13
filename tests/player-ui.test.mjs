import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const root = new URL("../", import.meta.url);
const html = await readFile(new URL("public/index.html", root), "utf8");
const css = await readFile(new URL("public/styles.css", root), "utf8");
const app = await readFile(new URL("public/app.js", root), "utf8");
const server = await readFile(new URL("server.mjs", root), "utf8");
const presets = JSON.parse(await readFile(new URL("data/character_presets.json", root), "utf8"));

function openingTag(id, tag = "form") {
  const match = html.match(new RegExp(`<${tag}[^>]*id=["']${id}["'][^>]*>`));
  assert.ok(match, `${id} must exist`);
  return match[0];
}

test("internal item and character record forms cannot appear in the player UI", () => {
  for (const id of ["possession-form", "cast-form"]) {
    const tag = openingTag(id);
    assert.match(tag, /\shidden(?:\s|>|=)/);
    assert.match(tag, /\sinert(?:\s|>|=)/);
    assert.match(tag, /aria-hidden=["']true["']/);
  }
  assert.match(css, /#possession-form\[hidden\]/);
  assert.match(css, /#cast-form\[hidden\]/);
  assert.doesNotMatch(app, /actionButton\(localized\(["']Edit["']/);
});

test("save writes are same-origin marked and long tasks keep one campaign identity", () => {
  assert.match(app, /headers\.set\("x-secret-fire-request", "1"\)/);
  assert.match(app, /localRequest\("\/api\/turn"/);
  assert.match(app, /localRequest\("\/api\/database\/import"/);
  assert.match(server, /validateHttpRequest\(request\.method, pathname, request\.headers, port\)/);
  assert.match(server, /runGameTurn\(action\.trim\(\), model, outputDensity, narratorSettings, campaign\)/);
  assert.match(server, /commitManifest\(manifest, campaign\)/);
  assert.match(server, /turn\/interrupt/);
});

test("manual narrator-memory authoring stays outside the player interface", () => {
  const tag = openingTag("lore-drawer", "details");
  assert.match(tag, /\shidden(?:\s|>|=)/);
  assert.match(tag, /\sinert(?:\s|>|=)/);
  assert.match(css, /\.archive-drawer\[hidden\]/);
});

test("the character sheet shows recorded abilities without an ability editor", () => {
  assert.match(html, /id=["']ability-list["']/);
  assert.match(html, /id=["']ability-loads["']/);
  assert.match(app, /fetch\(["']\/api\/abilities["']\)/);
  assert.doesNotMatch(html, /id=["']ability-form["']/);
  assert.doesNotMatch(app, /method:\s*["'](?:POST|PATCH|DELETE)["'][\s\S]{0,120}\/api\/abilities/);
  assert.match(css, /\.ability-card/);
  assert.match(app, /abilityLoads\.hidden = false/);
  assert.match(app, /function appendResolution\(resolution\)/);
  assert.match(css, /\.character-consequences/);
  assert.match(css, /\.turn-resolution/);
});

test("Arno is a server-backed complete starting character", () => {
  assert.equal(presets.presets.length, 1);
  const arno = presets.presets[0];
  assert.equal(arno.id, "arno");
  assert.equal(arno.title, "Arno");
  assert.equal(arno.defaults.player, "Arno");
  assert.equal(arno.setup.people.length, 4);
  assert.equal(arno.setup.items.length, 24);
  assert.equal(arno.setup.scene.state.threat, "calm");
  assert.match(arno.description, /迷失之地/);
  assert.match(arno.description, /多块大陆/);
  assert.match(arno.description, /环镜大陆/);
  assert.match(arno.description, /死灵法师.{0,20}复活/);
  assert.match(arno.description, /多支冒险者小队/);
  assert.match(arno.description, /故事继续/);
  assert.equal(arno.setup.threads.find((thread) => thread.id === "necromancer_revival_crisis").status, "active");
  assert.equal(arno.setup.threads.find((thread) => thread.id === "royal_adventurer_recruitment").status, "active");
  assert.doesNotMatch(JSON.stringify(arno), /明天下午，矿务使团/);
  assert.match(arno.defaults.character.opening_narration, /伊芙琳/);
  assert.match(arno.defaults.character.opening_narration, /你还是进门先看出口/);
  assert.match(arno.defaults.character.opening_narration, /根据目前的观察/);
  assert.match(arno.defaults.character.opening_narration, /没缺胳膊，没少腿/);
  assert.match(arno.defaults.character.opening_narration, /七年，三个月，十一天/);
  assert.doesNotMatch(arno.defaults.character.opening_narration, /赛芮娅·月迹|奥林·维斯|玛尔卡·赤砧|伊芙琳·诺斯/);
  assert.doesNotMatch(arno.defaults.character.opening_narration, /暗号|密信|封印石片/);
  assert.match(arno.setup.people.find((person) => person.id === "evelyn_nox").profile.role, /女公爵/);
  assert.deepEqual(arno.setup.scene.model.pressures, []);
  assert.doesNotMatch(JSON.stringify(arno), /屠龙者的再集结/);
  assert.match(app, /fetch\(["']\/api\/character-presets["']\)/);
  assert.match(app, /preset_id:\s*selectedCharacterPresetId/);
  assert.match(server, /characterPresetById/);
  assert.match(server, /title: "The Lost Lands"/);
  assert.match(html, /The Lost Lands/);
  assert.match(app, /"The Lost Lands": "迷失之地"/);
  assert.match(server, /"--setup", JSON\.stringify\(setup\)/);
  assert.match(server, /opening_narration/);
  assert.match(server, /Active story threads preserve long-term continuity/);
});

test("the first scene opens with authored prose before player input", () => {
  assert.match(app, /character\.opening_narration \|\| character\.opening_pressure/);
  assert.match(app, /The room is waiting for your answer\./);
  assert.match(css, /\.story-opening-lead[^{]*\{[^}]*white-space:pre-wrap/s);
});

test("preset stories live outside deletable player saves", () => {
  const presetList = html.indexOf('id="character-preset-list"');
  const saveList = html.indexOf('id="world-list"');
  const createForm = html.indexOf('id="world-form"');
  assert.ok(presetList > 0 && saveList > presetList && createForm > saveList);
  assert.match(html, /Preset stories are permanent templates/);
  assert.match(html, /id=["']preset-detail-panel["']/);
  assert.match(html, /id=["']start-preset-story["']/);
  assert.match(app, /View save/);
  assert.match(app, /function showPresetDetail\(preset\)/);
  assert.match(app, /function startPresetStory\(\)/);
  assert.doesNotMatch(app, /action\.addEventListener\("click", \(\) => \{\s*showWorlds\(true\)/);
  assert.match(server, /ability_catalog/);
});

test("recorded attributes hide the empty-profile guidance", () => {
  assert.match(app, /attributeSheetNote\.hidden = Boolean\(assignedCount\)/);
});

test("the Chinese character creator localizes preset and opening copy", () => {
  for (const phrase of ["开局角色", "选择一段资料完整的人生", "漂泊冒险者", "开场压力", "平静开始"]) {
    assert.match(app, new RegExp(phrase));
  }
  assert.match(app, /interfaceLanguage === "zh" \? "这个人" : "This person"/);
  assert.match(app, /filter\(Boolean\)\.map\(localized\)/);
});

test("party character details expose recorded attributes, specialties, and abilities", () => {
  assert.match(app, /person\.attributes/);
  assert.match(app, /person\.specialties/);
  assert.match(app, /person\.abilities/);
  assert.match(app, /能力、技法与法术/);
  assert.match(css, /\.npc-attribute-grid/);
  assert.match(css, /\.npc-ability-record/);
});

test("party cards lead with stable personal facts instead of transient relationship state", () => {
  const party = presets.presets[0].setup.people;
  for (const person of party) {
    for (const key of ["ancestry", "gender", "age_stage", "height_cm", "weight_kg", "appearance", "personality", "background"]) {
      assert.ok(person.profile[key], `${person.id} must record ${key}`);
    }
    assert.doesNotMatch(person.profile.role, /Arno|旧友/);
  }
  const malka = party.find((person) => person.id === "malka_redanvil");
  assert.match(malka.profile.role, /河港卫队副队长/);
  assert.doesNotMatch(malka.profile.role, /装卸工/);
  assert.match(app, /person-profile-facts/);
  assert.match(app, /person-profile-summary/);
  assert.doesNotMatch(app, /"与 Arno"\s*:\s*"With Arno"/);
  assert.doesNotMatch(app, /"眼下"\s*:\s*"Now"/);
  assert.doesNotMatch(app, /\(person\.memories \?\? \[\]\)\.slice/);
});

test("short game windows preserve a readable story viewport", () => {
  assert.match(css, /@media\(max-height:780px\)/);
  assert.match(css, /grid-template-rows:auto auto minmax\(11rem,1fr\) auto auto/);
  assert.match(css, /\.turn-inputs\{grid-template-columns:minmax\(0,1fr\) minmax\(0,1fr\)/);
  assert.match(css, /\.player-quickbar-list\{flex-wrap:nowrap;overflow-x:auto/);
});

test("journey journal separates character, gear, and party workflows", () => {
  assert.match(html, /id=["']jump-character["']/);
  assert.match(html, /id=["']jump-backpack["']/);
  assert.match(html, /id=["']jump-party["']/);
  assert.match(html, /id=["']character-profile-grid["']/);
  assert.match(html, /id=["']party-roster["']/);
  assert.match(app, /function showJournalSection\(section = "character"\)/);
  assert.match(app, /function focusPartyMemberGear\(personId\)/);
  assert.match(app, /加入小队/);
  assert.match(app, /离开小队/);
  assert.match(css, /\.party-overview/);
  assert.match(css, /\.character-profile-grid/);
});

test("journey keeps scene state in the play surface and nests backpacks under cards", () => {
  assert.match(html, /id=["']journey-context["']/);
  assert.match(html, /id=["']journey-location["']/);
  assert.match(html, /id=["']journey-activity["']/);
  assert.match(html, /id=["']journey-threat["']/);
  assert.match(html, /id=["']open-player-backpack["']/);
  assert.match(html, /id=["']open-party-backpack["']/);
  assert.match(html, /id=["']player-quickbar["']/);
  assert.match(app, /journeyLocation\.textContent = location/);
  assert.match(app, /function renderPlayerQuickbar/);
  assert.doesNotMatch(app, /appendActionReading\(data\.action_frame\)/);
  assert.doesNotMatch(app, /appendResolution\(data\.resolution\)/);
});

test("every story turn explicitly invokes the project adjudication skill", () => {
  assert.match(server, /\$secret-fire-adjudicator/);
  assert.match(server, /validateActionFrame\(response\.action_frame, action, adjudicationContext\)/);
  assert.match(server, /_action_plan: actionFrame/);
  assert.match(server, /agent_mode: true/);
  assert.match(server, /scene:\s*\{[^}]*resolution/s);
  assert.match(app, /summary\.textContent = interfaceLanguage === "zh" \? "行动计划"/);
  assert.match(app, /action-plan-grid/);
  assert.match(css, /\.action-plan-grid/);
});

test("recommended narration gives NPCs independent agency and migrates the passive default", () => {
  assert.match(app, /npcInitiative:\s*"active"/);
  assert.match(app, /const passiveRecommended/);
  assert.match(app, /migrated\.npcInitiative = "active"/);
  assert.match(server, /Character agency and scene movement/);
  assert.match(server, /NPCs are people pursuing lives, not interfaces/);
  assert.match(server, /first-boundary rule limits only how far the protagonist/);
  assert.match(server, /do not build the whole turn as one answer per NPC/);
  assert.match(server, /advance or complicate that thread/);
  assert.match(server, /include a matching entity update in manifest\.entities/);
  assert.match(server, /never replace detailed availability or intent with placeholders/);
  assert.match(server, /This boundary limits the protagonist's attempted plan only/);
});

test("the narrator uses one grounded GM move without forcing danger or player choices", () => {
  assert.match(server, /GM move — one living-world development at most/);
  for (const kind of ["none", "environment_response", "location_routine", "npc_initiative", "thread_development", "time_consequence", "discovery"]) {
    assert.match(server, new RegExp(kind));
  }
  assert.match(server, /Do not advance a distant plot merely because it is active/);
  assert.match(server, /Prefer an environment or location move when the cast has dominated recent narration/);
  assert.match(server, /The GM move contract chooses which source matters most/);
  assert.match(server, /gm_move: committed\.gm_move/);
  assert.doesNotMatch(html, /GM move|主持人动作/);
});

test("malformed narrator output is retried and never exposed as a JSON parser error", () => {
  assert.match(server, /Narrator returned non-JSON output; retrying once/);
  assert.match(server, /params\.item\.text\?\.trim\(\)/);
  assert.doesNotMatch(server, /params\.item\?\.type === "agentMessage" && !text/);
  assert.match(server, /叙事者本轮没有返回可用的游戏结果/);
  assert.match(app, /本轮没有写入存档，输入内容已保留，可以直接重新发送/);
  assert.match(app, /querySelectorAll\("\.turn-error"\)/);
  assert.match(app, /failure\.classList\.add\("turn-error"\)/);
});

test("the encyclopedia connects ability rules to the guide and relevant item categories", () => {
  assert.match(app, /"Abilities & techniques"/);
  assert.match(app, /ability_relation/);
  assert.match(app, /与能力的关系/);
  assert.match(app, /能力相关/);
});

test("encyclopedia chapters can collapse long entry lists", () => {
  assert.match(app, /collapsedUniverseLoreCategories/);
  assert.match(app, /chapter\.setAttribute\("aria-expanded", isExpanded \? "true" : "false"\)/);
  assert.match(css, /encyclopedia-branch\.expanded \.encyclopedia-chapter/);
});

test("item encyclopedia exposes hierarchical weapon, armor, and magic groups", () => {
  assert.match(app, /const encyclopediaItemSubgroups/);
  assert.match(app, /weapon-blades/);
  assert.match(app, /armor-body/);
  assert.match(app, /Wearables & protection/);
  assert.match(app, /wearable-clothing/);
  assert.match(app, /const magicCircleDefinitions/);
  assert.match(app, /Circle VIII · Legendary/);
  assert.match(app, /function magicCircleForEntry/);
  assert.match(app, /encyclopedia-subgroups/);
  assert.match(app, /subgroupHeading\.setAttribute\("aria-expanded"/);
  assert.match(css, /\.encyclopedia-subgroup-heading/);
});

test("item encyclopedia keeps storage language out of player-facing entries", () => {
  assert.doesNotMatch(app, /这里定义这一类物品的共同用途与边界/);
  assert.doesNotMatch(app, /This category defines shared use and limits/);
  assert.match(app, /使用与限制/);
  assert.match(app, /物品类型/);
});

test("the magic catalogue renders as lore inside the item browser", () => {
  assert.match(app, /\["Magic & rituals", "lore"\]/);
  assert.match(app, /\["Weapons", "item-types"\]/);
  assert.match(app, /source: "lore"/);
  assert.match(app, /"Magic rules": "魔法与仪式"/);
  assert.match(app, /function encyclopediaSection/);
  assert.match(app, /encyclopediaSection\(section\)\.source === "item-types"/);
  assert.doesNotMatch(app, /section !== "Magic & rituals"/);
  assert.match(app, /const magicEntryCount = entriesForSection\("Magic & rituals"\)\.length/);
  assert.match(app, /魔法及仪式条目/);
});

test("database metadata stays behind the player-facing encyclopedia", () => {
  assert.doesNotMatch(html, /id=["']universe-record-(?:type|status|region)["']/);
  assert.doesNotMatch(app, /appendRecordMetadata\(row, selectedEntry\)/);
  assert.match(app, /Structured records remain available to search and narrator retrieval/);
});

test("trade UI exposes only current offers, wallet balance, and local settlement", () => {
  assert.match(html, /id=["']resource-balance["']/);
  assert.match(html, /id=["']trade-offers["']/);
  assert.match(html, /id=["']transaction-history["']/);
  assert.match(app, /fetch\(["']\/api\/resources["']\)/);
  assert.match(app, /saveRequest\(["']\/api\/trades["']/);
  assert.match(server, /trade-commit/);
  assert.match(server, /The local wallet and item ledger are authoritative/);
  assert.doesNotMatch(html, /wallet-balance-input|price-editor|merchant-inventory-editor/);
});

test("party inventory is a read-only view grouped by current party members", () => {
  assert.match(html, /id=["']possessions-tabs["']/);
  assert.match(app, /activePossessionView = "player"/);
  assert.match(app, /function renderPartyPossessions/);
  assert.match(app, /loadedCast\?\.party/);
  assert.match(app, /partyIds\.has\(item\.holder\)/);
  assert.match(app, /item\.holder !== "player" \? \[\]/);
  assert.match(css, /\.party-inventory-member/);
  assert.match(css, /\.possessions-tabs/);
});

test("places belong to the save and remain returnable after leaving the scene", () => {
  assert.match(server, /Persistent place continuity/);
  assert.match(server, /Leaving a place unloads it from the immediate scene but never erases or replaces it/);
  assert.match(server, /manifest\.scene\.location_id/);
  assert.match(html, /Places established in this save remain here after you leave/);
  assert.match(html, /id=["']map-parent["']/);
  assert.match(html, /id=["']map-place-state["']/);
  assert.match(app, /data\.current_place\?\.parent_name/);
  assert.match(app, /route\.description/);
});
