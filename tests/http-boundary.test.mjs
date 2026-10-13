import test from "node:test";
import assert from "node:assert/strict";
import { Readable } from "node:stream";
import { HttpError, readJsonBody, validateHttpRequest } from "../http-boundary.mjs";

const trustedHeaders = {
  host: "127.0.0.1:4179",
  origin: "http://127.0.0.1:4179",
  "x-secret-fire-request": "1",
  "content-type": "application/json"
};

test("same-origin reads and marked JSON writes pass the local HTTP boundary", () => {
  assert.doesNotThrow(() => validateHttpRequest("GET", "/api/worlds", { host: "127.0.0.1:4179" }, 4179));
  assert.doesNotThrow(() => validateHttpRequest("POST", "/api/restart", trustedHeaders, 4179));
  assert.doesNotThrow(() => validateHttpRequest("POST", "/api/database/import", {
    ...trustedHeaders, "content-type": "application/vnd.sqlite3"
  }, 4179));
});

test("foreign hosts, origins, unmarked writes, and form content types are rejected", () => {
  const cases = [
    ["GET", "/", { host: "attacker.example" }, 403],
    ["POST", "/api/restart", { ...trustedHeaders, origin: "https://attacker.example" }, 403],
    ["POST", "/api/restart", { ...trustedHeaders, "x-secret-fire-request": undefined }, 403],
    ["POST", "/api/restart", { ...trustedHeaders, "content-type": "text/plain" }, 415]
  ];
  for (const [method, path, headers, status] of cases) {
    assert.throws(
      () => validateHttpRequest(method, path, headers, 4179),
      (error) => error instanceof HttpError && error.statusCode === status
    );
  }
});

function bodyStream(chunks, contentLength = null) {
  const stream = Readable.from(chunks);
  stream.headers = contentLength === null ? {} : { "content-length": String(contentLength) };
  return stream;
}

test("JSON body parsing enforces byte limits and reports malformed input", async () => {
  assert.deepEqual(await readJsonBody(bodyStream([Buffer.from('{"ok":true}')]), 64), { ok: true });
  await assert.rejects(readJsonBody(bodyStream([Buffer.from("12345")]), 4),
    (error) => error instanceof HttpError && error.statusCode === 413);
  await assert.rejects(readJsonBody(bodyStream([], 100), 4),
    (error) => error instanceof HttpError && error.statusCode === 413);
  await assert.rejects(readJsonBody(bodyStream([Buffer.from("not json")]), 64),
    (error) => error instanceof HttpError && error.statusCode === 400);
});
