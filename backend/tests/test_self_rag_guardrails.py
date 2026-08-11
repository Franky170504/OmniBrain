from __future__ import annotations

import unittest

from app.services.guardrail_service import RetrievalGuardrail


class SelfRagGuardrailAudit(unittest.TestCase):
    def test_weak_retrieval_requires_a_retry(self) -> None:
        self.assertFalse(RetrievalGuardrail.is_relevant([{"score": 0.22}]))
        self.assertTrue(RetrievalGuardrail.is_relevant([{"score": 0.78}]))

    def test_rewritten_query_is_narrower_than_original(self) -> None:
        original = "What were the risks?"
        self.assertNotEqual(RetrievalGuardrail.rewrite_query(original), original)
        self.assertIn("numerical evidence", RetrievalGuardrail.rewrite_query(original))

    def test_uncited_answer_is_blocked(self) -> None:
        answer = RetrievalGuardrail.validate_answer("The report was strong.", 1)
        self.assertIn("could not produce a cited answer", answer)

    def test_cited_answer_passes(self) -> None:
        answer = "Revenue increased by 10% [Source 1]."
        self.assertEqual(RetrievalGuardrail.validate_answer(answer, 1), answer)
