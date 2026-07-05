/**
 * HAL independent thought — no canned scripts; text and voice from live reasoning only.
 */
const HalIndependentThought = (function () {
  function config(halModels) {
    return (halModels && halModels.config && halModels.config.independentThought) || {};
  }

  function isEnabled(halModels) {
    const c = config(halModels);
    return c.enabled !== false;
  }

  function allowScriptSpeech(halModels) {
    return !isEnabled(halModels) || config(halModels).allowScriptSpeech === true;
  }

  function promptLines(halModels) {
    if (!isEnabled(halModels)) return [];
    return [
      "INDEPENDENT THOUGHT: Never recite templates, demo lines, pickVariant canned replies, or pre-written scripts.",
      "Every answer must be composed fresh from current tool results, imports, widgets, and snapshot — not from memory of stock phrases.",
      "If the model is unavailable, say plainly what is missing and what you checked — do not fall back to a scripted paragraph.",
      "Voice reads only what you just reasoned in this turn — never a separate briefing script.",
    ];
  }

  function enhanceRoute(route, halModels) {
    if (!isEnabled(halModels) || !route) return route;
    const r = Object.assign({}, route);
    if (r.text && String(r.text).trim()) {
      r.text = "";
      r.useModel = true;
    }
    if (r.intent === "help") {
      r.text = "";
      r.useModel = true;
    }
    if (r.useHalAboutMe) {
      r.useHalAboutMe = false;
      r.useModel = true;
      r.text = "";
    }
    return r;
  }

  function aboutMeQuery() {
    return "Who am I to you, and what is your independent read of this office right now? Use live program tools first — no canned introduction.";
  }

  function shouldSkipFastExecutor(halModels) {
    return isEnabled(halModels);
  }

  function spokenExcerpt(text, halModels) {
    const raw = String(text || "").replace(/\s+/g, " ").trim();
    if (!raw) return "";
    if (!isEnabled(halModels)) return null;
    const sentences = raw.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [raw];
    return sentences.slice(0, 4).join(" ").trim();
  }

  return {
    config,
    isEnabled,
    allowScriptSpeech,
    promptLines,
    enhanceRoute,
    aboutMeQuery,
    shouldSkipFastExecutor,
    spokenExcerpt,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = HalIndependentThought;
}
if (typeof globalThis !== "undefined") {
  globalThis.HalIndependentThought = HalIndependentThought;
}
if (typeof window !== "undefined") {
  window.HalIndependentThought = HalIndependentThought;
}
