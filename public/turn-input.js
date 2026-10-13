export function composeTurnInput(behavior, speech) {
  const action = behavior.trim();
  const words = speech.trim();
  if (!action && !words) return "";
  return [
    action ? `行动尝试：${action}` : "",
    words ? `角色说出的原话：${words}` : ""
  ].filter(Boolean).join("\n");
}
