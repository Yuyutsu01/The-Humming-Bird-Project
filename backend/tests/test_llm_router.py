# Automated Unit Test Suite for Phase 5 Resilient LLM Router
import asyncio
import unittest
from unittest.mock import MagicMock
import sys

# Mock optional heavy external libraries if not installed in active environment
for mod_name in ['pandas', 'yfinance', 'scipy', 'numpy']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from backend.app.services.llm_router import ResilientLLMRouter
from backend.app.services.ai_analyst import ai_analyst_service

class TestEIOSLLMRouter(unittest.IsolatedAsyncioTestCase):
    """
    Unit test suite for Phase 5 Resilient Multi-Tier LLM Router & Fallback Chain.
    """

    async def test_semantic_fallback_gold(self):
        router = ResilientLLMRouter()
        # Force fallback to Tier 4 by unsetting API keys & local server flags for test isolation
        router.gemini_key = None
        router.openai_key = None
        router.use_ollama = False
        
        res = await router.query("Why is gold price surging in India?")
        self.assertEqual(res["tier_used"], 4)
        self.assertEqual(res["provider"], "Offline Semantic Engine")
        self.assertIn("Gold prices are surging", res["text"])

    async def test_semantic_fallback_oil(self):
        router = ResilientLLMRouter()
        router.gemini_key = None
        router.openai_key = None
        router.use_ollama = False
        
        res = await router.query("How does Brent Crude impact Indian inflation?")
        self.assertEqual(res["tier_used"], 4)
        self.assertEqual(res["provider"], "Offline Semantic Engine")
        self.assertIn("Brent Crude oil spikes", res["text"])

    async def test_ai_analyst_service_integration(self):
        answer = await ai_analyst_service.ask_question("Explain crude oil price impacts")
        self.assertIn("engine", answer)
        self.assertIn("query", answer)
        self.assertGreater(len(answer["india_impact"]), 0)

if __name__ == "__main__":
    unittest.main()
