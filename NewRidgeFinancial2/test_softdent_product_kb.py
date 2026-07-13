"""SoftDent full product knowledge base loader + HAL policy."""

from __future__ import annotations

import unittest

from softdent_product_kb import (
    format_softdent_product_kb_hal_reply,
    load_softdent_product_kb,
    lookup_report,
    product_kb_summary,
    query_touches_softdent_product,
)


class SoftDentProductKbTests(unittest.TestCase):
    def test_kb_loads_with_toc_and_reports(self):
        kb = load_softdent_product_kb()
        self.assertGreaterEqual(int((kb.get("helpToc") or {}).get("entryCount") or 0), 1000)
        self.assertGreaterEqual(int((kb.get("reportCatalog") or {}).get("reportCountParsed") or 0), 100)
        summary = product_kb_summary()
        self.assertIn("Accounting", summary.get("categoryCounts") or {})
        self.assertGreater((summary.get("categoryCounts") or {}).get("Accounting", 0), 5)

    def test_lookup_aging_and_hal_reply(self):
        hits = lookup_report("Account Aging", limit=5)
        self.assertTrue(hits)
        self.assertTrue(any("aging" in str(h.get("name") or "").lower() for h in hits))
        text = format_softdent_product_kb_hal_reply("Account Aging")
        self.assertIn("FULL PRODUCT KB", text)
        self.assertIn("Aging", text)

    def test_query_touch_and_local_policy(self):
        self.assertTrue(query_touches_softdent_product("Tell me about the SoftDent product modules"))
        self.assertTrue(query_touches_softdent_product("What SoftDent reports are in Practice Management?"))
        from nr2_hal_gateway import try_local_policy_reply

        hit = try_local_policy_reply("Describe the SoftDent product Help catalog")
        self.assertIsNotNone(hit)
        self.assertEqual(hit.get("intent"), "policy:softdent-product-kb")
        self.assertIn("Help TOC", hit.get("text") or "")

    def test_compile_guidance_includes_product_kb(self):
        from softdent_signon import compile_softdent_signon_guidance

        guided = compile_softdent_signon_guidance("What is SoftDent charting in the full product?")
        self.assertIn("FULL PRODUCT KB", guided)


if __name__ == "__main__":
    unittest.main()
