const MUTATING_METHODS = new Set(["POST", "PATCH", "DELETE"]);

export class HttpError extends Error {
  constructor(statusCode, message) {
    super(message);
    this.name = "HttpError";
    this.statusCode = statusCode;
  }
}

function firstHeader(value) {
  return Array.isArray(value) ? value[0] : value;
}

function allowedHosts(port) {
  const suffix = Number(port) === 80 ? "" : `:${port}`;
  return new Set([`127.0.0.1${suffix}`, `localhost${suffix}`]);
}

export function validateHttpRequest(method, pathname, headers, port) {
  const host = String(firstHeader(headers.host) ?? "").toLowerCase();
  if (!allowedHosts(port).has(host)) {
    throw new HttpError(403, "This local service only accepts requests addressed to localhost.");
  }

  const normalizedMethod = String(method ?? "GET").toUpperCase();
  if (!MUTATING_METHODS.has(normalizedMethod)) return;

  const origin = String(firstHeader(headers.origin) ?? "");
  if (origin !== `http://${host}`) {
    throw new HttpError(403, "This save operation must come from the local game page.");
  }
  if (firstHeader(headers["x-secret-fire-request"]) !== "1") {
    throw new HttpError(403, "This save operation is missing its local request marker.");
  }

  const contentType = String(firstHeader(headers["content-type"]) ?? "").toLowerCase();
  const expected = pathname === "/api/database/import" ? "application/vnd.sqlite3" : "application/json";
  if (!contentType.startsWith(expected)) {
    throw new HttpError(415, `Expected ${expected}.`);
  }
}

export async function readJsonBody(request, limit = 2 * 1024 * 1024) {
  const declared = Number(firstHeader(request.headers?.["content-length"]) ?? 0);
  if (Number.isFinite(declared) && declared > limit) {
    throw new HttpError(413, "The request is larger than the 2 MB JSON limit.");
  }

  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    const buffer = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
    size += buffer.length;
    if (size > limit) throw new HttpError(413, "The request is larger than the 2 MB JSON limit.");
    chunks.push(buffer);
  }
  if (!size) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString("utf8"));
  } catch {
    throw new HttpError(400, "The request body must be valid JSON.");
  }
}
