# Automated Unit Test Suite for Phase 2 Data Provider Adapters
import asyncio
import unittest
from unittest.mock import MagicMock
import sys

# Mock optional heavy external libraries if not installed in active test environment
for mod_name in ['pandas', 'yfinance', 'scipy', 'numpy']:
    if mod_name not in sys.modules:
        sys.modules[mod_name] = MagicMock()

from backend.app.adapters.base import IDataAdapter
from backend.app.adapters.yfinance_adapter import YFinanceAdapter
from backend.app.adapters.fred_adapter import FREDAdapter
from backend.app.adapters.worldbank_adapter import WorldBankAdapter
from backend.app.adapters.rbi_adapter import RBIAdapter
from backend.app.adapters.rss_adapter import RSSAdapter
from backend.app.adapters.csv_adapter import CSVAdapter
from backend.app.core.container import container, DependencyContainer

class TestDataAdapters(unittest.IsolatedAsyncioTestCase):
    """
    Unit test cases for all 6 Data Provider Adapters and DI Container resolution.
    """
    
    async def test_yfinance_adapter(self):
        adapter = YFinanceAdapter()
        self.assertEqual(adapter.provider_name, "yfinance")
        
        # Test fallback / fetch
        price, change = await adapter.fetch_ticker_data("^NSEI")
        self.assertGreater(price, 0.0)
        
        snapshot = await adapter.fetch_snapshot(["^NSEI", "^GSPC"])
        self.assertIn("^NSEI", snapshot)
        self.assertEqual(snapshot["^NSEI"]["provider"], "yfinance")
        
        health = await adapter.get_health()
        self.assertEqual(health["provider"], "yfinance")
        self.assertIn(health["status"], ["healthy", "degraded", "unhealthy"])

    async def test_fred_adapter(self):
        adapter = FREDAdapter()
        self.assertEqual(adapter.provider_name, "FRED")
        
        ind = await adapter.fetch_indicator("FEDFUNDS")
        self.assertEqual(ind["symbol"], "FEDFUNDS")
        self.assertEqual(ind["latest_value"], 5.25)
        self.assertEqual(ind["provider"], "FRED")
        
        snapshot = await adapter.fetch_snapshot(["FEDFUNDS", "GS10"])
        self.assertIn("FEDFUNDS", snapshot)
        
        health = await adapter.get_health()
        self.assertEqual(health["status"], "healthy")

    async def test_worldbank_adapter(self):
        adapter = WorldBankAdapter()
        self.assertEqual(adapter.provider_name, "WorldBank")
        
        ind = await adapter.fetch_indicator("NY.GDP.MKTP.KD.ZG")
        self.assertEqual(ind["symbol"], "NY.GDP.MKTP.KD.ZG")
        self.assertEqual(ind["country"], "India")
        
        snapshot = await adapter.fetch_snapshot(["NY.GDP.MKTP.KD.ZG"])
        self.assertIn("NY.GDP.MKTP.KD.ZG", snapshot)
        
        health = await adapter.get_health()
        self.assertEqual(health["status"], "healthy")

    async def test_rbi_adapter(self):
        adapter = RBIAdapter()
        self.assertEqual(adapter.provider_name, "RBI")
        
        ind = await adapter.fetch_indicator("RBI_REPO")
        self.assertEqual(ind["symbol"], "RBI_REPO")
        self.assertEqual(ind["latest_value"], 6.50)
        
        snapshot = await adapter.fetch_snapshot(["RBI_REPO", "RBI_CRR"])
        self.assertIn("RBI_REPO", snapshot)
        
        health = await adapter.get_health()
        self.assertEqual(health["status"], "healthy")

    async def test_rss_adapter(self):
        adapter = RSSAdapter()
        self.assertEqual(adapter.provider_name, "RSS")
        
        feed = await adapter.fetch_news_feed(limit=5)
        self.assertGreater(len(feed), 0)
        
        ind = await adapter.fetch_indicator("Inflation")
        self.assertEqual(ind["provider"], "RSS")
        self.assertGreater(len(ind["articles"]), 0)
        
        health = await adapter.get_health()
        self.assertEqual(health["status"], "healthy")

    async def test_csv_adapter(self):
        adapter = CSVAdapter()
        self.assertEqual(adapter.provider_name, "CSV")
        
        res = await adapter.fetch_indicator("mock_series")
        self.assertEqual(res["symbol"], "mock_series")
        self.assertEqual(res["provider"], "CSV")
        self.assertGreater(len(res["data"]), 0)
        
        health = await adapter.get_health()
        self.assertEqual(health["provider"], "CSV")

    def test_container_adapter_resolutions(self):
        self.assertIsInstance(container.resolve(YFinanceAdapter), YFinanceAdapter)
        self.assertIsInstance(container.resolve(FREDAdapter), FREDAdapter)
        self.assertIsInstance(container.resolve(WorldBankAdapter), WorldBankAdapter)
        self.assertIsInstance(container.resolve(RBIAdapter), RBIAdapter)
        self.assertIsInstance(container.resolve(RSSAdapter), RSSAdapter)
        self.assertIsInstance(container.resolve(CSVAdapter), CSVAdapter)

if __name__ == "__main__":
    unittest.main()
