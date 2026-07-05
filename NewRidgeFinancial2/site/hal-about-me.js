/**
 * HAL about me — routes through independent agent reasoning (no canned script).
 */
const HalAboutMe = (function () {
  function queryText() {
    if (typeof HalIndependentThought !== "undefined" && HalIndependentThought.aboutMeQuery) {
      return HalIndependentThought.aboutMeQuery();
    }
    return "Who am I to you, and what is your independent read of this office right now? Use live program tools first.";
  }

  return {
    queryText,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = HalAboutMe;
}
if (typeof globalThis !== "undefined") {
  globalThis.HalAboutMe = HalAboutMe;
}
if (typeof window !== "undefined") {
  window.HalAboutMe = HalAboutMe;
}
