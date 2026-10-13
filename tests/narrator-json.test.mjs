import test from "node:test";
import assert from "node:assert/strict";
import { NarratorJsonError, parseNarratorJson } from "../narrator-json.mjs";

test("bare narrator JSON parses normally", () => {
  assert.deepEqual(parseNarratorJson('{"narration":"继续。","manifest":{}}'), {
    narration: "继续。", manifest: {}
  });
});

test("a fenced final object is recovered", () => {
  const value = parseNarratorJson('已完成核对。\n```json\n{"narration":"继续。","manifest":{}}\n```');
  assert.equal(value.narration, "继续。");
});

test("the last complete object wins over an earlier progress example", () => {
  const value = parseNarratorJson('先检查格式 {"example":true}\n最终结果：\n{"narration":"酒杯落在桌上。","manifest":{}}');
  assert.equal(value.narration, "酒杯落在桌上。");
  assert.equal(value.example, undefined);
});

test("plain prose produces a typed format error without exposing JSON internals", () => {
  assert.throws(
    () => parseNarratorJson("我会按裁决技能核对回合。"),
    (error) => error instanceof NarratorJsonError && !/Unexpected token/.test(error.message)
  );
});
