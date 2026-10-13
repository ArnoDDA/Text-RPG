import test from "node:test";
import assert from "node:assert/strict";
import { composeTurnInput } from "../public/turn-input.js";

test("action and speech are independently optional", () => {
  assert.equal(composeTurnInput("  走近门口  ", ""), "行动尝试：走近门口");
  assert.equal(composeTurnInput("", "  谁在里面？  "), "角色说出的原话：谁在里面？");
  assert.equal(composeTurnInput("  ", " \n "), "");
});

test("exact speech stays verbatim alongside an attempted action", () => {
  assert.equal(composeTurnInput("轻敲两下门", "我说：\"请开门。\""),
    "行动尝试：轻敲两下门\n角色说出的原话：我说：\"请开门。\"");
});
