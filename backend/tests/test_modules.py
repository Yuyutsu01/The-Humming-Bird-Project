# Automated Unit Test Suite for Phase 3 EIOS Modules and Repositories
import asyncio
import unittest
from unittest.mock import MagicMock
import sys

# Mock optional heavy external libraries if not installed in active environment
for mod_name in ['pandas', 'yfinance', 'scipy', 'numpy']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from backend.app.repositories.postgres_repo import PostgresRepository
from backend.app.repositories.timeseries_repo import TimeSeriesRepository
from backend.app.repositories.graph_repo import GraphRepository
from backend.app.repositories.vector_repo import VectorRepository
from backend.app.core.container import container
from backend.app.main import app

class TestEIOSModulesAndRepositories(unittest.IsolatedAsyncioTestCase):
    """
    Unit test suite for Phase 3 Repositories, Feature Plugins, and Gateway Auto-Discovery.
    """
    
    async def test_postgres_repository(self):
        repo = PostgresRepository()
        saved = await repo.save({"id": "user_01", "name": "Analyst User", "role": "economist"})
        self.assertEqual(saved["id"], "user_01")
        
        fetched = await repo.get_by_id("user_01")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["name"], "Analyst User")
        
        all_recs = await repo.list_all({"role": "economist"})
        self.assertEqual(len(all_recs), 1)
        
        deleted = await repo.delete("user_01")
        self.assertTrue(deleted)

    async def test_timeseries_repository(self):
        repo = TimeSeriesRepository()
        point = await repo.save({"symbol": "^NSEI", "price": 22800.0, "change_pct": 0.75})
        self.assertEqual(point["symbol"], "^NSEI")
        
        latest = await repo.get_by_id("^NSEI")
        self.assertIsNotNone(latest)
        self.assertEqual(latest["price"], 22800.0)
        
        history = await repo.list_all({"symbol": "^NSEI"})
        self.assertGreater(len(history), 0)

    async def test_graph_repository(self):
        repo = GraphRepository()
        node = await repo.save({"id": "oil", "label": "Crude Oil"})
        self.assertEqual(node["id"], "oil")
        
        edge = await repo.add_edge("oil", "usd_inr", "Weakens Rupee", "+")
        self.assertEqual(edge["source"], "oil")
        
        edges = await repo.get_edges()
        self.assertEqual(len(edges), 1)

    async def test_vector_repository(self):
        repo = VectorRepository()
        doc = await repo.save({"title": "RBI Inflation Report", "content": "Consumer inflation in India moderated."})
        self.assertIsNotNone(doc.get("id"))
        
        results = await repo.search_similar("inflation India")
        self.assertGreater(len(results), 0)

    def test_repository_container_resolutions(self):
        self.assertIsInstance(container.resolve(PostgresRepository), PostgresRepository)
        self.assertIsInstance(container.resolve(TimeSeriesRepository), TimeSeriesRepository)
        self.assertIsInstance(container.resolve(GraphRepository), GraphRepository)
        self.assertIsInstance(container.resolve(VectorRepository), VectorRepository)

    def test_dynamic_plugin_route_mounting(self):
        mounted_paths = [getattr(route, "path", "") for route in app.routes]
        
        # Verify dynamic plugin paths exist in gateway
        self.assertTrue(any("/api/market/snapshot" in p for p in mounted_paths))
        self.assertTrue(any("/api/news" in p for p in mounted_paths))
        self.assertTrue(any("/api/scenario/simulate" in p for p in mounted_paths))
        self.assertTrue(any("/api/economy/indicators" in p for p in mounted_paths))
        self.assertTrue(any("/api/ai/ask" in p for p in mounted_paths))

if __name__ == "__main__":
    unittest.main()
