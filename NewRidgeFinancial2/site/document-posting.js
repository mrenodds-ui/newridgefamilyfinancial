/**
 * Document posting validation and local audit trail (human-reviewed only).
 */
const DocumentPosting = (function () {
  function parseMoney(value) {
    const amount = Number(String(value || "").replace(/[^0-9.-]/g, ""));
    return Number.isFinite(amount) ? amount : 0;
  }

  function validateDocumentStatusTransition(doc, nextStatus, opts) {
    const issues = [];
    const vendor = String((doc && doc.vendor) || "").trim();
    const amount = parseMoney(doc && doc.amount);
    const date = String((doc && doc.date) || "").trim();
    if (nextStatus === "Ready to Post" || nextStatus === "Posted") {
      if (!vendor || vendor === "—") issues.push("Vendor or entity is required before posting review.");
      if (!date || date === "—") issues.push("Document date is required before posting review.");
      if (!amount) issues.push("Document amount is required before posting review.");
    }
    if (nextStatus === "Posted") {
      const reviewer = String((opts && opts.reviewedBy) || (doc && doc.reviewedBy) || "").trim();
      if (!reviewer) issues.push("Reviewer name is required before marking Posted.");
    }
    return { ok: issues.length === 0, issues };
  }

  function buildPostingAuditEntry({ doc, previousStatus, nextStatus, reviewedBy, actor, note }) {
    const at = new Date().toISOString();
    return {
      id: `audit-${Date.now().toString(36)}-${Math.floor(Math.random() * 1e4).toString(36)}`,
      at,
      docId: String((doc && doc.id) || "").trim(),
      vendor: String((doc && doc.vendor) || "").trim(),
      amount: String((doc && doc.amount) || "").trim(),
      fromStatus: previousStatus || null,
      toStatus: nextStatus,
      reviewedBy: reviewedBy ? String(reviewedBy).trim() : null,
      actor: actor ? String(actor).trim() : "Staff",
      note: note ? String(note).trim() : null,
    };
  }

  function appendPostingAudit(state, entry, limit) {
    if (!state || !entry) return state;
    const max = typeof limit === "number" ? limit : 100;
    const audit = Array.isArray(state.postingAudit) ? state.postingAudit.slice() : [];
    audit.unshift(entry);
    if (audit.length > max) audit.length = max;
    state.postingAudit = audit;
    return state;
  }

  return {
    parseMoney,
    validateDocumentStatusTransition,
    buildPostingAuditEntry,
    appendPostingAudit,
  };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = DocumentPosting;
}
if (typeof window !== "undefined") {
  window.DocumentPosting = DocumentPosting;
}
