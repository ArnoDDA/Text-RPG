function list(value) {
  return Array.isArray(value) ? value : [];
}

function presetPeople(catalog) {
  return list(catalog?.presets).flatMap((preset) => list(preset?.setup?.people));
}

function participantIds(brief) {
  const line = String(brief)
    .split("\n")
    .find((entry) => entry.startsWith("- Observable participants:"));
  if (!line) return [];
  return [...line.matchAll(/\(`([a-z0-9_]+)`;/g)].map((match) => match[1]);
}

function mentioned(person, action) {
  const text = String(action).toLocaleLowerCase("zh-CN");
  const names = [person?.name, ...list(person?.profile?.aliases)]
    .filter((value) => typeof value === "string" && value.trim());
  return names.some((name) => text.includes(name.toLocaleLowerCase("zh-CN")));
}

function speechProfileLines(profile) {
  const labels = {
    rhythm: "节奏",
    register: "用词",
    directness: "表达方式",
    humor: "幽默",
    reactions: "即时反应",
    emotional_shifts: "情绪变化",
    avoids: "避免的说法"
  };
  return Object.entries(profile && typeof profile === "object" ? profile : {})
    .filter(([key, value]) => labels[key] && typeof value === "string" && value.trim())
    .map(([key, value]) => `  - ${labels[key]}：${value.trim()}`);
}

function situationPattern(action) {
  const text = String(action);
  if (/危险|战斗|敌人|袭击|埋伏|追赶|逃跑|失控|监视|戒备|潜行|杀|攻击/.test(text)) return /危险|失控|监视|混乱/;
  if (/想念|担心|害怕|难过|伤|过去|七年|感情|喜欢|爱|关系|还好吗|怎么样/.test(text)) return /想念|担心|旧伤|不肯|被问/;
  if (/计划|办法|方案|路线|判断|同意|反对|拒绝|该不该|能不能|为什么/.test(text)) return /意见|否决|拒绝|不同意/;
  return null;
}

function styleExamples(person, action, limit = 2) {
  const examples = list(person?.profile?.dialogue_examples)
    .filter((example) => example && typeof example.situation === "string" && typeof example.text === "string");
  const preferred = situationPattern(action);
  const ordered = preferred
    ? [...examples.filter((example) => preferred.test(example.situation)), ...examples.filter((example) => !preferred.test(example.situation))]
    : examples;
  return ordered
    .slice(0, limit)
    .map((example) => `  - ${example.situation}：${example.text.trim()}`);
}

export function dialogueStyleGuide(catalog, brief, action) {
  const byId = new Map(presetPeople(catalog).map((person) => [person.id, person]));
  const present = participantIds(brief).map((id) => byId.get(id)).filter(Boolean).slice(0, 4);
  const rankedForExamples = [...present].sort((left, right) => Number(mentioned(right, action)) - Number(mentioned(left, action)));
  const exampleIds = new Set(rankedForExamples.slice(0, 2).map((person) => person.id));

  const lines = [
    "## Spoken dialogue — live conversation",
    "Keep quoted speech separate from the narrator's literary register. People speak in immediate, conversational Simplified Chinese: they may use short replies, fragments, corrections, pauses, interruptions, teasing, evasions, or an unfinished thought when that fits the moment.",
    "A spoken line needs only a local human purpose, such as answering, acknowledging, joking, deflecting, checking, disagreeing, or making a small request. It does not also need to explain lore, summarize motives, advance a relationship, and move the plot.",
    "Usually let one or two relevant people carry an exchange. Other present people may listen, react physically, continue what they were doing, or say nothing. Allow conversational space instead of giving the cast equal turns.",
    "Let emotion appear through word choice, timing, correction, and what remains unsaid. Reserve polished speeches and complete explanations for a person who deliberately chooses to give one."
  ];

  if (!present.length) return lines.join("\n");

  lines.push("", "### Present character speech anchors");
  for (const person of present) {
    const profileLines = speechProfileLines(person.profile?.speech_profile);
    if (!profileLines.length) continue;
    lines.push(`- ${person.name} (\`${person.id}\`)`, ...profileLines);
    if (exampleIds.has(person.id)) {
      const examples = styleExamples(person, action);
      if (examples.length) lines.push("  - 非剧情事实的口吻示例：", ...examples);
    }
  }
  lines.push("The examples demonstrate cadence and conversational behavior only. They are not past events, current facts, mandatory wording, or lines to repeat.");
  return lines.join("\n");
}

export const dialogueStyleInternals = { participantIds, presetPeople };
