# Automated Unit Test Suite for Phase 4 EIOS Autonomous Swarm Agents
import asyncio
import unittest
from unittest.mock import MagicMock
import sys

# Mock optional heavy external libraries if not installed in active environment
for mod_name in ['pandas', 'yfinance', 'scipy', 'numpy']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from backend.app.core.supervisor import SupervisorAgent
from backend.app.core.container import container
from backend.app.modules.news.agents.news_agent import NewsAgent
from backend.app.modules.macro.agents.macro_agent import MacroAgent
from backend.app.modules.forecast.agents.forecast_agent import ForecastAgent
from backend.app.modules.knowledge_graph.agents.graph_agent import GraphAgent
from backend.app.modules.risk.agents.risk_agent import RiskAgent

class TestEIOSSwarmAgents(unittest.IsolatedAsyncioTestCase):
    """
    Unit test suite for Phase 4 Autonomous Swarm Agents & Supervisor Orchestration.
    """

    def test_supervisor_intent_parsing(self):
        supervisor = SupervisorAgent()
        
        # Test macro intent
        tasks_oil = supervisor.parse_intent("Why is Brent Crude oil price rising?")
        agents_oil = [t["agent"] for t in tasks_oil]
        self.assertIn("macro_agent", agents_oil)
        self.assertIn("risk_agent", agents_oil)
        
        # Test forecast intent
        tasks_fc = supervisor.parse_intent("Show me inflation forecast for next year")
        agents_fc = [t["agent"] for t in tasks_fc]
        self.assertIn("forecast_agent", agents_fc)

    async def test_supervisor_orchestration(self):
        supervisor = container.resolve(SupervisorAgent)
        res = await supervisor.orchestrate("Why is gold surging?")
        
        self.assertIn("engine", res)
        self.assertIn("Gold Surge", res["title"])
        self.assertGreater(len(res["india_impact"]), 0)
        self.assertIn("tasks_executed", res)

    async def test_news_agent_sentiment(self):
        agent = NewsAgent()
        score_pos = await agent.analyze_sentiment("Markets rise on economic growth surge")
        self.assertEqual(score_pos["sentiment"], "bullish")
        
        score_neg = await agent.analyze_sentiment("Inflation fall drops market sentiment risk")
        self.assertEqual(score_neg["sentiment"], "bearish")

    async def test_macro_agent_sensitivity(self):
        agent = MacroAgent()
        sens = await agent.compute_sensitivity(oil_price=95.0, fed_rate=5.50)
        self.assertEqual(sens["oil_price"], 95.0)
        self.assertIsInstance(sens["simulated_cpi_delta"], float)

    async def test_forecast_agent_projection(self):
        agent = ForecastAgent()
        proj = await agent.generate_projection("CPI Inflation", "Prophet")
        self.assertEqual(proj["model"], "Prophet")
        self.assertEqual(proj["projected_growth"], 6.8)

    async def test_graph_agent_causality(self):
        agent = GraphAgent()
        chain = await agent.trace_causal_chain("oil", "stock_market")
        self.assertEqual(len(chain), 2)
        self.assertEqual(chain[0]["source"], "oil")

    async def test_risk_agent_evaluation(self):
        agent = RiskAgent()
        scores = await agent.evaluate_sector_risks()
        self.assertGreaterEqual(len(scores), 3)
        self.assertEqual(scores[0]["sector"], "Aviation")

if __name__ == "__main__":
    unittest.main()
