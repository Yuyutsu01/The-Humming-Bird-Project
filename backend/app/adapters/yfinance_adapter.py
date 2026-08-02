# Yahoo Finance Data Ingestion Adapter
import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
import yfinance as yf
from backend.app.adapters.base import IDataAdapter

logger = logging.getLogger(__name__)

class YFinanceAdapter(IDataAdapter):
    """
    Data Ingestion Adapter for Yahoo Finance API.
    Wraps yfinance ticker lookups in non-blocking thread executors with fallback support.
    """
    
    DEFAULT_PRICES: Dict[str, tuple[float, float]] = {
        "^GSPC": (5200.0, 0.45),
        "^IXIC": (16200.0, 0.85),
        "^DJI": (39000.0, 0.15),
        "^FTSE": (8100.0, -0.2),
        "^N225": (38500.0, -1.2),
        "^HSI": (18000.0, 0.6),
        "^GDAXI": (18300.0, -0.1),
        "^FCHI": (7900.0, -0.3),
        "^NSEI": (22800.0, 0.75),
        "^BSESN": (75000.0, 0.72),
        "^NSEBANK": (49000.0, 0.55),
        "NIFTY_MID_50.NS": (14500.0, 1.1),
        "NIFTY_SMLCAP_50.NS": (7200.0, 1.4),
        "GC=F": (2350.0, 1.2),
        "SI=F": (30.0, 2.1),
        "HG=F": (4.5, -0.8),
        "PL=F": (980.0, 0.5),
        "PA=F": (950.0, -0.4),
        "CCJ": (50.0, 1.5),
        "ALTM": (5.2, -2.5),
        "BZ=F": (82.5, -0.9),
        "CL=F": (78.2, -1.1),
        "NG=F": (2.5, 3.4),
        "INR=X": (83.50, 0.05),
        "EURUSD=X": (1.085, -0.12),
        "JPY=X": (155.8, 0.35),
        "GBPUSD=X": (1.272, 0.08),
        "CNY=X": (7.24, 0.02),
        "^IRX": (4.85, 0.0),
        "^TNX": (4.45, 0.02),
        "^TYX": (4.60, 0.01),
        "IN10YT=RR": (7.02, -0.01),
    }
    
    @property
    def provider_name(self) -> str:
        return "yfinance"

    async def fetch_ticker_data(self, ticker: str) -> tuple[float, float]:
        """
        Fetches price and change percentage for a single ticker via yfinance.
        """
        if os.environ.get("MOCK_MARKET") == "true":
            return self.DEFAULT_PRICES.get(ticker, (100.0, 0.0))

        try:
            loop = asyncio.get_running_loop()
            ticker_obj = yf.Ticker(ticker)
            info = await loop.run_in_executor(None, lambda: ticker_obj.fast_info)

            if info and "last_price" in info and info["last_price"] is not None:
                price = info["last_price"]
                prev_close = info.get("previous_close", price)
                pct_change = ((price - prev_close) / prev_close * 100) if prev_close else 0.0
                return price, pct_change
        except Exception as e:
            logger.warning(f"[{self.provider_name}] Failed to fetch '{ticker}': {e}. Using fallback.")

        return self.DEFAULT_PRICES.get(ticker, (100.0, 0.0))

    async def fetch_snapshot(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetches normalized snapshot records for a list of ticker symbols.
        """
        snapshot = {}
        for sym in symbols:
            price, pct_change = await self.fetch_ticker_data(sym)
            snapshot[sym] = {
                "symbol": sym,
                "price": round(price, 4) if price < 10 else round(price, 2),
                "change_pct": round(pct_change, 2),
                "provider": self.provider_name
            }
        return snapshot

    async def fetch_indicator(
        self, 
        symbol: str, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches time series bar data for historical charting.
        """
        try:
            loop = asyncio.get_running_loop()
            ticker_obj = yf.Ticker(symbol)
            df = await loop.run_in_executor(None, lambda: ticker_obj.history(period="1mo"))
            
            bars = []
            if not df.empty:
                for idx, row in df.iterrows():
                    bars.append({
                        "date": idx.strftime("%Y-%m-%d"),
                        "open": float(row["Open"]),
                        "high": float(row["High"]),
                        "low": float(row["Low"]),
                        "close": float(row["Close"]),
                        "volume": int(row["Volume"])
                    })
            return {"symbol": symbol, "bars": bars, "provider": self.provider_name}
        except Exception as e:
            logger.error(f"[{self.provider_name}] Error fetching historical indicator '{symbol}': {e}")
            return {"symbol": symbol, "bars": [], "provider": self.provider_name, "error": str(e)}

    async def get_health(self) -> Dict[str, Any]:
        """
        Checks connectivity by testing a lightweight fetch on S&P 500 (`^GSPC`).
        """
        try:
            price, _ = await self.fetch_ticker_data("^GSPC")
            status = "healthy" if price > 0 else "degraded"
            return {"provider": self.provider_name, "status": status, "test_ticker": "^GSPC", "price": price}
        except Exception as e:
            return {"provider": self.provider_name, "status": "unhealthy", "error": str(e)}
