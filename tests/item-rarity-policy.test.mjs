import test from "node:test";
import assert from "node:assert/strict";
import { applyRarityAvailability } from "../item-rarity-policy.mjs";

test("new high-rarity items need an appropriate source", () => {
  const streetSword = applyRarityAvailability({ name: "街边长剑", rarity: "rare" });
  assert.equal(streetSword.rarity, "common");
  assert.equal(streetSword.rarity_known, false);
  assert.equal(applyRarityAvailability({
    name: "工坊长剑", rarity: "rare", rarity_context: "specialist_access", rarity_basis: "由城中持证武器工坊出售"
  }).rarity, "rare");
  assert.equal(applyRarityAvailability({
    name: "大师长剑", rarity: "exceptional", rarity_context: "specialist_access", rarity_basis: "由知名武器工坊制作"
  }).rarity, "rare");
  assert.equal(applyRarityAvailability({
    name: "近卫长剑", rarity: "exceptional", rarity_context: "restricted_source", rarity_basis: "来自王室近卫封闭军械库"
  }).rarity, "exceptional");
});

test("legendary and mythic rarity follows established provenance", () => {
  const unidentified = applyRarityAvailability({
    name: "破晓之刃", rarity: "legendary", rarity_context: "restricted_source", rarity_basis: "在封印遗迹中发现"
  });
  assert.equal(unidentified.rarity, "exceptional");
  assert.equal(unidentified.rarity_known, false);

  const legendary = applyRarityAvailability({
    name: "破晓之刃", rarity: "legendary", rarity_context: "historic_provenance",
    rarity_basis: "王室编年史、守剑人谱系与剑身铭文共同证实它终结过北境战争"
  });
  assert.equal(legendary.rarity, "legendary");
  assert.equal(legendary.rarity_known, true);

  const mythic = applyRarityAvailability({
    name: "初火余烬", rarity: "mythic", rarity_context: "mythic_provenance",
    rarity_basis: "既有世界设定确认它是创世初火仅存的唯一余烬"
  });
  assert.equal(mythic.rarity, "mythic");
  assert.equal(mythic.rarity_known, true);
});

test("an existing named item keeps its confirmed rarity when its state changes", () => {
  const result = applyRarityAvailability(
    { id: "dawn_blade", name: "破晓之刃", rarity: "common", status: "lost" },
    [{ id: "dawn_blade", name: "破晓之刃", rarity: "legendary", rarity_known: true }]
  );
  assert.equal(result.rarity, "legendary");
  assert.equal(result.rarity_context, "existing_record");
});

test("an unidentified record can be identified by later evidence", () => {
  const result = applyRarityAvailability(
    {
      id: "dawn_blade", name: "破晓之刃", rarity: "legendary", rarity_context: "historic_provenance",
      rarity_basis: "三份独立史料和原主人的封印已经互相印证"
    },
    [{ id: "dawn_blade", name: "破晓之刃", rarity: "exceptional", rarity_known: false }]
  );
  assert.equal(result.rarity, "legendary");
  assert.equal(result.rarity_known, true);
});
