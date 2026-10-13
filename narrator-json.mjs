export class NarratorJsonError extends Error {
  constructor(text) {
    super("Narrator response did not contain a complete JSON object.");
    this.name = "NarratorJsonError";
    this.rawText = typeof text === "string" ? text.slice(0, 12000) : "";
    this.usage = null;
  }
}

function parseObject(candidate) {
  const value = JSON.parse(candidate);
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError("Narrator JSON must be an object.");
  }
  return value;
}

function balancedObjects(text) {
  const candidates = [];
  for (let start = 0; start < text.length; start += 1) {
    if (text[start] !== "{") continue;
    let depth = 0;
    let quoted = false;
    let escaped = false;
    for (let index = start; index < text.length; index += 1) {
      const character = text[index];
      if (quoted) {
        if (escaped) escaped = false;
        else if (character === "\\") escaped = true;
        else if (character === '"') quoted = false;
        continue;
      }
      if (character === '"') quoted = true;
      else if (character === "{") depth += 1;
      else if (character === "}") {
        depth -= 1;
        if (depth === 0) {
          candidates.push(text.slice(start, index + 1));
          start = index;
          break;
        }
      }
    }
  }
  return candidates;
}

export function parseNarratorJson(text) {
  if (typeof text !== "string" || !text.trim()) throw new NarratorJsonError(text);
  const trimmed = text.trim();
  try {
    return parseObject(trimmed);
  } catch {}

  const fenced = [...trimmed.matchAll(/```(?:json)?\s*([\s\S]*?)```/gi)].map((match) => match[1].trim());
  for (const candidate of fenced.reverse()) {
    try {
      return parseObject(candidate);
    } catch {}
  }

  // Codex may emit a short progress message before its final structured turn.
  // Prefer the last complete object because the final agent message arrives last.
  for (const candidate of balancedObjects(trimmed).reverse()) {
    try {
      return parseObject(candidate);
    } catch {}
  }
  throw new NarratorJsonError(text);
}
